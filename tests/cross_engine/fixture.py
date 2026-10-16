"""Shared deterministic, confidential-data-free cross-engine parity contract.

All rows originate in original public fictional CSV fixtures. Boundary-only
synthetic records are added identically for BOTH SQL Server and Oracle Free.
No environment/database connectivity is required for reference expectations.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
EXACT_CENTS = re.compile(r"(0|[1-9][0-9]*)\.[0-9]{2}\Z")
INSTANT = "%Y-%m-%dT%H:%M:%S"

# Deliberately invented ID range outside the 250-row source fixture.
EXTRA_CUSTOMERS = (
    (25, "Synthetic Tie Customer A", "Digital"),
    (26, "Synthetic Tie Customer B", "Digital"),
)
EXTRA_ORDERS = (
    (251, 25, "2024-02-29T23:59:59", "COMPLETED", "100.00"),
    (252, 26, "2024-02-29T23:59:59", "COMPLETED", "100.00"),
    (253, 25, "2024-03-01T00:00:00", "COMPLETED", "0.01"),
    (254, 26, "2024-02-01T00:00:00", "VOID", "9999.99"),
    (255, 1, "2024-02-01T00:00:00", "COMPLETED", "0.00"),
    (256, 1, "2024-03-01T00:00:00", "COMPLETED", "45.95"),
    (257, 2, "2024-02-28T23:59:59", "COMPLETED", "123.45"),
    (258, 3, "2024-02-29T00:00:00", "COMPLETED", "123.45"),
    (259, 2, "2024-01-31T23:59:59", "COMPLETED", "5.00"),
    (260, 3, "2024-04-01T00:00:00", "COMPLETED", "5.00"),
)
WINDOWS = {
    "february_leap": ("2024-02-01T00:00:00", "2024-03-01T00:00:00"),
    "leap_day": ("2024-02-29T00:00:00", "2024-03-01T00:00:00"),
    "march": ("2024-03-01T00:00:00", "2024-04-01T00:00:00"),
    "full_2024": ("2024-01-01T00:00:00", "2025-01-01T00:00:00"),
    "empty": ("2025-02-01T00:00:00", "2025-03-01T00:00:00"),
}


def fixture():
    customers = []
    with (ROOT / "examples/data/customers.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["customer_id", "display_name", "segment"]:
            raise ValueError("Customer fixture schema differs")
        for item in reader:
            ident = int(item["customer_id"])
            name, segment = item["display_name"], item["segment"]
            if not name or not segment:
                raise ValueError("Fixture contains an empty mandatory customer field")
            customers.append((ident, name, segment))
    orders = []
    with (ROOT / "examples/data/orders.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["order_id", "customer_id", "created_at", "status", "amount"]:
            raise ValueError("Order fixture schema differs")
        for item in reader:
            orders.append((
                int(item["order_id"]), int(item["customer_id"]),
                item["created_at"], item["status"], item["amount"],
            ))
    if len(customers) != 24 or len(orders) != 250:
        raise ValueError("The independently created source fixture has changed")
    customers += list(EXTRA_CUSTOMERS)
    orders += list(EXTRA_ORDERS)
    valid_customers = {c[0] for c in customers}
    if len(valid_customers) != len(customers) or len({o[0] for o in orders}) != len(orders):
        raise ValueError("Duplicate synthetic primary keys")
    for id_, customer_id, timestamp, status, amount in orders:
        if id_ < 1 or customer_id not in valid_customers or status not in ("COMPLETED", "VOID"):
            raise ValueError("Invalid order fixture foreign key or status")
        if datetime.strptime(timestamp, INSTANT).strftime(INSTANT) != timestamp:
            raise ValueError("Timestamp is not exact to one second")
        if not EXACT_CENTS.fullmatch(amount) or Decimal(amount) > Decimal("9999999999999999.99"):
            raise ValueError("Unexpected amount precision or unsafe amount")
    return customers, orders


def normal_amount(value) -> str:
    d = Decimal(str(value))
    if not d.is_finite() or d != d.quantize(Decimal("0.01")):
        raise ValueError("Amount is not a finite two-decimal value")
    return format(d, ".2f")


def canonical_rows(rows) -> list[list[str]]:
    return [[str(customer_id), normal_amount(amount)] for customer_id, amount in rows]


def expected_reports(orders: list[tuple]) -> dict:
    completed = [o for o in orders if o[3] == "COMPLETED"]
    def grouped(selected):
        totals = defaultdict(lambda: Decimal("0.00"))
        for _, customer_id, _, _, amount in selected:
            totals[customer_id] += Decimal(amount)
        return sorted(totals.items())

    february = grouped(o for o in completed
                       if "2024-02-01T00:00:00" <= o[2] < "2024-03-01T00:00:00")
    totals_all = grouped(completed)
    top = sorted(totals_all, key=lambda p: (-p[1], p[0]))[:10]
    windows = {
        name: canonical_rows(grouped(o for o in completed if start <= o[2] < end))
        for name, (start, end) in WINDOWS.items()
    }
    # Month × customer across the entire sample, including duplicates per customer.
    monthly = defaultdict(lambda: Decimal("0.00"))
    for _, customer_id, created, _, amount in completed:
        monthly[(created[:7], customer_id)] += Decimal(amount)
    months = [[month, str(customer), normal_amount(amount)]
              for (month, customer), amount in sorted(monthly.items())]
    return {
        "original_monthly_february": canonical_rows(february),
        "original_top_ten": canonical_rows(top),
        "by_window": windows,
        "by_month_customer": months,
        "source_customer_count": len({c[0] for c in fixture()[0]}),
        "source_order_count": len(orders),
        "completed_order_count": len(completed),
        "completed_amount_su": normal_amount(sum((Decimal(o[4]) for o in completed),
                                                  Decimal("0.00"))),
        "source_order_multiset_size": sum(Counter(orders).values()),
    }
