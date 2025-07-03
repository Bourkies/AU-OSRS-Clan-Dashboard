# dashboard/Streamlit_utils.py
# Utility functions for the Streamlit dashboard.

import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from pathlib import Path
try:
    import tomllib
except ImportError:
    import tomli as tomllib
import os

# --- Function to track local database file changes ---
@st.cache_data(ttl=10)
def get_local_db_state():
    """
    Gets the modification time and size of the local database file.
    This acts as a cache key. When the file is replaced by the ETL,
    this function's output will change. This change is detected by Streamlit,
    triggering a cache invalidation for any data-loading functions that call this.
    This ensures that the Streamlit app always displays the latest data after an ETL run.
    """
    data_source = os.environ.get("DATA_SOURCE", "Online (Production)")
    if data_source == 'Local (Development)':
        try:
            local_db_path_str = os.environ.get("LOCAL_DB_PATH")
            if local_db_path_str:
                local_db_path = Path(local_db_path_str)
                if local_db_path.exists():
                    # Return a tuple of modification time and size to be robust.
                    # This unique signature represents the file's current state.
                    return (local_db_path.stat().st_mtime, local_db_path.stat().st_size)
        except (FileNotFoundError, Exception):
            # If file is temporarily unavailable during ETL write, return None.
            return None
    # For production, we don't need file-based tracking.
    return "production"

# --- Connection Management ---

