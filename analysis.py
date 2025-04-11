# analysis.py
import pandas as pd
from datetime import datetime, timedelta
import traceback

# --- Popular Items Analysis (Using Unique Order Count) ---
def get_popular_items_by_frequency(merchant_id, datasets, days=30):
    """Analyzes popular items by unique order count in the last N days for a SPECIFIC merchant."""
    function_name = "get_popular_items_by_frequency"
    print(f"Analysis [{function_name}]: Analyzing for merchant: {merchant_id}, last {days} days.")
    try:
        # --- Input Validation ---
        required_tables = ['transaction_data', 'transaction_items', 'items']
        if not datasets or not all(k in datasets for k in required_tables):
            missing = [k for k in required_tables if k not in datasets] if datasets else required_tables
            return f"Error: Missing required data tables: {missing}."

        td_df = datasets['transaction_data']
        ti_df = datasets['transaction_items']
        i_df = datasets['items']

        # Define column names (ensure consistency)
        merchant_id_col = 'merchant_id'
        trans_id_col = 'order_id'
        ts_col_dt = 'order_time_dt'
        item_id_col = 'item_id'
        item_name_col = 'item_name'

        # Check required columns in dataframes
        if not all(c in td_df.columns for c in [merchant_id_col, ts_col_dt, trans_id_col]): return f"Error: Missing required columns in transaction_data."
        if not all(c in ti_df.columns for c in [trans_id_col, item_id_col, merchant_id_col]): return f"Error: Missing required columns in transaction_items."
        if not all(c in i_df.columns for c in [item_id_col, item_name_col]): return f"Error: Missing required columns in items."

        # Ensure key columns are correct type (should be handled by data_utils.py, but good resilience)
        if i_df[item_id_col].dtype != 'object': return f"Error: items.{item_id_col} is not string type."
        if ti_df[item_id_col].dtype != 'object': return f"Error: transaction_items.{item_id_col} is not string type."
        if ti_df[trans_id_col].dtype != 'object': return f"Error: transaction_items.{trans_id_col} is not string type."
        if td_df[merchant_id_col].dtype != 'object': return f"Error: transaction_data.{merchant_id_col} is not string type."


        # --- Date Range Calculation ---
        latest_date = td_df[ts_col_dt].max()
        if pd.isna(latest_date): return "Error: Cannot determine latest date from data."
        start_date = (latest_date.normalize() - timedelta(days=days-1)).replace(tzinfo=latest_date.tzinfo)
        end_date = latest_date
        print(f"Analysis [{function_name}]: Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # --- Data Filtering ---
        recent_trans = td_df[
            (td_df[merchant_id_col] == merchant_id) &
            (td_df[ts_col_dt] >= start_date) &
            (td_df[ts_col_dt] <= end_date)
        ]
        if recent_trans.empty:
            print(f"Analysis [{function_name}]: No recent transactions found for merchant {merchant_id}.")
            return None # Indicates no data, not an error

        recent_trans_ids = recent_trans[trans_id_col].unique()
        # Filter relevant transaction items FIRST by order_id
        relevant_items_df = ti_df[ti_df[trans_id_col].isin(recent_trans_ids)]
        # Optional: Filter again by merchant if order_id could contain multiple merchants (unlikely)
        # relevant_items_df = relevant_items_df[relevant_items_df[merchant_id_col] == merchant_id]
        if relevant_items_df.empty:
            print(f"Analysis [{function_name}]: No corresponding items found in transaction_items.")
            return None

        # --- MODIFIED Calculation: Count unique orders per item ---
        item_order_counts = relevant_items_df.groupby(item_id_col)[trans_id_col].nunique()
        item_frequency = item_order_counts.reset_index()
        item_frequency.columns = [item_id_col, 'unique_order_count'] # New column name
        # --- End Modification ---

        # Get TOP N most frequent by unique orders
        top_items_freq = item_frequency.sort_values(by='unique_order_count', ascending=False).head(5)
        if top_items_freq.empty:
            print(f"Analysis [{function_name}]: No items found after frequency count.")
            return None

        # --- Result Formatting ---
        top_items_details = pd.merge(top_items_freq, i_df[[item_id_col, item_name_col]], on=item_id_col, how='left')
        top_items_details[item_name_col] = top_items_details.apply(
            lambda row: row[item_name_col] if pd.notna(row[item_name_col]) else f'Unknown Item (ID: {row[item_id_col]})',
            axis=1
        )

        results = top_items_details.to_dict('records')
        for item in results: item['unique_order_count'] = int(item['unique_order_count']) # Ensure int type

        print(f"Analysis [{function_name}]: Found popular items for merchant {merchant_id}: {results}")
        return results

    except KeyError as e:
        print(f"Analysis Error [{function_name}]: Missing column {e}")
        return f"Error: Analysis failed due to missing column ({e}). Check data files and column names in code."
    except Exception as e:
        print(f"Analysis Error [{function_name}]: {e}")
        traceback.print_exc()
        return f"Error: An unexpected error occurred during {function_name}."


# --- Sales Summary Analysis ---
def get_sales_summary(merchant_id, datasets, time_period_str="last_7_days"):
    """Calculates sales summary for a SPECIFIC merchant."""
    function_name = "get_sales_summary"
    print(f"Analysis [{function_name}]: Analyzing for merchant: {merchant_id}, period: {time_period_str}")
    try:
        # --- Input Validation ---
        if not datasets or 'transaction_data' not in datasets: return "Error: Missing transaction_data table."
        trans_df = datasets['transaction_data']

        merchant_id_col = 'merchant_id'
        ts_col_dt = 'order_time_dt'
        order_value_col = 'order_value'
        order_id_col = 'order_id'
        required_cols = [merchant_id_col, ts_col_dt, order_value_col, order_id_col]
        if not all(c in trans_df.columns for c in required_cols):
             missing_cols = [c for c in required_cols if c not in trans_df.columns]
             return f"Error: Missing required columns in transaction_data: {missing_cols}."
        if not pd.api.types.is_numeric_dtype(trans_df[order_value_col]): return f"Error: '{order_value_col}' column is not numeric."
        if trans_df[merchant_id_col].dtype != 'object': return f"Error: transaction_data.{merchant_id_col} is not string type."


        # --- Date Range Calculation ---
        latest_date = trans_df[ts_col_dt].max()
        if pd.isna(latest_date): return "Error: Cannot determine date range."
        days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
        days = days_map.get(time_period_str, 30) # Default 30 days if invalid period string
        start_date = (latest_date.normalize() - timedelta(days=days-1)).replace(tzinfo=latest_date.tzinfo)
        end_date = latest_date
        print(f"Analysis [{function_name}]: Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # --- Data Filtering ---
        filtered_trans = trans_df[
            (trans_df[merchant_id_col] == merchant_id) &
            (trans_df[ts_col_dt] >= start_date) &
            (trans_df[ts_col_dt] <= end_date)
        ]
        if filtered_trans.empty:
            print(f"Analysis [{function_name}]: No transactions found for merchant {merchant_id} in the period.")
            return None

        # --- Calculation ---
        total_sales = filtered_trans[order_value_col].sum() # NaNs already handled during load
        order_count = filtered_trans[order_id_col].nunique()

        # --- Result Formatting ---
        results = {
            'total_sales': total_sales, 'order_count': order_count,
            'start_date': start_date.strftime('%Y-%m-%d'), 'end_date': end_date.strftime('%Y-%m-%d'),
            'period_analyzed': time_period_str
        }
        print(f"Analysis [{function_name}]: Calculated sales summary for merchant {merchant_id}: {results}")
        return results

    except KeyError as e:
        print(f"Analysis Error [{function_name}]: Missing column {e}")
        return f"Error: Analysis failed due to missing column ({e}). Check data files and column names in code."
    except Exception as e:
        print(f"Analysis Error [{function_name}]: {e}")
        traceback.print_exc()
        return f"Error: An unexpected error occurred during {function_name}."


# --- Regional Popular Cuisine Analysis ---
def get_popular_cuisines_in_city(city_id, datasets, days=90):
    """Analyzes popular cuisine tags based on unique order count across all merchants in a given city."""
    function_name = "get_popular_cuisines_in_city"
    print(f"Analysis [{function_name}]: Analyzing for city ID: {city_id}, last {days} days.")
    try:
        # --- Input Validation ---
        required_tables = ['merchant', 'transaction_data', 'transaction_items', 'items']
        if not datasets or not all(k in datasets for k in required_tables):
            missing = [k for k in required_tables if k not in datasets] if datasets else required_tables
            return f"Error: Missing required data tables: {missing}."

        m_df = datasets['merchant']
        td_df = datasets['transaction_data']
        ti_df = datasets['transaction_items']
        i_df = datasets['items']

        merchant_id_col = 'merchant_id'
        city_id_col = 'city_id'
        trans_id_col = 'order_id'
        ts_col_dt = 'order_time_dt'
        item_id_col = 'item_id'
        cuisine_tag_col = 'cuisine_tag'

        # Check required columns
        if city_id_col not in m_df.columns: return f"Error: Missing '{city_id_col}' in merchant table."
        if not all(c in td_df.columns for c in [merchant_id_col, ts_col_dt, trans_id_col]): return f"Error: Missing required columns in transaction_data."
        if not all(c in ti_df.columns for c in [trans_id_col, item_id_col]): return f"Error: Missing required columns in transaction_items."
        if not all(c in i_df.columns for c in [item_id_col, cuisine_tag_col]): return f"Error: Missing required columns ('{item_id_col}', '{cuisine_tag_col}') in items."

        # Ensure types for comparison/merge (assuming loaded as strings)
        if m_df[city_id_col].dtype != 'object': return f"Error: merchant.{city_id_col} is not string type."
        if i_df[item_id_col].dtype != 'object': return f"Error: items.{item_id_col} is not string type."
        if ti_df[item_id_col].dtype != 'object': return f"Error: transaction_items.{item_id_col} is not string type."
        if ti_df[trans_id_col].dtype != 'object': return f"Error: transaction_items.{trans_id_col} is not string type."
        if td_df[merchant_id_col].dtype != 'object': return f"Error: transaction_data.{merchant_id_col} is not string type."


        # --- Date Range Calculation ---
        latest_date = td_df[ts_col_dt].max()
        if pd.isna(latest_date): return "Error: Cannot determine date range."
        start_date = (latest_date.normalize() - timedelta(days=days-1)).replace(tzinfo=latest_date.tzinfo)
        end_date = latest_date
        print(f"Analysis [{function_name}]: Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # --- Data Filtering ---
        # 1. Get merchants in the target city
        merchants_in_city = m_df[m_df[city_id_col] == city_id][merchant_id_col].unique()
        if len(merchants_in_city) == 0:
            print(f"Analysis [{function_name}]: No merchants found for city ID {city_id}.")
            return None
        print(f"Analysis [{function_name}]: Found {len(merchants_in_city)} merchants in city {city_id}.")

        # 2. Filter transactions for these merchants and date range
        city_transactions = td_df[
            (td_df[merchant_id_col].isin(merchants_in_city)) &
            (td_df[ts_col_dt] >= start_date) &
            (td_df[ts_col_dt] <= end_date)
        ]
        if city_transactions.empty:
            print(f"Analysis [{function_name}]: No transactions found for city {city_id} within the date range.")
            return None
        city_order_ids = city_transactions[trans_id_col].unique()
        print(f"Analysis [{function_name}]: Found {len(city_order_ids)} orders in city {city_id} for the period.")

        # 3. Filter transaction items for these orders
        city_trans_items = ti_df[ti_df[trans_id_col].isin(city_order_ids)]
        if city_trans_items.empty:
            print(f"Analysis [{function_name}]: No transaction items found for the orders in city {city_id}.")
            return None

        # 4. Merge with items table to get non-empty cuisine tags
        items_with_cuisine = i_df[[item_id_col, cuisine_tag_col]].dropna(subset=[cuisine_tag_col])
        if items_with_cuisine.empty: return f"Error: No items found with cuisine tags in the items table."

        city_items_with_cuisine = pd.merge(
            city_trans_items[[trans_id_col, item_id_col]],
            items_with_cuisine,
            on=item_id_col,
            how='inner'
        )
        if city_items_with_cuisine.empty:
            print(f"Analysis [{function_name}]: No items with valid cuisine tags found in the transactions for city {city_id}.")
            return None
        print(f"Analysis [{function_name}]: Found {len(city_items_with_cuisine)} items with cuisine tags in city orders.")

        # --- Calculation ---
        # Count unique orders per cuisine tag
        cuisine_order_counts = city_items_with_cuisine.groupby(cuisine_tag_col)[trans_id_col].nunique()
        cuisine_frequency = cuisine_order_counts.sort_values(ascending=False)

        # --- Result Formatting ---
        top_cuisines = cuisine_frequency.head(5).index.tolist()

        if not top_cuisines:
            print(f"Analysis [{function_name}]: Could not determine top cuisines for city {city_id}.")
            return None

        print(f"Analysis [{function_name}]: Found top cuisines in city {city_id}: {top_cuisines}")
        return top_cuisines

    except KeyError as e:
        print(f"Analysis Error [{function_name}]: Missing column {e}")
        return f"Error: Analysis failed due to missing column ({e}). Check data files and column names in code."
    except Exception as e:
        print(f"Analysis Error [{function_name}]: {e}")
        traceback.print_exc()
        return f"Error: An unexpected error occurred during {function_name}."


# --- Low Performing Items Analysis (Using Unique Order Count) ---
def get_low_performing_items(merchant_id, datasets, days=30, top_n=5):
    """Analyzes low-performing items by unique order count in the last N days for a SPECIFIC merchant."""
    function_name = "get_low_performing_items"
    print(f"Analysis [{function_name}]: Analyzing for merchant: {merchant_id}, last {days} days, bottom {top_n}.")
    try:
        # --- Input Validation --- (Similar to popular items)
        required_tables = ['transaction_data', 'transaction_items', 'items']
        if not datasets or not all(k in datasets for k in required_tables):
            missing = [k for k in required_tables if k not in datasets] if datasets else required_tables
            return f"Error: Missing required data tables: {missing}."

        td_df = datasets['transaction_data']
        ti_df = datasets['transaction_items']
        i_df = datasets['items']

        merchant_id_col = 'merchant_id'
        trans_id_col = 'order_id'
        ts_col_dt = 'order_time_dt'
        item_id_col = 'item_id'
        item_name_col = 'item_name'

        if not all(c in td_df.columns for c in [merchant_id_col, ts_col_dt, trans_id_col]): return f"Error: Missing required columns in transaction_data."
        if not all(c in ti_df.columns for c in [trans_id_col, item_id_col, merchant_id_col]): return f"Error: Missing required columns in transaction_items."
        if not all(c in i_df.columns for c in [item_id_col, item_name_col]): return f"Error: Missing required columns in items."
        if i_df[item_id_col].dtype != 'object': return f"Error: items.{item_id_col} is not string type."
        if ti_df[item_id_col].dtype != 'object': return f"Error: transaction_items.{item_id_col} is not string type."
        if ti_df[trans_id_col].dtype != 'object': return f"Error: transaction_items.{trans_id_col} is not string type."
        if td_df[merchant_id_col].dtype != 'object': return f"Error: transaction_data.{merchant_id_col} is not string type."

        # --- Date Range Calculation ---
        latest_date = td_df[ts_col_dt].max()
        if pd.isna(latest_date): return "Error: Cannot determine latest date."
        start_date = (latest_date.normalize() - timedelta(days=days-1)).replace(tzinfo=latest_date.tzinfo)
        end_date = latest_date
        print(f"Analysis [{function_name}]: Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # --- Data Filtering --- (Identical to popular items)
        recent_trans = td_df[(td_df[merchant_id_col] == merchant_id) & (td_df[ts_col_dt] >= start_date) & (td_df[ts_col_dt] <= end_date)]
        if recent_trans.empty:
            print(f"Analysis [{function_name}]: No recent transactions found for merchant {merchant_id}.")
            return None

        recent_trans_ids = recent_trans[trans_id_col].unique()
        relevant_items_df = ti_df[ti_df[trans_id_col].isin(recent_trans_ids)]
        # Optional filter: relevant_items_df = relevant_items_df[relevant_items_df[merchant_id_col] == merchant_id]
        if relevant_items_df.empty:
            print(f"Analysis [{function_name}]: No corresponding items found.")
            return None

        # --- MODIFIED Calculation: Count unique orders per item ---
        item_order_counts = relevant_items_df.groupby(item_id_col)[trans_id_col].nunique()
        item_frequency = item_order_counts.reset_index()
        item_frequency.columns = [item_id_col, 'unique_order_count'] # New column name
        # --- End Modification ---

        # --- KEY DIFFERENCE: Sort ascending and take head ---
        bottom_items_freq = item_frequency.sort_values(by='unique_order_count', ascending=True).head(top_n)

        if bottom_items_freq.empty:
            print(f"Analysis [{function_name}]: No items found after frequency count.")
            return None

        # --- Result Formatting ---
        bottom_items_details = pd.merge(bottom_items_freq, i_df[[item_id_col, item_name_col]], on=item_id_col, how='left')
        bottom_items_details[item_name_col] = bottom_items_details.apply(
            lambda row: row[item_name_col] if pd.notna(row[item_name_col]) else f'Unknown Item (ID: {row[item_id_col]})',
            axis=1
        )

        results = bottom_items_details.to_dict('records')
        for item in results: item['unique_order_count'] = int(item['unique_order_count']) # Ensure int type

        print(f"Analysis [{function_name}]: Found low performing items for merchant {merchant_id}: {results}")
        return results

    except KeyError as e: return f"Error: Missing expected column ({e}). Check analysis logic and data."
    except Exception as e:
        print(f"Analysis Error [{function_name}]: {e}")
        traceback.print_exc()
        return f"Error: An unexpected error occurred during {function_name}."