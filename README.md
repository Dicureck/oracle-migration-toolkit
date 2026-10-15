<p align="center">
  <img src="assets/oracle-migration-banner.svg" alt="Oracle Migration Toolkit — Melissa Castro | Database Migration Engineering" width="100%">
</p>

<h1 align="center">Oracle Migration Toolkit</h1>
<p align="center"><strong>Assessment-first engineering for SQL Server → Oracle transitions.</strong></p>
<p align="center">
  <a href="https://github.com/Dicureck"><img alt="Author Melissa Castro" src="https://img.shields.io/badge/ENGINEER-Melissa%20Castro-60e0ff?style=for-the-badge&labelColor=111727"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/PYTHON-3.11%2B-9e8bff?style=for-the-badge&labelColor=111727">
  <img alt="Database" src="https://img.shields.io/badge/DIALECTS-T--SQL%20%2F%20PL--SQL-60e0ff?style=for-the-badge&labelColor=111727">
  <img alt="No database required for offline checks" src="https://img.shields.io/badge/MODE-OFFLINE%20FIRST-34d399?style=for-the-badge&labelColor=111727">
  <a href="https://github.com/Dicureck/oracle-migration-toolkit/actions"><img alt="CI workflow" src="https://img.shields.io/github/actions/workflow/status/Dicureck/oracle-migration-toolkit/ci.yml?style=for-the-badge&label=VALIDATION&labelColor=111727"></a>
</p>

<p align="center"><code>ASSESS → MAP → PLAN → VERIFY → REVIEW → DEPLOY (outside this toolkit)</code></p>

---

## 01 // Mission

SQL migration is not a search-and-replace operation. It is a **compatibility, dependency, and behavioral-equivalence problem**. This independent lab illustrates a review-driven approach to migrating SQL Server patterns into Oracle Database 12c+.

It combines a **conservative T-SQL feature scanner**, a **dependency-aware migration planner**, **synthetic business-rule contracts**, and **multiset reconciliation of exported query results**. All public code, object names, contracts, and datasets are fictional and created for this portfolio.

> **Scope:** This is a reproducible engineering demonstration—not a complete T-SQL parser, a production migration product, or proof of equivalence on live SQL Server and Oracle instances. The core CLI does **not connect to databases or execute SQL**.

## 02 // Architecture

```mermaid
flowchart LR
    A[Sample T-SQL] --> B[Lexical Risk Scanner]
    I[Object Inventory] --> C[Dependency Planner]
    S[Synthetic Contracts] --> D[Offline Reference Tests]
    E[SQL Server CSV] --> F[Multiset Reconciler]
    O[Oracle CSV] --> F
    B --> R[Review Artifacts]
    C --> R
    D --> R
    F --> R
    R --> H{Human Approval}
    H -->|Approved| Q[External Lab Validation]
```

| Engineering component | What it demonstrates | Validation boundary |
|---|---|---|
| Static compatibility assessment | Flags T-SQL patterns such as `TOP`, `DATEADD`, `DATEDIFF`, `IDENTITY`, temp tables | Heuristic rules; manual code review required |
| Dependency planner | Detects missing references/cycles and produces a deterministic topological order | Inventory-based; no schema introspection |
| Curated SQL patterns | Paired SQL Server / Oracle 12c+ demonstrations with semantic notes | Neither dialect is executed by CI |
| Business-rule contracts | Decimal-safe reference outcomes and deterministic tie-breaking | Python reference behavior, **not database parity** |
| CSV reconciliation | Detects missing, extra, and duplicate result rows in exported datasets | Exact formatted-string comparisons only |
| Synthetic generator | Deterministically creates imaginary customer/order CSV data | No real entities or client data |

## 03 // Try it in two minutes

**Requirements:** Python 3.11+ and a terminal. No database, credentials, Docker, or paid tool is necessary for the offline workflow.

```bash
# From the repository root
python -m pip install -e .

# Identify T-SQL constructs that need migration review
oracle-migration-lab assess sql/sqlserver --format markdown --output build/assessment.md

# Validate a fictional object inventory and order its dependencies
oracle-migration-lab plan examples/inventory.json --format markdown --output build/plan.md

# Check reference business behavior on purpose-built synthetic cases
oracle-migration-lab verify examples/contracts.json --output build/contracts.json

# Compare exported result sets INCLUDING duplicate-row multiplicity
oracle-migration-lab reconcile examples/exports/sqlserver_monthly_revenue.csv \
  examples/exports/oracle_monthly_revenue.csv --output build/reconciliation.json

# Fabricate deterministic CSVs (output folder must be empty/new)
oracle-migration-lab generate --out build/generated --customers 200 --orders 3000 --seed 42

# Run all offline unit tests
python -m unittest discover -s tests -v
```

