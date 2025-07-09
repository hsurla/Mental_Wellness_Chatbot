import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import requests
import os
from pathlib import Path

# Configuration
CLIENT_ID = "your-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "your-client-secret"
REDIRECT_URI = "http://localhost:8501"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email"]

# Create client_secrets.json
client_secrets = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "redirect_uris": [REDIRECT_URI]
    }
}

def get_google_auth_url():
    flow = Flow.from_client_config(
        client_secrets,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url

def get_user_info(code):
    flow = Flow.from_client_config(
        client_secrets,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    ).json()
    return userinfo

def login_page():
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login to Mental Wellness Chatbot")
    
    # Google OAuth Button
    auth_url = get_google_auth_url()
    st.markdown(f"""
    <a href="{auth_url}" target="_self">
        <button style="
            background-color: #4285F4;
            color: white;
            border: none;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
        ">
        Sign in with Google
        </button>
    </a>
    """, unsafe_allow_html=True)

    # Handle callback
    query_params = st.experimental_get_query_params()
    if 'code' in query_params:
        try:
            user_info = get_user_info(query_params['code'][0])
            st.session_state.user_email = user_info['email']
            st.session_state.logged_in = True
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
    
    return False