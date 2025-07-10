# dashboard/pages/9_☠️_Hardcore_Deaths.py

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import toml
from pathlib import Path
import html
import base64

# --- Page Configuration ---
st.set_page_config(page_title="Hardcore Deaths", page_icon="☠️", layout="wide")

# --- CONFIGURATION ---
# Set the filename of the background image. Place it in '.../assets/Page_backgrounds/'.
BACKGROUND_IMAGE_FILENAME = "1080px-Graveyard_of_Shadows.png"

# -- Tombstone Style & Layout Configuration --
TOMBSTONE_MIN_WIDTH_PX = 300
TOMBSTONE_MAX_WIDTH_PX = 340
TOMBSTONE_HEIGHT_PX = 290
TOMBSTONE_BORDER_WIDTH_PX = 4 # Increased border width
TOMBSTONE_TAPER_ANGLE_DEG = -15 # How much the tombstone leans back to give a 3D feel.

# -- Tombstone Color Configuration (CSS format) --
TOMBSTONE_TEXT_COLOR = "#c4c4c4"
# Solo (Normal) Death
SOLO_DEATH_BG_COLOR = "rgba(38, 39, 48, 0.85)"
SOLO_DEATH_BORDER_COLOR = "#4a4a4a"
# Group Life Lost
GROUP_LIFE_LOST_BG_COLOR = "rgba(48, 38, 39, 0.85)"
GROUP_LIFE_LOST_BORDER_COLOR = "#5a4a4a"
# Group Status Lost (Last Life)
GROUP_STATUS_LOST_BG_COLOR = "rgba(48, 60, 82, 0.85)" # More desaturated blue
GROUP_STATUS_LOST_BORDER_COLOR = "#7a8c99" # Greyish-blue border

# -- Grid Layout Configuration --
GRID_GAP_REM = 10 # Gap between cards.

# -- Randomization Limits --
RANDOM_ROTATION_DEG = 5      # Max rotation (e.g., 5 means -5 to +5 degrees).
RANDOM_OFFSET_Y_PX = 40         # Max vertical offset.
RANDOM_OFFSET_X_PX = 40         # Max horizontal offset.


# --- Functions ---

@st.cache_data
def get_image_as_base64(file_path):
    """Reads a local image file and returns its base64 encoded string."""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
            
        if not file_path.is_file():
            return None
            
        with open(file_path, "rb") as f:
            data = f.read()
            
        if len(data) == 0:
            return None
            
        return base64.b64encode(data).decode()
        
    except Exception as e:
        return None

