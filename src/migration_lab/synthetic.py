"""Deterministic fabricated CSV data for development and tests (no real PII)."""
from __future__ import annotations

import csv
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import random


def generate(out: Path, customers: int = 200, orders: int = 3000, seed: int = 42) -> dict:
    if not 1 <= customers <= 100_000 or not 0 <= orders <= 1_000_000:
        raise ValueError("customers: 1..100000; orders: 0..1000000")
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Output directory must be new or empty: {out}")
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    with (out / "customers.csv").open("w", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd, lineterminator="\n")
        writer.writerow(["customer_id", "display_name", "segment"])
        for idx in range(1, customers + 1):
            writer.writerow([idx, f"Synthetic Customer {idx:05d}", rng.choice(["SMB", "Mid-Market", "Enterprise"])])
    base = datetime(2024, 1, 1)
    with (out / "orders.csv").open("w", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd, lineterminator="\n")
        writer.writerow(["order_id", "customer_id", "created_at", "status", "amount"])
        for idx in range(1, orders + 1):
            timestamp = base + timedelta(minutes=rng.randrange(0, 365 * 24 * 60))
            status = rng.choices(["COMPLETED", "VOID"], weights=[88, 12], k=1)[0]
            cents = rng.randint(100, 500000)
            writer.writerow([idx, rng.randint(1, customers),
                             timestamp.isoformat(timespec="seconds"), status,
                             str((Decimal(cents) / 100).quantize(Decimal(".01")))])
    return {"synthetic": True, "seed": seed, "customers": customers,
            "orders": orders, "files": ["customers.csv", "orders.csv"]}
