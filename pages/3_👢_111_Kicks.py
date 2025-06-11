# dashboard/pages/3_👢_111_Kicks.py
# Refactored to display pre-aggregated kick data.

import streamlit as st
import pandas as pd
import random
import utils
import dashboard_texts as texts

st.title("👢 The '111' Leaderboard")
st.markdown("Who's getting the boot? This page tracks players who have been temporarily '111' kicked from the clan.")

df_kicked = utils.load_table("kicked_by_player_summary")
df_kickers = utils.load_table("kicker_summary")

if df_kicked.empty:
    st.warning("No kick data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_suffix = utils.display_time_period_selector(key_prefix="kicks")
    
    kicked_count_col = f'Times_Kicked_{period_suffix}' if period_suffix != "All_Time" else 'Times_Kicked_All_Time'
    kicker_count_col = f'Players_Kicked_{period_suffix}' if period_suffix != "All_Time" else 'Players_Kicked_All_Time'
    
    df_kicked_period = df_kicked[df_kicked[kicked_count_col] > 0]
    df_kickers_period = df_kickers[df_kickers[kicker_count_col] > 0] if not df_kickers.empty else pd.DataFrame()
    
    st.header("Hall of Infamy")
    if df_kicked_period.empty:
        st.info("It was a peaceful time... no one was kicked in this period.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            most_kicked_player = df_kicked_period.sort_values(by=kicked_count_col, ascending=False).iloc[0]
            player, count = most_kicked_player['Username'], int(most_kicked_player[kicked_count_col])
            message = random.choice(texts.TOP_KICKED_MESSAGES).format(player=player, count=count)
            st.info(message, icon="👢")

        with col2:
            if not df_kickers_period.empty:
                fastest_finger = df_kickers_period.sort_values(by=kicker_count_col, ascending=False).iloc[0]
                admin, count = fastest_finger['Admin'], int(fastest_finger[kicker_count_col])
                message = random.choice(texts.FASTEST_FINGER_MESSAGES).format(player=admin, count=count)
                st.info(message, icon="🔫")
    st.markdown("---")

    st.header("Leaderboards")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Top Most Kicked Players", value="")
        df_kicked_display = df_kicked_period[['Username', kicked_count_col]].sort_values(by=kicked_count_col, ascending=False)
        df_kicked_display.rename(columns={kicked_count_col: 'Times Kicked'}, inplace=True)
        st.dataframe(df_kicked_display, use_container_width=True, hide_index=True)

    with col2:
        st.metric(label="Top Most Trigger-Happy Admins", value="")
        if not df_kickers_period.empty:
            df_kickers_display = df_kickers_period[['Admin', kicker_count_col]].sort_values(by=kicker_count_col, ascending=False)
            df_kickers_display.rename(columns={kicker_count_col: 'Players Kicked'}, inplace=True)
            st.dataframe(df_kickers_display, use_container_width=True, hide_index=True)
        else:
            st.info("No admins kicked anyone this period.")