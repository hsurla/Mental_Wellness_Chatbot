# login.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests

# Configuration (REPLACE WITH YOURS)
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Must match Google Console

def login_page():
    if 'user_email' in st.session_state:
        return True

    # Initialize Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=["openid", "email", "profile"],
        redirect_uri=REDIRECT_URI
    )

    # Step 1: Show Login Button
    if 'code' not in st.experimental_get_query_params():
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.markdown(f"""
        <a href="{auth_url}">
            <button style="
                background: #4285F4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            ">Login with Google</button>
        </a>
        """, unsafe_allow_html=True)
        return False

    # Step 2: Handle Callback
    else:
        flow.fetch_token(code=st.experimental_get_query_params()['code'][0])
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {flow.credentials.token}"}
        ).json()
        
        st.session_state.user_email = userinfo['email']
        st.rerun()
        return True