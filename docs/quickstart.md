# Quickstart · offline lab

## Prerequisites

Python 3.11+ is required. The CLI and tests use Python's standard library; editable installation uses setuptools. **No live database is contacted.**

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Feature assessment

```bash
oracle-migration-lab assess sql/sqlserver --format markdown --output build/assessment.md
```

Review each reported rule and its line number. The scanner masks quoted string literals, SQL line comments, and nested block comments to reduce false positives. It does not build an abstract syntax tree. Dynamic SQL assembled across string fragments and runtime-dependent operations are not resolved.

## Dependency order

```bash
oracle-migration-lab plan examples/inventory.json --format markdown --output build/plan.md
```

All referenced objects must be present in the inventory; duplicate objects, unknown types, missing prerequisites and cycles raise errors. Proposed order is deterministic based on declared dependencies, but does not replace real database permission and object-state checks.

## Reference contracts

```bash
oracle-migration-lab verify examples/contracts.json --output build/contracts.json
```

Fixture 1 tests a leap-day period boundary and excludes a void transaction. Fixture 2 specifies a stable Top-N order when aggregate values tie. Results are computed by a Python reference implementation and compared to independently written expected values; there is **no SQL Server-to-Oracle execution** here.

## CSV result parity

```bash
oracle-migration-lab reconcile examples/exports/sqlserver_monthly_revenue.csv examples/exports/oracle_monthly_revenue.csv --output build/reconcile.json
```

Exported CSVs need the same logical column names. The comparator sorts columns by name, ignores row order, and tracks row counts as a multiset. Comparisons are exact; normalize SQL Server and Oracle numeric, timestamp, empty string and NULL formats before export.

## Synthetic data

```bash
oracle-migration-lab generate --out build/generated --seed 42 --customers 200 --orders 3000
```

A small checked-in synthetic dataset (24 customers and 250 orders) lives under `examples/data`. The generator refuses to overwrite a non-empty output directory. Customers are fictional strings, not pseudonymized real records.

## Exit codes

- `0` — success, including a successful comparison
- `1` — business contract or CSV reconciliation mismatch
- `2` — invalid arguments, missing files, malformed inventory or invalid input

## Integration testing checklist (not automated in CI)

1. Provision isolated SQL Server and Oracle **test-only** instances, with appropriate authorization.
2. Review target Oracle version, session NLS settings, timezone, and precision semantics.
3. Run source and target DDL in disposable schemas, after a human review.
4. Load the same synthetic dataset into both databases with explicit type conversions; do not rely on implicit identity reseeding.
5. Run corresponding queries and export identical logical columns with canonical formatting.
6. Reconcile full query outputs, including duplicate counts, with this CLI.
7. Check SQL execution plans and row counts independently; record environment, parameters and version details.
8. Document differences and approvals; never declare production readiness based solely on these offline checks.
