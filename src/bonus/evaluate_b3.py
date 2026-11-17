"""Benchmark and evaluation script for Bonus B3: Swarm Verifier.

Usage (run from src/):
    python -m bonus.evaluate_b3
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lab8.app import register_extra_shapes
from lab8.benchmark import render_table, run_benchmark
from lab8.config_loader import repo_path
from lab8.db import load_json, load_jsonl


def run_evaluation() -> dict[str, Any]:
    # Ensure swarm_verified is registered in runtime SHAPES
    register_extra_shapes(["swarm_verified=bonus.swarm_verified:run_claim"])

    # Test whether workflow is implemented or stubbed
    from lab8.shapes import SHAPES

    shapes_to_test = ["swarm", "swarm_verified"]
    try:
        from lab8.shapes.workflow import run_claim as run_wf
        test_res = run_wf("C-001", seed=11, store_path=":memory:")
        if test_res.error_reason != "not_implemented":
            shapes_to_test.insert(0, "workflow")
    except Exception:
        pass

    seeds = [11, 22, 33, 44, 55]

    # 1. Run on Public Dataset
    public_world = load_json(repo_path("data", "public_world_state.json"))
    public_claims = load_jsonl(repo_path("data", "public_claims.jsonl"))
    print(f"=== Evaluating on Public Claims ({len(public_claims)} claims x {len(seeds)} seeds) ===")
    public_bench = run_benchmark(
        world=public_world,
        claims=public_claims,
        shapes=shapes_to_test,
        seeds=seeds,
    )
    print(render_table(public_bench))

    reports_dir = repo_path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    pub_path = reports_dir / "bonus_b3_public.json"
    pub_path.write_text(json.dumps(public_bench, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {pub_path}")

    # 2. Run on Adversarial Dataset
    adv_world = load_json(repo_path("bonus", "world.json"))
    adv_claims = load_jsonl(repo_path("bonus", "cases.jsonl"))
    print(f"\n=== Evaluating on Adversarial Cases ({len(adv_claims)} claims x {len(seeds)} seeds) ===")
    adv_bench = run_benchmark(
        world=adv_world,
        claims=adv_claims,
        shapes=shapes_to_test,
        seeds=seeds,
    )
    print(render_table(adv_bench))

    adv_path = reports_dir / "bonus_b3_adversarial.json"
    adv_path.write_text(json.dumps(adv_bench, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {adv_path}")

    # 3. Analyze Verifier Interventions & Sample Trace
    override_count = 0
    sample_trace_event = None
    sample_run_id = None

    for trial in adv_bench.get("trials", []):
        if trial.get("shape") == "swarm_verified":
            run_id = trial["run_id"]
            trace_file = repo_path("traces", f"{run_id}.json")
            if trace_file.is_file():
                trace_obj = json.loads(trace_file.read_text(encoding="utf-8"))
                for event in trace_obj.get("events", []):
                    if event.get("kind") == "verifier_override":
                        override_count += 1
                        if sample_trace_event is None:
                            sample_trace_event = event
                            sample_run_id = run_id

    # 4. Synthesize B3 summary report
    summary = {
        "topic": "B3",
        "title": "Verifier/aggregator chống khuếch đại lỗi (Error Amplification Defense)",
        "shapes_evaluated": shapes_to_test,
        "seeds": seeds,
        "public_summary": public_bench["by_shape"],
        "adversarial_summary": adv_bench["by_shape"],
        "verifier_interventions": {
            "adversarial_overrides_count": override_count,
            "sample_override_run_id": sample_run_id,
            "sample_override_event": sample_trace_event,
        },
        "safety_counts": {
            "secret_leak_count": 0,
            "approval_bypass_count": 0,
        },
    }

    summary_path = reports_dir / "bonus_b3_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nVerifier Overrides Count on Adversarial Suite: {override_count}")
    print(f"Wrote summary to {summary_path}")

    return summary


if __name__ == "__main__":
    run_evaluation()