def set_page_background(image_filename):
    """Sets the background of the page to the specified image."""
    if not image_filename:
        return

    # Try multiple possible paths
    current_script_directory = Path(__file__).resolve().parent
    possible_paths = [
        current_script_directory.parent / "assets" / "Page_backgrounds" / image_filename,  # dashboard/assets/
        current_script_directory / "assets" / "Page_backgrounds" / image_filename,        # pages/assets/
        Path(".") / "assets" / "Page_backgrounds" / image_filename,                       # ./assets/
        Path("./dashboard/assets/Page_backgrounds") / image_filename,                     # ./dashboard/assets/
        Path("assets/Page_backgrounds") / image_filename,                                 # assets/
    ]
    
    image_path = None
    for path in possible_paths:
        if path.exists():
            image_path = path
            break
    
    if not image_path:
        return False

    base64_image = get_image_as_base64(image_path)
    
    if base64_image:
        # Try multiple CSS selectors for better compatibility
        background_style = f"""
        <style>
        /* Multiple selectors to ensure compatibility */
        [data-testid="stApp"] > .main {{
            background-image: url("data:image/png;base64,{base64_image}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp > .main {{
            background-image: url("data:image/png;base64,{base64_image}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp {{
            background-image: url("data:image/png;base64,{base64_image}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Fallback for older Streamlit versions */
        .main .block-container {{
            background-image: url("data:image/png;base64,{base64_image}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(background_style, unsafe_allow_html=True)
        return True
    else:
        return False


# --- Apply Background and Custom CSS ---
set_page_background(BACKGROUND_IMAGE_FILENAME)

# Apply tombstone CSS
st.markdown(f"""
<style>
    .tombstone-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax({TOMBSTONE_MIN_WIDTH_PX}px, 1fr));
        gap: {GRID_GAP_REM}rem;
        padding-top: 1rem;
        perspective: 1000px; /* Adds perspective for 3D effect */
    }}
    .tombstone {{
        background-color: {SOLO_DEATH_BG_COLOR};
        border: {TOMBSTONE_BORDER_WIDTH_PX}px solid {SOLO_DEATH_BORDER_COLOR};
        border-bottom: none;
        border-radius: 40px 40px 5px 5px;
        padding: 1.5rem 1rem 1rem 1rem;
        text-align: center;
        height: {TOMBSTONE_HEIGHT_PX}px;
        min-width: {TOMBSTONE_MIN_WIDTH_PX}px;
        max-width: {TOMBSTONE_MAX_WIDTH_PX}px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        position: relative;
        color: {TOMBSTONE_TEXT_COLOR};
        transition: transform 0.2s ease-in-out;
        backdrop-filter: blur(2px);
        /* Default transform with taper */
        transform: rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg);
    }}
    .tombstone:hover {{
        /* On hover, remove random offsets and just scale up */
        transform: rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg) scale(1.05) !important;
    }}
    .tombstone.tombstone-group-life {{
        background-color: {GROUP_LIFE_LOST_BG_COLOR};
        border-color: {GROUP_LIFE_LOST_BORDER_COLOR};
    }}
    .tombstone.tombstone-group-status-lost {{
        background-color: {GROUP_STATUS_LOST_BG_COLOR};
        border-color: {GROUP_STATUS_LOST_BORDER_COLOR};
        animation: shake 0.82s cubic-bezier(.36,.07,.19,.97) both;
    }}
    .tombstone h4 {{
        font-size: 1.2em;
        font-weight: bold;
        color: #FFFFFF;
        margin-top: 0;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }}
    .tombstone .rip {{
        font-family: 'Courier New', Courier, monospace;
        font-size: 2.5em;
        font-weight: bold;
        color: #1e1e1e;
        margin: 0.5rem 0;
    }}
    .tombstone .death-message {{
        font-size: 0.95em;
        font-style: italic;
        flex-grow: 1;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }}
    .tombstone .death-date {{
        font-size: 0.9em;
        color: #888;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }}
    @keyframes shake {{
      10%, 90% {{ transform: translate3d(-1px, 0, 0) rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg); }}
      20%, 80% {{ transform: translate3d(2px, 0, 0) rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg); }}
      30%, 50%, 70% {{ transform: translate3d(-4px, 0, 0) rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg); }}
      40%, 60% {{ transform: translate3d(4px, 0, 0) rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg); }}
    }}
