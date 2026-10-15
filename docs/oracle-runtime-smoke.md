# Oracle Free Runtime Smoke — Scope & Evidence

This opt-in CI integration builds on the existing **offline** Python checks with a **disposable Oracle Free 23** instance and independently created fictional rows.

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
