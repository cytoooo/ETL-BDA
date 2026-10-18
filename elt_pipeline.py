import sqlite3
import os
import pandas as pd
import logging
#Building a custom logger to document the flow of the pipeline
elt_logger = logging.getLogger(__name__)
handler = logging.FileHandler('elt_pipeline_log.log',mode='w')
elt_logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
elt_logger.setLevel(logging.INFO)
#Listing the expected files
expected_files = [
    'olist_customers_dataset.csv', 'olist_geolocation_dataset.csv',
    'olist_orders_dataset.csv', 'olist_order_items_dataset.csv',
    'olist_order_payments_dataset.csv', 'olist_order_reviews_dataset.csv',
    'olist_products_dataset.csv', 'olist_sellers_dataset.csv',
    'product_category_name_translation.csv'
]
#Logging a missing file
folder_contents = os.listdir('ecommerceDataset')
missing_files = [f for f in expected_files if f not in folder_contents]
if missing_files:
    error_msg = f"Pipeline failed: Missing expected files from directory: {missing_files}"
    elt_logger.error(error_msg)
    raise FileNotFoundError(error_msg)
#Connection object to communicate with local Database
conn=sqlite3.connect('ecommerce_warehouse.db')
#Iterating through files to build the staging tables
for file in expected_files:
    table_name = file.replace('.csv','')
    df = pd.read_csv(f"ecommerceDataset/{file}",low_memory=False)
    #Saving raw tables to the database
    elt_logger.info(f"Loading raw table: raw_{table_name}")
    df.to_sql(f"raw_{table_name}", conn, if_exists='replace', index=False)
    try:
        if file=='olist_customers_dataset.csv':
            #drop rows with missing ids
            elt_logger.info("cleaning customers and dropping null IDs")
            initial_rows = len(df)
            df = df.dropna(subset=['customer_id','customer_unique_id'])
            df['customer_zip_code_prefix'] = df['customer_zip_code_prefix'].astype(str).str.zfill(5)
            dropped_count = initial_rows - len(df)
            elt_logger.info(f"dropped {dropped_count} rows with null customer IDs")
        elif file=='olist_geolocation_dataset.csv':
            elt_logger.info("cleaning geolocation by aggregating the zip codes latitude and longitude values")
            initial_rows = len(df)
            #drop rows with missing coordinates
            df = df.dropna(subset=['geolocation_lat', 'geolocation_lng'])
            dropped_count = initial_rows - len(df)
            df['geolocation_zip_code_prefix'] = df['geolocation_zip_code_prefix'].astype(str).str.zfill(5)
            df = df.groupby('geolocation_zip_code_prefix').agg({'geolocation_lat':'mean','geolocation_lng':'mean','geolocation_city':'first','geolocation_state':'first'}).reset_index()
            elt_logger.info(f"dropped {dropped_count} rows with null latitude or longitude values")
        elif file=='olist_orders_dataset.csv':
            elt_logger.info("Cleaning orders: converting dates and dropping null IDs")
            initial_rows = len(df)
            df = df.dropna(subset=['order_id', 'customer_id'])
            dropped_count = initial_rows - len(df)
            date_cols = [
                'order_purchase_timestamp',
                'order_approved_at',
                'order_delivered_carrier_date',
                'order_delivered_customer_date',
                'order_estimated_delivery_date'
            ]
            for col in date_cols:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elt_logger.info(f"dropped {dropped_count} rows with null order or customer IDs")
        elif file=='olist_order_items_dataset.csv':
            elt_logger.info("Cleaning order items: parsing dates and dropping null IDs")
            initial_rows = len(df)
            df = df.dropna(subset=['order_id', 'product_id', 'seller_id'])
            dropped_count = initial_rows - len(df)
            df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')
            elt_logger.info(f"dropped {dropped_count} rows with null IDs")
        elif file=='olist_order_payments_dataset.csv':
            elt_logger.info("Cleaning order payments: dropping null order IDs")
            initial_rows = len(df)
            df = df.dropna(subset=['order_id'])
            dropped_count = initial_rows - len(df)
            elt_logger.info(f"dropped {dropped_count} rows with null order IDs")
        elif file=='olist_order_reviews_dataset.csv':
            elt_logger.info("Cleaning order reviews: parsing dates")
            initial_rows = len(df)
            df = df.dropna(subset=['review_id', 'order_id'])
            dropped_count = initial_rows - len(df)
            df['review_creation_date'] = pd.to_datetime(df['review_creation_date'], errors='coerce')
            df['review_answer_timestamp'] = pd.to_datetime(df['review_answer_timestamp'], errors='coerce')
            elt_logger.info(f"dropped {dropped_count} rows with null IDs")
        elif file=='olist_products_dataset.csv':
            elt_logger.info("Cleaning products: filling null categories and dropping null IDs")
            initial_rows = len(df)
            df = df.dropna(subset=['product_id'])
            dropped_count = initial_rows - len(df)
            # Count how many empty categories exist before we fill them
            filled_categories = df['product_category_name'].isna().sum()
            df['product_category_name'] = df['product_category_name'].fillna('unknown')
            elt_logger.info(f"dropped {dropped_count} rows with null product IDs and filled {filled_categories} missing categories")
        elif file=='olist_sellers_dataset.csv':
            elt_logger.info("Cleaning sellers: dropping null IDs and fixing zip codes")
            initial_rows = len(df)
            df = df.dropna(subset=['seller_id'])
            dropped_count = initial_rows - len(df)
            df['seller_zip_code_prefix'] = df['seller_zip_code_prefix'].astype(str).str.zfill(5)
            elt_logger.info(f"dropped {dropped_count} rows with null seller IDs")
        elif file=='product_category_name_translation.csv':
            elt_logger.info("Cleaning category translations")
            initial_rows = len(df)
            df = df.dropna()
            dropped_count = initial_rows - len(df)
            elt_logger.info(f"dropped {dropped_count} incomplete translation rows")
    except KeyError as e:
        error_msg = f"Pipeline failed: Missing expected column {e} in {file}"
        elt_logger.error(error_msg)
        raise KeyError(error_msg)
    df.to_sql(f"stg_{table_name}", conn, if_exists='replace',index=False)
#Building mart table
elt_logger.info("Building mart_orders_summary table")
mart_query = """
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.order_purchase_timestamp,
    SUM(i.price) AS total_order_value,
    MAX(r.review_score) AS review_score
FROM stg_olist_orders_dataset o
LEFT JOIN stg_olist_order_items_dataset i ON o.order_id = i.order_id
LEFT JOIN stg_olist_order_reviews_dataset r ON o.order_id = r.order_id
LEFT JOIN stg_olist_customers_dataset c ON o.customer_id = c.customer_id
GROUP BY 
    o.order_id, 
    o.customer_id, 
    c.customer_unique_id,
    o.order_status, 
    o.order_purchase_timestamp;
"""
mart_df = pd.read_sql(mart_query, conn)
mart_df.to_sql('mart_orders_summary', conn, if_exists='replace', index=False)
elt_logger.info("Pipeline complete.")
conn.close()