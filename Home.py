# dashboard/Home.py
# Main landing page for the Streamlit application.

import streamlit as st

# --- Page Configuration ---
# This should be the first Streamlit command in your app.
st.set_page_config(
    page_title="OSRS Clan Dashboard",
    page_icon="⚔️",
    layout="wide"
)

# --- Main "Home" Page ---
st.title("⚔️ OSRS Clan Reporter Dashboard")
st.markdown("Welcome to the clan's activity and achievement dashboard. Use the sidebar navigation on the left to view specific reports.")
st.info("💡 **Tip:** This dashboard connects directly to the clan's pre-processed database, so the data is always fast and up-to-date.", icon="💡")

st.markdown("---")

st.header("How This Works")
st.markdown("""
This dashboard is the front-end viewer for a complete ETL (Extract, Transform, Load) pipeline.

1.  **Extract & Parse**: A backend process fetches data from Discord, parses it, and stores it in a structured format.
2.  **Transform**: A daily script reads the parsed data and pre-calculates all the statistics, leaderboards, and summaries you see on these pages. This makes the dashboard extremely fast, as it doesn't need to perform heavy calculations.
3.  **Load & View**: The final summary tables are loaded into a production database, which this Streamlit app reads from.

- **Navigation**: Use the menu on the left to switch between different reports.
- **Data**: The data is cached for performance but is refreshed every 10 minutes to ensure you're seeing the latest information from the last pipeline run.
""")
