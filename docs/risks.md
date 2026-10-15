# Risk register & remaining work

| Risk | Why it matters | Treatment |
|---|---|---|
| SQL feature scanner misses dynamic SQL | Strings assembled at runtime are not syntactically visible | Explicit inventory and manual inspection |
| Target Oracle version differs | 12.1/12.2/19c/23c may differ in features and optimizer behavior | Target-specific compatibility tests |
| Calendar boundary drift | `DATEDIFF`, date subtraction and implicit timestamps vary | Boundary contracts + live database tests |
| `NULL`/empty string behavior differs | SQL Server and Oracle character semantics differ | Explicit domain fixtures, nullable column review |
| Duplicate row cardinality changes | Aggregates can hide joins multiplying or losing rows | Full exported-result multiset reconciliation |
| Identity or sequence changes | Key generation can affect child FK references | Controlled insert/reconciliation tests |
| No SQL Server/Oracle CI services | Current unit tests are offline | Implement opt-in integration suite once authorized |
| Performance unsupported | No live comparable execution plan measurements | Never claim speedups until benchmark evidence exists |

## Proposed future enhancements

- Optional sandbox database integration harness, behind explicit opt-in and isolation controls.
- A declarative, version-specific rule catalogue with static typing checks.
- Structured warnings for dynamic SQL and application-side query dependencies.
- Pluggable CSV normalization policies declared in a schema contract.
- Explain-plan capture and regression comparison for SQL Server and Oracle, with environment metadata.

These enhancements are proposals, not shipped functionality.
