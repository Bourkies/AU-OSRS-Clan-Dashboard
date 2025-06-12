# dashboard/Home.py
# Main landing page for the Streamlit application.

import streamlit as st
import Streamlit_utils
from datetime import datetime, timezone

# --- Page Configuration ---
st.set_page_config(
    page_title="AU OSRS Dashboard",
    page_icon="🇦🇺",
    layout="wide"
)

# --- Main "Home" Page ---
st.title("🇦🇺 AU OSRS Clan Dashboard 🇦🇺")

# --- Display Last Updated Time ---
last_updated_utc = Streamlit_utils.get_last_updated_timestamp()
if last_updated_utc:
    # Convert to local time for display if desired, otherwise show UTC
    # For this example, we'll display in a user-friendly format in UTC
    last_updated_str = last_updated_utc.strftime('%d %B %Y at %H:%M:%S UTC')
    st.success(f"**Last Updated:** {last_updated_str}", icon="✅")
else:
    st.warning("Last updated time not available. The ETL pipeline may not have run yet.", icon="⚠️")

st.info("**This is a preview**, some data maybe incorrect or fail to display. This project is a work in progress!", icon="💡")
st.markdown("Welcome to the official activity and achievement dashboard for the AU OSRS clan.")
st.markdown("---")

# Use columns to center and constrain the image width
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Using a placeholder as the original image is not available
    st.image("AU_OSRS_Flag.png", use_container_width=True)


st.header("Dashboard Features")
st.markdown("""
This dashboard provides a comprehensive look at our clan's activities, powered by data directly from our Discord server. Here's what you can explore:

- **💰 Valuable Drops:** Track the biggest earners and see who's getting lucky.
- **💀 PvP Leaderboards:** View the top killers and who's been taking a dirt nap in the wilderness.
- **📜 Clan Collection Log:** See our clan's progress on completing the collection log.
- **...and much more!**

Use the sidebar on the left to navigate through the different report pages. The data is updated automatically.
""")

st.header("Clan Links")
st.markdown("""
- **[🔗 Visit our Clan Website](https://www.auosrs.com.au/)**
- **[💬 Join our Discord Server](https://discord.gg/auosrs)**
""")

st.info("**Work In Progress:** This preview is a work in progress! Please contact the admin team to provide feedback or contribute to the project", icon="💡")
