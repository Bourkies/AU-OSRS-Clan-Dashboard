# dashboard/pages/8_🏆_Recent_Achievements.py
# Refactored to be fully data-driven.

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import dashboard_texts as texts
from datetime import datetime

st.set_page_config(page_title="Recent Achievements", page_icon="🏆", layout="wide")

# --- Page Configuration ---
# This dictionary drives the entire page. To add a new section, just add a new entry here.
# The `filter` function provides a way to apply custom logic to the DataFrame for each section.
ACHIEVEMENT_CONFIG = {
    "high_hitters": {
        "title": "Heil Hitters",
        "icon": "🫡",
        "broadcast_type": "Combat Task",
        "message": texts.HIGH_HITTER_MESSAGES,
        "formatter": lambda r: {'player': r.get('Username'), 'date': pd.to_datetime(r.get('Timestamp')).strftime('%Y-%m-%d')},
        "filter": lambda df: df[df['Task_Name'] == 'High Hitter']
    },
    "maxed_skills": {
        "title": "Maxed Skills",
        "icon": "🎉",
        "broadcast_type": "Level Up",
        "message": texts.MAXED_SKILL_MESSAGES,
        "formatter": lambda r: {'player': r.get('Username'), 'skill': r.get('Skill'), 'date': pd.to_datetime(r.get('Timestamp')).strftime('%Y-%m-%d')},
        "filter": lambda df: df[df['New_Level'].isin([99, 126])]
    },
    "combat_tasks": {
        "title": "Recent Combat Tasks",
        "icon": "⚔️",
        "broadcast_type": "Combat Task",
        "message": texts.COMBAT_TASK_MESSAGES,
        "formatter": lambda r: {'player': r.get('Username'), 'task': r.get('Task_Name'), 'tier': r.get('Tier'), 'date': pd.to_datetime(r.get('Timestamp')).strftime('%Y-%m-%d')},
        "filter": lambda df: df[df['Task_Name'] != 'High Hitter'] # Exclude high hitters from this general list
    },
    "diaries": {
        "title": "Recent Diary Completions",
        "icon": "🗺️",
        "broadcast_type": "Diary",
        "message": texts.DIARY_MESSAGES,
        "formatter": lambda r: {'player': r.get('Username'), 'diary': r.get('Task_Name'), 'tier': r.get('Tier'), 'date': pd.to_datetime(r.get('Timestamp')).strftime('%Y-%m-%d')}
    },
    "ca_tiers": {
        "title": "Recent Combat Achievement Tiers",
        "icon": "🛡️",
        "broadcast_type": "Combat Achievement Tier",
        "message": texts.CA_TIER_MESSAGES,
        "formatter": lambda r: {'player': r.get('Username'), 'tier': r.get('Tier'), 'date': pd.to_datetime(r.get('Timestamp')).strftime('%Y-%m-%d')}
    },
    "pets": {
        "title": "Recent Pet Drops",
        "icon": "🐾",
        "broadcast_type": "Pet",
        "message": ["Congratulations to {player} on receiving the {pet_name} pet on {date}!"],
        "formatter": lambda r: {'player': r.get('Username'), 'pet_name': r.get('Pet_Name'), 'date': pd.to_datetime(r.get('Timestamp')).strftime('%Y-%m-%d')}
    }
}

def display_section(df, config):
    """
    Generic function to display a section based on the configuration.
    """
    st.header(f"{config['icon']} {config['title']}")
    
    # Filter the dataframe for the specific broadcast type
    df_section = df[df['Broadcast_Type'] == config['broadcast_type']].copy()
    
    # Apply any additional custom filtering logic
    if 'filter' in config:
        df_section = config['filter'](df_section)

    if df_section.empty:
        st.info(f"No recent '{config['title']}' achievements found.")
        return

    # Display each achievement in the filtered dataframe
    for _, row in df_section.iterrows():
        try:
            # Safely format the message using the provided formatter
            format_dict = config['formatter'](row)
            message = random.choice(config['message']).format(**format_dict)
            st.success(message, icon=config['icon'])
        except (KeyError, TypeError) as e:
            # This helps debug if the data from the DB is missing a required column for the message
            st.error(f"Error formatting message for {config['title']}: {e}. Check the formatter and data.")
            
    st.markdown("---")


# --- Main Page Execution ---
st.title("🏆 Recent Clan Achievements")
st.markdown("A feed of the most recent significant achievements from around the clan.")

# Load the single, consolidated recents table
df_recents = utils.load_table("recents_list")

if df_recents.empty:
    st.warning("No recent achievement data could be loaded. The ETL pipeline may not have run yet.")
else:
    # Ensure Timestamp is in datetime format
    df_recents['Timestamp'] = pd.to_datetime(df_recents['Timestamp'], errors='coerce', utc=True)
    df_recents.dropna(subset=['Timestamp'], inplace=True)

    # Loop through the configuration and display each section
    for key, config in ACHIEVEMENT_CONFIG.items():
        display_section(df_recents, config)
