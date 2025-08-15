import streamlit as st
import streamlit.components.v1 as components
from threading import Thread
from werkzeug.serving import make_server
import time
import requests

# Import the server object from your Dash app
# Make sure you have a file named PlotlyMap.py with a Dash app in it
from PlotlyMap import server as dash_server

# Define the host and port for the Dash app
DASH_HOST = '0.0.0.0'
DASH_PORT = 8050

# --- Function to run the Dash app ---
# This function is cached so it only runs once
@st.cache_resource
def run_dash_server():
    """Starts the Dash server in a background thread."""
    thread = Thread(target=make_server(DASH_HOST, DASH_PORT, dash_server).serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(2) # Give the server a moment to start
    return thread

# --- Main Streamlit App ---

# Set the page to a wide layout
st.set_page_config(page_title="Streamlit + Dash Fullscreen", layout="wide")

st.title("Dash App with a Fullscreen Button 🚀")
st.write("The Dash app below is running in the background. Click the button to enter a true fullscreen mode.")


# Start the Dash server in the background
run_dash_server()

# --- MODIFICATION START ---
# We replace the simple iframe with a custom HTML component that includes a fullscreen button.

try:
    # Check if the Dash server is running
    requests.get(f"http://localhost:{DASH_PORT}")

    # Embed the custom HTML component
    components.html(
        f"""
        <style>
            #fullscreen-btn {{
                position: relative;
                z-index: 9999;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-family: sans-serif;
                font-weight: bold;
                margin-bottom: 10px;
                transition: background-color 0.3s;
            }}
            #fullscreen-btn:hover {{
                background-color: #0056b3;
            }}
            #iframe-container {{
                border: 2px solid #e6eaf1;
                border-radius: 8px;
                overflow: hidden; /* Keeps the iframe corners rounded */
            }}
        </style>

        <div>
            <button id="fullscreen-btn">View Fullscreen</button>
            <div id="iframe-container">
                <iframe id="dash-iframe" src="http://localhost:{DASH_PORT}" width="100%" height="800" frameBorder="0" allowfullscreen></iframe>
            </div>
        </div>

        <script>
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            const iframe = document.getElementById('dash-iframe');

            fullscreenBtn.addEventListener('click', function () {{
                if (iframe.requestFullscreen) {{
                    iframe.requestFullscreen();
                }} else if (iframe.mozRequestFullScreen) {{ /* Firefox */
                    iframe.mozRequestFullScreen();
                }} else if (iframe.webkitRequestFullscreen) {{ /* Chrome, Safari & Opera */
                    iframe.webkitRequestFullscreen();
                }} else if (iframe.msRequestFullscreen) {{ /* IE/Edge */
                    iframe.msRequestFullscreen();
                }}
            }});
        </script>
        """,
        height=900  # Adjust this height to fit your app's initial view
    )

except requests.ConnectionError:
    st.error(f"Failed to connect to the Dash server on port {DASH_PORT}. Please make sure it has started correctly.")

# --- MODIFICATION END ---
