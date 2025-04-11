# data_utils.py
import os
import pandas as pd
import traceback
from datetime import datetime # Keep if needed for potential future use here

# Assume data folder is in the same directory as app.py or set path accordingly
DATA_DIR = 'data'

def load_provided_data():
    """Loads and preprocesses all required CSV datasets.
    Returns:
        dict: A dictionary containing pandas DataFrames for each dataset if successful.
        None: If loading or critical preprocessing fails.
    """
    local_datasets = {} # Use a local dictionary to store loaded data
    print(f"Data Utils: Attempting to load datasets from '{DATA_DIR}' directory...")
    try:
        # --- Load data with correct index_col settings based on schema ---
        local_datasets['merchant'] = pd.read_csv(os.path.join(DATA_DIR, 'merchant.csv'))
        local_datasets['transaction_data'] = pd.read_csv(os.path.join(DATA_DIR, 'transaction_data.csv'), index_col=0)
        local_datasets['transaction_items'] = pd.read_csv(os.path.join(DATA_DIR, 'transaction_items.csv'), index_col=0)
        local_datasets['items'] = pd.read_csv(os.path.join(DATA_DIR, 'items.csv'))
        local_datasets['keywords'] = pd.read_csv(os.path.join(DATA_DIR, 'keywords.csv'), index_col=0)
        print("Data Utils: Initial dataset load complete.")

        # --- Data Preprocessing ---
        print("Data Utils: Starting data preprocessing...")

        # 1. Convert order_value to numeric, handle errors
        if 'transaction_data' in local_datasets and 'order_value' in local_datasets['transaction_data'].columns:
            local_datasets['transaction_data']['order_value'] = pd.to_numeric(local_datasets['transaction_data']['order_value'], errors='coerce')
            nan_count = local_datasets['transaction_data']['order_value'].isnull().sum()
            if nan_count > 0:
                print(f"Data Utils Warning: {nan_count} values in 'order_value' were non-numeric and have been set to 0.")
                local_datasets['transaction_data']['order_value'].fillna(0, inplace=True) # Fill NaN with 0 for calculations

        # 2. Convert ID columns to string type
        id_cols_to_str = {
            'merchant': ['merchant_id', 'city_id'],
            'transaction_data': ['merchant_id', 'order_id', 'eater_id'],
            'transaction_items': ['order_id', 'item_id', 'merchant_id'],
            'items': ['item_id', 'merchant_id']
        }
        for table, cols in id_cols_to_str.items():
            if table in local_datasets:
                for col in cols:
                    if col in local_datasets[table].columns:
                        if local_datasets[table][col].dtype != 'object': # Check if not already string/object
                            local_datasets[table][col] = local_datasets[table][col].astype(str).str.strip()
                    # else: print(f"Data Utils Info: Column '{col}' not found in table '{table}' for ID conversion.") # Optional info

        # 3. Convert transaction_data 'order_time' to datetime objects
        ts_col = 'order_time'
        if 'transaction_data' in local_datasets and ts_col in local_datasets['transaction_data'].columns:
            local_datasets['transaction_data']['order_time_dt'] = pd.to_datetime(local_datasets['transaction_data'][ts_col], errors='coerce')
            initial_rows = len(local_datasets['transaction_data'])
            # Drop rows where date conversion failed, as they are unusable for time series analysis
            local_datasets['transaction_data'].dropna(subset=['order_time_dt'], inplace=True)
            dropped_rows = initial_rows - len(local_datasets['transaction_data'])
            if dropped_rows > 0:
                print(f"Data Utils Info: Dropped {dropped_rows} rows due to invalid '{ts_col}' format.")
            print(f"Data Utils ✅: Column '{ts_col}' processed into 'order_time_dt'.")
        else:
            print(f"Data Utils ⚠️ Critical: Timestamp column '{ts_col}' not found in 'transaction_data'. Cannot proceed.")
            return None # Return None as timestamp is critical

        # 4. Check for presence of essential columns used in analysis functions
        req_cols_check = {
            'merchant': ['merchant_id', 'city_id'],
            'transaction_data': ['order_id', 'merchant_id', 'order_time_dt', 'order_value'],
            'transaction_items': ['order_id', 'item_id', 'merchant_id'],
            'items': ['item_id', 'item_name', 'cuisine_tag', 'merchant_id']
        }
        all_cols_present = True
        for table, cols in req_cols_check.items():
             if table not in local_datasets:
                 print(f"Data Utils ⚠️ Critical: Required data table '{table}' is missing.")
                 all_cols_present = False
                 continue # Skip column check if table is missing
             for col in cols:
                 if col not in local_datasets[table].columns:
                     print(f"Data Utils ⚠️ Critical: Required column '{col}' is missing in table '{table}'.")
                     all_cols_present = False

        if not all_cols_present:
             print("Data Utils ❌: Missing critical columns identified above. Data loading failed.")
             return None # Indicate failure

        # 5. Clean cuisine_tag (strip whitespace, replace empty strings with NA)
        if 'items' in local_datasets and 'cuisine_tag' in local_datasets['items'].columns:
             local_datasets['items']['cuisine_tag'] = local_datasets['items']['cuisine_tag'].astype(str).str.strip().replace('', pd.NA)
             # print(f"Data Utils Info: Unique cuisine tags after cleaning: {local_datasets['items']['cuisine_tag'].dropna().unique()}")

        print("Data Utils ✅: Data preprocessing finished successfully.")
        return local_datasets # Return the dictionary of DataFrames

    except FileNotFoundError as e:
        print(f"Data Utils ❌ FATAL: Data file not found: {e}. Ensure files are in '{DATA_DIR}'.")
        return None
    except KeyError as e:
        print(f"Data Utils ❌ FATAL: Missing expected column during processing: {e}. Check CSV header names.")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Data Utils ❌ FATAL: An unexpected error occurred during data loading/preprocessing: {e}")
        traceback.print_exc()
        return None