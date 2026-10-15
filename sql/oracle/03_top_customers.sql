-- Case 02 / Oracle Database 12c+ (demo objects only)
-- FETCH FIRST n ROWS ONLY is a row-limiting clause. ORDER BY must be stable.
SELECT o.customer_id,
       CAST(SUM(o.amount) AS NUMBER(18,2)) AS revenue
FROM demo_orders o
WHERE o.status = 'COMPLETED'
GROUP BY o.customer_id
ORDER BY revenue DESC, o.customer_id ASC
FETCH FIRST 10 ROWS ONLY;
