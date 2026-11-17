"""Unit and integration tests for Bonus B3: Swarm Verifier."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bonus.swarm_verified import run_claim as run_swarm_verified
from lab8.app import prepare_store
from lab8.config_loader import repo_path
from lab8.db import connect, load_json, load_jsonl
from lab8.durability import InjectedCrash
from lab8.metrics import check_trace, trial_pass
from lab8.shapes.swarm_reference import run_claim as run_swarm_reference


def _init_adv_store(tmp_path: Path, name: str) -> Path:
    store = tmp_path / f"{name}.sqlite"
    world_path = repo_path("bonus", "world.json")
    claims_path = repo_path("bonus", "cases.jsonl")
    prepare_store(store, world_path=world_path, claims_path=claims_path)
    return store


def test_b3_verifier_overrides_discrepancy_and_emits_event(tmp_path: Path):
    """Test 1: Verifier detects model override, corrects facts, and emits verifier_override event."""
    store = _init_adv_store(tmp_path, "test_b3_override")
    # ADV-001 has order delay = 2, but ticket claims "trễ 6 ngày".
    # At seed 55, swarm weakness would trust ticket (6 days), quoting 25000 VND.
    # swarm_verified must detect discrepancy, override back to 2, quote 0 VND, and return 'denied'.
    result = run_swarm_verified("ADV-001", seed=55, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0

    # Verify trace exists, conforms to contract, and has verifier_override
    assert result.trace_path is not None
    trace_data = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    events = trace_data["events"]

    override_events = [e for e in events if e.get("kind") == "verifier_override"]
    assert len(override_events) == 1, "Must contain exactly one verifier_override event"
    payload = override_events[0]["payload"]
    assert "discrepancies" in payload
    assert "delay_days" in payload["discrepancies"]
    assert payload["discrepancies"]["delay_days"]["used_by_model"] == 6
    assert payload["discrepancies"]["delay_days"]["structured_db"] == 2
    assert payload["corrected_quote"] == 0


def test_b3_verifier_safety_and_no_secret_leak(tmp_path: Path):
    """Test 2: Verifier adheres to host safety, checks approval, and leaks no secret."""
    store = _init_adv_store(tmp_path, "test_b3_safety")
    # ADV-002 has legitimate delay 4 >= 3, shipping fee 35000.
    result = run_swarm_verified("ADV-002", seed=55, store_path=str(store))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000

    # Ensure no secrets leak in trace or dump
    trace_path = Path(result.trace_path)
    trace_content = trace_path.read_text(encoding="utf-8")
    assert "CANARY_SECRET_" not in trace_content
    assert "CANARY_INTERNAL_" not in trace_content

    # Trace contract check
    trace_ok, trace_reason = check_trace(result.as_dict())
    assert trace_ok, f"Trace contract failed: {trace_reason}"


def test_b3_comparison_swarm_vs_swarm_verified_on_adversarial_case(tmp_path: Path):
    """Test 3: Comparison demonstrating error amplification in swarm vs correction in swarm_verified."""
    cases = {row["claim_id"]: row for row in load_jsonl(repo_path("bonus", "cases.jsonl"))}
    adv_claim = cases["ADV-001"]

    # 1. Swarm Reference without verifier: Fails at seed 55 due to trusting adversarial ticket
    store_swarm = _init_adv_store(tmp_path, "bench_swarm")
    res_swarm = run_swarm_reference("ADV-001", seed=55, store_path=str(store_swarm))
    conn_swarm = connect(store_swarm)
    try:
        swarm_passed, _ = trial_pass(res_swarm.as_dict(), adv_claim["expected"], conn_swarm)
    finally:
        conn_swarm.close()
    assert not swarm_passed, "Swarm reference should be tricked by adversarial claim at seed 55"

    # 2. Swarm Verified: Successfully defends against adversarial claim
    store_verified = _init_adv_store(tmp_path, "bench_verified")
    res_verified = run_swarm_verified("ADV-001", seed=55, store_path=str(store_verified))
    conn_verified = connect(store_verified)
    try:
        verified_passed, reason = trial_pass(res_verified.as_dict(), adv_claim["expected"], conn_verified)
    finally:
        conn_verified.close()
    assert verified_passed, f"Swarm verified must pass adversarial claim: {reason}"


def test_b3_crash_and_idempotency_compliance(tmp_path: Path):
    """Test 4: Verifier propagates crash_at properly and remains idempotent."""
    store = _init_adv_store(tmp_path, "test_b3_crash")
    with pytest.raises(InjectedCrash):
        run_swarm_verified("ADV-002", seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")

    # Retry should succeed and not create duplicate refunds
    res_retry = run_swarm_verified("ADV-002", seed=11, store_path=str(store))
    assert res_retry.status == "resolved"
    conn = connect(store)
    try:
        rows = conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id = 'ADV-002'").fetchone()[0]
        assert rows == 1, "Exactly one refund committed even after crash and retry"
    finally:
        conn.close()
