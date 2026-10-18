-- 4. Repeat-purchase rate (Using customer_unique_id)
WITH CustomerOrderCounts AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM stg_olist_customers_dataset c
    JOIN stg_olist_orders_dataset o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
),
RepeatCustomers AS (
    SELECT 
        COUNT(*) AS total_unique_customers,
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS returning_customers
    FROM CustomerOrderCounts
)
SELECT 
    total_unique_customers,
    returning_customers,
    ROUND((CAST(returning_customers AS FLOAT) / total_unique_customers) * 100, 2) AS repeat_purchase_rate_pct
FROM RepeatCustomers;