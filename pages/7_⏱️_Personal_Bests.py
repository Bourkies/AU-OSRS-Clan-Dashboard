# dashboard/pages/7_⏱️_Personal_Bests.py

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import toml

st.set_page_config(page_title="Personal Bests", page_icon="⏱️", layout="wide")

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        return toml.load('dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

def display_hall_of_fame(df_pbs, texts):
    """Calculates and displays the players with the most records."""
    st.header("🏆 Biggest Sweats (All-Time Records)")
    page_texts = texts.get('personal_bests', {})
    
    if df_pbs.empty or 'Holder' not in df_pbs.columns:
        st.info("No all-time records found to determine the biggest sweats.")
        return
    
    # Explode holders for records held by multiple people (e.g., "Player A & Player B")
    all_holders = df_pbs['Holder'].dropna().str.split(r'\s*&\s*').explode().str.strip()
    
    sweatiest_count = page_texts.get('sweatiest_players_count', 3)
    top_players = all_holders.value_counts().nlargest(sweatiest_count)
    
    if top_players.empty:
        st.info("No players currently hold any records.")
        return
        
    messages = page_texts.get('sweatiest_players_messages', [])
    random.shuffle(messages)

    for i, (player, count) in enumerate(top_players.items()):
        if messages:
            message = messages[i % len(messages)].format(player=player, count=count)
            st.success(message, icon="⭐")
        else:
             st.success(f"⭐ **{player}** holds **{count}** record(s)!", icon="⭐")

# --- Main Page ---
st.title("⏱️ Personal Bests")
st.markdown("This board shows the fastest all-time records achieved by clan members for various bosses and activities.")

df_pbs = Streamlit_utils.load_table("personal_bests_summary")
texts = load_texts()

if df_pbs.empty:
    st.warning("No Personal Best data could be loaded. The ETL pipeline may not have run yet.")
else:
    # Always display the Hall of Fame based on All-Time records
    display_hall_of_fame(df_pbs, texts)
    st.markdown("---")
    
    st.subheader("All-Time Leaderboard")
    
    # Display the final table, calculating height to avoid scrolling
    st.dataframe(
        df_pbs,
        column_config={
            "Task": "Task",
            "Holder": "Record Holder",
            "Time": "Time",
            "Date": st.column_config.DateColumn("Date Achieved", format="YYYY-MM-DD")
        },
        use_container_width=True, 
        hide_index=True,
        height=(len(df_pbs) + 1) * 35 + 3
    )
