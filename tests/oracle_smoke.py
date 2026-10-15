"""Optional live Oracle Free smoke test using original synthetic SQL fixtures.

This verifies target-engine compilation and small example outputs only.
It does NOT assert SQL Server-to-Oracle cross-engine equivalence, Oracle 12.1 parity,
or production readiness. Requires a disposable local Oracle Free service.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import oracledb

ROOT = Path(__file__).resolve().parents[1]
DSN = os.getenv("ORACLE_SMOKE_DSN", "127.0.0.1:1521/FREEPDB1")
ADMIN_PASSWORD = os.environ["ORACLE_PASSWORD"]
OUT = ROOT / "build" / "oracle-runtime-smoke.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def connect_with_retry():
    error = None
    for attempt in range(90):
        try:
            return oracledb.connect(user="system", password=ADMIN_PASSWORD, dsn=DSN)
        except oracledb.Error as exc:
            error = exc
            if attempt % 12 == 0:
                print(f"Waiting for disposable Oracle Free service; attempt {attempt+1}/90")
            time.sleep(5)
    raise RuntimeError("Oracle Free service did not become ready") from error


def stripped_sql(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    # These *original example files* have single-line comments and no
    # SQL string literals containing semicolons.
    text = "\n".join(re.sub(r"--.*", "", line) for line in text.splitlines())
    return text.strip()


def main():
    admin = connect_with_retry()
    try:
        with admin.cursor() as cur:
            cur.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            version = str(cur.fetchone()[0])
            ephemeral_password = "Smoke" + secrets.token_hex(14)
            cur.execute(f'CREATE USER SYNTHSMOKE IDENTIFIED BY "{ephemeral_password}"')
            cur.execute("GRANT CREATE SESSION, CREATE TABLE TO SYNTHSMOKE")
            cur.execute("ALTER USER SYNTHSMOKE QUOTA UNLIMITED ON USERS")
        admin.commit()
        with oracledb.connect(user="SYNTHSMOKE",
                              password=ephemeral_password, dsn=DSN) as connection:
            with connection.cursor() as cur:
                for statement in stripped_sql("sql/oracle/01_schema.sql").split(";"):
                    if statement.strip():
                        cur.execute(statement)
                customers = [
                    (1, "Fictional Customer One", "Retail"),
                    (2, "Fictional Customer Two", "Wholesale"),
                    (3, "Fictional Customer Three", "Digital"),
                ]
                cur.executemany(
                    "INSERT INTO demo_customers(customer_id, display_name, segment) "
                    "VALUES (:1, :2, :3)", customers)
                orders = [
                    (1, 1, datetime(2024, 2, 2), "COMPLETED", Decimal("19.25")),
                    (2, 1, datetime(2024, 2, 28), "COMPLETED", Decimal("5.75")),
                    (3, 2, datetime(2024, 2, 29), "COMPLETED", Decimal("12.40")),
                    (4, 2, datetime(2024, 2, 3), "VOID", Decimal("99.00")),
                    (5, 2, datetime(2024, 3, 1), "COMPLETED", Decimal("33.00")),
                    (6, 3, datetime(2024, 2, 9), "COMPLETED", Decimal("2.00")),
                ]
                cur.executemany(
                    "INSERT INTO demo_orders(order_id, customer_id, created_at, status, amount) "
                    "VALUES (:1, :2, :3, :4, :5)", orders)
                connection.commit()
                cur.execute(stripped_sql("sql/oracle/02_monthly_revenue.sql").rstrip(";"))
                monthly = [(int(i), Decimal(str(amount))) for i, amount in cur.fetchall()]
                assert monthly == [(1, Decimal("25.00")), (2, Decimal("12.40")), (3, Decimal("2.00"))], monthly
                cur.execute(stripped_sql("sql/oracle/03_top_customers.sql").rstrip(";"))
                top = [(int(i), Decimal(str(amount))) for i, amount in cur.fetchall()]
                assert [customer_id for customer_id, _ in top] == [2, 1, 3], top

                cur.execute("SELECT COUNT(*) FROM demo_customers")
                count_before = cur.fetchone()[0]
                block = (ROOT / "sql/oracle/04_returning_id.sql").read_text(encoding="utf-8")
                block = block[block.index("DECLARE") :].rsplit("/", 1)[0].strip()
                cur.execute(block)
                cur.execute("SELECT COUNT(*) FROM demo_customers")
                assert cur.fetchone()[0] == count_before, "Example must rollback its insert"
        evidence = {
            "status": "verified-synthetic-oracle-free-smoke",
            "oracle_banner": version,
            "database": "Disposable Oracle Free PDB",
            "source_examples": [
                "01_schema.sql", "02_monthly_revenue.sql",
                "03_top_customers.sql", "04_returning_id.sql",
            ],
            "synthetic_customers": 3,
            "synthetic_orders": 6,
            "monthly_revenue": [(i, format(v, ".2f")) for i, v in monthly],
            "top_customers": [(i, format(v, ".2f")) for i, v in top],
            "returning_id_rollback": True,
            "scope": "Oracle Free target-engine syntax and illustrative outputs only",
            "not_verified": [
                "Oracle 12.1 compatibility",
                "SQL Server cross-engine parity",
                "production behavior",
            ],
        }
        OUT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print("PASS: live Oracle Free schema, fictional revenue, ordered top customers and rollback")
    finally:
        admin.close()


if __name__ == "__main__":
    main()
