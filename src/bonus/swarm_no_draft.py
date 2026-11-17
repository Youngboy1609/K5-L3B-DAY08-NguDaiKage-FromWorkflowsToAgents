"""Ablation R4 — swarm tham chiếu với bước draft bật hoặc tắt.

File này là bản chép của `lab8/shapes/swarm_reference.py`. Chỉ khác hai điểm:

1. Tên shape (và vì thế run id) là tham số, để biến thể không ghi đè trace của swarm gốc.
2. Ba lời gọi `complete(..., purpose="draft", ...)` nằm sau cờ `draft`.

Mọi thứ khác giữ nguyên, kể cả hai lời gọi peer/parse và khối REFERENCE_WEAKNESS
(seed chia hết cho 5 tin số ngày trong ticket). Không thêm event trace nào, vì metric
`steps` đếm số event: thêm event là thêm một biến thứ hai.

Hai hàm cùng chữ ký `run_claim` của lab:

- `run_claim`          — nhánh thí nghiệm, tắt draft (shape `swarm_no_draft`).
- `run_claim_control`  — nhánh đối chứng, bật draft (shape `swarm_draft_control`).
  Nhánh này phải cho kết quả trùng swarm gốc; nếu không, bản chép đã lệch.

Chạy cạnh swarm gốc, từ thư mục `src/`:

    python -m lab8.benchmark --shapes swarm,swarm_draft_control,swarm_no_draft \
        --extra-shape swarm_draft_control=bonus.swarm_no_draft:run_claim_control \
        --extra-shape swarm_no_draft=bonus.swarm_no_draft:run_claim \
        --out reports/research_ablation.json
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import tool_cost

SHAPE_NO_DRAFT = "swarm_no_draft"
SHAPE_CONTROL = "swarm_draft_control"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Nhánh thí nghiệm: swarm tham chiếu, tắt bước draft."""
    return _entry(claim_id, seed, store_path, crash_at, shape=SHAPE_NO_DRAFT, draft=False)


def run_claim_control(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Nhánh đối chứng: cùng bản chép, bật draft. Phải trùng swarm gốc."""
    return _entry(claim_id, seed, store_path, crash_at, shape=SHAPE_CONTROL, draft=True)


def _entry(
    claim_id: str,
    seed: int,
    store_path: str,
    crash_at: str | None,
    *,
    shape: str,
    draft: bool,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at, shape=shape, draft=draft)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
    shape: str,
    draft: bool,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id(shape, claim_id, seed)
    trace = _Trace(run_id)
    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape=shape,
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        if draft:  # ABLATION: draft 1/3
            complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape=shape,
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim_row["principal_id"]
    )
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {"lookup_order": order_view, "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or [])})
    if not order_view.get("visible"):
        if draft:  # ABLATION: draft 2/3
            complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return finish(
            conn,
            shape=shape,
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=order_view.get("reason"),
        )

    order = dict(order_view["order"])
    # REFERENCE_WEAKNESS: giữ nguyên như swarm gốc. Ablation không sửa điểm yếu này.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    quote_payload = investigated["tools"]["compute_compensation"]
    # Recompute if the weakness rewrote delay. Otherwise keep the investigator quote.
    if order["delay_days"] != order_view["order"]["delay_days"]:
        from lab8.tools import compute_compensation

        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    if draft:  # ABLATION: draft 3/3
        complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return finish(
            conn,
            shape=shape,
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote_payload.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape=shape,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )
    return finish(
        conn,
        shape=shape,
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )


class _Trace:
    """Local alias so a crash can still flush. Wraps lab8.trace.Trace."""

    def __init__(self, run_id: str) -> None:
        from lab8.trace import Trace

        self._inner = Trace(run_id)

    def add(self, kind: str, payload: dict) -> None:
        self._inner.add(kind, payload)

    def write(self) -> str:
        return self._inner.write()

    @property
    def run_id(self) -> str:
        return self._inner.run_id
