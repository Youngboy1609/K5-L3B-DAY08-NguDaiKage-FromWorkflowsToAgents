"""Ablation R4: bật/tắt bước draft trên swarm tham chiếu (bonus/swarm_no_draft.py).

Ba điều phải đúng thì phép so sánh mới chỉ có một biến:

1. Nhánh đối chứng (bản chép, bật draft) trùng swarm gốc. Nếu lệch, bản chép đã đổi
   thứ gì đó ngoài draft và mọi chênh lệch đo được đều không quy được cho draft.
2. Nhánh tắt draft giữ nguyên quyết định và số tool call; chỉ usage của model giảm.
3. Điểm yếu tham chiếu (seed 55 tin số ngày trong ticket) vẫn còn ở biến thể.

Mỗi lần chạy dùng một file SQLite mới, giống cách benchmark cô lập từng trial.
"""

from __future__ import annotations

import time

import pytest

from bonus.swarm_no_draft import SHAPE_CONTROL, SHAPE_NO_DRAFT
from bonus.swarm_no_draft import run_claim as swarm_no_draft
from bonus.swarm_no_draft import run_claim_control as swarm_control
from lab8.db import connect, init_store
from lab8.metrics import check_trace, trial_pass
from lab8.shapes.swarm_reference import run_claim as swarm
from tests.conftest import BY_ID, CLAIMS, WORLD

SEEDS = [11, 22, 33, 44, 55]
CLAIM_IDS = [row["claim_id"] for row in CLAIMS]

# Quyết định nghiệp vụ và phần việc không liên quan tới model.
DECISION_FIELDS = ("status", "proposal_amount", "refund_effects", "committed_audit_count", "tool_calls", "error_reason")
# Usage của model: draft là một lời gọi model, nên chỉ nhóm này được phép đổi.
USAGE_FIELDS = ("model_calls", "input_tokens", "output_tokens", "cost_estimate")


def _run(fn, tmp_path, name: str, claim_id: str, seed: int):
    """Chạy một nhánh trên DB mới. Trả về (kết quả dạng dict, pass/fail theo nhãn public)."""
    store = tmp_path / f"{name}-{claim_id}-{seed}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    started_at = time.time()
    result = fn(claim_id, seed=seed, store_path=str(store)).as_dict()
    conn = connect(store)
    try:
        passed, _reason = trial_pass(result, BY_ID[claim_id]["expected"], conn, started_at=started_at)
    finally:
        conn.close()
    return result, passed


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("claim_id", CLAIM_IDS)
def test_control_arm_reproduces_the_reference_swarm(tmp_path, claim_id, seed):
    reference, reference_passed = _run(swarm, tmp_path, "reference", claim_id, seed)
    control, control_passed = _run(swarm_control, tmp_path, "control", claim_id, seed)
    for field in DECISION_FIELDS + USAGE_FIELDS:
        assert control[field] == reference[field], field
    assert control_passed == reference_passed


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("claim_id", CLAIM_IDS)
def test_turning_draft_off_changes_model_usage_only(tmp_path, claim_id, seed):
    control, control_passed = _run(swarm_control, tmp_path, "control", claim_id, seed)
    treated, treated_passed = _run(swarm_no_draft, tmp_path, "no-draft", claim_id, seed)
    for field in DECISION_FIELDS:
        assert treated[field] == control[field], field
    assert treated_passed == control_passed
    # Mỗi claim public đi qua đúng một trong ba chỗ gọi draft.
    assert treated["model_calls"] == control["model_calls"] - 1
    assert treated["input_tokens"] < control["input_tokens"]
    assert treated["output_tokens"] < control["output_tokens"]
    assert treated["cost_estimate"] < control["cost_estimate"]


def test_reference_weakness_survives_the_ablation(tmp_path):
    """T02: ticket ghi trễ 5 ngày, order ghi 2. Seed 55 vẫn phải trả sai như swarm gốc."""
    outcomes = {seed: _run(swarm_no_draft, tmp_path, "weakness", "C-002", seed)[1] for seed in (11, 55)}
    assert outcomes == {11: True, 55: False}


@pytest.mark.parametrize(
    ("fn", "shape"),
    [(swarm_no_draft, SHAPE_NO_DRAFT), (swarm_control, SHAPE_CONTROL)],
)
def test_each_arm_has_its_own_run_id_and_a_contract_trace(public_db, fn, shape):
    started_at = time.time()
    result = fn("C-001", seed=11, store_path=str(public_db)).as_dict()
    assert result["shape"] == shape
    assert result["run_id"] == f"R-{shape}-C-001-s11"
    assert check_trace(result, started_at=started_at) == (True, "ok")
