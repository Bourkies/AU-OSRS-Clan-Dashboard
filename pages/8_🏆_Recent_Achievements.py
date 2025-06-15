# dashboard/pages/8_🏆_Recent_Achievements.py

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import toml
from pathlib import Path

current_script_directory = Path(__file__).resolve().parent

st.set_page_config(page_title="Recent Achievements", page_icon="🏆", layout="wide")

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        return toml.load(current_script_directory.parent / 'dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

def format_achievement(row, texts):
    """Formats a row from the achievements DataFrame into a displayable string."""
    broadcast_type = row.get('Broadcast_Type')
    page_texts = texts.get('recent_achievements', {})
    
    player = f"**{row.get('Username', 'Someone')}**"
    date = pd.to_datetime(row.get('Timestamp')).strftime('%Y-%m-%d')
    
    if broadcast_type == 'Maxed Skill (99)':
        messages = page_texts.get('maxed_skill_messages', [])
        return random.choice(messages).format(player=player, skill=row.get('Skill'), date=date)
    
    if broadcast_type == 'Maxed Combat':
        return f"👑 On {date}, {player} has achieved the highest combat level of 126!"

    elif broadcast_type == 'Level Up':
        messages = page_texts.get('level_up_messages', [])
        return random.choice(messages).format(player=player, level=row.get('New_Level'), skill=row.get('Skill'), date=date)

    elif broadcast_type == 'Combat Task':
        messages = page_texts.get('combat_task_messages', [])
        return random.choice(messages).format(player=player, tier=row.get('Tier'), task=row.get('Task_Name'), date=date)

    elif broadcast_type == 'Diary':
        messages = page_texts.get('diary_messages', [])
        return random.choice(messages).format(player=player, tier=row.get('Tier'), diary=row.get('Task_Name'), date=date)
        
    elif broadcast_type == 'Combat Achievement Tier':
        messages = page_texts.get('ca_tier_messages', [])
        return random.choice(messages).format(player=player, tier=row.get('Tier'), date=date)

    elif broadcast_type == 'Pet':
        messages = page_texts.get('pet_messages', [])
        return random.choice(messages).format(player=player, pet_name=row.get('Pet_Name'), date=date)

    elif broadcast_type == 'Quest':
        messages = page_texts.get('quest_messages', [])
        return random.choice(messages).format(player=player, quest_name=row.get('Task_Name'), date=date)

    return f"🏆 On {date}, {player} achieved: {row.get('Content', 'something noteworthy!')}"

# --- Main Page ---
st.title("🏆 Recent Achievements")
st.markdown("A live feed of the latest and greatest accomplishments from across the clan.")

df_achievements = Streamlit_utils.load_table("recent_achievements")
texts = load_texts()

if df_achievements.empty:
    st.warning("No recent achievements could be loaded. The ETL pipeline may not have run yet.")
else:
    limit = st.sidebar.slider(
        "Achievements to show per category:",
        min_value=1,
        max_value=25,
        value=5,
        step=1
    )
    
    st.markdown("---")
    
    # Define the order of sections
    section_order = [
        "Maxed Skill (99)",
        "Maxed Combat",
        "Pet",
        "Level Up",
        "Combat Task",
        "Diary",
        "Quest",
        "Combat Achievement Tier"
    ]
    
    available_types = df_achievements['Broadcast_Type'].unique()
    
    for ach_type in section_order:
        if ach_type in available_types:
            st.subheader(ach_type)
            df_section = df_achievements[df_achievements['Broadcast_Type'] == ach_type].head(limit)
            
            if df_section.empty:
                st.info(f"No recent '{ach_type}' achievements to display.")
            else:
                for index, row in df_section.iterrows():
                    achievement_message = format_achievement(row, texts)
                    st.info(achievement_message)
            st.markdown("---")