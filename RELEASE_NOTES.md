# Oracle Migration Toolkit · v0.1.0

First official public release of an **original, synthetic SQL Server-to-Oracle engineering toolkit**.

## Included

- Conservative offline T-SQL compatibility analysis and risk reporting.
- Dependency-aware object installation planning.
- Original PL/SQL examples, synthetic test contracts and duplicate-aware CSV reconciliation.
- Automated Python unit tests across supported runtimes.
- Controlled Oracle Free runtime smoke that executes original sample SQL against a **temporary Oracle test database**.

## Verification

Publication is gated on **both** the successful offline **Migration Lab CI** and **Oracle Free — Synthetic Runtime Smoke** workflows for the tagged commit. No production access is required.

## Important boundaries

An Oracle Free runtime smoke is **not** proof of Oracle 12.1 compatibility or full live SQL Server–Oracle behavioral equivalence. The toolkit does not automatically translate proprietary procedures; it creates reviewable evidence for migration engineers. No actual client objects or records appear.

[Toolkit README](https://github.com/Dicureck/oracle-migration-toolkit#readme) · [Engineering methodology](https://github.com/Dicureck/Dicureck/blob/main/knowledge-base/database-migration.md)
