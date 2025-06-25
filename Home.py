# dashboard/Home.py
# Main landing page for the Streamlit application.

import streamlit as st
import Streamlit_utils
from datetime import datetime, timezone
from pathlib import Path
import os

current_script_directory = Path(__file__).resolve().parent
image_path = current_script_directory / "AU_OSRS_Flag.png"

# --- Page Configuration ---
st.set_page_config(
    page_title="AU OSRS Dashboard",
    page_icon="🇦🇺",
    layout="wide"
)

# --- Main "Home" Page ---
st.title("🇦🇺 AU OSRS Clan Dashboard 🇦🇺")

# --- Display Data Source and Last Updated Time in Sidebar ---
data_source = os.environ.get("DATA_SOURCE", "Online (Production)")

st.sidebar.title("Dashboard Info")
if data_source == 'Online (Production)':
    last_updated_utc = Streamlit_utils.get_last_updated_timestamp()
    if last_updated_utc:
        last_updated_str = last_updated_utc.strftime('%d %b %Y, %H:%M UTC')
        st.sidebar.success(f"**Data Source:** Online\n\n**Last Updated:** {last_updated_str}", icon="✅")
    else:
        st.sidebar.warning("Data Source: Online\n\nLast updated time not available.", icon="⚠️")
else:
    db_relative_path = st.secrets.get("local_db_path", "data/optimised_data.db")
    local_db_path = Path(__file__).parent.parent / "ETL" / db_relative_path
    db_mod_time_str = "Not found"
    if os.path.exists(local_db_path):
        db_mod_time = os.path.getmtime(local_db_path)
        db_mod_time_str = datetime.fromtimestamp(db_mod_time).strftime('%d %b %Y, %H:%M')

    st.sidebar.info(f"**Data Source:** Local DB\n\n**DB Last Modified:** {db_mod_time_str}", icon="💻")

st.sidebar.markdown("---")


st.info("**This is a preview**, some data maybe incorrect or fail to display. This project is a work in progress!", icon="💡")
st.error("TO DO:")
st.markdown("""
- Verify data
- Replace AI place holder text on all pages
- Re order and correct titles on pages
- Other improvements, changes and additions PLEASE SHARE FEED BACK!
- Remove Duplicate data/Set a date for data collection to start (13/6/25 best day to start)
- Correctly set the clan clog previous data and group correctly
- Fix big H small h issue is ELT pipeline
- Add slider to each page for number of MVP’s to display
""")

st.markdown("---")

# Use columns to center and constrain the image width
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Using a placeholder as the original image is not available
    st.image(str(image_path), use_container_width=True)


st.header("Dashboard Features")
st.markdown("""
This dashboard provides a comprehensive look at our clan's activities, powered by data directly from our Discord server. Here's what you can explore:

- **💰 Valuable Drops:** Track the biggest earners and see who's getting lucky.
- **💀 PvP Leaderboards:** View the top killers and who's been taking a dirt nap in the wilderness.
- **📜 Clan Collection Log:** See our clan's progress on completing the collection log.
- **...and much more!**
- ** Data refreshed every 1-4 Hours** To ensure your broadcasts are tracked install the Clan Chat Webhook plugin as per discord pin in chat-logs channel            

Use the sidebar on the left to navigate through the different report pages. The data is updated automatically.
""")

st.header("Clan Links")
st.markdown("""
- **[🔗 Visit our Clan Website](https://www.auosrs.com.au/)**
- **[💬 Join our Discord Server](https://discord.gg/auosrs)**
""")

st.info("**Work In Progress:** This preview is a work in progress! Please contact the admin team to provide feedback or contribute to the project", icon="💡")

