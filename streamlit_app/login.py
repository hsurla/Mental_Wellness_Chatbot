import streamlit as st
import requests
import bcrypt
from streamlit_oauth import OAuth2Component
from database.database import find_user, add_user

# Google OAuth2 credentials
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"

# Initialize OAuth2 component
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

def show_login_success():
    st.balloons()
    st.success("✅ Login successful!")
    st.session_state.show_login_badge = True

def login_page():
    st.markdown("### 🔐 Sign in with Google")

    if "token" not in st.session_state:
        token = oauth2.authorize_button(
            name="Continue with Google",
            redirect_uri=REDIRECT_URI,
            scope=["openid", "email", "profile"],
            access_type="offline",
            prompt="consent"
        )
        if token:
            st.session_state.token = token

    if "token" in st.session_state:
        access_token = st.session_state.token.get("access_token")
        if access_token:
            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                email = user_info["email"]

                st.session_state["username"] = email
                st.session_state["logged_in"] = True

                if not find_user(email):
                    add_user(email, "")  # Register Google user (empty password)

                show_login_success()
                return
            else:
                st.error("❌ Failed to retrieve user info.")
        else:
            st.error("❌ Invalid access token.")

    # Fallback manual login (optional)
    st.markdown("---")
    st.subheader("Or login manually")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = find_user(username)
            if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.success(f"✅ Welcome, {username}!")
                st.session_state["username"] = username
                st.session_state["logged_in"] = True
                show_login_success()
            elif user:
                st.error("Incorrect password.")
            else:
                st.error("User not found.")
