# dashboard/pages/10_🎯_Bingo_Board.py
# A new page to display an interactive OSRS bingo board using HTML/CSS.

import streamlit as st
import yaml
from pathlib import Path
import base64
from PIL import Image
import html
import time
import os

# --- Page Configuration ---
st.set_page_config(page_title="OSRS Bingo", page_icon="�", layout="wide")

# --- Helper Functions ---

def load_config_uncached(path):
    """Loads the YAML configuration file for the bingo board without caching."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        st.error(f"Error loading or parsing bingo_board.yml: {e}")
        return None

@st.cache_data(ttl=3600)
def load_config_cached(path):
    """Loads the YAML configuration file for the bingo board with caching for production."""
    return load_config_uncached(path)

@st.cache_data
def load_background_image(file_path):
    """
    Reads a local image file, returns its base64 encoded string,
    and its dimensions (width, height).
    """
    try:
        path = Path(file_path)
        if not path.is_file():
            st.warning(f"Background image not found at: {file_path}")
            return None, 0, 0
        
        with Image.open(path) as img:
            width, height = img.size

        with open(path, "rb") as f:
            b64_string = base64.b64encode(f.read()).decode()
            
        return b64_string, width, height
    except Exception as e:
        st.error(f"Error reading background image: {e}")
        return None, 0, 0

def generate_board_html(tiles_config, defaults, bg_image_b64, aspect_ratio, show_tile_names):
    """Generates the full HTML and CSS for the interactive bingo board."""
    
    # --- CSS Styling ---
    styles = f"""
    <style>
        .bingo-container {{
            position: relative;
            width: 100%;
            padding-bottom: {aspect_ratio * 100}%; /* Maintain aspect ratio */
            background-image: url("data:image/png;base64,{bg_image_b64}");
            background-size: contain;
            background-repeat: no-repeat;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .bingo-tile {{
            position: absolute;
            display: flex;
            justify-content: center;
            align-items: center;
            text-decoration: none;
            transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
            cursor: pointer; /* Indicates it's clickable */
        }}
        .bingo-tile:hover {{
            background-color: #FFFFFF33; /* White with 20% opacity on hover */
            border-color: #FFFFFF;
        }}
        .tile-name {{
            color: {defaults.get('font_fill', '#FFFFFFF2')};
            font-size: {defaults.get('font_size', 14)}px;
            font-weight: bold;
            text-align: center;
            padding: 2px;
            text-shadow: 1px 1px 2px black;
            pointer-events: none; /* Make text non-interactive */
        }}
        
        /* --- Custom Tooltip Styles --- */
        .tooltip-base {{
            visibility: hidden;
            opacity: 0;
            background-color: #222;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 10;
            transition: opacity 0.3s;
            pointer-events: none;
            width: 200px; /* Default width */
            left: 50%;
            transform: translateX(-50%);
        }}
        
        /* Wider tooltip for longer descriptions */
        .tooltip-wide {{
            width: 300px;
        }}
        
        /* Position tooltip ABOVE the tile */
        .tooltip-above {{
            bottom: 110%;
        }}
        .tooltip-above::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #222 transparent transparent transparent;
        }}

        /* Position tooltip BELOW the tile */
        .tooltip-below {{
            top: 110%;
        }}
        .tooltip-below::after {{
            content: "";
            position: absolute;
            bottom: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: transparent transparent #222 transparent;
        }}

        /* Show tooltip on hover (desktop) or focus (mobile tap) */
        .bingo-tile:hover .tooltip-base,
        .bingo-tile:focus .tooltip-base {{
            visibility: visible;
            opacity: 1;
        }}
    </style>
    """
    
    # --- HTML Generation ---
    tiles_html = ""
    if tiles_config:
        for tile in tiles_config:
            pos = tile.get("position", {})
            size = tile.get("size", {})
            style_override = tile.get("style_override", {})

            # --- Logic for smart tooltip ---
            description = tile.get('description', '')
            y_position = pos.get('y_pct', 0)
            
            # Check for manual override, otherwise position automatically
            override_pos = tile.get('tooltip_position')
            if override_pos == 'top':
                position_class = "tooltip-above"
            elif override_pos == 'bottom':
                position_class = "tooltip-below"
            else: # Automatic positioning
                position_class = "tooltip-below" if y_position < 50 else "tooltip-above"
            
            # Determine width
            width_class = "tooltip-wide" if len(description) > 60 else ""
            
            tooltip_classes = f"tooltip-base {position_class} {width_class}"
            
            # Content for the custom tooltip
            tooltip_html = f"<strong>{html.escape(tile.get('name', ''))}</strong>"
            if description:
                tooltip_html += f"<br><small>{html.escape(description)}</small>"

            # Inline styles for positioning and individual overrides
            inline_style = (
                f"left: {pos.get('x_pct', 0)}%; "
                f"top: {pos.get('y_pct', 0)}%; "
                f"width: {size.get('width_pct', 0)}%; "
                f"height: {size.get('height_pct', 0)}%; "
                f"border: {style_override.get('stroke_width', defaults.get('stroke_width', 2))}px solid {style_override.get('stroke_color', defaults.get('stroke_color', '#FFFFFFB3'))}; "
                f"background-color: {style_override.get('fill_color', defaults.get('fill_color', '#00000033'))}; "
                f"transform: rotate({tile.get('rotation', 0)}deg);"
            )
            
            tile_name_span = f"<span class='tile-name'>{html.escape(tile.get('name', ''))}</span>" if show_tile_names else ""

            # Add tabindex='0' to make the <a> tag focusable for mobile tap
            # Add onclick="event.preventDefault();" to stop the new tab behavior
            tiles_html += (
                f'<a href="#" onclick="event.preventDefault();" class="bingo-tile" style="{inline_style}" tabindex="0">'
                f"{tile_name_span}"
                f'<span class="{tooltip_classes}">{tooltip_html}</span>'
                f'</a>'
            )

    full_html = f"{styles}<div class='bingo-container'>{tiles_html}</div>"
    return full_html


# --- Main Page Logic ---
st.title("🎯 OSRS Clan Bingo")
st.markdown("Hover over a tile on the board to see its details. On mobile, tap a tile.")

# --- Sidebar Controls ---
st.sidebar.header("Board Options")

# Check environment variable to decide whether to show setup mode
# To enable, run streamlit with: APP_ENV=development streamlit run Home.py
is_dev_mode = os.environ.get("APP_ENV") == "development"
setup_mode = False

if is_dev_mode:
    setup_mode = st.sidebar.toggle("🛠️ Setup Mode", value=False)

if setup_mode:
    st.sidebar.info("Setup mode enabled. Config will refresh instantly.")
    show_tile_names = st.sidebar.toggle(
        "Show Tile Names on Board",
        value=True,
        help="Display tile names directly on the shapes for easy setup."
    )
    if st.sidebar.button("🔄 Refresh Config"):
        st.rerun()
else:
    # Default behavior for regular users (production)
    show_tile_names = False


# Define paths relative to the script location
current_dir = Path(__file__).parent
config_path = current_dir / "bingo_board.yml"

# Load config based on mode
config = load_config_uncached(config_path) if setup_mode else load_config_cached(config_path)

if not config:
    st.error("bingo_board.yml could not be loaded. Check the file for errors.")
    st.stop()

# --- Load Board and Tile Settings ---
board_settings = config.get("board_settings", {})
defaults = config.get("defaults", {})
tiles_config = config.get("tiles", [])

# Load background image and get its dimensions
image_path = current_dir / board_settings.get("background_image", "bingo_board_placeholder.png")
bg_image_b64, img_width, img_height = load_background_image(image_path)

if not bg_image_b64:
    st.error("Could not load the background image. Please check the path in bingo_board.yml.")
    st.stop()

# --- Generate and Display Board ---
aspect_ratio = img_height / img_width if img_width > 0 else 1
board_html = generate_board_html(tiles_config, defaults, bg_image_b64, aspect_ratio, show_tile_names)

st.markdown(board_html, unsafe_allow_html=True)