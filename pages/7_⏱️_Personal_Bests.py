# dashboard/pages/7_⏱️_Personal_Bests.py

import streamlit as st
import pandas as pd
import random
import Streamlit_utils
import toml
from pathlib import Path
import json

# --- Page Configuration ---
st.set_page_config(page_title="Personal Bests", page_icon="⏱️", layout="wide")


# --- Functions ---
@st.cache_data(ttl=300)
def load_texts():
    """Loads text snippets from the TOML file."""
    try:
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
            st.success(message)
        else:
             st.success(f"**{player}** holds **{count}** record(s)!", icon="⭐")

def create_record_holder_table(df_pbs):
    """Creates a DataFrame of all record holders and their total record count from the provided dataframe."""
    if df_pbs.empty or 'Holder' not in df_pbs.columns:
        return pd.DataFrame()
        
    all_holders = df_pbs['Holder'].dropna().str.split(',').explode().str.strip()
    holder_counts = all_holders.value_counts().reset_index()
    holder_counts.columns = ['Record Holder', 'Records Held']
    return holder_counts.sort_values(by='Records Held', ascending=False)

# --- Main Page Logic ---
st.title("⏱️ Personal Bests")
st.markdown("This board shows the fastest records achieved by clan members. Got a missing record? Contact an admin to have it added!")

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
    
    st.subheader("⏱️ Leaderboard")

    # --- Display each group and its records ---
    for group_name in groups_to_display:
        st.subheader(group_name)
        df_group = df_pbs[df_pbs['Group'] == group_name].copy()
        
        # --- Sort items within the group based on toggle ---
        if not sort_items_alpha and group_name in item_orders:
            # Apply config order
            item_order_list = item_orders[group_name]
            df_group['Task'] = pd.Categorical(df_group['Task'], categories=item_order_list, ordered=True)
            df_group.sort_values('Task', inplace=True)
        else:
            # Apply alphabetical order
            df_group.sort_values('Task', inplace=True)

        st.dataframe(
            df_group[['Task', 'Holder', 'Time', 'Date']],
            column_config={
                "Task": "Task",
                "Holder": "Record Holder(s)",
                "Time": "Time",
                "Date": st.column_config.DateColumn("Date Achieved", format="YYYY-MM-DD")
            },
            use_container_width=True, 
            hide_index=True,
            height=(len(df_group) + 1) * 35 + 3
        )
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
