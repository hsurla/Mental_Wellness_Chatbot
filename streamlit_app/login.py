# streamlit_app/login.py
import streamlit as st
from streamlit_oauth import OAuth2Component
import requests

# Google OAuth2 Configuration
client_id = "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
client_secret = "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"
auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
redirect_uri = "http://localhost:8501"  # Must exactly match your Google Cloud Console

# Initialize OAuth2 component
oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint=auth_url,
    token_endpoint=token_url
)

# Dummy local credentials (for manual login)
USER_CREDENTIALS = {
    "demo_user": "demo_pass"
}

def login_page():
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")

    # --- Manual Login Form ---
    with st.form("manual_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state.user_email = f"{username}@localapp"
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown("---")
    st.subheader("Or sign in with Google")

    # --- Google OAuth2 Button ---
    token = oauth2.authorize_button(
        name="Continue with Google",
        redirect_uri=redirect_uri,
        scope="openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    )

    # --- Token Handling ---
    if token:
        st.warning("OAuth token response:")
        st.json(token)  # For debugging

        # ✅ Access nested token
        if 'token' in token and 'access_token' in token['token']:
            access_token = token['token']['access_token']

            # Get user info from Google
            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            if "email" in userinfo:
                st.session_state.user_email = userinfo["email"]
                st.success(f"Logged in as {userinfo['email']}")
                st.rerun()
            else:
                st.error("Failed to fetch user info from Google.")
        else:
            st.error("Google login failed: No access_token returned.")
            if "error" in token:
                st.error(f"OAuth Error: {token['error']}")

    return False
