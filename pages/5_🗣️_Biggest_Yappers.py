# dashboard/pages/5_🗣️_Biggest_Yappers.py

import streamlit as st
import pandas as pd
import Streamlit_utils
import random
import toml

st.set_page_config(page_title="Biggest Yappers", page_icon="🗣️", layout="wide")

# --- Helper Functions ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        return toml.load('dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

def display_yapper_leaderboard(df, period_suffix, title, messages, icon, mvp_count):
    """Generic function to display a yapper leaderboard section."""
    st.header(title)
    
    count_col = f'Count_{period_suffix}'
    if df.empty or count_col not in df.columns:
        st.info(f"Nobody was yapping about this in the selected period.")
        return

    df_period = df[df[count_col] > 0].copy()
    
    if df_period.empty:
        st.info(f"Nobody was yapping about this in the selected period.")
        return

    # MVP Section
    st.subheader("Period MVP")
    top_yappers = df_period.sort_values(by=count_col, ascending=False).head(mvp_count)
    
    random.shuffle(messages)
    for i, row in enumerate(top_yappers.itertuples()):
        player = row.Username
        count = int(getattr(row, count_col))
        message = messages[i % len(messages)].format(player=player, count=count)
        st.success(message, icon=icon)

    st.markdown("---")
    
    # Leaderboard Table
    st.subheader("Leaderboard")
    leaderboard = df_period.sort_values(by=count_col, ascending=False)
    st.dataframe(
        leaderboard,
        column_config={
            "Username": "Player",
            count_col: "Count"
        },
        column_order=("Username", count_col),
        use_container_width=True, 
        hide_index=True
    )

# --- Main Page Execution ---
st.title("🗣️ The Biggest Yappers")
st.markdown("Who's the chattiest in the clan? This page tracks who's saying the important things.")

texts = load_texts()
dashboard_config = Streamlit_utils.load_dashboard_config()

# Load data for all yapper categories
df_menaces = Streamlit_utils.load_table("menaces_111_summary")
df_gzers = Streamlit_utils.load_table("big_gzers_summary")
df_cya_hick = Streamlit_utils.load_table("cya_hick_crew_summary")

if df_menaces.empty and df_gzers.empty and df_cya_hick.empty:
    st.warning("No chat count data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_options_map = Streamlit_utils.get_time_period_options(dashboard_config)
    st.sidebar.markdown("### Select Time Period")
    
    ordered_suffixes = ['Custom_Days', 'Prev_Week', 'Prev_Month', 'YTD', 'All_Time']
    suffix_to_label_map = {v: k for k, v in period_options_map.items()}
    ordered_labels = [suffix_to_label_map[suffix] for suffix in ordered_suffixes if suffix in suffix_to_label_map]

    selected_period_label = st.sidebar.radio(
        "Choose a time period:", 
        ordered_labels,
        key="yappers_time_period", 
        horizontal=False,
    )
    
    period_suffix = period_options_map.get(selected_period_label)
    
    st.header(f"Displaying Report for: {selected_period_label}")
    st.markdown("---")
    
    page_texts = texts.get('yappers', {})

    col1, col2 = st.columns(2)
    with col1:
        if not df_menaces.empty:
            display_yapper_leaderboard(
                df_menaces, 
                period_suffix, 
                "The Menaces (111)", 
                page_texts.get('top_yapper_messages', []), 
                "🗣️",
                page_texts.get('top_yapper_count', 1)
            )
    with col2:
        if not df_gzers.empty:
            display_yapper_leaderboard(
                df_gzers, 
                period_suffix, 
                "The GZers (gz)", 
                page_texts.get('top_gzer_messages', []), 
                "🎉",
                page_texts.get('top_gzer_count', 1)
            )

    st.markdown("---")
    if not df_cya_hick.empty:
        display_yapper_leaderboard(
            df_cya_hick, 
            period_suffix, 
            "The 'cya hick' Crew", 
            ["**{player}** is the biggest hick, saying it {count} times."], 
            "👋",
            1
        )

