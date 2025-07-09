import streamlit as st
import requests
import bcrypt
from database.database import find_user, add_user

# ---- Google OAuth2 Setup ----
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Or your deployed Streamlit URL

from requests_oauthlib import OAuth2Session

# OAuth2 Config
CLIENT_ID = "your_client_id"
AUTHORIZE_URL = "https://provider.com/oauth2/authorize"
TOKEN_URL = "https://provider.com/oauth2/token"
REDIRECT_URI = "http://localhost:8501"  # Must match provider settings
SCOPE = ["openid", "email", "profile"]

oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
auth_url, _ = oauth.authorization_url(AUTHORIZE_URL)

st.markdown(f"[Login Here]({auth_url})")

result = oauth2.authorize_button("Login with Provider")
if result:
    st.write("Token:", result.get('token'))

def show_login_success(username):
    st.balloons()
    st.session_state["username"] = username
    st.session_state["logged_in"] = True
    st.session_state["show_login_badge"] = True
    st.success(f"✅ Logged in as {username}")
    st.rerun()

def login_page():
    if st.session_state.get("logged_in"):
        st.success(f"✅ Already logged in as {st.session_state['username']}")
        return

    st.title("Login to Mental Wellness Chatbot")

    # ---- Google OAuth Button ----
    st.subheader("🔐 Sign in with Google")

    token = oauth2.authorize_button(
        name="Continue with Google",
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
        access_type="offline",
        prompt="consent"
    )

    if token and token.get("access_token"):
        access_token = token["access_token"]
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_response.status_code == 200:
            user_info = userinfo_response.json()
            email = user_info.get("email")

            # Register Google user if not already in DB
            if not find_user(email):
                add_user(email, "")  # Empty password

            show_login_success(email)
            return
        else:
            st.error("❌ Failed to retrieve user info.")

    # ---- Manual login fallback ----
    st.markdown("---")
    st.subheader("👤 Or login manually")

    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = find_user(username)
            if user:
                if bcrypt.checkpw(password.encode(), user["password"].encode()):
                    show_login_success(username)
                else:
                    st.error("❌ Incorrect password.")
            else:
                st.error("❌ User not found.")
