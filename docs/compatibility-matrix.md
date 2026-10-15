# Compatibility matrix · SQL Server to Oracle 12c+

| T-SQL concept | Oracle pattern | Review requirement |
|---|---|---|
| `SELECT TOP (n) ... ORDER BY` | `ORDER BY ... FETCH FIRST n ROWS ONLY` | Stable deterministic order; inspect ties/`WITH TIES` |
| `DATEADD(month, n, date)` | `ADD_MONTHS(date, n)` | End-of-month behavior and DATE vs TIMESTAMP |
| `DATEDIFF(day, a, b)` | **No universal one-line equivalent** | SQL Server counts *boundaries*, not elapsed whole days |
| `GETDATE()` | `CURRENT_TIMESTAMP` / `SYSTIMESTAMP` / `SYSDATE` | Chosen time zone and return type |
| `ISNULL(x, y)` | `COALESCE(x, y)` or `NVL(x, y)` | Return type, conversion precedence, length, evaluation semantics |
| `IDENTITY(seed, step)` | `GENERATED ... AS IDENTITY` or sequence | Legacy key preservation, generated vs explicit key inserts |
| `OUTPUT INSERTED.id` | `RETURNING id INTO variable` | Single vs bulk DML and transaction behavior |
| `@table TABLE(...)` | Collection / SQL type / GTT | Lifetime, session semantics and query access |
| `#temporary_table` | GTT, PTT if supported, or alternate design | Privileges, object lifecycle and session cleanup |
| `TRY...CATCH` | PL/SQL `EXCEPTION` | Error mapping, retry and rollback rules |
| `NVARCHAR` / `NVARCHAR2` | NVARCHAR2 length semantics | Character set, max length, collation |
| `DATETIME2` | `TIMESTAMP(p)` | Precision and implicit timezone assumptions |
| `DECIMAL(18,2)` | `NUMBER(18,2)` | Precision/scale and rounding |
| `INCLUDE` index columns | Key index or alternative access path | Oracle optimizer/statistics; don't blindly duplicate index shape |
| `GO` batch delimiter | SQL client dependent `/` for PL/SQL blocks | `GO` is not SQL syntax and `/` is not a PL/SQL language statement |

## Non-goals

This document deliberately avoids replacing complex vendor-specific syntax through global string substitutions. Application-specific XML, user-defined functions, `MERGE`, procedural loops, optimizer hints, collation and dynamic SQL require focused analysis and live verification. Oracle 12c has release-specific differences (12.1 vs 12.2) that need target-version checks.
