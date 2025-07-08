# streamlit_app/login.py

import streamlit as st
import requests
import bcrypt
from streamlit_oauth import OAuth2Component
from database.database import find_user, add_user

# 🔐 Replace with your actual credentials
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # or your hosted domain

# Set up OAuth2 for Google
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    redirect_uri=REDIRECT_URI,
)

def login_page():
    if st.session_state.get("logged_in"):
        st.success(f"✅ Logged in as {st.session_state['username']}")
        return

    st.markdown("### 🔐 Login with Google")
    result = oauth2.authorize_button(
        name="Continue with Google",
        icon="🌐",
        scopes=["openid", "email", "profile"],
        use_container_width=True
    )

    if result and "token" in result:
        # Get user info from Google
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {result['token']['access_token']}"}
        )
        if userinfo_response.status_code == 200:
            user_info = userinfo_response.json()
            email = user_info["email"]
            st.session_state["username"] = email
            st.session_state["logged_in"] = True
            st.session_state["show_login_badge"] = True

            # If first time, add user to DB with empty password
            if not find_user(email):
                add_user(email, "")

            st.rerun()
        else:
            st.error("❌ Failed to retrieve user info from Google.")

    st.markdown("---")

    # Optional manual login fallback
    st.title("Manual Login")
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = find_user(username)
            if user:
                if bcrypt.checkpw(password.encode(), user["password"].encode()):
                    st.session_state["username"] = username
                    st.session_state["logged_in"] = True
                    st.session_state["show_login_badge"] = True
                    st.success(f"✅ Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")
