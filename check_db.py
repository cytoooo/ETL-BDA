import sqlite3
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
conn = sqlite3.connect('ecommerce_warehouse.db')
table_query = """
              SELECT name
              FROM sqlite_master
              WHERE type = 'table'
                AND (name LIKE 'stg_%' OR name = 'mart_orders_summary')
              ORDER BY name; \
              """
tables_df = pd.read_sql(table_query, conn)
tables_list = tables_df['name'].tolist()
for table in tables_list:
    print(f"\n{'=' * 50}")
    print(f"VIEWING TABLE: {table}")
    print(f"{'=' * 50}")
    data_query = f"SELECT * FROM {table} LIMIT 5;"
    df = pd.read_sql(data_query, conn)
    print(df)
    print("\n")
conn.close()