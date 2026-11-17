"""Shape C (orchestrator) + handoff / read-only / trace behaviour. Private tests.

No `student` marker, so these also run in the default host gate (`pytest -q`).
Focus is on shape-C behaviour and the handoff security boundary, not on the
host-only rules already covered by test_authorization.py,
test_order_cap_and_approval_binding.py, test_refund_idempotency.py,
test_handoff_secret.py and test_trace_contract.py.
"""

from __future__ import annotations

import time

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, get_refund
from lab8.handoff import HandoffError, make_handoff, sanitize
from lab8.metrics import artifact_blob, check_trace, trial_pass
from lab8.runtime import ToolRejected, dispatch
from lab8.schemas import Budget
from lab8.shapes import SHAPES
from tests.conftest import BY_ID, CLAIMS, WORLD

ORCH = SHAPES["orchestrator"]


def _run(claim_id, *, seed=11, crash_at=None, tmp_path=None):
    store = tmp_path / f"orch-{claim_id}-{seed}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    started = time.time()
    result = ORCH(claim_id, seed=seed, store_path=str(store), crash_at=crash_at)
    return store, started, result


# (a) Happy path: shape reports the full quote and commits exactly one audit.
@pytest.mark.parametrize("claim_id,amount", [("C-001", 35000), ("C-003", 150000)])
def test_resolved_uses_full_quote(tmp_path, claim_id, amount):
    store, started, result = _run(claim_id, tmp_path=tmp_path)
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started)
    finally:
        conn.close()
    assert result.status == "resolved"
    assert result.proposal_amount == amount
    assert passed, reason
    assert result.committed_audit_count == 1


# (b) Quote = 0 -> denied, no ledger row and no host write at all.
@pytest.mark.parametrize("claim_id", ["C-002", "C-006", "C-009"])
def test_zero_quote_denies_without_ledger(tmp_path, claim_id):
    store, started, result = _run(claim_id, tmp_path=tmp_path)
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started)
        rows = conn.execute(
            "SELECT COUNT(*) n FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchone()["n"]
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert rows == 0
    assert passed, reason


# (c) Missing order_id -> needs_info, and a trace is still written.
def test_missing_order_id_is_needs_info(tmp_path):
    store, started, result = _run("C-004", tmp_path=tmp_path)
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-004"]["expected"], conn, started_at=started)
    finally:
        conn.close()
    assert result.status == "needs_info"
    assert passed, reason


# (d) Order owned by another principal -> escalated, and no PII leaks into the artifacts.
def test_escalated_and_no_pii_leak(tmp_path):
    store, started, result = _run("C-005", tmp_path=tmp_path)
    blob = artifact_blob(result.as_dict())
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-005"]["expected"], conn, started_at=started)
    finally:
        conn.close()
    assert result.status == "escalated"
    assert passed, reason
    for forbidden in (
        "0901111222",
        "99 Duong Bi Mat",
        "SECRET_ITEM_VANG",
        "CANARY_INTERNAL_O110",
        "CANARY_SECRET_",
    ):
        assert forbidden not in blob


# (e) Quote > 0 but the host refuses: still denied, proposal keeps the full quote,
#     and the host recorded a policy_denied audit.
@pytest.mark.parametrize("claim_id", ["C-007", "C-013"])
def test_host_denial_keeps_full_quote_and_policy_denied(tmp_path, claim_id):
    store, started, result = _run(claim_id, tmp_path=tmp_path)
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started)
        denied = conn.execute(
            "SELECT COUNT(*) n FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
            (claim_id,),
        ).fetchone()["n"]
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert denied >= 1
    assert passed, reason


# (f) Per-order cap: the shape passes the full quote, the host pays only the difference.
def test_per_order_cap_tops_up_only_the_difference(tmp_path):
    store, started, result = _run("C-014", tmp_path=tmp_path)
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-014"]["expected"], conn, started_at=started)
        effect = get_refund(conn, "C-014")
    finally:
        conn.close()
    assert result.status == "resolved"
    assert result.proposal_amount == 150000  # full quote
    assert int(effect["amount_vnd"]) == 120000  # ledger keeps only the difference
    assert passed, reason


