# dashboard/Home.py
# Main landing page for the Streamlit application.

import streamlit as st
import Streamlit_utils
from datetime import datetime
from pathlib import Path
import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from streamlit_js_eval import streamlit_js_eval

current_script_directory = Path(__file__).resolve().parent
image_path = current_script_directory / "AU_OSRS_Flag.png"

# --- Page Configuration ---
st.set_page_config(
    page_title="AU OSRS Dashboard",
    page_icon="🇦🇺",
    layout="wide"
)

# --- Initialize session state for timezone if it doesn't exist ---
if 'user_timezone' not in st.session_state:
    st.session_state.user_timezone = None

# --- Main "Home" Page ---
st.title("🇦🇺 AU OSRS Clan Dashboard 🇦🇺")

# --- Display Data Source and Last Updated Time in Sidebar ---
data_source = os.environ.get("DATA_SOURCE", "Online (Production)")

st.sidebar.title("Dashboard Info")

# --- ADDED: Refresh Button ---
if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()


# This runs only once per session to get the timezone.
if st.session_state.user_timezone is None:
    user_tz_str = streamlit_js_eval(js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone", key="tz_eval")
    if user_tz_str:
        # If we successfully got the timezone, store it and rerun the script
        st.session_state.user_timezone = user_tz_str
        st.rerun()

# Use the stored timezone for display
user_tz_str = st.session_state.user_timezone
last_updated_utc = Streamlit_utils.get_last_updated_timestamp()

if last_updated_utc:
    # Ensure the UTC timestamp is timezone-aware
    if last_updated_utc.tzinfo is None:
        last_updated_utc = last_updated_utc.replace(tzinfo=ZoneInfo("UTC"))
    
    # Format UTC time string first as a fallback
    last_updated_utc_str = last_updated_utc.strftime('%d %b %Y, %H:%M %Z')
    display_timestamp = f"**Last Updated (UTC):** {last_updated_utc_str}"

    # If we have the user's timezone, create a local time string and prepend it
    if user_tz_str:
        try:
            local_tz = ZoneInfo(user_tz_str)
            last_updated_local = last_updated_utc.astimezone(local_tz)
            last_updated_local_str = last_updated_local.strftime('%d %b %Y, %H:%M %Z')
            display_timestamp = (
                f"**Last Updated (Your Time):** {last_updated_local_str}\n\n"
                + display_timestamp
            )
        except ZoneInfoNotFoundError:
            # If the browser timezone isn't recognized, we just show UTC
            pass

    # Display the final timestamp string
    if data_source == 'Online (Production)':
        st.sidebar.success(f"**Data Source:** Online\n\n{display_timestamp}", icon="✅")
    else: # Local (Development)
        st.sidebar.info(f"**Data Source:** Local DB\n\n{display_timestamp}", icon="💻")
else:
    # Fallback message if the timestamp can't be found
    if data_source == 'Online (Production)':
        st.sidebar.warning("Data Source: Online\n\nLast updated time not available.", icon="⚠️")
    else:
        st.sidebar.warning("Data Source: Local DB\n\nCould not read last updated time from `run_metadata` table.", icon="⚠️")

st.sidebar.markdown("---")


st.info("**This is a preview**, some data maybe incorrect or fail to display. This project is a work in progress!", icon="💡")
st.error("TO DO:")
st.markdown("""
- Verify data
- Replace AI place holder text on all pages
- Re order and correct titles on pages
- Other improvements, changes and additions PLEASE SHARE FEED BACK!
- Correctly set the clan clog previous data and group correctly
- Add slider to each page for number of MVP's to display
- last 14 day tables not loading
""")

st.markdown("---")

# Use columns to center and constrain the image width
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
																
    st.image(str(image_path), use_container_width=True)


st.header("Dashboard Features")
st.markdown("""
This dashboard provides a comprehensive look at our clan's activities, powered by data directly from our Discord server. Here's what you can explore:

- **💰 Valuable Drops:** Track the biggest earners and see who's getting lucky.
- **💀 PvP Leaderboards:** View the top killers and who's been taking a dirt nap in the wilderness.
- **📜 Clan Collection Log:** See our clan's progress on completing the collection log.
- **...and much more!**
- **Data refreshed every 15-20 Minutes** To ensure your broadcasts are tracked install the Clan Chat Webhook plugin as per discord pin in chat-logs channel
- **Combine your accounts!** If you want to group your charcters, or peformed a name change and what your data to move to your new name contact the admin team.                        

Use the sidebar on the left to navigate through the different report pages. The data is updated automatically.
""")

st.header("Clan Links")
st.markdown("""
- **[🔗 Visit our Clan Website](https://www.auosrs.com.au/)**
- **[💬 Join our Discord Server](https://discord.gg/auosrs)**
""")

st.info("**Work In Progress:** This preview is a work in progress! Please contact the admin team to provide feedback or contribute to the project", icon="💡")

