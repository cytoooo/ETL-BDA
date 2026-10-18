-- 2. Top 3 product categories per customer state by revenue
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