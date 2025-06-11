# dashboard/pages/2_💀_PvP_Leaderboard.py
# Refactored to display pre-aggregated PvP data.

import streamlit as st
import pandas as pd
import utils
import dashboard_texts as texts

st.title("💀 PvP Leaderboards")
st.markdown("This page shows leaderboards for player kills and deaths in the Wilderness.")

df_kills = utils.load_table("pvp_kills_summary")
df_deaths = utils.load_table("pvp_deaths_summary")

if df_kills.empty or df_deaths.empty:
    st.warning("No PvP data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_suffix = utils.display_time_period_selector(key_prefix="pvp")
    
    kills_count_col = f'Kills_{period_suffix}' if period_suffix != "All_Time" else 'Kills_All_Time'
    kills_value_col = f'Total_Value_{period_suffix}'
    deaths_count_col = f'Deaths_{period_suffix}' if period_suffix != "All_Time" else 'Deaths_All_Time'
    deaths_value_col = f'Total_Value_Lost_{period_suffix}' if period_suffix != "All_Time" else 'Total_Value_Lost_All_Time'
    
    st.header("Hall of Shame")
    df_shame = df_deaths[df_deaths['Username'].isin(texts.HALL_OF_SHAME_CONFIG.keys())]
    df_shame_period = df_shame[df_shame[deaths_count_col] > 0]
    
    if df_shame_period.empty:
        st.info("The usual suspects have kept themselves safe this period. Well done.")
    else:
        for _, row in df_shame_period.iterrows():
            player = row['Username']
            deaths = int(row[deaths_count_col])
            value_lost = f"{int(row[deaths_value_col]):,}"
            st.info(texts.get_shame_message(player, deaths, value_lost), icon="😭")
    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Killers (The Winners)")
        df_killers_period = df_kills[df_kills[kills_count_col] > 0].sort_values(by=kills_value_col, ascending=False)
        if df_killers_period.empty:
            st.info("No kills recorded for this period.")
        else:
            df_killers_display = df_killers_period[['Username', kills_value_col, kills_count_col]]
            df_killers_display[kills_value_col] = df_killers_display[kills_value_col].apply(lambda x: f"{int(x):,} gp")
            df_killers_display.rename(columns={'Username':'Player', kills_value_col: 'Value from Kills', kills_count_col: 'Kills'}, inplace=True)
            st.dataframe(df_killers_display, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Top 'Sitters' (The Losers)")
        df_deathers_period = df_deaths[df_deaths[deaths_count_col] > 0].sort_values(by=deaths_count_col, ascending=False)
        if df_deathers_period.empty:
            st.info("No deaths recorded for this period.")
        else:
            df_deathers_display = df_deathers_period[['Username', deaths_value_col, deaths_count_col]]
            df_deathers_display[deaths_value_col] = df_deathers_display[deaths_value_col].apply(lambda x: f"{int(x):,} gp")
            df_deathers_display.rename(columns={'Username':'Player', deaths_value_col: 'Value Lost', deaths_count_col: 'Deaths'}, inplace=True)
            st.dataframe(df_deathers_display, use_container_width=True, hide_index=True)
