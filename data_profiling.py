import os
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
for file in os.listdir('ecommerceDataset'):
    if file.endswith('.csv'):
        print("\n" + "=" * 80)
        print(f"FILE: {file}")
        print("*" * 80)
        df = pd.read_csv(f"ecommerceDataset/{file}", nrows=5)
        print(df.head())
