# Proposed Migration Dependency Order

> Review-only plan. This file does not run DDL/DML.

| # | Object | Type | Dependencies | Approval |
| ---: | --- | --- | --- | --- |
| 1 | `DEMO_AUDIT_SEQ` | sequence | — | Standard verification |
| 2 | `DEMO_CUSTOMERS` | table | — | Standard verification |
| 3 | `DEMO_ORDERS` | table | `DEMO_CUSTOMERS` | Standard verification |
| 4 | `DEMO_MONTHLY_REVENUE_V` | view | `DEMO_ORDERS`, `DEMO_CUSTOMERS` | Standard verification |
| 5 | `DEMO_ORDER_TOTAL` | function | `DEMO_ORDERS` | Manual review |
| 6 | `DEMO_REPORTING_PKG` | package | `DEMO_ORDER_TOTAL`, `DEMO_MONTHLY_REVENUE_V` | Manual review |
| 7 | `DEMO_SAMPLE_DATA` | data | `DEMO_ORDERS`, `DEMO_CUSTOMERS` | Manual review |
| 8 | `DEMO_RECONCILIATION` | procedure | `DEMO_SAMPLE_DATA`, `DEMO_REPORTING_PKG` | Standard verification |
