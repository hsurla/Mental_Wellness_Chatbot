import streamlit as st
from streamlit.components.v1 import html
import json

st.set_page_config(page_title="Google Login Example", layout="centered")

st.title("🌐 Google Sign-In Inside Streamlit")

if "user_email" not in st.session_state:
    st.session_state.user_email = None

CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"  # Replace with your actual client ID

# JS + HTML code for Google Sign-In popup
html_code = f"""
<div id="g_id_onload"
     data-client_id="{CLIENT_ID}"
     data-context="signin"
     data-ux_mode="popup"
     data-callback="handleCredentialResponse"
     data-auto_prompt="false">
</div>
<div class="g_id_signin"
     data-type="standard"
     data-shape="rectangular"
     data-theme="outline"
     data-text="sign_in_with"
     data-size="large"
     data-logo_alignment="left">
</div>
<script src="https://accounts.google.com/gsi/client" async defer></script>
<script>
    function handleCredentialResponse(response) {{
        const token = response.credential;
        const iframe = parent.document.querySelector('iframe[title="streamlit_app"]');
        iframe.contentWindow.postMessage({{ type: "credential", token: token }}, "*");
    }}
</script>
"""

html(html_code, height=300)

# Receive Google ID token via Streamlit's JS-message listener
from streamlit_javascript import st_javascript

result = st_javascript("""
window.token = null;
window.addEventListener("message", (event) => {
  if (event.data.type === "credential") {
    window.token = event.data.token;
  }
});
window.token;
""")

if result:
    # Send token to Google's API to verify
    import requests
    google_token_url = "https://oauth2.googleapis.com/tokeninfo"
    response = requests.get(f"{google_token_url}?id_token={result}")
    if response.status_code == 200:
        info = response.json()
        st.session_state.user_email = info["email"]

if st.session_state.user_email:
    st.success(f"✅ Logged in as {st.session_state.user_email}")
    st.write("Now you can proceed to app features...")
