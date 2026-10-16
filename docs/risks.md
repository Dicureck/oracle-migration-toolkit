# Risk register & remaining work

| Risk | Why it matters | Treatment |
|---|---|---|
| SQL feature scanner misses dynamic SQL | Strings assembled at runtime are not syntactically visible | Explicit inventory and manual inspection |
| Target Oracle version differs | 12.1/12.2/19c/23c may differ in features and optimizer behavior | Target-specific compatibility tests |
| Calendar boundary drift | `DATEDIFF`, date subtraction and implicit timestamps vary | Boundary contracts + live database tests |
| `NULL`/empty string behavior differs | SQL Server and Oracle character semantics differ | Explicit domain fixtures, nullable column review |
| Duplicate row cardinality changes | Aggregates can hide joins multiplying or losing rows | Full exported-result multiset reconciliation |
| Identity or sequence changes | Key generation can affect child FK references | Controlled insert/reconciliation tests |
| Oracle 12.1 engine not tested | New cross-engine CI executes modern Oracle Free 26ai, **not** Oracle 12.1.0.2 | Use authorized 12.1 sandbox before target compatibility claims |
| Performance / execution plans unsupported | Equivalent results are not evidence of identical query plans, indexes or optimizer performance | Capture actual plans on each version separately before any performance claim |

## Proposed future enhancements

- **Implemented:** [isolated two-engine SQL Server/Oracle Free CI](verified-cross-engine-parity-2026-10-16.md) with full source equality, reference report reconciliation, five date windows, rollback and a confirmed empty-string semantics difference.
- A declarative, version-specific rule catalogue with static typing checks.
- Structured warnings for dynamic SQL and application-side query dependencies.
- Pluggable CSV normalization policies declared in a schema contract.
- Explain-plan capture and regression comparison for SQL Server and Oracle, with environment metadata.

These enhancements are proposals, not shipped functionality.
