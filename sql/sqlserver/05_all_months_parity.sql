-- Same original fictional aggregate for isolated SQL Server Developer CI.
-- Result grain: month (YYYY-MM) × customer, status COMPLETED; amount DECIMAL(18,2).
SELECT CONVERT(char(7), created_at, 120) AS report_month,
       customer_id,
       CAST(SUM(amount) AS DECIMAL(18,2)) AS amount_su
FROM dbo.demo_orders
WHERE status = 'COMPLETED'
GROUP BY CONVERT(char(7), created_at, 120), customer_id
ORDER BY report_month, customer_id;
