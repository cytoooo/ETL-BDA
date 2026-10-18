import os
# Dictionary containing the 5 required SQL queries
sql_queries = {
    "01_mom_revenue.sql": """-- 1. Month-over-month revenue and growth %
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
""",

    "02_top_categories_by_state.sql": """-- 2. Top 3 product categories per customer state by revenue
WITH StateCategoryRevenue AS (
    SELECT 
        c.customer_state,
        p.product_category_name,
        SUM(i.price) AS category_revenue
    FROM stg_olist_orders_dataset o
    JOIN stg_olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN stg_olist_order_items_dataset i ON o.order_id = i.order_id
    JOIN stg_olist_products_dataset p ON i.product_id = p.product_id
    WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL
    GROUP BY c.customer_state, p.product_category_name
),
RankedCategories AS (
    SELECT 
        customer_state,
        product_category_name,
        ROUND(category_revenue, 2) AS revenue,
        DENSE_RANK() OVER (PARTITION BY customer_state ORDER BY category_revenue DESC) AS rank
    FROM StateCategoryRevenue
)
SELECT customer_state, rank, product_category_name, revenue
FROM RankedCategories
WHERE rank <= 3;
""",

    "03_rolling_avg_orders.sql": """-- 3. 7-day rolling average of daily order count
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
""",

    "04_repeat_purchase_rate.sql": """-- 4. Repeat-purchase rate (Using customer_unique_id)
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
""",

    "05_delivery_delay_vs_reviews.sql": """-- 5. Average delivery delay vs estimated delivery date & review score
WITH OrderDelays AS (
    SELECT 
        o.order_id,
        r.review_score,
        -- SQLite uses JULIANDAY to calculate the difference between dates in days
        (JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date)) AS delay_days
    FROM stg_olist_orders_dataset o
    JOIN stg_olist_order_reviews_dataset r ON o.order_id = r.order_id
    WHERE o.order_delivered_customer_date IS NOT NULL 
      AND o.order_estimated_delivery_date IS NOT NULL
      AND r.review_score IS NOT NULL
)
SELECT 
    review_score,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay_days_vs_estimate,
    ROUND(MAX(delay_days), 2) AS worst_delay_in_days
FROM OrderDelays
GROUP BY review_score
ORDER BY review_score DESC;
"""
}
# Creating the .sql files
print("Generating SQL script files...")
for filename, sql_content in sql_queries.items():
    with open(filename, "w") as file:
        file.write(sql_content.strip())
    print(f"Created: {filename}")