# dashboard/pages/3_👢_111_Kicks.py

import streamlit as st
import pandas as pd
import Streamlit_utils
import random
import toml
from datetime import datetime, timezone

st.set_page_config(page_title="111 Kicks", page_icon="👢", layout="wide")

# --- Helper Functions ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        return toml.load('dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

def display_mvp(title, df_summary, messages, count, player_col, count_col):
    """Generic function to display an MVP section for kicks."""
    st.subheader(title)
    
    if df_summary.empty or count_col not in df_summary.columns:
        st.info(f"No data available for this section.")
        return

    df_filtered = df_summary[df_summary[count_col] > 0]
    if df_filtered.empty:
        st.info(f"No qualifying players for this section.")
        return

    mvps = df_filtered.sort_values(by=count_col, ascending=False).head(count)
    if mvps.empty:
        st.info(f"No qualifying players for this section.")
        return
        
    random.shuffle(messages)

    for i, row in enumerate(mvps.itertuples()):
        format_dict = {}
        format_dict['player'] = getattr(row, player_col, 'N/A')
        format_dict['count'] = int(getattr(row, count_col, 0))
        
        msg_template = messages[i % len(messages)]
        st.success(msg_template.format(**format_dict))

# --- Main Page Execution ---
st.title("👢 '111' Kicks Leaderboard")
st.markdown("Who's getting the boot? This page tracks players who have been temporarily '111' kicked from the clan.")

texts = load_texts()
dashboard_config = Streamlit_utils.load_dashboard_config()
df_kicked = Streamlit_utils.load_table("kicked_by_player_summary")
df_kickers = Streamlit_utils.load_table("kicker_summary")

if df_kicked.empty and df_kickers.empty:
    st.warning("No kick data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_options_map = Streamlit_utils.get_time_period_options(dashboard_config)
    st.sidebar.markdown("### Select Time Period")
    
    ordered_suffixes = ['Custom_Days', 'Prev_Week', 'Prev_Month', 'YTD', 'All_Time']
    suffix_to_label_map = {v: k for k, v in period_options_map.items()}
    ordered_labels = [suffix_to_label_map[suffix] for suffix in ordered_suffixes if suffix in suffix_to_label_map]

    selected_period_label = st.sidebar.radio(
        "Choose a time period:", 
        ordered_labels,
        key="kicks_time_period", 
        horizontal=False,
    )
    
    period_suffix = period_options_map.get(selected_period_label)
    
    st.header(f"Displaying Report for: {selected_period_label}")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.header("The Kicked")
        page_texts = texts.get('kicks', {})
        
        # Most Kicked MVP
        display_mvp(
            "Most Kicked",
            df_kicked,
            page_texts.get('top_kicked_messages', []),
            page_texts.get('top_kicked_count', 1),
            'Username',
            f'Count_{period_suffix}'
        )
        st.markdown("---")
        
        # Kicked Leaderboard
        st.subheader("Leaderboard")
        count_col_kicked = f'Count_{period_suffix}'
        if not df_kicked.empty and count_col_kicked in df_kicked.columns:
            df_kicked_period = df_kicked[df_kicked[count_col_kicked] > 0]
            if not df_kicked_period.empty:
                df_display = df_kicked_period.sort_values(by=count_col_kicked, ascending=False)
                st.dataframe(
                    df_display,
                    column_config={
                        "Username": "Player",
                        count_col_kicked: "Times Kicked"
                    },
                    column_order=("Username", count_col_kicked),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No one was kicked in this period.")
        else:
            st.info("No kick data available.")

    with col2:
        st.header("The Kickers")
        page_texts = texts.get('kicks', {})

        # Trigger Happy MVP
        display_mvp(
            "Most Trigger-Happy Admin",
            df_kickers,
            page_texts.get('fastest_finger_messages', []),
            page_texts.get('fastest_finger_count', 1),
            'Action_By',
            f'Count_{period_suffix}'
        )
        st.markdown("---")
        
        # Kicker Leaderboard
        st.subheader("Leaderboard")
        count_col_kickers = f'Count_{period_suffix}'
        if not df_kickers.empty and count_col_kickers in df_kickers.columns:
            df_kickers_period = df_kickers[df_kickers[count_col_kickers] > 0]
            if not df_kickers_period.empty:
                df_display = df_kickers_period.sort_values(by=count_col_kickers, ascending=False)
                st.dataframe(
                    df_display,
                    column_config={
                        "Action_By": "Admin",
                        count_col_kickers: "Players Kicked"
                    },
                    column_order=("Action_By", count_col_kickers),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No admins kicked anyone this period.")
        else:
            st.info("No kicker data available.")
