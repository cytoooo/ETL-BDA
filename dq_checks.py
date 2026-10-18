import sqlite3
import pandas as pd
import logging
# Building a logger for documenting the data quality check process
dq_logger = logging.getLogger('dq_checks')
handler = logging.FileHandler('elt_pipeline_log.log', mode='a')
dq_logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
dq_logger.setLevel(logging.INFO)
def run_data_quality_checks():
    dq_logger.info("Starting Data Quality Checks")
    # Connecting to the database created by the ELT pipeline
    conn = sqlite3.connect('ecommerce_warehouse.db')
    dq_checks = {
        "1. Null or Duplicate order_id": """
                                         SELECT COUNT(*)
                                         FROM (SELECT order_id
                                               FROM stg_olist_orders_dataset
                                               GROUP BY order_id
                                               HAVING COUNT(order_id) > 1
                                                   OR order_id IS NULL);
                                         """,
        "2. Delivered date earlier than purchase date": """
                                                        SELECT COUNT(*)
                                                        FROM stg_olist_orders_dataset
                                                        WHERE order_delivered_customer_date < order_purchase_timestamp;
                                                        """,
        "3. Payment total not matching item price + freight": """
                                                              SELECT COUNT(*)
                                                              FROM (SELECT o.order_id,
                                                                           ROUND(SUM(i.price + i.freight_value), 2) as item_total,
                                                                           ROUND(MAX(p.pay_total), 2)               as payment_total
                                                                    FROM stg_olist_orders_dataset o
                                                                             JOIN stg_olist_order_items_dataset i ON o.order_id = i.order_id
                                                                             JOIN (SELECT order_id, SUM(payment_value) as pay_total
                                                                                   FROM stg_olist_order_payments_dataset
                                                                                   GROUP BY order_id) p
                                                                                  ON o.order_id = p.order_id
                                                                    GROUP BY o.order_id
                                                                    HAVING ABS(item_total - payment_total) > 0.10);
                                                              """,
        "4. Orders with no matching customer record": """
                                                      SELECT COUNT(*)
                                                      FROM stg_olist_orders_dataset o
                                                               LEFT JOIN stg_olist_customers_dataset c ON o.customer_id = c.customer_id
                                                      WHERE c.customer_id IS NULL;
                                                      """,
        "5. Review score outside 1-5 range": """
                                             SELECT COUNT(*)
                                             FROM stg_olist_order_reviews_dataset
                                             WHERE review_score < 1
                                                OR review_score > 5
                                                OR review_score IS NULL;
                                             """
    }
    total_failures = 0
    print("\n" + "*" * 50)
    print("DATA QUALITY REPORT")
    print("*" * 50)
    for check_name, sql_query in dq_checks.items():
        failed_rows = pd.read_sql(sql_query, conn).iloc[0, 0]
        if failed_rows > 0:
            dq_logger.warning(f"DQ FAILED: {check_name} ({failed_rows} rows violated)")
            print(f"FAILED: {check_name} ({failed_rows} rows violated)")
            total_failures += failed_rows
        else:
            dq_logger.info(f"DQ PASSED: {check_name}")
            print(f"PASSED: {check_name}")
    print("=" * 50 + "\n")
    conn.close()
    if total_failures > 0:
        error_msg = f"PIPELINE ALARM: {total_failures} total rows violated rules."
        dq_logger.error(error_msg)
        raise ValueError(error_msg)
    dq_logger.info("Pipeline finished successfully with all DQ checks passed.")
if __name__ == "__main__":
    run_data_quality_checks()