@st.cache_resource(ttl=300)
def init_supabase_connection():
    """Initializes and caches the Supabase (Production) connection."""
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        return st.connection("supabase", type=SupabaseConnection, url=url, key=key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase connection: {e}. Check environment variables.")
        return None

def init_local_connection():
    """
    Initializes a new, non-cached connection to the local SQLite database.
    This is intentionally not cached with @st.cache_resource to prevent a
    persistent file lock, which would block the ETL process from replacing the database file.
    A new connection engine is created for each query and then disposed of.
    """
    try:
        local_db_path_str = os.environ.get("LOCAL_DB_PATH")
        if not local_db_path_str:
            st.error("LOCAL_DB_PATH environment variable is not set.")
            return None
        
        local_db_path = Path(local_db_path_str)

        if not local_db_path.exists():
            st.error(f"Local database file not found at the container path: {local_db_path}")
            return None

        # Return a new engine every time to avoid locking the file.
        return create_engine(f"sqlite:///{local_db_path.resolve()}")
    except Exception as e:
        st.error(f"Failed to initialize local SQLite connection: {e}")
        return None

def init_connection():
    """
    Initializes a connection to the database based on environment variables.
    - Production (Supabase) connections are cached for performance.
    - Local (SQLite) connections are NOT cached to prevent file locks.
    """
    data_source = os.environ.get("DATA_SOURCE", "Online (Production)")

    if data_source == 'Online (Production)':
        return init_supabase_connection()
    else: # Local (Development)
        return init_local_connection()

@st.cache_data(ttl=300)
def load_table(table_name: str) -> pd.DataFrame:
    """
    Loads an entire pre-aggregated table from the selected database.
    For local development, this function's cache is automatically invalidated
    when the database file is updated by the ETL process.
    """
    # By calling this function, we make st.cache_data aware of the db file's state.
    # When the file changes, the output of get_local_db_state() changes, and
    # Streamlit automatically invalidates the cache for this function.
    get_local_db_state()
    
    conn = init_connection()
    if conn is None: 
        st.error("Database connection is not available.")
        return pd.DataFrame()

    data_source = os.environ.get("DATA_SOURCE", "Online (Production)")

    try:
        if data_source == 'Online (Production)':
            response = conn.client.table(table_name).select("*").execute()
            df = pd.DataFrame(response.data)
        else: # Local (Development)
            # Using the connection object directly ensures it's properly closed
            # after the read operation, further helping to prevent file locks.
            with conn.connect() as connection:
                df = pd.read_sql_table(table_name, connection)

        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce', utc=True)
        return df
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e) or "no such table" in str(e).lower():
            st.warning(f"Table '{table_name}' not found in '{data_source}' source. The ETL might not have run for it yet.")
        else:
            st.error(f"Error loading table '{table_name}' from '{data_source}': {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_last_updated_timestamp() -> datetime:
    """Fetches the last ETL run timestamp from the metadata table."""
    df_meta = load_table('run_metadata')
    if not df_meta.empty and 'last_updated_utc' in df_meta.columns:
        # Handle potential empty dataframe after an ETL run before data is populated
        if df_meta['last_updated_utc'].iloc[0] is not None:
            return pd.to_datetime(df_meta['last_updated_utc'].iloc[0], utc=True)
    return None

@st.cache_data(ttl=300)
def load_dashboard_config() -> dict:
    """
    Loads the dashboard configuration table.
    """
    df = load_table('dashboard_config')
    if df.empty:
        return {}
    return pd.Series(df.value.values, index=df.key).to_dict()

def get_time_period_options(dashboard_config: dict) -> dict:
    """
    Generates the list of time period options for the sidebar, using
    the static labels generated by the ETL process.
    """
    prev_week_label = dashboard_config.get('label_prev_week', 'Previous Week')
    prev_month_label = dashboard_config.get('label_prev_month', 'Previous Month')
    ytd_label = dashboard_config.get('label_ytd', 'Year-to-Date')
    custom_days_label = dashboard_config.get('label_custom_days', 'Last 14 Days')

    options = {
        "All-Time": "All_Time",
        ytd_label: "YTD",
        prev_month_label: "Prev_Month",
        prev_week_label: "Prev_Week",
        custom_days_label: "Custom_Days"
    }
    return options
    
def format_gp(value):
    """
    Formats a numeric value into a human-readable GP string.
    """
    if pd.isna(value) or value is None:
        return "0 gp"
    return f"{int(value):,} gp"

def get_chart_data_for_period(df_timeseries, selected_period_label, dashboard_config, period_options_map, run_time, value_to_chart='Value'):
    """
    Filters the timeseries data for the selected period and prepares it for charting.
    Can chart 'Value' or 'Count'.
    """
    period_suffix = period_options_map.get(selected_period_label)
    cumulative_col = 'Cumulative_Value' if value_to_chart == 'Value' else 'Cumulative_Count'

    start_date, end_date, target_freq = None, None, None

    if period_suffix == 'Custom_Days':
        custom_days = int(dashboard_config.get('custom_lookback_days', 14))
        target_freq = '6H' if custom_days <=14 else 'D'
        start_date = (run_time - timedelta(days=custom_days)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = run_time
    elif period_suffix == 'Prev_Week':
        target_freq = 'D'
        week_start_day_name = dashboard_config.get('week_start_day', 'Monday')
        weekday_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        week_start_day_num = weekday_map.get(week_start_day_name, 0)
        
        days_since_week_start = (run_time.weekday() - week_start_day_num + 7) % 7
        start_of_current_week = (run_time - timedelta(days=days_since_week_start)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_of_current_week
        start_date = end_date - timedelta(days=7)
    elif period_suffix == 'Prev_Month':
        target_freq = 'D'
        end_date = run_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=1)).replace(day=1)
    elif period_suffix == 'YTD':
        target_freq = 'W'
        start_date = run_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = run_time
    else: # All-Time
        target_freq = 'W'

    if not target_freq: return pd.DataFrame()

    df_filtered_by_freq = df_timeseries[df_timeseries['Frequency'] == target_freq].copy()
    if df_filtered_by_freq.empty:
        return pd.DataFrame()

    df_filtered_by_freq['Date'] = pd.to_datetime(df_filtered_by_freq['Date'], utc=True)
    df_filtered_by_freq.sort_values('Date', inplace=True)

    if period_suffix == 'All_Time':
        df_all_time = df_filtered_by_freq.copy()
        df_all_time['Value'] = df_all_time[cumulative_col]
        
        if not df_all_time.empty:
            first_date = df_all_time.iloc[0]['Date']
            zero_date = first_date - timedelta(days=7)
            zero_row = pd.DataFrame([{'Date': zero_date, 'Value': 0}])
            return pd.concat([zero_row, df_all_time[['Date', 'Value']]], ignore_index=True)
        return df_all_time

    df_before_period = df_filtered_by_freq[df_filtered_by_freq['Date'] < start_date]
    start_value = df_before_period.iloc[-1][cumulative_col] if not df_before_period.empty else 0
    
    df_in_period = df_filtered_by_freq[(df_filtered_by_freq['Date'] >= start_date) & (df_filtered_by_freq['Date'] < end_date)].copy()
    
    df_in_period['Value'] = df_in_period[cumulative_col] - start_value
    
    zero_row = pd.DataFrame([{'Date': start_date, 'Value': 0}])
    
    return pd.concat([zero_row, df_in_period[['Date', 'Value']]], ignore_index=True)