You can also use `python -m migration_lab` in place of the installed command. See [`docs/quickstart.md`](docs/quickstart.md) for commands and interpretations.

## 04 // Paired migration patterns

| Case | SQL Server source | Oracle 12c+ candidate | Risk discussed |
|---|---|---|---|
| Date-window aggregation | [`02_monthly_revenue.sql`](sql/sqlserver/02_monthly_revenue.sql) | [`02_monthly_revenue.sql`](sql/oracle/02_monthly_revenue.sql) | Inclusive/exclusive boundaries, leap day, timestamp precision |
| Deterministic Top-N ranking | [`03_top_customers.sql`](sql/sqlserver/03_top_customers.sql) | [`03_top_customers.sql`](sql/oracle/03_top_customers.sql) | `TOP` vs `FETCH FIRST`; mandatory tie-breaker |
| Retrieving generated keys | [`04_returning_id.sql`](sql/sqlserver/04_returning_id.sql) | [`04_returning_id.sql`](sql/oracle/04_returning_id.sql) | `OUTPUT INSERTED` vs `RETURNING INTO`; transaction scope |
| Basic schema mapping | [`01_schema.sql`](sql/sqlserver/01_schema.sql) | [`01_schema.sql`](sql/oracle/01_schema.sql) | `IDENTITY`, precision, `INCLUDE` index behavior |

A separate inventory models a **dependency graph of eight imaginary database objects**, with manual review flags for sensitive stages.

## 05 // Data quality: compare actual exports, not just totals

One row missing from a migrated query can disappear behind a matching `SUM`. This lab compares **multisets**: same values *and* same number of appearances.

```bash
# PASS — same rows in different order, even with differently ordered columns
oracle-migration-lab reconcile examples/exports/sqlserver_monthly_revenue.csv examples/exports/oracle_monthly_revenue.csv

# EXPECTED FAILURE — one occurrence of a duplicate is missing
oracle-migration-lab reconcile examples/exports/sqlserver_monthly_revenue.csv examples/exports/oracle_monthly_revenue_mismatch.csv
```

Exit code `0` means a match; `1` means a mismatch; invalid input returns exit code `2`. Standardize date, numeric and NULL formatting before export. See [`docs/reconciliation.md`](docs/reconciliation.md).

## 06 // Project map

```text
oracle-migration-toolkit/
├── .github/workflows/ci.yml     # Offline tests + review artifacts
├── assets/                     # Original cyber-noir branding
├── docs/                       # Method, decisions and limitations
├── examples/
│   ├── contracts.json          # Leap-day and deterministic-ranking contracts
│   ├── inventory.json          # Fictional dependency graph
│   ├── data/                   # Small fabricated CSV dataset
│   └── exports/                # Synthetic matching / mismatching reports
├── sql/{sqlserver,oracle}/     # Side-by-side curated SQL examples
├── src/migration_lab/          # Static assessment and validation utilities
└── tests/                      # Self-contained Python unittest suite
```

## 07 // Verification & engineering maturity

- **31 local Python unit tests passed** in the authoring environment, covering scanner masking, dependency validation, reference contract cases, CSV multiset semantics, CLI output, and deterministic data generation.
- GitHub Actions runs offline tests on Python 3.11, 3.12 and 3.13, then generates review artifacts.
- **No SQL Server / Oracle integration tests have been run for this lab.** SQL examples must be reviewed and executed in isolated, authorized test databases before claiming engine-level equivalence.
- All SQL is provided as **illustrative examples**, not as a production deployment script.

There are intentionally **no** advertised migration throughput gains, no claims of 1:1 production conversions, and no fabricated customer case studies.

## 08 // Further reading

- [Quickstart and command outputs](docs/quickstart.md)
- [Migration methodology](docs/methodology.md)
- [SQL Server → Oracle compatibility matrix](docs/compatibility-matrix.md)
- [Reconciliation design](docs/reconciliation.md)
- [Architecture and engineering decisions](docs/architecture.md)
- [Risk register and limitations](docs/risks.md)
- [Security and responsible use](SECURITY.md)

---

<p align="center"><strong>Melissa Castro</strong> · Data Analytics & Business Intelligence · SQL Engineering · Automation<br>
<sub>Building reliable data systems through measurable, reviewable engineering.</sub></p>
