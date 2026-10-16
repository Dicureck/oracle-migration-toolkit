# Migration methodology · risk before syntax

## Phase 1 — Inventory

Inventory all objects, source dialect features, type declarations and dependencies. Capture stored formulas, dynamic SQL and code called by applications. Record source/target database versions, schema mappings and privileges. The example `examples/inventory.json` models a fictional eight-object database; it is **not** a customer's data dictionary.

## Phase 2 — Static assessment

Run the scanner against a *permitted* local sample. Classify each occurrence by likely review effort. One flagged token does not mean the statement is invalid in Oracle; absence of flags does not imply compatibility.

## Phase 3 — Semantic design

For every pattern, write down a contract before choosing target syntax:

- Required inputs and column types
- NULL and empty-string behavior
- Time-zone and datetime precision assumptions
- Date boundary conventions
- Duplicate multiplicity and stable sort order
- Identifier case and NLS behavior
- Transaction, exception, isolation and locking expectations

A `DATEDIFF(day, a, b)` call counts date boundaries, rather than simply computing elapsed 24-hour periods. Do not translate it mechanically to `b - a`.

## Phase 4 — Plan dependencies

Topologically order prerequisite tables, types, sequences, functions, views and procedures. **A topological order is necessary but not sufficient:** runtime dynamic references, permissions and object compilation may still block deployment. Stop on unresolved dependencies.

## Phase 5 — Prepare reproducible cases

Use fictitious identifiers and deterministic synthetic records. Include edge cases (leap day, period end, ties, nulls, duplicate joins). Store expected outcomes separately so tests fail when business logic drifts.

## Phase 6 — Validate at two levels

1. **Offline checks:** inventory correctness, lint-style risk detection, reference contract consistency and CSV bag reconciliation. GitHub Actions covers these.
2. **Target engine smoke tests:** an [Oracle Free 26ai CI run](oracle-runtime-smoke.md) verified compilation/execution of original synthetic Oracle sample SQL. This is **not** an Oracle 12.1 compatibility test.
3. **Bounded full two-engine runtime comparison: VERIFIED.** An [October 16, 2026 CI run](verified-cross-engine-parity-2026-10-16.md) executed the original SQL Server and Oracle Free SQL separately using the **same 26 invented customers and 260 orders**, verified complete source rows, five date windows, exact numeric aggregates, deterministic Top 10 ordering and rollback, and independently compared the returned values to Python Decimal reference data. **Only SQL Server Developer 2022 and Oracle Free 26ai** were executed.
4. **Still required for the actual older target:** Oracle **12.1.0.2-specific compilation/execution**, plans, Unicode/NLS variants, identity/sequence behavior and transaction/concurrency requirements; the modern Oracle Free success cannot substitute for these.

## Phase 7 — Govern release

Obtain explicit sign-off for schema changes and DML. Use backups, approved change windows, rollback procedures and named ownership. Never execute this project's illustrative examples in a production database.
