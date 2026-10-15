-- Case 01 / SQL Server (demo objects only)
-- Contract: 2024-02, left-inclusive/right-exclusive period, status COMPLETED.
-- Important: DATEADD(month,1,..) is reviewed for this first-of-month boundary.
DECLARE @period_start DATETIME2(0) = '2024-02-01T00:00:00';

SELECT o.customer_id,
       CAST(SUM(o.amount) AS DECIMAL(18,2)) AS revenue
FROM dbo.demo_orders AS o
WHERE o.created_at >= @period_start
  AND o.created_at < DATEADD(month, 1, @period_start)
  AND o.status = 'COMPLETED'
GROUP BY o.customer_id
ORDER BY o.customer_id;
