-- Original cross-engine proof, Oracle Free 26ai tested target only; 12.1 is NOT verified.
-- Result grain: month (YYYY-MM) × customer, status COMPLETED; amount NUMBER(18,2).
SELECT TO_CHAR(created_at, 'YYYY-MM') AS report_month,
       customer_id,
       CAST(SUM(amount) AS NUMBER(18,2)) AS amount_su
FROM demo_orders
WHERE status = 'COMPLETED'
GROUP BY TO_CHAR(created_at, 'YYYY-MM'), customer_id
ORDER BY report_month, customer_id;
