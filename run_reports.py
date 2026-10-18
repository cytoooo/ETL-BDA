import sqlite3
import pandas as pd
import glob
def generate_reports():
    print("Connecting to Data Warehouse...")
    conn = sqlite3.connect('ecommerce_warehouse.db')
    # Accessing the created SQL files
    sql_files = sorted(glob.glob("*.sql"))
    if not sql_files:
        print("No .sql files found in this directory.")
        return
    for file in sql_files:
        print("\n" + "*" * 60)
        print(f"EXECUTING: {file}")
        print("=" * 60)
        with open(file, 'r') as f:
            sql_query = f.read()
        # Executing the SQL and loading the result into a Pandas DataFrame for clean printing
        try:
            df = pd.read_sql_query(sql_query, conn)
            print(df.to_string(index=False))  # Prints the clean table without Pandas row numbers
        except Exception as e:
            print(f"Error running {file}: {e}")
    conn.close()
if __name__ == "__main__":
    generate_reports()