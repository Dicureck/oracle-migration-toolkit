-- Case 02 / SQL Server (demo objects only)
-- A unique secondary key makes rankings deterministic when totals tie.
SELECT TOP (10)
       o.customer_id,
       CAST(SUM(o.amount) AS DECIMAL(18,2)) AS revenue
FROM dbo.demo_orders AS o
WHERE o.status = 'COMPLETED'
GROUP BY o.customer_id
ORDER BY revenue DESC, o.customer_id ASC;
