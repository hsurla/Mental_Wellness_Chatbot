import streamlit as st
import requests
import bcrypt
from streamlit_oauth import OAuth2Component
from database.database import find_user, add_user

# ---- Google OAuth2 Setup ----
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Update this if hosted remotely

oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

def show_login_success(username):
    st.balloons()
    st.session_state["username"] = username
    st.session_state["logged_in"] = True
    st.session_state["show_login_badge"] = True
    st.experimental_rerun()


def login_page():
    if st.session_state.get("logged_in"):
        st.success("✅ Already logged in.")
        return

    st.title("Login to Mental Wellness Chatbot")

    # ---- Google Sign-In ----
    st.markdown("### 🔐 Sign in with Google")
    token = oauth2.authorize_button(
        name="Continue with Google",
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
        access_type="offline",
        prompt="consent"
    )

    if token and token.get("access_token"):
        access_token = token["access_token"]

        # Get user info
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code == 200:
            user_info = userinfo_response.json()
            email = user_info.get("email")

            # Store new user if not found
            if not find_user(email):
                add_user(email, "")  # Register Google user with empty password

            show_login_success(email)
            return
        else:
            st.error("❌ Failed to retrieve user info.")

    st.markdown("---")

    # ---- Manual Login ----
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
