# dashboard/pages/4_🐍_Stolen_Whips.py
# Refactored to display pre-aggregated data.

import streamlit as st
import pandas as pd
import utils
import dashboard_texts as texts

st.title("🐍 Stolen Whips Leaderboard")
st.markdown(f"All whips belong to **{texts.WHIP_QUEEN}**. This page tracks all whips stolen by other clan members.")

df_whips = utils.load_table("stolen_whips_summary")

if df_whips.empty:
    st.warning("No whip data could be loaded. The ETL pipeline may not have run yet.")
else:
    period_suffix = utils.display_time_period_selector(key_prefix="whips")
    
    count_col = f'Whips_Stolen_{period_suffix}' if period_suffix != "All_Time" else 'Whips_Stolen_All_Time'
    value_col = f'Total_Value_{period_suffix}'
    
    df_period = df_whips[df_whips[count_col] > 0].copy()
    
    st.header("State of the Whips")
    
    queen_stats = df_whips[df_whips['Username'] == texts.WHIP_QUEEN]
    queen_count = int(queen_stats[count_col].sum()) if not queen_stats.empty else 0

    thieves_df = df_period[df_period['Username'] != texts.WHIP_QUEEN]
    total_stolen = int(thieves_df[count_col].sum())
    top_thief_series = thieves_df.sort_values(by=count_col, ascending=False)
    top_thief = top_thief_series.iloc[0]['Username'] if not top_thief_series.empty else "nobody"

    shame_message = texts.WHIP_SHAME_MESSAGE.format(
        queen=texts.WHIP_QUEEN, queen_count=queen_count,
        total_stolen=total_stolen, top_thief=top_thief
    )
    st.info(shame_message, icon="👑")
    st.markdown("---")

    st.header("The Thieves")
    if thieves_df.empty:
        st.success("No whips have been stolen in this period. All is right with the world.")
    else:
        thieves_display = thieves_df[['Username', count_col, value_col]].sort_values(by=count_col, ascending=False)
        thieves_display[value_col] = thieves_display[value_col].apply(lambda x: f"{int(x):,} gp")
        thieves_display.rename(columns={'Username': 'Player', count_col: 'Whips Stolen', value_col: 'Total Value'}, inplace=True)
        st.dataframe(thieves_display, use_container_width=True, hide_index=True)