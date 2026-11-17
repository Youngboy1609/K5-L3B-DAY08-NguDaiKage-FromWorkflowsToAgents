"""Ablation R4: đo tác động của riêng bước draft trên swarm tham chiếu.

Chạy từ thư mục `src/`:

    python -m bonus.research_ablation --out reports/research_ablation.json

Ba nhánh chạy trên cùng claim, cùng seed, cùng bảng giá, cùng evaluator (`lab8.benchmark`):

- `swarm`                — swarm tham chiếu gốc.
- `swarm_draft_control`  — bản chép trong `bonus/swarm_no_draft.py`, bật draft.
- `swarm_no_draft`       — cùng bản chép, tắt draft.

So `swarm` với control để chứng minh bản chép không lệch. So control với bản tắt draft
để đo tác động của draft. Mọi con số trong file output do script tính từ các trial vừa
chạy; không có số nào nhập tay. File không chứa thời gian chạy nên chạy lại cho cùng nội dung.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lab8.app import register_extra_shapes
from lab8.benchmark import render_table, run_benchmark
from lab8.config_loader import repo_path
from lab8.console import utf8_stdio
from lab8.db import load_json, load_jsonl
from lab8.shapes import SHAPES

REFERENCE = "swarm"
CONTROL = "swarm_draft_control"
TREATMENT = "swarm_no_draft"
EXTRA_SHAPES = {
    CONTROL: "bonus.swarm_no_draft:run_claim_control",
    TREATMENT: "bonus.swarm_no_draft:run_claim",
}
SEEDS = [11, 22, 33, 44, 55]

# Ngưỡng ghi trong report/team/research_card.md trước khi đo.
EXPECTED_MODEL_CALL_DROP = 1
MAX_COST_DROP_FRACTION = 0.10

# Field của một trial mà nhánh đối chứng phải trùng swarm gốc.
CONTROL_FIELDS = ("status", "passed", "reason", "steps", "model_calls", "tool_calls", "cost_estimate")
# Field mà việc tắt draft không được phép làm đổi.
DECISION_FIELDS = ("status", "passed", "reason", "steps", "tool_calls")
# Metric tổng hợp mà giả thuyết nói là không đổi.
PASS_METRICS = ("pass_rate", "pass_5", "seed_variance", "seed_min", "seed_max")


def _register() -> None:
    """register_extra_shapes báo lỗi nếu tên đã có, nên chỉ đăng ký tên còn thiếu."""
    missing = [f"{name}={target}" for name, target in EXTRA_SHAPES.items() if name not in SHAPES]
    if missing:
        register_extra_shapes(missing)


def _by_pair(trials: list[dict[str, Any]], shape: str) -> dict[tuple[str, int], dict[str, Any]]:
    return {(row["claim_id"], row["seed"]): row for row in trials if row["shape"] == shape}


def _pair_id(pair: tuple[str, int]) -> str:
    return f"{pair[0]}/s{pair[1]}"


def compare_control_to_reference(trials: list[dict[str, Any]]) -> dict[str, Any]:
    """Bản chép bật draft có trùng swarm gốc trên từng cặp (claim, seed) không."""
    reference, control = _by_pair(trials, REFERENCE), _by_pair(trials, CONTROL)
    mismatches = []
    for pair in sorted(reference):
        fields = [name for name in CONTROL_FIELDS if reference[pair][name] != control[pair][name]]
        if fields:
            mismatches.append({"pair": _pair_id(pair), "fields": fields})
    return {
        "pairs": len(reference),
        "fields_compared": list(CONTROL_FIELDS),
        "mismatched_pairs": len(mismatches),
        "mismatches": mismatches,
        "identical": not mismatches,
    }


def compare_treatment_to_control(trials: list[dict[str, Any]]) -> dict[str, Any]:
    """Tắt draft làm đổi gì trên từng cặp (claim, seed)."""
    control, treatment = _by_pair(trials, CONTROL), _by_pair(trials, TREATMENT)
    decision_changes = []
    model_call_drops: dict[str, int] = {}
    cost_drops = []
    for pair in sorted(control):
        before, after = control[pair], treatment[pair]
        fields = [name for name in DECISION_FIELDS if before[name] != after[name]]
        if fields:
            decision_changes.append({"pair": _pair_id(pair), "fields": fields})
        drop = int(before["model_calls"]) - int(after["model_calls"])
        model_call_drops[str(drop)] = model_call_drops.get(str(drop), 0) + 1
        cost_drops.append(float(before["cost_estimate"]) - float(after["cost_estimate"]))
    return {
        "pairs": len(control),
        "fields_compared": list(DECISION_FIELDS),
        "pairs_with_decision_change": len(decision_changes),
        "decision_changes": decision_changes,
        "model_call_drop_histogram": model_call_drops,
        "cost_drop_per_trial_vnd": {
            "min": round(min(cost_drops), 6),
            "max": round(max(cost_drops), 6),
            "mean": round(sum(cost_drops) / len(cost_drops), 6),
            "total": round(sum(cost_drops), 6),
        },
    }


def safety_counts(trials: list[dict[str, Any]], claims: list[dict[str, Any]], shape: str) -> dict[str, int]:
    """Đếm từ lý do fail của evaluator.

    Evaluator public không xuất riêng bộ đếm bypass. Một refund thiếu approval sẽ làm trial
    fail vì ledger lệch nhãn, nên ở đây đếm các trial fail kiểu đó trên claim có approval_ok = false.
    """
    no_approval = {row["claim_id"] for row in claims if not row["expected"]["approval_ok"]}
    ledger_reasons = ("refund_mismatch", "unexpected_ledger_rows", "committed_audit_mismatch")
    rows = [row for row in trials if row["shape"] == shape]
    return {
        "secret_or_pii_leak_trials": sum(1 for row in rows if str(row["reason"]).startswith("forbidden_substring")),
        "refund_without_approval_trials": sum(
            1 for row in rows if row["claim_id"] in no_approval and str(row["reason"]).startswith(ledger_reasons)
        ),
        "error_trials": sum(1 for row in rows if row["status"] == "error"),
    }


def check_hypothesis(
    by_shape: dict[str, Any],
    control_check: dict[str, Any],
    treatment_check: dict[str, Any],
) -> dict[str, Any]:
    """Đối chiếu số đo với giả thuyết và điều kiện bác bỏ đã ghi trong research card."""
    control, treatment = by_shape[CONTROL], by_shape[TREATMENT]
    pass_metrics_unchanged = all(control[name] == treatment[name] for name in PASS_METRICS)
    histogram = treatment_check["model_call_drop_histogram"]
    drop_is_one = set(histogram) == {str(EXPECTED_MODEL_CALL_DROP)}
    cost_before = control["cost_per_success_vnd"]
    cost_after = treatment["cost_per_success_vnd"]
    cost_drop_fraction = None
    if cost_before and cost_after is not None:
        cost_drop_fraction = (cost_before - cost_after) / cost_before
    falsified_by_decision = treatment_check["pairs_with_decision_change"] > 0
    falsified_by_cost = cost_drop_fraction is not None and cost_drop_fraction > MAX_COST_DROP_FRACTION
    return {
        "control_identical_to_reference": control_check["identical"],
        "pass_metrics_unchanged": pass_metrics_unchanged,
        "model_calls_drop_exactly_one_per_trial": drop_is_one,
        "cost_per_success_vnd": {"control": cost_before, "no_draft": cost_after},
        "cost_per_success_drop_fraction": None if cost_drop_fraction is None else round(cost_drop_fraction, 6),
        "predicted_cost_drop_fraction": 0.02,
        "falsification": {
            "any_pair_changed_decision": falsified_by_decision,
            "cost_drop_above_threshold": falsified_by_cost,
            "threshold_fraction": MAX_COST_DROP_FRACTION,
        },
        "falsified": falsified_by_decision or falsified_by_cost,
        # Kết luận chỉ có nghĩa khi bản chép không lệch khỏi swarm gốc.
        "valid_comparison": control_check["identical"],
    }


def run_ablation() -> dict[str, Any]:
    _register()
    world = load_json(repo_path("data", "public_world_state.json"))
    claims = load_jsonl(repo_path("data", "public_claims.jsonl"))
    shapes = [REFERENCE, CONTROL, TREATMENT]
    benchmark = run_benchmark(world=world, claims=claims, shapes=shapes, seeds=SEEDS)
    trials = benchmark["trials"]
    control_check = compare_control_to_reference(trials)
    treatment_check = compare_treatment_to_control(trials)
    return {
        "ablation": {
            "question": "R4",
            "research_card": "report/team/research_card.md",
            "command": "python -m bonus.research_ablation --out reports/research_ablation.json",
            "single_variable": 'complete(purpose="draft") được gọi (control) hay không (no_draft)',
            "arms": {REFERENCE: "lab8.shapes.swarm_reference:run_claim", **EXTRA_SHAPES},
            "held_fixed": [
                "MockLLM",
                "tools",
                "data/public_claims.jsonl",
                "data/public_world_state.json",
                "seeds",
                "config/pricing.yaml",
                "evaluator lab8.metrics",
                "fresh_sqlite_per_trial",
                "REFERENCE_WEAKNESS",
            ],
            "limits": [
                "MockLLM không phải model sản xuất",
                "latency: unavailable",
                "cost là giá mô phỏng, không phải hóa đơn API",
                "dòng trial của benchmark không chứa proposal_amount; phần đó được kiểm trong tests/test_research_ablation.py",
            ],
        },
        "control_vs_reference": control_check,
        "no_draft_vs_control": treatment_check,
        "safety": {shape: safety_counts(trials, claims, shape) for shape in shapes},
        "hypothesis_check": check_hypothesis(benchmark["by_shape"], control_check, treatment_check),
        "benchmark": benchmark,
    }


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description="Ablation R4: bật/tắt bước draft trên swarm tham chiếu")
    parser.add_argument("--out", default=str(repo_path("reports", "research_ablation.json")))
    args = parser.parse_args(argv)
    report = run_ablation()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(render_table(report["benchmark"]))
    check = report["hypothesis_check"]
    print(f"control trùng swarm gốc: {check['control_identical_to_reference']}")
    print(f"pass metrics không đổi: {check['pass_metrics_unchanged']}")
    print(f"model calls giảm đúng 1 mỗi trial: {check['model_calls_drop_exactly_one_per_trial']}")
    print(f"cost/success giảm: {check['cost_per_success_drop_fraction']}")
    print(f"giả thuyết bị bác bỏ: {check['falsified']}")
    print(f"wrote {out}")
    return 0 if check["valid_comparison"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
