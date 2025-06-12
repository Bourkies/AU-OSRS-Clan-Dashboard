# dashboard/pages/7_⏱️_Personal_Bests.py
# Refactored to display the pre-calculated personal bests table with time selector.

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import dashboard_texts as texts

st.set_page_config(page_title="Personal Bests", page_icon="⏱️", layout="wide")

st.title("⏱️ Personal Bests")
st.markdown("This board shows the fastest times achieved by clan members for various bosses and activities.")

def display_hall_of_fame(df_all_time):
    """Calculates and displays the players with the most records."""
    st.header("🏆 Biggest Sweats (All-Time Records)")
    if df_all_time.empty or 'Holder_All_Time' not in df_all_time.columns:
        st.info("No all-time records found to determine the biggest sweats.")
        return
        
    # Explode holders for records held by multiple people
    all_holders = df_all_time['Holder_All_Time'].dropna().str.split(r'\s*&\s*').explode().str.strip()
    top_players = all_holders.value_counts().nlargest(3)
    
    if top_players.empty:
        st.info("No players currently hold any records.")
        return
        
    cols = st.columns(len(top_players))
    for i, (player, count) in enumerate(top_players.items()):
        with cols[i]:
            message = random.choice(texts.SWEATIEST_PLAYERS_MESSAGES).format(player=player, count=count)
            st.info(message, icon="⭐")

# --- Main Page ---
df_pbs = utils.load_table("personal_bests_summary")

if df_pbs.empty:
    st.warning("No Personal Best data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_suffix = utils.display_time_period_selector(key_prefix="pbs")
    
    holder_col = f'Holder_{period_suffix}'
    pb_col = f'PB_{period_suffix}'
    
    # Always display the Hall of Fame based on All-Time records
    display_hall_of_fame(df_pbs)
    st.markdown("---")
    
    # Filter for the selected time period
    df_period = df_pbs.dropna(subset=[holder_col, pb_col])
    
    if df_period.empty:
        st.info("No new personal bests were set in this time period.")
    else:
        st.subheader("Leaderboard")
        df_display = df_period[['Task_Name', holder_col, pb_col]].sort_values(by='Task_Name')
        df_display.rename(columns={
            'Task_Name': 'Task',
            holder_col: 'Record Holder',
            pb_col: 'Personal Best'
        }, inplace=True)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
