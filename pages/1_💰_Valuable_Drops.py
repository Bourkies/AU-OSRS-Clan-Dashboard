# dashboard/pages/1_💰_Valuable_Drops.py
# Refactored to display pre-aggregated data and a new dynamic, granular timeseries chart.

import streamlit as st
import pandas as pd
import utils
import dashboard_texts as texts
import random
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="Valuable Drops", page_icon="💰", layout="wide")

def get_chart_data_for_period(df_timeseries, selected_period_label, dashboard_config):
    """
    Filters the pivoted timeseries data to get the correct granularity and date range
    for the selected time period, and adjusts the data to start from zero.
    """
    custom_days = int(dashboard_config.get('custom_lookback_days', 14))
    week_start_day = dashboard_config.get('week_start_day', 'Monday')
    weekday_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

    freq_map = {
        "All-Time": "W", "Year-to-Date": "W", "Last Month": "D",
        "Last Week": "6H", f"Last {custom_days} Days": "6H"
    }
    target_freq = freq_map.get(selected_period_label)

    df_filtered_by_freq = df_timeseries[df_timeseries['Frequency'] == target_freq].copy()
    if df_filtered_by_freq.empty:
        return pd.DataFrame()

    df_filtered_by_freq['Date'] = pd.to_datetime(df_filtered_by_freq['Date'], utc=True)
    df_filtered_by_freq.sort_values('Date', inplace=True)
    
    today = datetime.now(timezone.utc)
    start_date = None

    if selected_period_label == "Year-to-Date":
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif selected_period_label == "Last Month":
        start_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = (start_of_this_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif selected_period_label == "Last Week":
        start_of_week_offset = (today.weekday() - weekday_map.get(week_start_day, 0)) % 7
        start_date = (today - timedelta(days=start_of_week_offset)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif selected_period_label == f"Last {custom_days} Days":
        start_date = (today - timedelta(days=custom_days)).replace(hour=0, minute=0, second=0, microsecond=0)

    if not start_date:
        # For "All-Time", we don't need to adjust the start point
        return df_filtered_by_freq

    # Filter for data within the period
    df_period_data = df_filtered_by_freq[df_filtered_by_freq['Date'] >= start_date].copy()
    
    # Find the last cumulative value *before* the period started
    df_before_period = df_filtered_by_freq[df_filtered_by_freq['Date'] < start_date]
    
    start_value = 0
    if not df_before_period.empty:
        start_value = df_before_period.iloc[-1]['Cumulative_Value']

    # Adjust the series to start from 0 relative to the period's beginning
    df_period_data['Cumulative_Value'] = df_period_data['Cumulative_Value'] - start_value
    
    # Add a zero point at the start of the period to anchor the chart
    if not df_period_data.empty and df_period_data.iloc[0]['Date'] > start_date:
        zero_row = pd.DataFrame([{'Date': start_date, 'Cumulative_Value': 0}])
        df_period_data = pd.concat([zero_row, df_period_data]).reset_index(drop=True)
    
    # Ensure the first data point is exactly 0 if it's at the start date
    if not df_period_data.empty and df_period_data.iloc[0]['Date'] == start_date:
        df_period_data.at[0, 'Cumulative_Value'] = 0

    return df_period_data

def display_mvp_section(df_period_summary, df_biggest_drop, value_col):
    """Displays the MVP section for top earner and biggest single drop."""
    st.header("🏆 Period MVPs")
    
    mvp_config = texts.VALUABLE_DROPS_MVP_CONFIG
    top_earners_count = mvp_config.get("top_earners_count", 1)
    biggest_drops_count = mvp_config.get("biggest_drops_count", 1)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Earner(s)")
        if not df_period_summary.empty:
            top_earners = df_period_summary.sort_values(by=value_col, ascending=False).head(top_earners_count)
            for _, earner in top_earners.iterrows():
                player = earner['Username']
                value_gp = utils.format_gp(earner[value_col])
                message = random.choice(texts.TOP_EARNER_MESSAGES).format(player=player, value=value_gp)
                st.info(message, icon="🤑")
        else:
            st.info("No drops to determine a top earner for this period.")

    with col2:
        st.subheader("Biggest Drop(s)")
        if not df_biggest_drop.empty:
            biggest_drops = df_biggest_drop.head(biggest_drops_count)
            for _, drop in biggest_drops.iterrows():
                player = drop['Username']
                item = drop['Item_Name']
                value_gp = utils.format_gp(drop['Item_Value'])
                message = random.choice(texts.BIGGEST_DROP_MESSAGES).format(player=player, item=item, value=value_gp)
                st.info(message, icon="💎")
        else:
            st.info("No drops to determine the biggest drop for this period.")

    st.markdown("---")

# --- Main Page ---
st.title("💰 Valuable Drops")
st.markdown("This page shows leaderboards and trends for the most valuable drops received by clan members.")

# --- Load Data ---
df_drops_summary = utils.load_table("valuable_drops_summary")
df_recents = utils.load_table("recents_list")
df_timeseries = utils.load_table("valuable_drops_timeseries")
df_biggest_drops = utils.load_table("biggest_drops_by_period")
dashboard_config = utils.load_dashboard_config()

if df_drops_summary.empty:
    st.warning("No valuable drop summary data could be loaded. The ETL pipeline may not have run for this table yet.")
else:
    # --- Time Period Selector ---
    custom_days = dashboard_config.get('custom_lookback_days', '14')
    period_options = [f"Last {custom_days} Days", "Last Week", "Last Month", "Year-to-Date", "All-Time"]
    st.sidebar.markdown("### Select Time Period")
    selected_period_label = st.sidebar.radio(
        "Choose a time period:", 
        period_options, 
        key="drops_time_period", 
        horizontal=True,
        index=0
    )
    
    period_map = { "All-Time": "All_Time", "Year-to-Date": "YTD", "Last Month": "Last_Month", "Last Week": "Last_Week", f"Last {custom_days} Days": "Custom_Days" }
    period_suffix = period_map.get(selected_period_label, "Custom_Days")
    st.header(f"Displaying Report for: {selected_period_label}")

    value_col = f'Value_{period_suffix}'
    count_col = f'Count_{period_suffix}'
    
    if count_col in df_drops_summary.columns and value_col in df_drops_summary.columns:
        df_period_summary = df_drops_summary[df_drops_summary[count_col] > 0].copy()
    else:
        df_period_summary = pd.DataFrame()

    df_biggest_drop_period = df_biggest_drops[df_biggest_drops['Period'] == period_suffix]

    # --- MVP Section ---
    display_mvp_section(df_period_summary, df_biggest_drop_period, value_col)

    # --- Leaderboards ---
    st.subheader("Leaderboards")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Top Earners by Total Value", value="")
        if not df_period_summary.empty:
            top_earners = df_period_summary.sort_values(by=value_col, ascending=False)[['Username', value_col, count_col]]
            top_earners.rename(columns={'Username': 'Player', value_col: 'Total Value', count_col: 'Drops'}, inplace=True)
            top_earners['Total Value'] = top_earners['Total Value'].apply(utils.format_gp)
            st.dataframe(top_earners, use_container_width=True, hide_index=True)
        else:
            st.info("No valuable drops recorded for this time period.")
            
    with col2:
        st.metric(label="Most Recent Valuable Drops", value="")
        valuable_drop_types = ['Valuable Drop', 'Clue Scroll Item', 'Raid Loot']
        
        today = datetime.now(timezone.utc)
        start_date = None
        end_date = today # Default end date is now
        custom_days_int = int(custom_days)
        week_start_day = dashboard_config.get('week_start_day', 'Monday')
        weekday_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

        if selected_period_label == "Year-to-Date":
            start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif selected_period_label == "Last Month":
            end_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_date = (end_date - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif selected_period_label == "Last Week":
            start_of_week_offset = (today.weekday() - weekday_map.get(week_start_day, 0)) % 7
            start_date = (today - timedelta(days=start_of_week_offset)).replace(hour=0, minute=0, second=0, microsecond=0)
            # FIX: End date for "Last Week" should be the end of that week, not the current time.
            end_date = start_date + timedelta(days=7)
        elif selected_period_label == f"Last {custom_days} Days":
            start_date = (today - timedelta(days=custom_days_int)).replace(hour=0, minute=0, second=0, microsecond=0)

        df_recents['Timestamp'] = pd.to_datetime(df_recents['Timestamp'], utc=True)
        df_recent_drops = df_recents[df_recents['Broadcast_Type'].isin(valuable_drop_types)]

        if start_date:
            # FIX: Ensure end_date is respected in the filter
            df_recent_drops = df_recent_drops[(df_recent_drops['Timestamp'] >= start_date) & (df_recent_drops['Timestamp'] < end_date)]

        if not df_recent_drops.empty:
            df_recent_drops = df_recent_drops.sort_values(by='Timestamp', ascending=False)
            df_recent_drops['Date'] = pd.to_datetime(df_recent_drops['Timestamp']).dt.strftime('%Y-%m-%d')
            df_recent_drops['Value'] = df_recent_drops['Item_Value'].apply(utils.format_gp)
            df_recent_drops.rename(columns={'Username': 'Player', 'Item_Name': 'Item'}, inplace=True)
            st.dataframe(df_recent_drops[['Date', 'Player', 'Item', 'Value']], use_container_width=True, hide_index=True)
        else: 
            st.info("No recent drops found for this period.")

    # --- Timeseries Chart ---
    st.markdown("---")
    if df_timeseries.empty:
        st.info("No timeseries data available to plot.")
    else:
        df_chart_data = get_chart_data_for_period(df_timeseries, selected_period_label, dashboard_config)
        
        if df_chart_data.empty:
            st.info("No drop data to plot for the selected time period.")
        else:
            total_gp_in_period = df_chart_data['Cumulative_Value'].max()
            total_gp_formatted = utils.format_gp(total_gp_in_period)
            st.subheader(f"Drops Over Time (Cumulative Total: {total_gp_formatted})")
            
            df_chart_data.set_index('Date', inplace=True)
            st.line_chart(df_chart_data['Cumulative_Value'])
