-- 3. 7-day rolling average of daily order count
WITH DailyOrders AS (
    SELECT 
        DATE(order_purchase_timestamp) AS order_date,
        COUNT(order_id) AS daily_order_count
    FROM stg_olist_orders_dataset
    WHERE order_date IS NOT NULL
    GROUP BY order_date
)
SELECT 
    order_date,
    daily_order_count,
    ROUND(AVG(daily_order_count) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7d_avg
FROM DailyOrders;