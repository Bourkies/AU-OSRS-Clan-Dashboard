# dashboard/pages/1_💰_Valuable_Drops.py
# REBUILT to use new dynamic data structures and display logic.

import streamlit as st
import pandas as pd
import Streamlit_utils
import random
import toml
from pathlib import Path
from datetime import datetime, timedelta, timezone

current_script_directory = Path(__file__).resolve().parent

st.set_page_config(page_title="Valuable Drops", page_icon="💰", layout="wide")

# --- Helper functions for this page ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        texts_path = current_script_directory.parent / 'dashboard_texts.toml'
        return toml.load(texts_path)
    except FileNotFoundError:
        st.error(f"Error: `dashboard_texts.toml` not found at expected path '{texts_path}'. Please ensure the file exists in the project root directory.")
        return {}
    except Exception as e:
        st.error(f"Failed to load or parse dashboard_texts.toml: {e}")
        return {}

def display_mvp_section(df_leaderboard, df_period_detail, texts, value_col):
    """Displays the MVP section for top earners and biggest single drops."""
    st.header("🏆 Period MVPs")
    
    page_texts = texts.get('valuable_drops', {})
    
    top_earners_count = page_texts.get('top_earners_count', 1)
    biggest_drops_count = page_texts.get('biggest_drops_count', 1)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top Earner{'s' if top_earners_count > 1 else ''}")
        if not df_leaderboard.empty and value_col in df_leaderboard.columns:
            top_earners = df_leaderboard.sort_values(by=value_col, ascending=False).head(top_earners_count)
            
            messages = page_texts.get('top_earner_messages', [])
            random.shuffle(messages)
            
            for i, row in enumerate(top_earners.itertuples()):
                player = row.Username
                value_gp = Streamlit_utils.format_gp(getattr(row, value_col))
                
                if messages:
                    message = messages[i % len(messages)].format(player=player, value=value_gp)
                    st.success(message)
                else:
                    st.success(f"🤑 **{player}** was a top earner with **{value_gp}**.")
        else:
            st.info("No drops to determine a top earner for this period.")

    with col2:
        st.subheader(f"Biggest Drop{'s' if biggest_drops_count > 1 else ''}")
        if not df_period_detail.empty:
            biggest_drops = df_period_detail.sort_values(by='Item_Value', ascending=False).head(biggest_drops_count)

            messages = page_texts.get('biggest_drop_messages', [])
            random.shuffle(messages)

            for i, row in enumerate(biggest_drops.itertuples()):
                player = row.Username
                item = row.Item_Name
                value_gp = Streamlit_utils.format_gp(row.Item_Value)

                if messages:
                    message = messages[i % len(messages)].format(player=player, item=item, value=value_gp)
                    st.success(message)
                else:
                    st.success(f"🎉 **{player}** had a huge drop: a **{item}** worth **{value_gp}**!")
        else:
            st.info("No drops to determine the biggest drop for this period.")

    st.markdown("---")


# --- Main Page Execution ---
st.title("💰 Valuable Drops")
st.markdown("This page shows leaderboards and trends for valuable drops received by clan members.")

texts = load_texts()
dashboard_config = Streamlit_utils.load_dashboard_config()
df_leaderboard_summary = Streamlit_utils.load_table("valuable_drops_summary")
df_timeseries = Streamlit_utils.load_table("valuable_drops_timeseries")
df_meta = Streamlit_utils.load_table("run_metadata")
run_time = pd.to_datetime(df_meta['last_updated_utc'].iloc[0], utc=True) if not df_meta.empty else datetime.now(timezone.utc)

if df_leaderboard_summary.empty:
    st.warning("No valuable drop data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_options_map = Streamlit_utils.get_time_period_options(dashboard_config)
    st.sidebar.markdown("### Select Time Period")
    
    ordered_suffixes = ['Custom_Days', 'Prev_Week', 'Prev_Month', 'YTD', 'All_Time']
    suffix_to_label_map = {v: k for k, v in period_options_map.items()}
    ordered_labels = [suffix_to_label_map[suffix] for suffix in ordered_suffixes if suffix in suffix_to_label_map]

    selected_period_label = st.sidebar.radio(
        "Choose a time period:", 
        ordered_labels,
        key="drops_time_period", 
        horizontal=False,
    )
    
    period_suffix = period_options_map.get(selected_period_label)
    
    if not period_suffix:
        st.error("Could not determine the selected time period. Please try again.")
        st.stop()
        
    st.header(f"Displaying Report for: {selected_period_label}")

    value_col = f'Value_{period_suffix}'
    count_col = f'Count_{period_suffix}'
    
    if count_col in df_leaderboard_summary.columns:
        df_period_leaderboard = df_leaderboard_summary[df_leaderboard_summary[count_col] > 0].copy()
    else:
        df_period_leaderboard = pd.DataFrame()

    df_period_detail = Streamlit_utils.load_table(f"valuable_drops_detail_{period_suffix.lower()}")
    
    if not df_period_detail.empty or not df_period_leaderboard.empty:
        display_mvp_section(df_period_leaderboard, df_period_detail, texts, value_col)

    st.subheader("Leaderboards & Details")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Top Earners by Total Value", value="")
        if not df_period_leaderboard.empty:
            top_earners = df_period_leaderboard.sort_values(by=value_col, ascending=False)[['Username', value_col, count_col]]
            
            st.dataframe(
                top_earners, 
                column_config={
                    "Username": "Player",
                    value_col: st.column_config.NumberColumn("Total GP Value", format="%d"),
                    count_col: "Drops"
                },
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No valuable drops recorded for this time period.")
            
    with col2:
        top_drops_limit = int(dashboard_config.get('top_drops_limit', 50))
        if period_suffix in ['YTD', 'All_Time']:
            title = f"Top {top_drops_limit} Most Valuable Drops"
            display_df = df_period_detail.sort_values(by='Item_Value', ascending=False).head(top_drops_limit)
        else:
            title = "All Drops This Period"
            display_df = df_period_detail
        
        st.metric(label=title, value="")
        if not display_df.empty:
            display_df_formatted = display_df.copy()
            display_df_formatted['Date'] = display_df_formatted['Timestamp'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                display_df_formatted,
                column_config={
                    "Date": "Date",
                    "Username": "Player",
                    "Item_Name": "Item",
                    "Item_Value": st.column_config.NumberColumn("GP Value", format="%d")
                },
                column_order=("Date", "Username", "Item_Name", "Item_Value"),
                use_container_width=True, 
                hide_index=True
            )
        else: 
            st.info("No drops found for this period.")

    st.markdown("---")
    st.subheader("GP Gained Over Time")
    if df_timeseries.empty:
        st.info("No timeseries data available to plot.")
    else:
        chart_data = Streamlit_utils.get_chart_data_for_period(df_timeseries, selected_period_label, dashboard_config, period_options_map, run_time)
        
        if not chart_data.empty:
            total_gp_in_period = chart_data['Value'].max()
            total_gp_formatted = Streamlit_utils.format_gp(total_gp_in_period)
            st.metric(label=f"Total GP Gained in Period", value=total_gp_formatted)
            st.line_chart(chart_data.set_index('Date')['Value'])
        else:
            st.info("No drop data to plot for the selected time period.")