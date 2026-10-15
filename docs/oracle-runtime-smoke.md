# Oracle Free Runtime Smoke — Scope & Evidence

This isolated CI integration builds on the existing **offline** Python checks with a **disposable Oracle Free** instance (the first successful run reported **Oracle AI Database 26ai Free, Release 23.26.3.0.0**) and independently created fictional rows.

The workflow runs only when the smoke script, original Oracle SQL, or the workflow changes, or by explicit manual dispatch. It does not install or connect to any real client database.

## Checks

1. Start an isolated Oracle Free PDB with an ephemeral credential.
2. Create a new disposable test schema with only schema creation grants.
3. Run original `sql/oracle/01_schema.sql` as Oracle SQL statements.
4. Insert three fictional customers and six orders, including leap-day, a voided order and a next-month order.
5. Run `02_monthly_revenue.sql` and `03_top_customers.sql` on the actual database and assert synthetic outputs.
6. Run `04_returning_id.sql` as PL/SQL, confirming its test INSERT was rolled back.
7. Save the Oracle banner and sample test results as a short-lived GitHub Actions artifact.

## Limitations

A successful run confirms a **specific Oracle Free version only**. It does not prove compatibility with Oracle 12.1.0.2, nor SQL Server-to-Oracle result equivalence, nor production deployment suitability.

The unrelated static migration toolkit checks remain the canonical evidence for its offline assessment, planning and CSV reconciliation behavior.

[Offline CI workflow](../.github/workflows/ci.yml) · [Runtime workflow](../.github/workflows/oracle-runtime.yml) · [Migration methodology](methodology.md).


## Verified execution · 2026-10-15

The [successful Oracle Free runtime CI run](https://github.com/Dicureck/oracle-migration-toolkit/actions/runs/38815481933) created the schema, inserted synthetic fixtures, executed both report queries and validated that the PL/SQL identity-return example rolled back its new record. The [original JSON evidence is version-controlled](../evidence/oracle-free-runtime-2026-10-15.json), not solely a temporary Actions artifact.

**Environment:** Oracle AI Database 26ai Free 23.26.3.0.0 (actual database banner), temporary PDB. The Oracle 12.1 target version and cross-engine equivalence remain out of scope.
