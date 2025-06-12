# dashboard/pages/2_💀_PvP_Leaderboard.py
# Rebuilt to mirror the structure of the Valuable Drops page.

import streamlit as st
import pandas as pd
import Streamlit_utils
import random
import toml
from pathlib import Path
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="PvP Leaderboard", page_icon="💀", layout="wide")

# --- Helper Functions ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        texts_path = 'dashboard_texts.toml'
        return toml.load(texts_path)
    except FileNotFoundError:
        st.error(f"Error: `dashboard_texts.toml` not found at expected path '{texts_path}'.")
        return {}
    except Exception as e:
        st.error(f"Failed to load or parse dashboard_texts.toml: {e}")
        return {}

def display_column_content(column_type, texts, dashboard_config, period_options_map, run_time):
    """
    Generic function to display the content for either the 'Kills' or 'Deaths' column.
    """
    page_texts = texts.get('pvp_leaderboard', {})
    
    # --- Load Data ---
    summary_table = f"pvp_{column_type.lower()}_summary"
    detail_table_prefix = f"pvp_{column_type.lower()}_detail_"
    timeseries_table = f"pvp_{column_type.lower()}_timeseries"

    df_summary = Streamlit_utils.load_table(summary_table)
    df_timeseries = Streamlit_utils.load_table(timeseries_table)

    if df_summary.empty:
        st.warning(f"No PvP {column_type} data could be loaded. The ETL pipeline may not have run yet.")
        return

    # --- Time Period Selector (gets value from the main selector) ---
    selected_period_label = st.session_state.pvp_time_period
    period_suffix = period_options_map.get(selected_period_label)

    if not period_suffix:
        st.error("Could not determine time period.")
        return

    df_detail = Streamlit_utils.load_table(f"{detail_table_prefix}{period_suffix.lower()}")

    value_col = f'Value_{period_suffix}'
    count_col = f'Count_{period_suffix}'
    
    df_period_summary = df_summary[df_summary[count_col] > 0] if count_col in df_summary.columns else pd.DataFrame()

    # --- MVP Section ---
    if column_type == "Kills":
        st.header("🏆 Kill MVPs")
        mvp_count = page_texts.get('most_valuable_pk_count', 1)
        st.subheader(f"Most Valuable PKer{'s' if mvp_count > 1 else ''}")
        if not df_period_summary.empty:
            mvps = df_period_summary.sort_values(by=value_col, ascending=False).head(mvp_count)
            messages = page_texts.get('most_valuable_pk_messages', [])
            random.shuffle(messages)
            for i, row in enumerate(mvps.itertuples()):
                msg = messages[i % len(messages)] if messages else "💥 **{player}** was the top PKer with **{count}** kills for **{value}**."
                st.success(msg.format(player=row.Username, count=getattr(row, count_col), value=Streamlit_utils.format_gp(getattr(row, value_col))))
        else:
            st.info("No PKers this period.")

        st.subheader("Biggest Single PK")
        if not df_detail.empty:
             biggest_pk = df_detail.sort_values(by='Item_Value', ascending=False).iloc[0]
             st.success(f"☠️ **{biggest_pk['Username']}** landed a massive **{Streamlit_utils.format_gp(biggest_pk['Item_Value'])}** kill on **{biggest_pk['Opponent']}**!")
        else:
             st.info("No PKs to determine the biggest.")

    else: # Deaths Column
        st.header("Hall of Shame")
        shame_config = page_texts.get('hall_of_shame', {})
        default_shame = page_texts.get('default_shame_messages', [])
        
        shameful_players = df_period_summary[df_period_summary['Username'].isin(shame_config.keys())]
        if shameful_players.empty:
            st.info("The usual suspects kept themselves safe this period. Well done.")
        else:
            for _, row in shameful_players.iterrows():
                player = row['Username']
                msg_template = shame_config.get(player) or random.choice(default_shame)
                st.error(msg_template.format(player=player, deaths=row[count_col], value=Streamlit_utils.format_gp(row[value_col])))


    # --- Leaderboard Table ---
    st.markdown("---")
    st.subheader(f"Leaderboard: Top {column_type}")
    if not df_period_summary.empty:
        display_df = df_period_summary.sort_values(by=value_col, ascending=False)[['Username', value_col, count_col]]
        display_df.rename(columns={'Username': 'Player', value_col: 'Total Value', count_col: column_type}, inplace=True)
        display_df['Total Value'] = display_df['Total Value'].apply(Streamlit_utils.format_gp)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"No {column_type.lower()} recorded for this time period.")

    # --- Chart ---
    st.markdown("---")
    st.subheader(f"{column_type} Over Time")
    if not df_timeseries.empty:
        chart_data = Streamlit_utils.get_chart_data_for_period(df_timeseries, selected_period_label, dashboard_config, period_options_map, run_time, 'Count')
        if not chart_data.empty:
            st.metric(label=f"Total {column_type} in Period", value=f"{int(chart_data['Value'].max()):,}")
            st.line_chart(chart_data.set_index('Date')['Value'])
        else:
            st.info(f"No {column_type.lower()} data to plot for this period.")
    else:
        st.info("No timeseries data available for this report.")


# --- Main Page Execution ---
st.title("💀 PvP Leaderboard")
st.markdown("Who are the hunters and who are the hunted? This page tracks all PvP action.")

texts = load_texts()
dashboard_config = Streamlit_utils.load_dashboard_config()
df_meta = Streamlit_utils.load_table("run_metadata")
run_time = pd.to_datetime(df_meta['last_updated_utc'].iloc[0], utc=True) if not df_meta.empty else datetime.now(timezone.utc)

period_options_map = Streamlit_utils.get_time_period_options(dashboard_config)
st.sidebar.markdown("### Select Time Period")

ordered_suffixes = ['Custom_Days', 'Prev_Week', 'Prev_Month', 'YTD', 'All_Time']
suffix_to_label_map = {v: k for k, v in period_options_map.items()}
ordered_labels = [suffix_to_label_map[suffix] for suffix in ordered_suffixes if suffix in suffix_to_label_map]

# Use session_state to keep the selection consistent across the page
if 'pvp_time_period' not in st.session_state:
    st.session_state.pvp_time_period = ordered_labels[0]

st.sidebar.radio(
    "Choose a time period:", 
    ordered_labels,
    key="pvp_time_period", 
    horizontal=False,
)

st.header(f"Displaying Report for: {st.session_state.pvp_time_period}")

col1, col2 = st.columns(2)

with col1:
    display_column_content("Kills", texts, dashboard_config, period_options_map, run_time)

with col2:
    display_column_content("Deaths", texts, dashboard_config, period_options_map, run_time)
