import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def generate_simple_metrics_and_charts():
    print("Connecting to the database...")
    conn = sqlite3.connect('ecommerce_warehouse.db')
    sns.set_theme(style="whitegrid")
    #NORTH STAR METRIC - Total Monthly Revenue
    print("Generating: Total Monthly Revenue...")
    query_revenue = """
                    SELECT STRFTIME('%Y-%m', o.order_purchase_timestamp) AS month, 
            SUM(p.payment_value) AS total_revenue
                    FROM stg_olist_orders_dataset o
                        JOIN stg_olist_order_payments_dataset p \
                    ON o.order_id = p.order_id
                    WHERE o.order_status = 'delivered'
                      AND month IS NOT NULL
                    GROUP BY month
                    ORDER BY month; \
                    """
    df_rev = pd.read_sql_query(query_revenue, conn)
    plt.figure(figsize=(10, 5))
    plt.plot(df_rev['month'], df_rev['total_revenue'], marker='o', color='blue', linewidth=2)
    plt.title('North Star: Total Monthly Revenue', fontsize=14, pad=10)
    plt.ylabel('Revenue')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('01_monthly_revenue.png')
    plt.close()
    #GUARDRAIL - Average Delivery Time
    print("Generating: Average Delivery Time...")
    query_delivery = """
                     SELECT STRFTIME('%Y-%m', order_purchase_timestamp) AS month, 
            AVG(JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_purchase_timestamp)) AS avg_delivery_days
                     FROM stg_olist_orders_dataset
                     WHERE order_status = 'delivered'
                       AND month IS NOT NULL
                     GROUP BY month
                     ORDER BY month; \
                     """
    df_del = pd.read_sql_query(query_delivery, conn)
    plt.figure(figsize=(10, 5))
    plt.bar(df_del['month'], df_del['avg_delivery_days'], color='orange')
    plt.title('Guardrail: Average Delivery Time (Days) per Month', fontsize=14, pad=10)
    plt.ylabel('Days to Deliver')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('02_average_delivery_time.png')
    plt.close()
    #GUARDRAIL - Review Score Distribution
    print("Generating: Review Score Pulse...")
    query_reviews = """
                    SELECT review_score, \
                           COUNT(*) AS total_reviews
                    FROM stg_olist_order_reviews_dataset
                    WHERE review_score IS NOT NULL
                    GROUP BY review_score
                    ORDER BY review_score; \
                    """
    df_rev_score = pd.read_sql_query(query_reviews, conn)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df_rev_score, x='review_score', y='total_reviews', palette='viridis')
    plt.title('Guardrail: Overall Review Score Distribution', fontsize=14, pad=10)
    plt.xlabel('Review Score (1 to 5)')
    plt.ylabel('Number of Reviews')
    plt.tight_layout()
    plt.savefig('03_review_scores.png')
    plt.close()
    #GUARDRAIL - Order Cancellation Rate
    print("Generating: Order Cancellation Rate...")
    query_cancel = """
                   SELECT STRFTIME('%Y-%m', order_purchase_timestamp) AS month, 
            SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS cancel_rate_pct
                   FROM stg_olist_orders_dataset
                   WHERE month IS NOT NULL
                   GROUP BY month
                   ORDER BY month; \
                   """
    df_cancel = pd.read_sql_query(query_cancel, conn)
    plt.figure(figsize=(10, 5))
    plt.plot(df_cancel['month'], df_cancel['cancel_rate_pct'], marker='x', color='red', linewidth=2)
    plt.title('Guardrail: Monthly Order Cancellation Rate (%)', fontsize=14, pad=10)
    plt.ylabel('Cancellation Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('04_cancellation_rate.png')
    plt.close()

    conn.close()
if __name__ == "__main__":
    generate_simple_metrics_and_charts()