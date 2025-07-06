# dashboard/pages/7_⏱️_Personal_Bests.py

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import toml
from pathlib import Path
import json
import html

# --- Page Configuration ---
st.set_page_config(page_title="Personal Bests", page_icon="⏱️", layout="wide")


# --- Functions ---
@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
        # Adjust the path to correctly locate dashboard_texts.toml in the parent directory
        current_script_directory = Path(__file__).resolve().parent
        return toml.load(current_script_directory.parent / 'dashboard_texts.toml')
    except Exception as e:
        st.error(f"Failed to load dashboard_texts.toml: {e}")
        return {}

def display_hall_of_fame(df_pbs, texts):
    """Calculates and displays the players with the most records from the provided dataframe."""
    st.header("🏆 Biggest Sweats")
    page_texts = texts.get('personal_bests', {})
    
    if df_pbs.empty or 'Holder' not in df_pbs.columns:
        st.info("No records found to determine the biggest sweats.")
        return
    
    all_holders = df_pbs['Holder'].dropna().str.split(',').explode().str.strip()
    # MODIFICATION: Filter out empty strings so they are not counted as a record holder.
    all_holders = all_holders[all_holders != '']
    
    sweatiest_count = page_texts.get('sweatiest_players_count', 3)
    top_players = all_holders.value_counts().nlargest(sweatiest_count)
    
    if top_players.empty:
        st.info("No players currently hold any records.")
        return
        
    messages = page_texts.get('sweatiest_players_messages', [])
    random.shuffle(messages)

    cols = st.columns(len(top_players))
    for i, (player, count) in enumerate(top_players.items()):
        with cols[i]:
            if messages:
                message = messages[i % len(messages)].format(player=player, count=count)
                st.success(message)
            else:
                 st.success(f"**{player}** holds **{count}** record(s)!", icon="⭐")

def create_record_holder_table(df_pbs):
    """Creates a DataFrame of all record holders and their total record count from the provided dataframe."""
    if df_pbs.empty or 'Holder' not in df_pbs.columns:
        return pd.DataFrame()
        
    all_holders = df_pbs['Holder'].dropna().str.split(',').explode().str.strip()
    # MODIFICATION: Filter out empty strings so they are not counted as a record holder.
    all_holders = all_holders[all_holders != '']
    
    holder_counts = all_holders.value_counts().reset_index()
    holder_counts.columns = ['Record Holder', 'Records Held']
    return holder_counts.sort_values(by='Records Held', ascending=False)

def display_pb_card(task, holder, time, date):
    """Returns the HTML for a single Personal Best record card."""
    
    unclaimed = time == "0:00" or not holder
    card_class = "pb-card-unclaimed" if unclaimed else "pb-card"
    
    # Format holder string - now always shows all holders
    holder_display = "Unclaimed" if unclaimed else holder

    # Format date string
    date_display = ""
    if pd.notna(date):
        try:
            date_display = f"📅 {pd.to_datetime(date).strftime('%d %b %Y')}"
        except (ValueError, TypeError):
            date_display = "" # Keep it blank if date is invalid

    # Escape content to prevent HTML injection or rendering errors
    safe_task = html.escape(task)
    safe_holder = html.escape(holder_display)
    safe_time = html.escape(time.strip() if isinstance(time, str) else str(time))

    # Return the HTML string as a single block to avoid introducing whitespace/indentation
    # issues that can confuse Streamlit's HTML renderer.
    return (
        f'<div class="{card_class}">'
        f'<h4>{safe_task}</h4>'
        f'<div class="time">{safe_time}</div>'
        f'<div class="holder">👤 {safe_holder}</div>'
        f'<div class="date">{date_display}</div>'
        f'</div>'
    )


# --- Main Page Logic ---
st.title("⏱️ Personal Bests")
st.markdown("This board shows the fastest records achieved by clan members. Got a missing record? Contact an admin to have it added!")
st.info("The display is a work in progress")