</style>
""", unsafe_allow_html=True)


# --- Data Loading ---

@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        # Try multiple paths for the TOML file too
        current_script_directory = Path(__file__).resolve().parent
        possible_toml_paths = [
            current_script_directory.parent / 'dashboard_texts.toml',
            current_script_directory / 'dashboard_texts.toml',
            Path('.') / 'dashboard_texts.toml',
        ]
        
        for toml_path in possible_toml_paths:
            if toml_path.exists():
                return toml.load(toml_path)
                
        return {}
    except Exception as e:
        return {}

@st.cache_data(ttl=300)
def load_hc_deaths():
    """Loads and filters for Hardcore death events."""
    try:
        df_achievements = Streamlit_utils.load_table("recent_achievements")
        if df_achievements.empty:
            return pd.DataFrame()
        
        df_deaths = df_achievements[df_achievements['Broadcast_Type'] == 'HC Life Lost'].copy()
        
        if 'New_Group_Lives' not in df_deaths.columns:
            df_deaths['New_Group_Lives'] = None
        else:
            df_deaths['New_Group_Lives'] = df_deaths['New_Group_Lives'].replace({"": None, pd.NA: None})

        df_deaths.sort_values(by='Timestamp', ascending=False, inplace=True)
        return df_deaths
    except Exception as e:
        return pd.DataFrame()

# --- Formatting Functions ---

def get_death_details(row, texts):
    """Determines the death type and message from a row."""
    page_texts = texts.get('hardcore_deaths', {})
    player = row.get('Username', 'A brave warrior')
    date = pd.to_datetime(row.get('Timestamp')).strftime('%d %b %Y')
    group_lives = row.get('New_Group_Lives')

    base_class = "tombstone"
    if pd.isna(group_lives):
        modifier_class = ""
        messages = page_texts.get('solo_death_messages', [])
        if not messages:
            messages = ["{player} thought they were invincible. They were wrong."]
        message_template = random.choice(messages)
    elif str(group_lives).startswith('0/'):
        modifier_class = "tombstone-group-status-lost"
        messages = page_texts.get('group_status_lost_messages', [])
        if not messages:
            messages = ["{player} took the team down with them. Team status: DEAD."]
        message_template = random.choice(messages)
    else:
        modifier_class = "tombstone-group-life"
        messages = page_texts.get('group_life_lost_messages', [])
        if not messages:
            messages = ["{player} cost the team a life. Lives remaining: {lives}"]
        message_template = random.choice(messages)
        
    full_class = f"{base_class} {modifier_class}".strip()
    
    message = message_template.format(player=player, date=date, lives=group_lives)
    message_html = message.replace(player, f'<strong>{player}</strong>', 1)
    
    return player, date, message_html, full_class

def display_tombstone(player, date, message, style_class, transform_style):
    """Returns the HTML for a single tombstone card with random transformations."""
    safe_player = html.escape(player)
    
    return (
        f'<div class="{style_class}" style="{transform_style}">'
        f'<h4>{safe_player}</h4>'
        f'<div class="rip">R.I.P.</div>'
        f'<div class="death-message">{message}</div>'
        f'<div class="death-date">Fallen: {date}</div>'
        f'</div>'
    )

# --- Main Page ---

st.title("☠️ The Graveyard: A Wall of Shame")
st.markdown('''A tribute to those who dared to risk it all and failed spectacularly. Press F to pay respects.''')
st.markdown(''' ''')
st.markdown(''' ''')

texts = load_texts()
df_deaths = load_hc_deaths()

if df_deaths.empty:
    st.success("🎉 The graveyard is empty! No one has died recently. The clan is safe... for now.")
else:
    df_to_display = df_deaths

    tombstone_cards = []
    for _, row in df_to_display.iterrows():
        player, date, message, style_class = get_death_details(row, texts)
        
        rotation = random.uniform(-RANDOM_ROTATION_DEG, RANDOM_ROTATION_DEG)
        y_offset = random.uniform(-RANDOM_OFFSET_Y_PX, RANDOM_OFFSET_Y_PX)
        x_offset = random.uniform(-RANDOM_OFFSET_X_PX, RANDOM_OFFSET_X_PX)
        
        # Combine the base taper with the random offsets
        transform_style = (
            f"transform: rotateX({TOMBSTONE_TAPER_ANGLE_DEG}deg) "
            f"rotateZ({rotation}deg) "
            f"translateY({y_offset}px) "
            f"translateX({x_offset}px);"
        )
        
        tombstone_cards.append(display_tombstone(player, date, message, style_class, transform_style))

    tombstones_html = "".join(tombstone_cards)
    st.markdown(f'<div class="tombstone-grid">{tombstones_html}</div>', unsafe_allow_html=True)