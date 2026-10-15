# Architecture & decisions

## Components

- `scanner.py`: regular-expression rules over executable tokens after masking line/block comments and quoted literals. Reports positions and remediation notes, without attempting rewriting.
- `planner.py`: validates inventory schema, enforces exact dependencies and computes deterministic topological order via Kahn's algorithm and a priority queue.
- `contracts.py`: computes Decimal-based synthetic reference outcomes for grouped monthly totals and deterministic Top-N ranking.
- `reconcile.py`: uses `Counter` over CSV records after sorting logical columns. Detects missing rows, extra rows and duplicate count differences.
- `synthetic.py`: deterministic `random.Random(seed)` fake dataset generator with stable CSV line endings. Enforces bounds and refuses accidental overwrite.
- `cli.py`: user-facing `assess`, `plan`, `verify`, `reconcile`, `generate` entry points with stable status codes.

## Decision log

**D-001: Avoid regex-only automatic translation.** T-SQL and PL/SQL have non-trivial control flow, type inference, date and transaction semantics. A heuristic scanner is more honest and auditable than a converter that silently changes logic.

**D-002: Zero direct database credentials.** An offline-first design lowers demonstration risk, keeps CI fast and reproducible, and avoids accidental production writes.

**D-003: Multiset comparison, not DISTINCT.** Equal totals and sets are insufficient when join multiplicity changes. Count duplicate rows to detect cardinality drift.

**D-004: Decimal arithmetic for contract money.** `decimal.Decimal` avoids floating-point artifacts in reference assertions.

**D-005: Explicit determinism.** Source and target Top-N SQL examples include secondary `customer_id` ordering. Tests use fixed seeds and handcrafted edge cases.

**D-006: Honest verification labels.** Python reference tests cannot establish that SQL Server and Oracle produce identical results. Integration validation is a separate stage with environment capture and human approval.

## Known constraints

- The lexical scanner does not resolve complete T-SQL grammar, dynamic SQL or the full semantics of SQL stored in strings.
- Feature findings can be false positives or false negatives. Review output is intentionally advisory.
- Oracle behavior varies with version, NLS settings, session time zone, collation, datatypes and privileges.
- CSV value matching is exact; a separate canonicalization policy must be agreed for target outputs.
- GitHub Actions runs Python tests only, not database integration suites.
