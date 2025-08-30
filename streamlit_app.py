# streamlit_app.py
import streamlit as st

# --- Configuration ---
# Replace this with the public URL you get after deploying your Dash app to Cloud Run
# Example: "https://my-dash-app-xyz-uc.a.run.app"
DASH_APP_URL = "http://127.0.0.1:8050/"


# --- Main Streamlit App ---

st.set_page_config(layout="wide")

st.title("Streamlit App with Embedded Dash App")
st.write("This Streamlit app embeds a Dash application that is hosted as a separate service on Google Cloud Run.")


# --- Embedding the Dash App ---

if DASH_APP_URL == "https://your-dash-app-url.a.run.app":
    st.warning("Please update the `DASH_APP_URL` variable in the code with the actual URL of your deployed Dash app.")
else:
    st.header("Embedded Dash Application")
    st.write(f"The Dash app is running at: {DASH_APP_URL}")
    # Embed the Dash app using an iframe
    st.components.v1.iframe(DASH_APP_URL, height=800)

st.info("This Streamlit app and the embedded Dash app are running as two separate, independent services on Google Cloud Run.")
