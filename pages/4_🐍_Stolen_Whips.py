# dashboard/pages/4_🐍_Stolen_Whips.py

import streamlit as st
import pandas as pd
import Streamlit_utils
import random
import toml
from datetime import datetime, timezone

st.set_page_config(page_title="Stolen Whips", page_icon="🐍", layout="wide")

# --- Helper Functions ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        return toml.load('dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

# --- Main Page Execution ---
st.title("🐍 Stolen Whips Leaderboard")

texts = load_texts()
dashboard_config = Streamlit_utils.load_dashboard_config()
df_whips = Streamlit_utils.load_table("stolen_whips_summary")

page_texts = texts.get('stolen_whips', {})
whip_queen = page_texts.get('whip_queen', 'Abby Queen')

st.markdown(f"All whips belong to **{whip_queen}**. This page tracks all whips stolen by other clan members.")
st.markdown("---")

if df_whips.empty:
    st.warning("No whip data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_options_map = Streamlit_utils.get_time_period_options(dashboard_config)
    st.sidebar.markdown("### Select Time Period")
    
    ordered_suffixes = ['Custom_Days', 'Prev_Week', 'Prev_Month', 'YTD', 'All_Time']
    suffix_to_label_map = {v: k for k, v in period_options_map.items()}
    ordered_labels = [suffix_to_label_map[suffix] for suffix in ordered_suffixes if suffix in suffix_to_label_map]

    selected_period_label = st.sidebar.radio(
        "Choose a time period:", 
        ordered_labels,
        key="whips_time_period", 
        horizontal=False,
    )
    
    period_suffix = period_options_map.get(selected_period_label)
    count_col = f'Count_{period_suffix}'
    value_col = f'Value_{period_suffix}'

    st.header(f"State of the Whips for: {selected_period_label}")

    if count_col in df_whips.columns:
        df_period = df_whips[df_whips[count_col] > 0].copy()
        
        queen_stats = df_period[df_period['Username'] == whip_queen]
        queen_count = int(queen_stats[count_col].sum()) if not queen_stats.empty else 0

        thieves_df = df_period[df_period['Username'] != whip_queen]
        total_stolen = int(thieves_df[count_col].sum())
        
        top_thief = "nobody"
        if not thieves_df.empty:
            top_thief_series = thieves_df.sort_values(by=count_col, ascending=False)
            top_thief = top_thief_series.iloc[0]['Username']

        # Display Shame Message
        shame_messages = page_texts.get('whip_shame_messages', [])
        if shame_messages:
            message = random.choice(shame_messages).format(
                queen=whip_queen, 
                queen_count=queen_count,
                total_stolen=total_stolen, 
                top_thief=top_thief
            )
            st.info(message, icon="👑")
        
        st.markdown("---")
        st.subheader("The Thieves")
        if thieves_df.empty:
            st.success("No whips have been stolen in this period. All is right with the world.")
        else:
            thieves_display = thieves_df.sort_values(by=count_col, ascending=False)
            st.dataframe(
                thieves_display,
                column_config={
                    "Username": "Thief",
                    count_col: "Whips Stolen",
                    value_col: st.column_config.NumberColumn("Total Value", format="%,d")
                },
                column_order=("Username", count_col, value_col),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No whip data available for this period.")
