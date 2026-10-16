-- Parameters are driver-bound ISO values, never SQL interpolation.
DECLARE @StartDate DATETIME2(0) = CONVERT(DATETIME2(0), %s, 126);
DECLARE @EndDate DATETIME2(0) = CONVERT(DATETIME2(0), %s, 126);
SELECT customer_id,
       CAST(SUM(amount) AS DECIMAL(18,2)) AS revenue
FROM dbo.demo_orders
WHERE created_at >= @StartDate
  AND created_at < @EndDate
  AND status = 'COMPLETED'
GROUP BY customer_id
ORDER BY customer_id;
