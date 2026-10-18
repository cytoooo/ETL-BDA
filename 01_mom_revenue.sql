-- 1. Month-over-month revenue and growth %
WITH MonthlyRevenue AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS order_month,
        SUM(p.payment_value) AS total_revenue
    FROM stg_olist_orders_dataset o
    JOIN stg_olist_order_payments_dataset p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered' AND order_month IS NOT NULL
    GROUP BY order_month
),
MoMGrowth AS (
    SELECT 
        order_month,
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY order_month) AS prev_month_revenue
    FROM MonthlyRevenue
)
SELECT 
    order_month,
    ROUND(total_revenue, 2) AS current_revenue,
    ROUND(prev_month_revenue, 2) AS previous_revenue,
    ROUND(((total_revenue - prev_month_revenue) / prev_month_revenue) * 100, 2) AS growth_percentage
FROM MoMGrowth;