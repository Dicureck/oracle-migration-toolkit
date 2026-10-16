-- Binds :1 and :2 as ISO 8601 strings; half-open TIMESTAMP(0) range.
SELECT customer_id,
       CAST(SUM(amount) AS NUMBER(18,2)) AS revenue
FROM demo_orders
WHERE created_at >= TO_TIMESTAMP(:1, 'YYYY-MM-DD"T"HH24:MI:SS')
  AND created_at <  TO_TIMESTAMP(:2, 'YYYY-MM-DD"T"HH24:MI:SS')
  AND status = 'COMPLETED'
GROUP BY customer_id
ORDER BY customer_id;
