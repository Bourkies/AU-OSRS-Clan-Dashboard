# dashboard/pages/8_🏆_Recent_Achievements.py

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import toml
from pathlib import Path
import html
import re

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

def get_achievement_message(row, texts):
    """Gets the formatted message for an achievement and converts markdown to HTML."""
    broadcast_type = row.get('Broadcast_Type')
    page_texts = texts.get('recent_achievements', {})
    
    player = html.escape(row.get('Username', 'Someone'))
    date = pd.to_datetime(row.get('Timestamp')).strftime('%d %b %Y')
    
    new_level_val = row.get('New_Level')
    level = int(new_level_val) if pd.notna(new_level_val) else 0

    message_map = {
        'Maxed Skill (99)': ('maxed_skill_messages', {'player': player, 'skill': row.get('Skill'), 'date': date}),
        'Maxed Combat': (f"On {date}, **{player}** achieved the highest combat level of 126!", {}),
        'Level Up': ('level_up_messages', {'player': player, 'level': level, 'skill': row.get('Skill'), 'date': date}),
        'Combat Task': ('combat_task_messages', {'player': player, 'tier': row.get('Tier'), 'task': row.get('Task_Name'), 'date': date}),
        'Diary': ('diary_messages', {'player': player, 'tier': row.get('Tier'), 'diary': row.get('Task_Name'), 'date': date}),
        'Combat Achievement Tier': ('ca_tier_messages', {'player': player, 'tier': row.get('Tier'), 'date': date}),
        'Pet': ('pet_messages', {'player': player, 'pet_name': row.get('Pet_Name'), 'date': date}),
        'Quest': ('quest_messages', {'player': player, 'quest_name': row.get('Task_Name'), 'date': date})
    }
    
    raw_message = f"🏆 On {date}, **{player}** achieved: {html.escape(row.get('Content', 'something noteworthy!'))}"

    if broadcast_type in message_map:
        msg_info, format_args = message_map[broadcast_type]
        if isinstance(msg_info, str) and not format_args:
            raw_message = msg_info.format(player=player, date=date)
        else:
            messages = page_texts.get(msg_info, [])
            if messages:
                raw_message = random.choice(messages).format(**format_args)
    
    # FIX: Convert markdown bold `**text**` to HTML `<strong>text</strong>` for proper rendering.
    html_message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', raw_message)
    return html_message


def display_achievement_card(row, texts, color_map):
    """Returns the HTML for a single achievement card."""
    broadcast_type = row.get('Broadcast_Type')
    card_class = color_map.get(broadcast_type, 'card-default')
    
    message = get_achievement_message(row, texts)
    date = pd.to_datetime(row.get('Timestamp')).strftime('%d %b %Y')
    title = html.escape(broadcast_type)

    return (
        f'<div class="ach-card {card_class}">'
        f'<div class="ach-title">{title}</div>'
        f'<div class="ach-message">{message}</div>'
        f'<div class="ach-date">{date}</div>'
        f'</div>'
    )

# --- Main Page ---
st.title("🏆 Recent Achievements")
st.markdown("A live feed of the latest and greatest accomplishments from across the clan.")

# --- Custom CSS for Achievement Cards ---
st.markdown("""
<style>
    .feed-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 1rem;
    }
    .ach-card {
        border-left: 5px solid;
        border-radius: 8px;
        padding: 1rem;
        background-color: #262730; /* secondaryBackgroundColor */
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 140px; /* Increased height for title */
    }
    .ach-title {
        font-size: 0.9em;
        font-weight: bold;
        color: #CCCCCC;
        text-align: center;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #444;
        padding-bottom: 0.5rem;
    }
    .ach-message {
        font-size: 1em;
        color: #FAFAFA; /* textColor */
        margin-bottom: 0.5rem;
        flex-grow: 1;
    }
    .ach-message strong {
        color: #A4E0DC; /* A slightly different color for emphasis */
        font-weight: bold;
    }
    .ach-date {
        font-size: 0.85em;
        color: #888;
        text-align: right;
    }

    /* Color mapping */
    .card-maxed { border-color: #FFD700; } /* Gold */
    .card-pet { border-color: #DDA0DD; } /* Plum */
    .card-level-up { border-color: #4682B4; } /* SteelBlue */
    .card-combat { border-color: #DC143C; } /* Crimson */
    .card-diary-quest { border-color: #8B4513; } /* SaddleBrown */
    .card-default { border-color: #008080; } /* Teal */
</style>
""", unsafe_allow_html=True)


df_achievements = Streamlit_utils.load_table("recent_achievements")
texts = load_texts()

if df_achievements.empty:
    st.warning("No recent achievements could be loaded. The ETL pipeline may not have run yet.")
else:
    limit = st.sidebar.slider(
        "Number of achievements to show:",
        min_value=5,
        max_value=100,
        value=25,
        step=5
    )
    
    st.markdown("---")
    
    # Map broadcast types to CSS classes for colors
    color_map = {
        "Maxed Skill (99)": "card-maxed",
        "Maxed Combat": "card-maxed",
        "Pet": "card-pet",
        "Level Up": "card-level-up",
        "Combat Task": "card-combat",
        "Combat Achievement Tier": "card-combat",
        "Diary": "card-diary-quest",
        "Quest": "card-diary-quest"
    }
    
    # FIX: Grab the latest of each category, then show the rest chronologically.
    available_types = df_achievements['Broadcast_Type'].dropna().unique()
    latest_from_each_type = []
    indices_of_latest = []

    # Step 1: Get the single latest achievement from each category.
    for ach_type in available_types:
        latest_for_type = df_achievements[df_achievements['Broadcast_Type'] == ach_type].head(1)
        if not latest_for_type.empty:
            latest_from_each_type.append(latest_for_type)
            indices_of_latest.append(latest_for_type.index[0])

    # Step 2: Combine the "latest" achievements and sort them by date.
    if latest_from_each_type:
        latest_df = pd.concat(latest_from_each_type)
        latest_df.sort_values(by='Timestamp', ascending=False, inplace=True)

        # Step 3: Get the rest of the achievements, excluding the ones we already grabbed.
        rest_df = df_achievements.drop(indices_of_latest)

        # Step 4: Combine the two lists. The 'latest' ones will be at the top, sorted amongst themselves.
        # The rest will follow, already in chronological order.
        final_df = pd.concat([latest_df, rest_df])
        
        # Step 5: Apply the user-selected limit.
        df_to_display = final_df.head(limit)
    else:
        # Fallback if no achievements are found
        df_to_display = df_achievements.head(limit)

    if not df_to_display.empty:
        card_html_list = [display_achievement_card(row, texts, color_map) for index, row in df_to_display.iterrows()]
        st.markdown(f'<div class="feed-container">{"".join(card_html_list)}</div>', unsafe_allow_html=True)
    else:
        st.info("No achievements to display with the current settings.")
