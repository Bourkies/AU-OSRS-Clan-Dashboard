# dashboard/pages/6_📜_Clan_CLog.py

import streamlit as st
import pandas as pd
import Streamlit_utils

st.set_page_config(page_title="Clan Collection Log", page_icon="📜", layout="wide")

st.title("📜 Clan Collection Log")
st.markdown("A summary of all unique items collected by the clan, combining historical and current data.")

df_clog = Streamlit_utils.load_table("collection_log_summary")
dashboard_config = Streamlit_utils.load_dashboard_config()

if df_clog.empty:
    st.warning("No collection log data could be loaded. The ETL pipeline may not have run yet.")
else:
    other_group_name = dashboard_config.get('other_group_name', 'Miscellaneous')
    
    # Filter out items that have never been obtained
    df_display_all = df_clog[df_clog['All_Time_Count'] > 0]

    groups = sorted(df_display_all['Group'].unique())
    # Move "Other" group to the end
    if other_group_name in groups:
        groups.remove(other_group_name)
        groups.append(other_group_name)

    st.sidebar.header("Filter by Group")
    selected_groups = st.sidebar.multiselect(
        "Select groups to display:", options=groups, default=groups
    )
    
    if not selected_groups:
        st.info("Please select one or more groups from the sidebar to view data.")
    else:
        df_filtered = df_display_all[df_display_all['Group'].isin(selected_groups)]
        
        for group_name in selected_groups:
            st.subheader(group_name)
            df_group = df_filtered[df_filtered['Group'] == group_name].copy()
            
            # Define the columns and their new names
            display_columns = {
                'Item_Name': 'Item',
                'All_Time_Count': 'All-Time',
                'YTD_Count': 'This Year',
                'Prev_Month_Count': 'Last Month',
                'Prev_Week_Count': 'Last Week',
                'Custom_Days_Count': f"Last {dashboard_config.get('custom_lookback_days', 14)} Days"
            }
            
            # Select and rename columns
            df_display = df_group[list(display_columns.keys())]
            df_display = df_display.rename(columns=display_columns)

            st.dataframe(
                df_display.sort_values(by='All-Time', ascending=False),
                use_container_width=True, hide_index=True,
                height=(len(df_display) + 1) * 35 + 3
            )
            st.markdown("---")
