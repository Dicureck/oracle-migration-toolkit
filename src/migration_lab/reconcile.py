"""Compare exported SQL results as multisets (including duplicate row counts).

This does not open database connections. Export query results with matching column
names, equivalent canonical value formatting, and the same ordering policy.
"""
from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path


def _read(path: Path) -> tuple[list[str], Counter[tuple[str, ...]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        cols = reader.fieldnames
        if not cols or len(cols) != len(set(cols)):
            raise ValueError(f"CSV must have unique named columns: {path}")
        if any(not name or not name.strip() for name in cols):
            raise ValueError(f"CSV has blank column names: {path}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Malformed CSV rows in {path}")
    return cols, Counter(tuple(row[col] for col in sorted(cols)) for row in rows)


def reconcile(left: Path, right: Path) -> dict:
    left_cols, lcount = _read(left)
    right_cols, rcount = _read(right)
    if set(left_cols) != set(right_cols):
        raise ValueError(f"CSV schemas differ: left={sorted(left_cols)}, right={sorted(right_cols)}")
    missing, extra = lcount - rcount, rcount - lcount
    cols = sorted(left_cols)
    def entries(counter: Counter, limit: int = 20) -> list[dict]:
        return [{"values": dict(zip(cols, key)), "count": count} for key, count in sorted(counter.items())[:limit]]
    return {"method": "byte_exact_csv_multiset_comparison_not_sql_execution",
            "matching": not missing and not extra,
            "columns": cols,
            "left_rows": sum(lcount.values()), "right_rows": sum(rcount.values()),
            "missing_rows_total": sum(missing.values()), "extra_rows_total": sum(extra.values()),
            "missing_in_right": entries(missing), "extra_in_right": entries(extra),
            "diff_preview_truncated": len(missing) > 20 or len(extra) > 20,
            "note": "Export timestamps, decimals and NULLs in identical canonical forms before comparing."}
