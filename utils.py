# dashboard/utils.py
# Utility functions for the Streamlit dashboard.

import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import datetime

@st.cache_resource
def init_connection():
    """
    Initializes a connection to the Supabase database using credentials
    stored in Streamlit's secrets management.
    """
    try:
        # This version explicitly reads the URL and Key from Streamlit's secrets
        # and passes them to the connection function. This is more reliable.
        #
        # Make sure you have a .streamlit/secrets.toml file with this structure:
        # [connections.supabase]
        # url="YOUR_SUPABASE_URL"
        # key="YOUR_SUPABASE_KEY"
        
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        return st.connection("supabase", type=SupabaseConnection, url=url, key=key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase connection: {e}. Please check your .streamlit/secrets.toml file.")
        return None

@st.cache_data(ttl=600)
def load_table(table_name: str) -> pd.DataFrame:
    """
    Loads an entire pre-aggregated table from the database.
    This function is cached to prevent re-fetching data on every interaction.
    """
    conn = init_connection()
    if conn is None: 
        st.error("Database connection is not available.")
        return pd.DataFrame()

    try:
        response = conn.client.table(table_name).select("*").execute()
        df = pd.DataFrame(response.data)
        # Convert timestamp column if it exists
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce', utc=True)
        return df
    except Exception as e:
        # Provide more specific feedback for common errors
        if "relation" in str(e) and "does not exist" in str(e):
            st.warning(f"Table '{table_name}' not found. The ETL pipeline may not have run for this table yet.")
        else:
            st.error(f"An error occurred while loading data from table '{table_name}': {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_dashboard_config() -> dict:
    """
    Loads the dashboard configuration table (e.g., for custom_lookback_days).
    """
    df = load_table('dashboard_config')
    if df.empty:
        return {}
    # Convert the key-value DataFrame to a dictionary for easy access
    return pd.Series(df.value.values, index=df.key).to_dict()

def display_time_period_selector(key_prefix="main") -> str:
    """
    Displays radio buttons in the sidebar for selecting a time period.
    Returns the corresponding column name suffix for the database (e.g., "YTD").
    """
    st.sidebar.markdown("### Select Time Period")
    
    # Load dynamic config from the database
    dashboard_config = load_dashboard_config()
    custom_days = dashboard_config.get('custom_lookback_days', '14')

    # Define the full set of time period options
    period_options = ["All-Time", "Year-to-Date", "Last Month", "Last Week", f"Last {custom_days} Days"]
    
    # Create the radio button selector
    time_period_label = st.sidebar.radio(
        "Choose a time period:",
        period_options,
        key=f"{key_prefix}_time_period",
        horizontal=True, # Makes the selector more compact
    )
    
    # Map the user-friendly selection to the database column suffix
    period_map = {
        "All-Time": "All_Time",
        "Year-to-Date": "YTD",
        "Last Month": "Last_Month",
        "Last Week": "Last_Week",
        f"Last {custom_days} Days": "Custom_Days"
    }
    
    st.header(f"Displaying Report for: {time_period_label}")
    return period_map.get(time_period_label, "All_Time")

def format_gp(value):
    """
    Formats a numeric value into a human-readable GP string, e.g., '1,234,567 gp'.
    Handles potential None or NaN values gracefully.
    """
    if pd.isna(value) or value is None:
        return "0 gp"
    return f"{int(value):,} gp"