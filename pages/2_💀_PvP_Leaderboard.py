# dashboard/pages/2_💀_PvP_Leaderboard.py
# Rebuilt to the new two-column layout with mirrored MVP sections and Hall of Shame search.

import streamlit as st
import pandas as pd
import Streamlit_utils
import random
import toml
from datetime import datetime, timezone
from pathlib import Path

current_script_directory = Path(__file__).resolve().parent

st.set_page_config(page_title="PvP Leaderboard", page_icon="💀", layout="wide")

# --- Helper Functions ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        return toml.load(current_script_directory.parent / 'dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

def display_mvp(title, count, df_summary, df_detail, messages, format_string, sort_col_summary, sort_col_detail, period_suffix, is_loss=False):
    """Generic function to display an MVP section."""
    st.subheader(title)
    is_summary_based = '{count}' in format_string
    df_to_use = df_summary if is_summary_based else df_detail
    sort_col = sort_col_summary if is_summary_based else sort_col_detail

    if df_to_use.empty:
        st.info(f"No data available for this section.")
        return

    # Filter out zero values before sorting
    df_filtered = df_to_use[df_to_use[sort_col] > 0].copy()

    # Filter summary data for the current period
    if is_summary_based:
        if f"Count_{period_suffix}" in df_filtered.columns:
            df_period_data = df_filtered[df_filtered[f"Count_{period_suffix}"] > 0].copy()
        else:
            df_period_data = pd.DataFrame()
    else:
        df_period_data = df_filtered

    if df_period_data.empty:
        st.info(f"No qualifying players for this section.")
        return

    # For losses, we still want the highest value, so always sort descending
    mvps = df_period_data.sort_values(by=sort_col, ascending=False).head(count)
    if mvps.empty:
        st.info(f"No qualifying players for this section.")
        return

    random.shuffle(messages)

    for i, row in enumerate(mvps.itertuples()):
        format_dict = {}
        format_dict['player'] = getattr(row, 'Username', 'N/A')
        
        value = getattr(row, sort_col, 0)
        format_dict['value'] = Streamlit_utils.format_gp(value)

        if '{count}' in format_string:
            format_dict['count'] = int(getattr(row, f"Count_{period_suffix}", 0))

        msg_template = messages[i % len(messages)] if messages else "No message template found: {player} {value} {count}"
        st.success(msg_template.format(**format_dict))


def display_column(column_type, texts, dashboard_config, period_suffix, run_time, period_options_map, selected_period_label):
    """Displays a full column for Kills or Deaths."""
    page_texts = texts.get('pvp_leaderboard', {})
    st.header(f"The {column_type}")

    df_summary = Streamlit_utils.load_table(f"pvp_{column_type.lower()}_summary")
    df_detail = Streamlit_utils.load_table(f"pvp_{column_type.lower()}_detail_{period_suffix.lower()}")
    df_timeseries = Streamlit_utils.load_table(f"pvp_{column_type.lower()}_timeseries")

    # --- MVP Section ---
    if column_type == "Kills":
        display_mvp("Most Valuable PKer", page_texts.get('most_valuable_pker_count', 1), df_summary, df_detail, page_texts.get('most_valuable_pker_messages', []), "{player} {count} {value}", f"Value_{period_suffix}", "Item_Value", period_suffix)
        display_mvp("Biggest Single PK", page_texts.get('biggest_pk_count', 1), df_summary, df_detail, page_texts.get('biggest_pk_messages', []), "{player} {value}", f"Value_{period_suffix}", "Item_Value", period_suffix)
    else: # Deaths
        display_mvp("Most Valuable Donor", page_texts.get('most_valuable_donor_count', 1), df_summary, df_detail, page_texts.get('most_valuable_donor_messages', []), "{player} {count} {value}", f"Value_{period_suffix}", "Item_Value", period_suffix, is_loss=True)
        display_mvp("Biggest Single Loss", page_texts.get('biggest_loss_count', 1), df_summary, df_detail, page_texts.get('biggest_loss_messages', []), "{player} {value}", f"Value_{period_suffix}", "Item_Value", period_suffix, is_loss=True)

    st.markdown("---")

    # --- Summary Leaderboard ---
    st.subheader("Leaderboard")
    if not df_summary.empty and f"Count_{period_suffix}" in df_summary.columns:
        df_period_summary = df_summary[df_summary[f"Count_{period_suffix}"] > 0].copy()
        if not df_period_summary.empty:
            df_display = df_period_summary.sort_values(by=f"Value_{period_suffix}", ascending=False)
            st.dataframe(
                df_display,
                column_config={
                    "Username": "Player",
                    f"Value_{period_suffix}": st.column_config.NumberColumn(f"Total GP {column_type}", format="%,d"),
                    f"Count_{period_suffix}": column_type
                },
                column_order=("Username", f"Value_{period_suffix}", f"Count_{period_suffix}"),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"No {column_type.lower()} recorded for this period.")
    else:
        st.info(f"No {column_type.lower()} data available.")

    # --- Detailed History Table ---
    st.markdown("---")
    top_limit = int(dashboard_config.get('top_drops_limit', 50))
    if period_suffix in ['YTD', 'All_Time']:
        title = f"Top {top_limit} Most Valuable {column_type}"
        display_df = df_detail.sort_values(by='Item_Value', ascending=False).head(top_limit)
    else:
        title = f"All {column_type} This Period"
        display_df = df_detail
    
    st.subheader(title)
    if not display_df.empty:
        st.dataframe(
            display_df,
            column_config={
                "Timestamp": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Username": "Player",
                "Opponent": "Opponent",
                "Item_Value": st.column_config.NumberColumn("GP Value", format="%,d")
            },
            column_order=("Timestamp", "Username", "Opponent", "Item_Value"),
            use_container_width=True, 
            hide_index=True
        )
    else: 
        st.info(f"No {column_type.lower()} found for this period.")


    # --- Timeseries Chart ---
    st.markdown("---")
    st.subheader(f"GP {('Gained' if column_type == 'Kills' else 'Lost')} Over Time")
    if not df_timeseries.empty:
        chart_data = Streamlit_utils.get_chart_data_for_period(df_timeseries, selected_period_label, dashboard_config, period_options_map, run_time, 'Value')
        if not chart_data.empty:
            total_gp_in_period = chart_data['Value'].max() if not chart_data['Value'].empty else 0
            st.metric(label=f"Total GP {('Gained' if column_type == 'Kills' else 'Lost')} in Period", value=Streamlit_utils.format_gp(total_gp_in_period))
            st.line_chart(chart_data.set_index('Date')['Value'])
        else:
            st.info("No data to plot for this period.")
    else:
        st.info("No timeseries data available.")

