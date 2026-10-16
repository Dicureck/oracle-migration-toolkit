# Output reconciliation design

A migration can preserve aggregate totals while changing row multiplicity. This demo compares result exports as **multisets**, not plain sets.

## Algorithm

1. Read both CSV files with headers; reject missing/duplicate headers and malformed rows.
2. Require the same column *names*; column order may differ.
3. Sort header names to build canonical row tuples.
4. Count tuple occurrences with `collections.Counter`.
5. Subtract counts to identify missing and extra occurrences; report total differences and bounded previews.

Complexity is approximately `O(n * k + m * k)` plus sorting distinct rows for the preview, for `n,m` rows and `k` columns. Row ordering is intentionally ignored.

## Counterexample

Left contains `(10, 17.00)` twice. Right contains `(10, 17.00)` once. A `SELECT DISTINCT` comparison would incorrectly say "equal". Our reconciler reports one missing occurrence and exits with status `1`.

## Comparison policy

Current behavior compares literal CSV field strings. Export date/time in the same ISO precision, format numeric values to the same scale, document NULL encoding and normalize case/collation according to the business contract **before exporting**. Do not trim or coerce silently in the reconciler; doing so risks hiding migration defects.

## What this proves

The tool proves *exported outputs* are identical under the declared string-format policy. It does not execute either query, ensure equivalent execution plans, or confirm that two database engines themselves produced the exported files.


## Live cross-engine complement (executed October 2026)

The existing CLI remains an **offline CSV multiset comparator**. A separate [real SQL Server ↔ Oracle Free workflow](../.github/workflows/cross-engine-parity.yml) now loads the exact same fictional 260-order fixture into **both temporary database engines**, verifies each stored row, executes the original February and deterministic Top 10 SQL and further month/date-window statements, normalizes each result to explicit two-decimal strings and checks every returned row against independent Python Decimal reference results.

[Successful run](https://github.com/Dicureck/oracle-migration-toolkit/actions/runs/38946759282) · [Permanent raw engine outputs and authoritative parity verdict](../evidence/cross-engine/ci-38946759282/) · [Technical case study](verified-cross-engine-parity-2026-10-16.md).

This live validator does **not** silently normalize zero-length strings: SQL Server returned EMPTY while Oracle returned NULL for the same literal test. Both observations are preserved as a migration risk, not interpreted as equivalent. Oracle 12.1 was not tested.