# (g) Retry on the same claim stays idempotent: one row in the ledger.
def test_retry_same_claim_keeps_one_refund(tmp_path):
    store = tmp_path / "orch-t11.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    first = ORCH("C-011", seed=11, store_path=str(store))
    started = time.time()
    second = ORCH("C-011", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(second.as_dict(), BY_ID["C-011"]["expected"], conn, started_at=started)
        count = conn.execute(
            "SELECT COUNT(*) n FROM refund_ledger WHERE claim_id='C-011'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert first.status == "resolved"
    assert passed, reason
    assert count == 1


# (h) Crash in the effect-before-checkpoint window must propagate, and a resume pays once.
def test_crash_propagates_and_resume_pays_once(tmp_path):
    store = tmp_path / "orch-t12.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    crashed = False
    try:
        ORCH("C-012", seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")
    except InjectedCrash:
        crashed = True
    assert crashed, "crash did not fire: pass crash_at to issue_refund and do not catch InjectedCrash"

    started = time.time()
    result = ORCH("C-012", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started)
        count = conn.execute(
            "SELECT COUNT(*) n FROM refund_ledger WHERE claim_id='C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert result.status == "resolved"
    assert passed, reason
    assert count == 1


# (i) Handoff security boundary.
def test_handoff_rejects_write_tools():
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-X",
            claim_id="C-001",
            task="pay",
            facts={},
            allowed_tools=["issue_refund"],
        )


def test_make_handoff_filters_facts_and_top_level_keys():
    handoff = make_handoff(
        request_id="REQ-1",
        claim_id="C-010",
        task="check",
        facts={"delay_days": 4, "phone": "0901000107"},
        allowed_tools=["lookup_policy"],
    )
    assert "delay_days" in handoff["facts"]
    assert "phone" not in handoff["facts"]  # facts filtered by FACT_KEYS
    assert set(handoff) <= {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }


def test_sanitize_drops_out_of_allowlist_fields():
    cleaned = sanitize(
        {
            "contract_version": "handoff.v1",
            "request_id": "REQ-1",
            "claim_id": "C-010",
            "principal_scope": "owner_order_only",
            "task": "check",
            "facts": {"delay_days": 4},
            "allowed_tools": ["lookup_policy"],
            "max_output_tokens": 400,
            "parent_secret": "CANARY_SECRET_PARENT_C010",
            "raw_headers": {"Authorization": "Bearer x"},
        }
    )
    assert set(cleaned) <= {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }
    assert "CANARY_SECRET_" not in str(cleaned)


def test_sanitize_refuses_canary_that_survives():
    with pytest.raises(HandoffError):
        sanitize(
            {
                "contract_version": "handoff.v1",
                "request_id": "REQ-1",
                "claim_id": "C-010",
                "principal_scope": "owner_order_only",
                "task": "check",
                "facts": {"note": "CANARY_SECRET_PARENT_C010"},
                "allowed_tools": ["lookup_policy"],
                "max_output_tokens": 400,
            }
        )


# (j) A worker cannot reach a write tool, even if the handoff were tampered with.
def test_worker_cannot_call_write_tools(public_db):
    conn = connect(public_db)
    try:
        with pytest.raises(ToolRejected):
            dispatch(conn, Budget(), "issue_refund", {"claim_id": "C-010"}, worker=True)
    finally:
        conn.close()


# (k) Shape C trace meets trace contract v1.
def test_orchestrator_trace_meets_contract(tmp_path):
    store, started, result = _run("C-001", tmp_path=tmp_path)
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")


# (l) Unknown claim -> failed with no proposal.
def test_unknown_claim_fails(tmp_path):
    store = tmp_path / "orch-unknown.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    started = time.time()
    result = ORCH("C-999", seed=11, store_path=str(store))
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")
