-- 5. Average delivery delay vs estimated delivery date & review score
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