# --- Custom CSS for PB Cards ---
st.markdown("""
<style>
    /* Grid container for responsive card layout */
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 1rem;
    }
    .pb-card {
        background-color: #004020; /* secondaryBackgroundColor */
        border: 2px solid #D4AF37; /* primaryColor */
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 220px; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-width: 340px;
        max-width: 450px;
    }
    .pb-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    .pb-card-unclaimed {
        background-color: #111e2b; /* Darker version of page background */
        border: 2px solid #555;
        border-radius: 10px;
        padding: 1rem;
        opacity: 0.7;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-width: 340px;
        max-width: 450px;
    }
    .pb-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.15em;
        color: #FFFFFF; /* textColor */
        font-weight: bold;
        text-align: center;
        flex-grow: 1;
        margin-bottom: -2rem;
    }
    .pb-card .time {
        font-size: 2em;
        font-weight: bold;
        color: #D4AF37; /* primaryColor */
        text-align: center;
        margin-bottom: -1rem;
    }
    .pb-card-unclaimed .time {
        color: #888;
    }
    .pb-card .holder, .pb-card .date {
        font-size: 1.15em;
        color: #FFFFFF; /* textColor */
        text-align: center;
    }
    /* Style for the expander title */
    div[data-testid="stExpander"] summary p {
        font-size: 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


df_pbs = Streamlit_utils.load_table("personal_bests_summary")
dashboard_config = Streamlit_utils.load_dashboard_config()
texts = load_texts()

if df_pbs.empty:
    st.warning("No Personal Best data could be loaded. The ETL pipeline may not have run yet.")
else:
    # --- Sidebar Sorting Toggles ---
    st.sidebar.header("Display Options")
    default_group_sort = dashboard_config.get('pb_default_group_sort', 'config')
    sort_groups_alpha = st.sidebar.toggle("Sort Groups Alphabetically", value=(default_group_sort == 'alphabetical'))

    default_item_sort = dashboard_config.get('pb_default_item_sort', 'alphabetical')
    sort_items_alpha = st.sidebar.toggle("Sort Records Alphabetically", value=(default_item_sort == 'alphabetical'))

    # --- Get Group and Item Order from Config ---
    group_order = json.loads(dashboard_config.get('pb_group_order', '[]'))
    item_orders = json.loads(dashboard_config.get('pb_item_orders', '{}'))
    other_group_name = dashboard_config.get('pb_other_group_name', 'Miscellaneous PBs')
    if other_group_name not in group_order:
        group_order.append(other_group_name)

    # --- Determine Group Display Order ---
    if sort_groups_alpha:
        groups_to_display = sorted([g for g in group_order if g in df_pbs['Group'].unique()])
    else:
        groups_to_display = [g for g in group_order if g in df_pbs['Group'].unique()]
    
    display_hall_of_fame(df_pbs, texts)
    st.markdown("---")
    
    # --- Display each group and its records ---
    for group_name in groups_to_display:
        # FIX: Use an expander for each group to prevent rendering issues
        with st.expander(group_name, expanded=True):
            df_group = df_pbs[df_pbs['Group'] == group_name].copy()
            
            # --- Sort items within the group based on toggle ---
            if not sort_items_alpha and group_name in item_orders:
                # Apply config order
                config_order = list(dict.fromkeys(item_orders.get(group_name, [])))
                tasks_in_df = df_group['Task'].unique()
                ordered_tasks = [task for task in config_order if task in tasks_in_df]
                other_tasks = sorted([task for task in tasks_in_df if task not in ordered_tasks])
                final_order = ordered_tasks + other_tasks
                
                if final_order:
                    df_group['Task'] = pd.Categorical(df_group['Task'], categories=final_order, ordered=True)
                    df_group.sort_values('Task', inplace=True)
            else:
                # Apply alphabetical order
                df_group.sort_values('Task', inplace=True)

            # --- Display records as cards in a responsive grid ---
            card_html_list = [display_pb_card(row.Task, row.Holder, row.Time, row.Date) for row in df_group.itertuples()]
            
            # Join all card HTML into one string and wrap in the grid container
            st.write(f'<div class="card-container">{"".join(card_html_list)}</div>', unsafe_allow_html=True)
        
    st.markdown("---")

    st.subheader("👑 Record Holder Leaderboard")
    
    df_holder_counts = create_record_holder_table(df_pbs)
    
    if not df_holder_counts.empty:
        st.dataframe(
            df_holder_counts,
            use_container_width=True,
            hide_index=True,
            height=(len(df_holder_counts) + 1) * 35 + 3
        )
    else:
        st.info("No record holders found in the data.")
