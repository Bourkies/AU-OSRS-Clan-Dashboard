# dashboard/pages/6_📜_Clan_CLog.py

import streamlit as st
import pandas as pd
import Streamlit_utils
import json
import html
import os
import base64
import re

st.set_page_config(page_title="Clan Collection Log", page_icon="📜", layout="wide")

# --- Define paths to assets ---
# The only file you now need from the osrsreboxed-db is 'items-complete.json'
# https://github.com/0xNeffarion/osrsreboxed-db/blob/master/osrsreboxed/docs/items-complete.json
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
CUSTOM_ICON_DIR = os.path.join(ASSETS_DIR, "custom_icons")
# Path to the local item data file that includes base64 icons
ITEM_DATA_PATH = os.path.join(ASSETS_DIR, "items-complete.json")

# --- Helper function to load all item data from a single local file ---
@st.cache_data
def load_item_data(path):
    """
    Loads item data from a local JSON file, creating two mappings:
    1. A mapping from lowercase item name to its base64 icon data URI.
    2. A mapping from lowercase item name to its wiki URL.
    This function prioritizes items where 'noted' is false.
    """
    if not os.path.exists(path):
        st.error(f"Fatal Error: The item data file was not found at {path}")
        return {}, {}
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Use an intermediate dictionary to handle noted/un-noted priority.
    processed_items = {}
    for item_id, item_details in data.items():
        name = item_details.get('name')
        if not name:
            continue
        
        name_lower = name.lower()
        is_noted = item_details.get('noted', True)

        # We want to store the item if it's the first one we've seen with this name,
        # or if it's the un-noted version, which takes priority.
        if name_lower not in processed_items or not is_noted:
            processed_items[name_lower] = {
                'icon': item_details.get('icon'),
                'wiki_url': item_details.get('wiki_url')
            }

    # Create the final maps from the processed data.
    name_to_icon_map = {
        name: f"data:image/png;base64,{details['icon']}"
        for name, details in processed_items.items()
        if details.get('icon')
    }
    name_to_wiki_url_map = {
        name: details['wiki_url']
        for name, details in processed_items.items()
        if details.get('wiki_url')
    }
    
    return name_to_icon_map, name_to_wiki_url_map

