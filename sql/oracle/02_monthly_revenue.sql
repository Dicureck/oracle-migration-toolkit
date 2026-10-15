-- Case 01 / Oracle Database 12c+ (demo objects only)
-- Oracle's DATE/TIMESTAMP, interval and time-zone behavior must be validated.
WITH params AS (
    SELECT TO_TIMESTAMP('2024-02-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AS period_start
    FROM dual
)
SELECT o.customer_id,
       CAST(SUM(o.amount) AS NUMBER(18,2)) AS revenue
FROM demo_orders o
CROSS JOIN params p
WHERE o.created_at >= p.period_start
  AND o.created_at < CAST(ADD_MONTHS(TRUNC(CAST(p.period_start AS DATE), 'MM'), 1) AS TIMESTAMP)
  AND o.status = 'COMPLETED'
GROUP BY o.customer_id
ORDER BY o.customer_id;
