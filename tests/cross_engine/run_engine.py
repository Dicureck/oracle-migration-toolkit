"""Live, isolated engine run against one original shared synthetic data contract.

Two separate CI jobs execute the same paired artifacts, then a third job
reconciles both engine outputs and independent Python exact-Decimal reference.
Requires only loopback Docker engines. NEVER connects to client databases.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sys
import time

# Allows "python tests/cross_engine/run_engine.py" with no package installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cross_engine.fixture import fixture, expected_reports, canonical_rows, normal_amount, WINDOWS, ROOT

EXPECTED_SQL_DATABASE = "OracleParitySyntheticCI"
EXPECTED_ORACLE_USER = "SYNTHPARITY"


def sql_from(path: str) -> str:
    source = (ROOT / path).read_text(encoding="utf-8")
    return "\n".join(line for line in source.splitlines()
                     if not line.lstrip().startswith("--")).strip().rstrip(";")


def wait_connection(engine: str, password: str):
    last_error = None
    for attempt in range(90):
        try:
            if engine == "sqlserver":
                import pymssql
                return pymssql.connect(server="127.0.0.1", port=14333, user="sa",
                                       password=password, database="master",
                                       autocommit=True, login_timeout=5, timeout=45)
            import oracledb
            return oracledb.connect(user="system", password=password,
                                    dsn="127.0.0.1:1521/FREEPDB1")
        except Exception as exc:
            last_error = exc
            if attempt % 12 == 0:
                print(f"Waiting for disposable {engine} container ({attempt+1}/90)", flush=True)
            time.sleep(5)
    raise RuntimeError(f"Disposable {engine} did not start") from last_error


def create_lab(engine: str, admin, admin_password: str):
    if engine == "sqlserver":
        import pymssql
        with admin.cursor() as c:
            c.execute("SELECT DB_ID(%s)", (EXPECTED_SQL_DATABASE,))
            if c.fetchone()[0] is not None:
                raise RuntimeError("Refusing to touch any existing SQL Server database")
            c.execute(f"CREATE DATABASE [{EXPECTED_SQL_DATABASE}]")
        connection = pymssql.connect(server="127.0.0.1", port=14333, user="sa",
                                     password=admin_password, database=EXPECTED_SQL_DATABASE,
                                     autocommit=True, login_timeout=8, timeout=45)
        with connection.cursor() as c:
            script = sql_from("sql/sqlserver/01_schema.sql")
            for statement in re.split(r"(?im)^\s*GO\s*$", script):
                if statement.strip():
                    c.execute(statement)
        return connection, None
    import oracledb
    user_password = "Parity" + secrets.token_hex(16)
    with admin.cursor() as c:
        c.execute(f'CREATE USER {EXPECTED_ORACLE_USER} IDENTIFIED BY "{user_password}"')
        c.execute(f"GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE TO {EXPECTED_ORACLE_USER}")
        c.execute(f"ALTER USER {EXPECTED_ORACLE_USER} QUOTA UNLIMITED ON USERS")
    connection = oracledb.connect(user=EXPECTED_ORACLE_USER, password=user_password,
                                  dsn="127.0.0.1:1521/FREEPDB1")
    with connection.cursor() as c:
        for statement in sql_from("sql/oracle/01_schema.sql").split(";"):
            if statement.strip():
                c.execute(statement)
    return connection, EXPECTED_ORACLE_USER


def load_shared_fixtures(engine: str, connection, customers, orders):
    converted_orders = [
        (order_id, customer_id, datetime.fromisoformat(instant), status, Decimal(amount))
        for order_id, customer_id, instant, status, amount in orders
    ]
    with connection.cursor() as c:
        if engine == "sqlserver":
            c.execute("SET IDENTITY_INSERT dbo.demo_customers ON")
            c.executemany(
                "INSERT INTO dbo.demo_customers(customer_id,display_name,segment) VALUES(%s,%s,%s)",
                customers,
            )
            c.execute("SET IDENTITY_INSERT dbo.demo_customers OFF")
            c.execute("SET IDENTITY_INSERT dbo.demo_orders ON")
            c.executemany(
                "INSERT INTO dbo.demo_orders(order_id,customer_id,created_at,status,amount) "
                "VALUES(%s,%s,%s,%s,%s)", converted_orders,
            )
            c.execute("SET IDENTITY_INSERT dbo.demo_orders OFF")
        else:
            c.executemany(
                "INSERT INTO demo_customers(customer_id,display_name,segment) "
                "VALUES (:1,:2,:3)", customers,
            )
            c.executemany(
                "INSERT INTO demo_orders(order_id,customer_id,created_at,status,amount) "
                "VALUES (:1,:2,:3,:4,:5)", converted_orders,
            )
            connection.commit()


def verify_storage(engine: str, connection, customers, orders):
    prefix = "dbo." if engine == "sqlserver" else ""
    with connection.cursor() as c:
        c.execute("SELECT customer_id,display_name,segment FROM " + prefix +
                  "demo_customers ORDER BY customer_id")
        actual_customers = [tuple(row) for row in c.fetchall()]
        c.execute("SELECT order_id,customer_id,created_at,status,amount FROM " + prefix +
                  "demo_orders ORDER BY order_id")
        actual_orders = [tuple(row) for row in c.fetchall()]
    if actual_customers != customers:
        raise AssertionError(f"{engine}: customer row/Unicode text parity failed")
    if len(actual_orders) != len(orders):
        raise AssertionError(f"{engine}: order count differs")
    for db_row, ref in zip(actual_orders, orders):
        expected = (ref[0], ref[1], datetime.fromisoformat(ref[2]), ref[3], ref[4])
        if tuple(db_row[:4]) != expected[:4] or normal_amount(db_row[4]) != expected[4]:
            raise AssertionError(f"{engine}: original order {ref[0]} field mismatch")
    return True


def fetch(connection, sql: str, args=None):
    with connection.cursor() as c:
        if args is None:
            c.execute(sql)
        else:
            c.execute(sql, args)
        return list(c.fetchall())


def verify_rollback(engine: str, connection):
    prefix = "dbo." if engine == "sqlserver" else ""
    with connection.cursor() as c:
        c.execute(f"SELECT amount FROM {prefix}demo_orders WHERE order_id=251")
        before = normal_amount(c.fetchone()[0])
        if engine == "sqlserver":
            c.execute("BEGIN TRANSACTION")
            try:
                c.execute(f"UPDATE {prefix}demo_orders SET amount=amount+1 WHERE order_id=251")
                c.execute("ROLLBACK TRANSACTION")
            except Exception:
                c.execute("IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION")
                raise
        else:
            c.execute("SAVEPOINT synthetic_parity_test")
            c.execute(f"UPDATE {prefix}demo_orders SET amount=amount+1 WHERE order_id=251")
            c.execute("ROLLBACK TO SAVEPOINT synthetic_parity_test")
        c.execute(f"SELECT amount FROM {prefix}demo_orders WHERE order_id=251")
        after = normal_amount(c.fetchone()[0])
    if before != after or before != "100.00":
        raise AssertionError(f"{engine}: transaction rollback failed")
    return True


def session_info(engine: str, connection, admin):
    if engine == "sqlserver":
        version, edition, collation = fetch(connection,
            "SELECT CONVERT(varchar(64), SERVERPROPERTY('ProductVersion')), "
            "CONVERT(varchar(64), SERVERPROPERTY('Edition')), "
            "CONVERT(varchar(128), DATABASEPROPERTYEX(DB_NAME(), 'Collation'))")[0]
        return {"engine_version":str(version),"edition":str(edition),
                "collation":str(collation),"time_precision":"DATETIME2(0)",
                "amount_precision":"DECIMAL(18,2)"}
    version = fetch(admin, "SELECT banner FROM v$version WHERE ROWNUM=1")[0][0]
    nls = dict(fetch(connection,
        "SELECT parameter,value FROM nls_session_parameters "
        "WHERE parameter IN ('NLS_DATE_FORMAT','NLS_NUMERIC_CHARACTERS','NLS_SORT')"))
    return {"engine_version":str(version),"nls_session":nls,
            "time_precision":"TIMESTAMP(0)","amount_precision":"NUMBER(18,2)"}


def run(engine: str, out: Path):
    if os.environ.get("PARITY_ISOLATED_CI") != "YES":
        raise RuntimeError("Refusing database connection outside explicitly isolated synthetic CI")
    pwd_key = "SQLLAB_PASSWORD" if engine == "sqlserver" else "ORACLE_PASSWORD"
    password = os.environ.get(pwd_key, "")
    if len(password) < 12:
        raise RuntimeError("Missing random ephemeral CI-only database password")

    customers, orders = fixture()
    expected = expected_reports(orders)
    checksum = hashlib.sha256(json.dumps({"customers":customers,"orders":orders},
                                         separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    admin = wait_connection(engine, password)
    connection = None
    created_name = None
    try:
        connection, created_name = create_lab(engine, admin, password)
        load_shared_fixtures(engine, connection, customers, orders)
        verify_storage(engine, connection, customers, orders)
        prefix = "sqlserver" if engine == "sqlserver" else "oracle"
        monthly = canonical_rows(fetch(connection, sql_from(f"sql/{prefix}/02_monthly_revenue.sql")))
        top = canonical_rows(fetch(connection, sql_from(f"sql/{prefix}/03_top_customers.sql")))
        months = [[str(month).strip(),str(customer_id),normal_amount(amount)]
                  for month,customer_id,amount in fetch(connection,
                      sql_from(f"sql/{prefix}/05_all_months_parity.sql"))]
        if monthly != expected["original_monthly_february"] or top != expected["original_top_ten"]:
            raise AssertionError(f"{engine}: original published paired query returned incorrect rows")
        if months != expected["by_month_customer"]:
            raise AssertionError(f"{engine}: month-by-customer results diverge from reference")
        by_window = {}
        for label, (start, end) in WINDOWS.items():
            rows = fetch(connection, sql_from(f"sql/{prefix}/06_window_parity.sql"), (start, end))
            by_window[label] = canonical_rows(rows)
            if by_window[label] != expected["by_window"][label]:
                raise AssertionError(f"{engine}: date boundary or amount mismatch in {label}")

        # A deliberate incompatibility MUST be disclosed: Oracle '' is NULL.
        if engine == "sqlserver":
            got = fetch(connection, "SELECT CASE WHEN '' IS NULL THEN 'NULL' ELSE 'EMPTY' END")[0][0]
        else:
            got = fetch(connection, "SELECT CASE WHEN '' IS NULL THEN 'NULL' ELSE 'EMPTY' END FROM dual")[0][0]
        expected_empty = "EMPTY" if engine == "sqlserver" else "NULL"
        if got != expected_empty:
            raise AssertionError(f"{engine}: empty string/null behavior differed unexpectedly")

        rollback = verify_rollback(engine, connection)
        report = {
            "engine":engine,"execution_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "scope":"isolated real-engine SQL execution on entirely synthetic data",
            "database_version_and_settings":session_info(engine, connection, admin),
            "fixture_sha256":checksum,
            "counts":{"customers":len(customers),"orders":len(orders),
                      "completed":expected["completed_order_count"]},
            "round_trip_all_source_rows":True,
            "results":{"original_monthly_february":monthly,"original_top_ten":top,
                       "by_window":by_window,"by_month_customer":months},
            "transaction_rollback":rollback,
            "empty_string_behavior":got,
            "deliberate_known_nonparity":"Oracle empty string = NULL, SQL Server empty string != NULL",
            "not_verified":["Oracle Database 12.1.0.2","production integration","NLS-independent Unicode semantics",
                            "multi-user concurrency or cross-engine performance"],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(f"PASS {engine}: {len(orders)} exact order rows and original/native paired SQL "
              f"matched Python reference, {len(WINDOWS)} date windows, rollback; "
              "documented empty-string divergence")
    finally:
        if connection:
            connection.close()
        if engine == "sqlserver":
            if admin:
                # Only drop a DB this invocation successfully created.
                if connection is not None:
                    with admin.cursor() as c:
                        c.execute(f"ALTER DATABASE [{EXPECTED_SQL_DATABASE}] "
                                  "SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
                        c.execute(f"DROP DATABASE [{EXPECTED_SQL_DATABASE}]")
            admin.close()
        else:
            # Created only in isolated disposable Oracle Free container.
            if created_name:
                with admin.cursor() as c:
                    c.execute(f"DROP USER {EXPECTED_ORACLE_USER} CASCADE")
            admin.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("sqlserver","oracle"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.engine, args.out)
