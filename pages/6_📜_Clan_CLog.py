# dashboard/pages/6_📜_Clan_CLog.py

import streamlit as st
import pandas as pd
import Streamlit_utils
from pathlib import Path
import json

st.set_page_config(page_title="Clan Collection Log", page_icon="📜", layout="wide")

st.title("📜 Clan Collection Log")
st.markdown("A summary of all unique items collected by the clan, combining historical and current data.")

df_clog = Streamlit_utils.load_table("collection_log_summary")
dashboard_config = Streamlit_utils.load_dashboard_config()

if df_clog.empty:
    st.warning("No collection log data could be loaded. The ETL pipeline may not have run yet.")
else:
    # Filter out items that have never been obtained
    df_display_all = df_clog[df_clog['All_Time_Count'] > 0].copy()

    # --- Sidebar Sorting Toggles ---
    st.sidebar.header("Display Options")
    default_group_sort = dashboard_config.get('clog_default_group_sort', 'config')
    sort_groups_alpha = st.sidebar.toggle("Sort Groups Alphabetically", value=(default_group_sort == 'alphabetical'))

    default_item_sort = dashboard_config.get('clog_default_item_sort', 'alphabetical')
    sort_items_alpha = st.sidebar.toggle("Sort Items Alphabetically", value=(default_item_sort == 'alphabetical'), key="clog_item_sort")

    # --- Get Group and Item Order from Config ---
    group_order = json.loads(dashboard_config.get('clog_group_order', '[]'))
    item_orders = json.loads(dashboard_config.get('clog_item_orders', '{}'))
    other_group_name = dashboard_config.get('clog_other_group_name', 'Miscellaneous Drops')
    if other_group_name not in group_order:
        group_order.append(other_group_name)

    # --- Determine Group Display Order ---
    if sort_groups_alpha:
        groups_to_display = sorted([g for g in group_order if g in df_display_all['Group'].unique()])
    else:
        groups_to_display = [g for g in group_order if g in df_display_all['Group'].unique()]

    # --- Sidebar Group Filter ---
    st.sidebar.header("Filter by Group")
    selected_groups = st.sidebar.multiselect(
        "Select groups to display:", options=groups_to_display, default=groups_to_display
    )
    
    if not selected_groups:
        st.info("Please select one or more groups from the sidebar to view data.")
    else:
        df_filtered = df_display_all[df_display_all['Group'].isin(selected_groups)]
        
        for group_name in groups_to_display:
            if group_name in selected_groups:
                st.subheader(group_name)
                df_group = df_filtered[df_filtered['Group'] == group_name].copy()
                
                # --- Sort items within the group based on toggle ---
                if not sort_items_alpha and group_name in item_orders:
                    item_order_list = item_orders[group_name]
                    df_group['Item_Name'] = pd.Categorical(df_group['Item_Name'], categories=item_order_list, ordered=True)
                    df_group.sort_values('Item_Name', inplace=True)
                else:
                    df_group.sort_values('Item_Name', inplace=True)
                
                display_columns = {
                    'Item_Name': 'Item',
                    'All_Time_Count': 'All-Time',
                    'YTD_Count': 'This Year',
                    'Prev_Month_Count': 'Last Month',
                    'Prev_Week_Count': 'Last Week',
                    'Custom_Days_Count': f"Last {dashboard_config.get('custom_lookback_days', 14)} Days"
                }
                
                df_display = df_group[list(display_columns.keys())]
                df_display = df_display.rename(columns=display_columns)

                st.dataframe(
                    df_display, # Already sorted
                    use_container_width=True, hide_index=True,
                    height=(len(df_display) + 1) * 35 + 3
                )
                st.markdown("---")
