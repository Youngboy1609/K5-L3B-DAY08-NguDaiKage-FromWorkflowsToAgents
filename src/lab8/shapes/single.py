"""Shape B: one bounded ReAct loop, with money and writes controlled by code."""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import dispatch, run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed = seed, crash_at = crash_at )
    finally:
        conn.close()

def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))

    def end(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {
            "status": status,
            "proposal_amount": proposal,
            "reason": reason
        })
        return finish(
            conn, shape = "single", claim_id = claim_id, seed = seed,
            status = status, proposal_amount = proposal, budget = budget,
            trace = trace, error_reason = reason
        )

    claim = dispatch( conn, budget, "get_claim_view", {"claim_id": claim_id}, worker = True)
    if not claim.get("found"):
        return end("failed", reason = "unknown_claim")
    if not claim.get("order_id"):
        return end("needs_info", reason = "missing_order_id")

    # MockLLM has no structured tool-call response, so the decision policy
    # chooses only allowlisted read tools from the current observation.
    # Ticket text never controls the amount, order ID, policy, or selected tool.
    observed: dict[str, Any] = {}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        last_tool = observation.get("last_tool")
        last_result = observation.get("last_result") or {}
        if last_tool:
            observed[last_tool] = last_result

        complete(budget, seed = seed, purpose = "decide", prompt = f"claim={claim_id}; last_tool={last_tool}")
        if "lookup_order" not in observed:
            return {"tool": "lookup_order", "args": {
                "order_id": claim["order_id"], "principal_id": claim["principal_id"],
            }}
        if not observed["lookup_order"].get("visible"):
            return {"final": {"status": "escalated", "reason": observed["lookup_order"].get("reason")}}
        if "lookup_policy" not in observed:
            return {"tool": "lookup_policy", "args": {}}
        if "lookup_refund_history" not in observed:
            return {"tool": "lookup_refund_history", "args": {
                "order_id": claim["order_id"], "principal_id": claim["principal_id"],
            }}
        if "compute_compensation" not in observed:
            return {"tool": "compute_compensation", "args": {
                "order": observed["lookup_order"]["order"],
            }}
        return {"final": {"status": "quoted"}}

    outcome = run_react(
        conn, budget, observation={"claim": {"claim_id": claim_id}},
        decide=decide, max_steps=8, worker=True,
    )
    if outcome["stopped"] == "step_cap":
        return end("failed", reason="step_cap")
    final = outcome["final"]
    if final["status"] == "escalated":
        return end("escalated", reason=final.get("reason"))

    quote = observed["compute_compensation"]
    proposal = int(quote["amount_vnd"])
    trace.add("quote", {"amount_vnd": proposal, "clause_ids": quote["clause_ids"]})
    if proposal <= 0:
        return end("denied", reason=quote.get("reason"))

    # Give the host the full entitlement. It applies approval and the per-order
    # cap within the write transaction, including on retries after a crash.
    try:
        refund = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    if not refund["ok"]:
        return end("failed" if refund["conflict"] else "denied", proposal, refund["reason"])
    return end("resolved", proposal)
