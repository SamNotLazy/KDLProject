# streamlit_app.py
import streamlit as st
import streamlit.components.v1 as components

# --- Page Configuration ---
# Set the page to a wide layout to give the Dash app maximum space.
# This is the only "UI" configuration needed from the Streamlit side.
st.set_page_config(
    page_title="Dash App Viewer",
    layout="wide"
)

# --- Important Notes on Running ---
# This Streamlit script acts as a simple, barebones container.
# It does not have any of its own UI elements.
#
# To run this setup:
# 1. Run your Dash app in one terminal (e.g., `python your_dash_app.py`).
# 2. Run this Streamlit app in a second terminal (`streamlit run streamlit_app.py`).
#
# To "tear down" or stop, simply stop both terminal processes (Ctrl+C).
# Rerunning this Streamlit script will just reload the iframe; it doesn't need
# complex teardown logic because the Dash app is a separate, independent process.

# --- Embedded Dash App ---

# The URL where your Dash app is being served.
# Make sure this port matches the one your Dash app is running on.
DASH_APP_URL = "http://127.0.0.1:8050"

# Use streamlit.components.v1.iframe to embed the Dash app.
# The height is set to a large value to fill most of the vertical space.
# You can adjust this value based on your Dash app's content.
try:
    components.iframe(DASH_APP_URL, height=1000, scrolling=True)
except Exception as e:
    # If the Dash app is not running, display an error message.
    st.error(f"Could not connect to the Dash app. Please ensure it's running at {DASH_APP_URL}.")
    st.error(f"Details: {e}")
