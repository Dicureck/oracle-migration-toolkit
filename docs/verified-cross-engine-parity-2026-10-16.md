# Verified Cross-Engine Behavior · SQL Server 2022 ↔ Oracle Free 26ai

**October 16, 2026 · Original independent fictional case study.**

[Successful real two-engine GitHub Actions execution](https://github.com/Dicureck/oracle-migration-toolkit/actions/runs/38946759282) · [Permanent machine-readable verdict](../evidence/cross-engine/ci-38946759282/parity-verdict.json) · [SQL Server source output](../evidence/cross-engine/ci-38946759282/sqlserver.json) · [Oracle source output](../evidence/cross-engine/ci-38946759282/oracle.json).

## Engineering question

Can the same source records be migrated from SQL Server to Oracle while preserving the **actual** results of selected business queries, rather than merely comparing code syntax or fabricated exports?

The original [T-SQL](../sql/sqlserver/) and [Oracle SQL](../sql/oracle/) examples were executed against **independent live database containers**. A third GitHub Actions job compared both engines' returned values against the **independently computed Python Decimal reference**.

## Runtime and reproducible dataset

| Property | Source SQL Server | Target Oracle |
|---|---|---|
| Actual runtime | Developer Edition 16.0.4305.5 | Oracle AI Database **26ai Free** Release 23.26.3.0.0 |
| Timestamp column | DATETIME2(0) | TIMESTAMP(0) |
| Amount | DECIMAL(18,2) | NUMBER(18,2) |
| Captured session settings | SQL_Latin1_General_CP1_CI_AS collation | NLS_DATE_FORMAT = DD-MON-RR, NLS_NUMERIC_CHARACTERS = \`.,\`, NLS_SORT = BINARY |
| Source | 26 identical invented customers; 260 identical invented orders | Same source hash; all stored source fields verified |
| Isolation | Ephemeral disposable database on 127.0.0.1 | Ephemeral disposable PDB user on 127.0.0.1 |

The 24 customers and 250 orders already committed under [examples/data](../examples/data/) were extended with **two invented tie-breaker customers and ten original boundary orders**. All 260 records contain fabricated IDs, naive second-precision timestamps, status and fixed two-decimal **synthetic units (SU)**. No client/company records, database exports, credentials or proprietary business rules were used.

## Live query-by-query results

| Verification | Result |
|---|---:|
| Exact customer records re-read and compared | 26 / 26, both engines |
| Exact order records re-read and compared | 260 / 260, both engines |
| Completed order count | 232 |
| Sum of completed synthetic amounts | 568,398.83 SU |
| Original paired February monthly-revenue query | **14 identical rows** |
| Original paired deterministic Top 10 customers | **10 identical ordered rows** |
| Additional all-month × customer aggregation | **160 identical rows** |
| February 2024, including leap-day end boundary | 14 identical customer groups |
| Leap day 2024 only | 3 identical customer groups |
| March 2024 | 18 identical customer groups |
| Entire year 2024 | 26 identical customer groups |
| Future empty-range query | 0 rows in both |
| Transaction UPDATE followed by ROLLBACK | Original amount restored on both engines |

The **same independently generated SHA-256 source fingerprint** is archived for each engine: \`602d3ee334b14561...\` (full hash is in JSON). No database result differences were tolerated for the supported query contract.

## A real, expected incompatibility: empty strings and NULL

In the same live tests:

| SQL expression | SQL Server | Oracle Free |
|---|---|---|
| \`CASE WHEN '' IS NULL THEN 'NULL' ELSE 'EMPTY' END\` | **EMPTY** | **NULL** |

This is **not** counted as parity. Oracle treats the zero-length character string as null whereas SQL Server does not. A real migration must define and verify an explicit normalization policy for nullable/text columns before comparing business results. Equality of these numeric/date queries does not waive that difference.

## How the tests work

~~~mermaid
flowchart TD
 A[Original public fictional CSVs] --> B[Strict 260-row validated fixture]
 B --> C[Isolated SQL Server Developer CI]
 B --> D[Isolated Oracle Free CI]
 B --> E[Independent Python Decimal reference]
 C --> F[Stored row and T-SQL query output JSON]
 D --> G[Stored row and Oracle SQL output JSON]
 F --> H{All rows and windows equal?}
 G --> H
 E --> H
 H -->|No| I[Fail closed: no parity publication]
 H -->|Yes| J[Check rollback and known NULL difference]
 J --> K[Archive raw engine JSON and verdict in Git]
~~~

The [source loader and boundary fixtures](../tests/cross_engine/fixture.py), [two-engine execution harness](../tests/cross_engine/run_engine.py), [strict evidence comparator](../tests/cross_engine/compare.py) and [isolated workflow](../.github/workflows/cross-engine-parity.yml) are version-controlled and reproducible. CI also tests deliberate mismatches to ensure it fails on a changed cent value, missing date window or omitted rollback evidence.

The live engine scripts are limited to isolated databases/users. All credentials are ephemeral and generated inside GitHub Actions. The disposable SQL Server database and Oracle test schema are dropped; the database containers are destroyed after the run.

## What is and is not proven

**Verified:** the two actual database engines returned equivalent rows and decimal values for these specific original paired examples and extended half-open date-window queries, on the same invented source rows; source round trips and isolated transactional rollback passed; empty-string/NULL differences were independently confirmed.

**NOT verified:**

- **Oracle Database 12.1.0.2**: Oracle Free 26ai behavior does not certify that older version's SQL features, compatibility settings, optimizer, NLS, privileges or object semantics.
- Full stored-procedure/application migration parity, original legacy data formats, and comprehensive data type/Unicode/time-zone semantics.
- Cross-engine transaction isolation under concurrency, inter-database atomicity, deadlocks or deployment rollback in a production release.
- Actual SQL Server/Oracle explain/actual plans for these paired migration queries; engine execution validates **results**, not plan equivalence.
- Performance parity, production throughput or a general migration success rate.

This is a **bounded, honest migration proof**, not a claim that every SQL Server object can be translated one-to-one to Oracle.

## Next stage

For full target readiness, reproduce the paired cases on an **authorized Oracle 12.1.0.2 test system**, capture its actual banner, compilation errors, session NLS settings and full result reconciliation. Review identity/sequence policy, Unicode and empty-string mapping, concurrent transactions and native execution plans. None of this requires exposing production client data.

[Compatibility matrix](compatibility-matrix.md) · [Migration methodology](methodology.md) · [Tool risk register](risks.md) · [Issue #9](https://github.com/Dicureck/Dicureck/issues/9).
