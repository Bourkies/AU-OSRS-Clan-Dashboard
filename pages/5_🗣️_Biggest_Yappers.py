# dashboard/pages/5_🗣️_Biggest_Yappers.py
# Refactored to display pre-aggregated chat data.

import streamlit as st
import pandas as pd
import random
import utils
import dashboard_texts as texts

def display_yapper_leaderboard(df, period_suffix, title, messages, icon):
    st.header(title)
    
    count_col = f'Count_{period_suffix}'
    df_period = df[df[count_col] > 0].copy()
    
    if df_period.empty:
        st.info(f"Nobody was yapping about this in the selected period.")
        return

    top_yapper = df_period.sort_values(by=count_col, ascending=False).iloc[0]
    player, count = top_yapper['Username'], int(top_yapper[count_col])
    message = random.choice(messages).format(player=player, count=count)
    st.info(message, icon=icon)

    st.metric(label=f"Top Yappers (by count)", value="")
    leaderboard = df_period[['Username', count_col]].sort_values(by=count_col, ascending=False)
    leaderboard.rename(columns={'Username': 'Player', count_col: 'Count'}, inplace=True)
    st.dataframe(leaderboard, use_container_width=True, hide_index=True)

# --- Main Page Content ---
st.title("🗣️ The Biggest Yappers")
st.markdown("Who's the chattiest in the clan? This page tracks who's saying the important things.")

df_big_gzers = utils.load_table("Big Gzers")
df_111 = utils.load_table("111")
df_cya_hick = utils.load_table("cya hick")

if df_big_gzers.empty and df_111.empty and df_cya_hick.empty:
    st.warning("No chat count data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_suffix = utils.display_time_period_selector(key_prefix="yappers")
    
    col1, col2 = st.columns(2)
    with col1:
        if not df_111.empty:
            display_yapper_leaderboard(df_111, period_suffix, "The Menaces (111)", texts.TOP_YAPPER_MESSAGES, "🗣️")
    with col2:
        if not df_big_gzers.empty:
            display_yapper_leaderboard(df_big_gzers, period_suffix, "The GZers (gz)", texts.TOP_GZER_MESSAGES, "🎉")

    st.markdown("---")
    if not df_cya_hick.empty:
        display_yapper_leaderboard(df_cya_hick, period_suffix, "The 'cya hick' Crew", ["{player} said it {count} times."], "👋")