# --- Main Page Execution ---
st.title("💀 PvP Leaderboard")
st.markdown("Who are the hunters and who are the hunted? This page tracks all PvP action.")

texts = load_texts()
dashboard_config = Streamlit_utils.load_dashboard_config()
df_meta = Streamlit_utils.load_table("run_metadata")
run_time = pd.to_datetime(df_meta['last_updated_utc'].iloc[0], utc=True) if not df_meta.empty else datetime.now(timezone.utc)

# --- Hall of Shame Search ---
st.header("Hall of Shame")
df_deaths_summary = Streamlit_utils.load_table("pvp_deaths_summary")
if not df_deaths_summary.empty:
    all_players = sorted(df_deaths_summary['Username'].unique())
    page_texts = texts.get('pvp_leaderboard', {})
    default_player = page_texts.get('hall_of_shame_default_search', "")
    
    try:
        default_index = all_players.index(default_player) + 1 if default_player in all_players else 0
    except (ValueError, IndexError):
        default_index = 0

    search_options = [""] + all_players
    searched_player = st.selectbox("Search for a player to see their shame stats:", options=search_options, index=default_index)

    if searched_player:
        # We need to re-select the time period here for context
        period_options_map_shame = Streamlit_utils.get_time_period_options(dashboard_config)
        if 'pvp_time_period_label' in st.session_state:
             period_suffix_shame = period_options_map_shame.get(st.session_state.pvp_time_period_label)
             player_stats_row = df_deaths_summary[df_deaths_summary['Username'] == searched_player]
        
             deaths = 0
             value_lost = 0
             if not player_stats_row.empty:
                 deaths = int(player_stats_row.iloc[0].get(f'Count_{period_suffix_shame}', 0))
                 value_lost = player_stats_row.iloc[0].get(f'Value_{period_suffix_shame}', 0)

             if deaths > 0:
                 shame_messages = page_texts.get('hall_of_shame_messages', {})
                 msg_template = shame_messages.get(searched_player, shame_messages.get('default', ''))
                 st.error(msg_template.format(player=searched_player, deaths=deaths, value=Streamlit_utils.format_gp(value_lost)))
             else:
                 no_deaths_template = page_texts.get('no_deaths_message', "Safe! **{player}** has no recorded deaths for this period.")
                 st.success(no_deaths_template.format(player=searched_player))
else:
    st.info("No death summary data available for search.")

st.markdown("---")

# --- Time Period Selector ---
period_options_map = Streamlit_utils.get_time_period_options(dashboard_config)
st.sidebar.markdown("### Select Time Period")

ordered_suffixes = ['Custom_Days', 'Prev_Week', 'Prev_Month', 'YTD', 'All_Time']
suffix_to_label_map = {v: k for k, v in period_options_map.items()}
ordered_labels = [suffix_to_label_map[suffix] for suffix in ordered_suffixes if suffix in suffix_to_label_map]

if 'pvp_time_period_label' not in st.session_state:
    st.session_state.pvp_time_period_label = ordered_labels[0]
if st.session_state.pvp_time_period_label not in ordered_labels:
    st.session_state.pvp_time_period_label = ordered_labels[0]
    
selected_period_label = st.sidebar.radio(
    "Choose a time period:", 
    ordered_labels, 
    key="pvp_time_period_label_selector",
    index=ordered_labels.index(st.session_state.pvp_time_period_label)
)
st.session_state.pvp_time_period_label = selected_period_label

st.header(f"Displaying Report for: {selected_period_label}")
st.markdown("---")

period_suffix = period_options_map.get(selected_period_label)

col1, col2 = st.columns(2)
with col1:
    display_column("Kills", texts, dashboard_config, period_suffix, run_time, period_options_map, selected_period_label)
with col2:
    display_column("Deaths", texts, dashboard_config, period_suffix, run_time, period_options_map, selected_period_label)