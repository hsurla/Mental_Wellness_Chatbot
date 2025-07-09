import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests

# Configuration (REPLACE WITH YOURS)
CLIENT_ID = "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Must match Google Console

# Dummy credentials (for demo purposes only – replace with secure auth in production)
USER_CREDENTIALS = {
    "demo_user": "demo_pass"
}

def login_page():
    if 'user_email' in st.session_state:
        return True

    st.subheader("🔐 Manual Sign-In")

    # Manual Login Form
    with st.form("manual_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state.user_email = f"{username}@localapp"
                st.success(f"Logged in as {username}")
                st.rerun()
                return True
            else:
                st.error("Invalid username or password")

    st.markdown("---")

    # Google Sign-In
    st.subheader("🔓 Or sign in with Google")

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

    params = st.query_params
    if 'code' not in params:
        auth_url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            include_granted_scopes="true"
        )
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

    # Handle Google OAuth callback
    try:
        code = params['code']
        flow.fetch_token(code=code)

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
            st.error("Failed to fetch user info from Google.")
            return False

    except Exception as e:
        st.error(f"Google Login failed: {e}")
        return False
