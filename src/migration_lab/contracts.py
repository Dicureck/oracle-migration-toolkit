"""Offline business-rule contracts for synthetic, cross-dialect examples.

This validates independently encoded expected outcomes, not execution in SQL Server/Oracle.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path


CENT = Decimal("0.01")


def monthly_revenue(contract: dict) -> list[dict]:
    start = datetime.fromisoformat(contract["start_inclusive"])
    end = datetime.fromisoformat(contract["end_exclusive"])
    if start >= end:
        raise ValueError("Period end must follow period start")
    sums: dict[int, Decimal] = {}
    for row in contract["records"]:
        if row["status"] != "COMPLETED":
            continue
        created = datetime.fromisoformat(row["created_at"])
        if start <= created < end:
            customer = int(row["customer_id"])
            sums[customer] = sums.get(customer, Decimal("0")) + Decimal(str(row["amount"]))
    return [{"customer_id": cid,
             "revenue": str(amount.quantize(CENT, rounding=ROUND_HALF_UP))}
            for cid, amount in sorted(sums.items())]


def top_customers(contract: dict) -> list[int]:
    limit = contract["limit"]
    if type(limit) is not int or limit < 0:
        raise ValueError("Top-N limit must be a non-negative integer")
    rows = contract["records"]
    return [int(r["customer_id"]) for r in sorted(
        rows, key=lambda r: (-Decimal(str(r["revenue"])), int(r["customer_id"])))[:limit]]


def verify_contracts(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    contracts = data.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        raise ValueError("Provide a non-empty contracts array")
    results = []
    for item in contracts:
        kind = item["kind"]
        if kind == "monthly_revenue":
            actual = monthly_revenue(item)
        elif kind == "top_customers":
            actual = top_customers(item)
        else:
            raise ValueError(f"Unknown contract kind: {kind}")
        expected = item["expected"]
        results.append({"name": item["name"], "kind": kind,
                        "passed": actual == expected, "expected": expected, "actual": actual})
    return {"method": "offline_reference_contracts_not_cross_database_execution",
            "passed": sum(r["passed"] for r in results),
            "failed": sum(not r["passed"] for r in results), "results": results}
