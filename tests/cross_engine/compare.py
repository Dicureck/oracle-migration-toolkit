"""Authoritative independent two-engine comparison and immutable evidence promotion.

Both engines must have run their *original* SQL queries against identical fictional
source rows and passed the independently computed Python Decimal reference.
Known empty-string/NULL difference is documented as an expected incompatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cross_engine.fixture import fixture, expected_reports, WINDOWS


def reconcile(sql_file: Path, oracle_file: Path) -> dict:
    source = {}
    customers, orders = fixture()
    expected = expected_reports(orders)
    checksum = hashlib.sha256(json.dumps({"customers": customers, "orders": orders},
                                         separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
    for engine, path in (("sqlserver", sql_file), ("oracle", oracle_file)):
        item = json.loads(path.read_text(encoding="utf-8"))
        if item.get("engine") != engine or item.get("fixture_sha256") != checksum:
            raise ValueError(f"{engine}: incorrect engine or shared source checksum")
        if item.get("counts") != {"customers":26,"orders":260,
                                  "completed":expected["completed_order_count"]}:
            raise ValueError(f"{engine}: source cardinality mismatch")
        if item.get("round_trip_all_source_rows") is not True:
            raise ValueError(f"{engine}: source verification missing")
        if item.get("transaction_rollback") is not True:
            raise ValueError(f"{engine}: rollback verification missing")
        if not item.get("database_version_and_settings", {}).get("engine_version"):
            raise ValueError(f"{engine}: missing actual database engine banner/version")
        results = item.get("results", {})
        for category in ("original_monthly_february","original_top_ten","by_month_customer"):
            if results.get(category) != expected[category]:
                raise ValueError(f"{engine}: database results disagree with independent reference: {category}")
        if set(results.get("by_window", {})) != set(WINDOWS):
            raise ValueError(f"{engine}: incomplete date windows")
        for name in WINDOWS:
            if results["by_window"][name] != expected["by_window"][name]:
                raise ValueError(f"{engine}: wrong half-open result {name}")
        if item.get("empty_string_behavior") != ("EMPTY" if engine=="sqlserver" else "NULL"):
            raise ValueError(f"{engine}: unacknowledged empty-string incompatibility")
        source[engine] = item
    if source["sqlserver"]["results"] != source["oracle"]["results"]:
        raise ValueError("Actual SQL Server and Oracle result rows differ despite reference checks")
    return {
        "status":"verified-cross-engine-synthetic-parity",
        "fixture_sha256":checksum,
        "source":{"customers":len(customers),"orders":len(orders),
                  "completed":expected["completed_order_count"],
                  "completed_amount_su":expected["completed_amount_su"]},
        "engines":{
            key: {"version_and_settings":item["database_version_and_settings"],
                  "transaction_rollback":True,
                  "source_rows_exact":True,
                  "empty_string_behavior":item["empty_string_behavior"]}
            for key,item in source.items()
        },
        "tests":{
            "original_paired_monthly_revenue":len(expected["original_monthly_february"]),
            "original_paired_top_ten":len(expected["original_top_ten"]),
            "month_by_customer_groups":len(expected["by_month_customer"]),
            "date_windows":{
                name: len(expected["by_window"][name]) for name in WINDOWS
            },
            "cross_engine_full_result_equivalence":True,
            "independent_decimal_reference_equivalence":True,
            "same_complete_source_rows":True,
            "transactional_rollback_both":True,
        },
        "expected_difference":{
            "feature":"zero-length character literal",
            "sqlserver":"EMPTY (not NULL)",
            "oracle":"NULL",
            "resolution":"Explicit mapping/review required; not all cross-engine semantics are identical.",
        },
        "excluded":["Oracle 12.1.0.2 runtime validation","production system behavior",
                    "cross-database atomic transactions","SQL Server/Oracle performance parity",
                    "all timezone, NLS and collation configurations"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlserver",type=Path,required=True)
    parser.add_argument("--oracle",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    outcome = reconcile(args.sqlserver,args.oracle)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PASS: original SQL Server ↔ Oracle Free SQL results equal over 260 orders, "
          "five windows and transaction rollback; expected empty-string difference documented")


if __name__ == "__main__":
    main()
