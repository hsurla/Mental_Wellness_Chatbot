# login.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests

# Configuration (REPLACE WITH YOURS)
CLIENT_ID = "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Must exactly match what you set in Google Cloud Console

def login_page():
    if 'user_email' in st.session_state:
        return True

    # Initialize OAuth2 Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        redirect_uri=REDIRECT_URI
    )

    # Step 1: Show Login Button
    params = st.experimental_get_query_params()
    if 'code' not in params:
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
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

    # Step 2: Handle Google Callback
    try:
        code = params['code'][0]
        flow.fetch_token(code=code)

        # Get user info from Google
        token = flow.credentials.token
        userinfo_resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )

        if userinfo_resp.status_code == 200:
            userinfo = userinfo_resp.json()
            st.session_state.user_email = userinfo.get("email")
            st.rerun()
            return True
        else:
            st.error("Failed to fetch user info.")
            return False

    except Exception as e:
        st.error(f"Login failed: {e}")
        return False