# --- Helper function to get image as base64 (for custom icons) ---
@st.cache_data
def get_image_as_base64(file_path):
    """Reads a local image file and returns its base64 encoded string."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Custom CSS for the responsive card grid layout ---
st.markdown("""
<style>
    /*
     VVV CHANGE THE FONT SIZE AND STYLE OF THE EXPANDER TITLE HERE VVV
     Using 'data-testid' is a stable way to target Streamlit components.
    */
    div[data-testid="stExpander"] summary p {
        font-size: 1.2rem; /* Example values: 1.2rem, 18px, 1.5em */
        font-weight: bold;
    }
    /* ^^^ CHANGE THE FONT SIZE AND STYLE OF THE EXPANDER TITLE HERE ^^^ */

    .card-grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 10px;
    }
    .item-card {
        background-color: #0A1931;
        border: 1px solid #D4AF37;
        border-radius: 7px;
        padding: 10px 42px 10px 10px;
        height: 110px;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
    }
    .icon-container {
        width: 42px;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        flex-shrink: 0;
    }
    .item-icon {
        max-height: 32px;
        max-width: 32px;
    }
    .text-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        height: 100%;
        overflow: hidden;
    }
    .item-name {
        font-size: 0.9em;
        font-weight: bold;
        color: #FFFFFF;
        text-align: left;
    }
    .item-count {
        font-size: 1.1em;
        color: #D4AF37;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)


st.title("📜 Clan Collection Log")
st.markdown("A summary of all unique items collected by the clan")

# --- Data Loading ---
df_clog = Streamlit_utils.load_table("collection_log_summary")
dashboard_config = Streamlit_utils.load_dashboard_config()
# Load both the icon and wiki URL maps using our new function
item_icon_map, item_wiki_url_map = load_item_data(ITEM_DATA_PATH)


if df_clog.empty:
    st.warning("No collection log data could be loaded. The ETL pipeline may not have run yet.")
elif not item_icon_map:
    st.error("Could not load item data. Please ensure `items-complete.json` is in the `assets` folder.")
else:
    # Filter out items that have never been obtained
    df_display_all = df_clog[df_clog['All_Time_Count'] > 0].copy()

    # --- Get Group and Item Order from Config ---
    group_order_from_config = json.loads(dashboard_config.get('clog_group_order', '[]'))
    item_orders = json.loads(dashboard_config.get('clog_item_orders', '{}'))
    other_group_name = dashboard_config.get('clog_other_group_name', 'Miscellaneous Drops')
    if other_group_name not in group_order_from_config:
        group_order_from_config.append(other_group_name)

    # Determine the actual groups present in the data to be displayed
    actual_groups_in_data = sorted(df_display_all['Group'].unique())

    # --- Sidebar ---
    st.sidebar.header("Display Options")

    # Sorting Toggles
    default_group_sort = dashboard_config.get('clog_default_group_sort', 'config')
    sort_groups_alpha = st.sidebar.toggle("Sort Groups Alphabetically", value=(default_group_sort == 'alphabetical'))

    default_item_sort = dashboard_config.get('clog_default_item_sort', 'alphabetical')
    sort_items_alpha = st.sidebar.toggle("Sort Items Alphabetically", value=(default_item_sort == 'alphabetical'), key="clog_item_sort")

    st.sidebar.markdown("---")
    
    # Determine Group Display Order based on the toggle
    if sort_groups_alpha:
        groups_to_display_options = actual_groups_in_data
    else:
        # Filter config order to only include groups that actually have data
        groups_to_display_options = [g for g in group_order_from_config if g in actual_groups_in_data]

    # Filtering Section
    st.sidebar.header("Filter by Group")
    # Initialize session state for the multiselect if it doesn't exist
    if 'selected_clog_groups' not in st.session_state:
        st.session_state.selected_clog_groups = groups_to_display_options

    # Select/Deselect All buttons
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Select All", use_container_width=True, key="clog_select_all"):
        st.session_state.selected_clog_groups = groups_to_display_options
        st.rerun()
    if col2.button("Deselect All", use_container_width=True, key="clog_deselect_all"):
        st.session_state.selected_clog_groups = []
        st.rerun()

    selected_groups = st.sidebar.multiselect(
        "Select groups to display:",
        options=groups_to_display_options,
        default=st.session_state.selected_clog_groups,
        key="clog_group_selector"
    )
    st.session_state.selected_clog_groups = selected_groups


    # --- Main Page Display ---
    if not selected_groups:
        st.info("Please select one or more groups from the sidebar to view data.")
    else:
        df_filtered = df_display_all[df_display_all['Group'].isin(selected_groups)]

        if sort_groups_alpha:
             final_group_render_order = sorted(selected_groups)
        else:
             final_group_render_order = [g for g in group_order_from_config if g in selected_groups]

        for group_name in final_group_render_order:
            # Use an expander for each group. The title style is set in the CSS above.
            with st.expander(label=group_name, expanded=True):
                df_group = df_filtered[df_filtered['Group'] == group_name].copy()
                
                # Sort items within the group based on toggle
                if not sort_items_alpha and group_name in item_orders:
                    item_order_list = item_orders.get(group_name, [])
                    df_group['Item_Name'] = pd.Categorical(df_group['Item_Name'], categories=item_order_list, ordered=True)
                    df_group.sort_values('Item_Name', inplace=True)
                else:
                    df_group.sort_values('Item_Name', inplace=True)
                
                # --- Card Display Logic ---
                items_in_group = df_group.to_dict('records')
                
                card_html_list = []
                for item in items_in_group:
                    safe_item_name = html.escape(item['Item_Name'])
                    item_name_lower = item['Item_Name'].lower().strip()
                    
                    # --- UPDATED ICON LOGIC ---
                    icon_html = ""
                    icon_src = ""
                    
                    # 1. Try to find the custom name-based icon first
                    custom_icon_filename = re.sub(r'[^a-zA-Z0-9_]', '', item['Item_Name'].replace(' ', '_')) + ".webp"
                    custom_icon_path = os.path.join(CUSTOM_ICON_DIR, custom_icon_filename)
                    
                    if os.path.exists(custom_icon_path):
                        icon_b64 = get_image_as_base64(custom_icon_path)
                        if icon_b64:
                            icon_src = f"data:image/webp;base64,{icon_b64}"
                    
                    # 2. If not found, fall back to the direct icon map from items-complete.json
                    if not icon_src:
                        icon_src = item_icon_map.get(item_name_lower)

                    # 3. Build the final icon HTML, adding a link if a wiki URL exists.
                    if icon_src:
                        icon_img_tag = f'<img src="{icon_src}" class="item-icon">'
                        wiki_url = item_wiki_url_map.get(item_name_lower)
                        if wiki_url:
                            # Wrap the image in a clickable link
                            icon_html = f'<a href="{html.escape(wiki_url)}" target="_blank" rel="noopener noreferrer">{icon_img_tag}</a>'
                        else:
                            icon_html = icon_img_tag
                    # --- End Icon Logic ---
                    
                    icon_container_html = f'<div class="icon-container">{icon_html}</div>'

                    # --- Text Content ---
                    text_container_html = (
                        '<div class="text-container">'
                        f'<div class="item-name">{safe_item_name}</div>'
                        f'<div class="item-count">{item["All_Time_Count"]:,}</div>'
                        '</div>'
                    )

                    card_html = (
                        f'<div class="item-card">{icon_container_html}{text_container_html}</div>'
                    )
                    card_html_list.append(card_html)
                
                all_cards_html = "".join(card_html_list)
                grid_html = f'<div class="card-grid-container">{all_cards_html}</div>'
                
                st.markdown(grid_html, unsafe_allow_html=True)
