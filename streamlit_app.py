import streamlit as st
import subprocess
from time import sleep

# Define the port your Dash app will run on
DASH_PORT = 8050

# Use st.cache_resource to run this function only once.
@st.cache_resource
def start_dash_app():
    # Use gunicorn to run the Dash app
    # 'dash_app:server' refers to the 'server' variable in your 'dash_app.py'
    process = subprocess.Popen(
        ["gunicorn", "PlotlyMap:server", f"--bind=0.0.0.0:{DASH_PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    st.write("Dash App Started!")
    # Give the app a moment to start
    sleep(5)
    return process

# --- Main Streamlit App ---

st.set_page_config(layout="wide")


# Start the Dash app
dash_process = start_dash_app()

st.write(f"It's running in the background and served at http://localhost:{DASH_PORT}")

st.components.v1.iframe(f"http://localhost:{DASH_PORT}")

st.info("This Streamlit app is the 'parent' that launched the Dash app.")