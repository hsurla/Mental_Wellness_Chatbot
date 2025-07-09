import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests
import os
from pathlib import Path

# Configuration - MUST REPLACE WITH YOUR VALUES
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email"]

# Create client_secrets.json if not exists
if not Path("client_secrets.json").exists():
    with open("client_secrets.json", "w") as f:
        f.write(f"""{{
            "web": {{
                "client_id": "{CLIENT_ID}",
                "client_secret": "{CLIENT_SECRET}",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "redirect_uris": ["{REDIRECT_URI}"]
            }}
        }}""")

def get_google_auth_url():
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['openid', 'emial', 'profile' ],
        redirect_uri=REDIRECT_URI
    )
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    return authorization_url

def login_page():
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")
    
    auth_url = get_google_auth_url()
    st.markdown(f"""
    <a href="{auth_url}">
        <button style="
            background: #4285F4;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        ">
        Sign in with Google
        </button>
    </a>
    """, unsafe_allow_html=True)

    if 'code' in st.experimental_get_query_params():
        code = st.experimental_get_query_params()['code'][0]
        try:
            flow = Flow.from_client_secrets_file(
                'client_secrets.json',
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            flow.fetch_token(code=code)
            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {flow.credentials.token}"}
            ).json()
            st.session_state.user_email = userinfo['email']
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
    
    return False