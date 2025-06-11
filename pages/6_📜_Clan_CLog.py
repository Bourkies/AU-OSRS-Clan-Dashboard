# dashboard/pages/6_📜_Clan_CLog.py
# Refactored to display the pre-calculated collection log summary.

import streamlit as st
import pandas as pd
import utils

st.title("📜 Clan Collection Log")
st.markdown("A summary of all unique items collected by the clan, combining historical and current data.")

df_clog = utils.load_table("collection_log_summary")

if df_clog.empty:
    st.warning("No collection log data could be loaded. The ETL pipeline may not have run yet.")
else:
    groups = sorted(df_clog['Group'].unique())
    
    st.sidebar.header("Filter by Group")
    selected_groups = st.sidebar.multiselect(
        "Select groups to display:", options=groups, default=groups
    )
    
    if not selected_groups:
        st.info("Please select one or more groups from the sidebar to view data.")
    else:
        df_filtered = df_clog[df_clog['Group'].isin(selected_groups)]
        for group_name in selected_groups:
            st.header(group_name)
            df_group = df_filtered[df_filtered['Group'] == group_name].copy()
            
            df_display = df_group[['Item_Name', 'All_Time_Count', 'YTD_Count', 'Last_Month_Count', 'Last_Week_Count']]
            df_display.rename(columns={
                'Item_Name': 'Item', 'All_Time_Count': 'All-Time',
                'YTD_Count': 'This Year', 'Last_Month_Count': 'Last Month', 'Last_Week_Count': 'Last Week'
            }, inplace=True)

            st.dataframe(
                df_display.sort_values(by='All-Time', ascending=False),
                use_container_width=True, hide_index=True,
                height=(len(df_display) + 1) * 35 + 3
            )
            st.markdown("---")