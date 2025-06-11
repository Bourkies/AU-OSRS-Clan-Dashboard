# dashboard/pages/1_💰_Valuable_Drops.py
# Refactored to display pre-aggregated data and a new timeseries chart.

import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="Valuable Drops", page_icon="💰", layout="wide")

st.title("💰 Most Valuable Drops")
st.markdown("This page shows leaderboards and trends for the most valuable drops received by clan members.")

# --- Load Data ---
# Use the correct table name as defined in config.toml
df_drops_summary = utils.load_table("valuable_drops_summary")
df_recents = utils.load_table("recents_list")
# Load the new timeseries data
df_timeseries = utils.load_table("valuable_drops_timeseries")

if df_drops_summary.empty:
    st.warning("No valuable drop summary data could be loaded. The ETL pipeline may not have run for this table yet.")
else:
    period_suffix = utils.display_time_period_selector(key_prefix="drops")
    
    # Define column names based on selected period
    value_col = f'Value_{period_suffix}'
    count_col = f'Count_{period_suffix}'
    
    df_period = df_drops_summary[df_drops_summary[count_col] > 0].copy()
    
    if df_period.empty:
        st.info("No valuable drops were recorded for this time period.")
    else:
        # --- Leaderboards ---
        st.subheader("Leaderboards")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label="Top Earners by Total Value", value="")
            top_earners = df_period.sort_values(by=value_col, ascending=False)
            
            # Select and rename columns for display
            top_earners_display = top_earners[['Username', value_col, count_col]]
            top_earners_display.rename(columns={'Username': 'Player', value_col: 'Total Value', count_col: 'Drops'}, inplace=True)
            
            # Format the GP value
            top_earners_display['Total Value'] = top_earners_display['Total Value'].apply(utils.format_gp)
            st.dataframe(top_earners_display, use_container_width=True, hide_index=True)
        
        with col2:
            st.metric(label="Most Recent Valuable Drops", value="")
            valuable_drop_types = ['Valuable Drop', 'Clue Scroll Item', 'Raid Loot']
            df_recent_drops = df_recents[df_recents['Broadcast_Type'].isin(valuable_drop_types)]
            
            if not df_recent_drops.empty:
                df_recent_drops['Date'] = pd.to_datetime(df_recent_drops['Timestamp']).dt.strftime('%Y-%m-%d')
                df_recent_drops['Value'] = df_recent_drops['Item_Value'].apply(utils.format_gp)
                df_recent_drops.rename(columns={'Username': 'Player', 'Item_Name': 'Item'}, inplace=True)
                st.dataframe(df_recent_drops[['Date', 'Player', 'Item', 'Value']], use_container_width=True, hide_index=True)
            else:
                st.info("No recent drops found.")

# --- Timeseries Chart ---
st.markdown("---")
st.subheader("Valuable Drops Over Time")
if df_timeseries.empty:
    st.info("No timeseries data available to plot.")
else:
    # Ensure 'Date' is a datetime object for plotting
    df_timeseries['Date'] = pd.to_datetime(df_timeseries['Date'])
    df_timeseries.set_index('Date', inplace=True)
    
    # Let user choose what to plot
    chart_metric = st.selectbox(
        "Select metric to plot:",
        ("Total Value", "Number of Drops")
    )
    
    if chart_metric == "Total Value":
        st.line_chart(df_timeseries['Total_Value'])
    else:
        st.line_chart(df_timeseries['Count'])