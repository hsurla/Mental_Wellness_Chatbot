import streamlit as st
from streamlit_oauth import OAuth2Component
import os

# Optional: load from .env
# from dotenv import load_dotenv
# load_dotenv()

client_id= "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
client_secret= "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"
# ✅ DO NOT pass `redirect_uri` to OAuth2Component in this version
oauth = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    scope="openid email profile"
)

# Define redirect URI separately (for the authorize_button)
redirect_uri = "http://localhost:8501"  # Or your deployed URL

def login_page():
    st.title("🧠 Mental Wellness Chatbot Login")

    if "user" not in st.session_state:
        st.session_state.user = None
    if "forgot_mode" not in st.session_state:
        st.session_state.forgot_mode = False

    if st.session_state.user:
        st.success(f"✅ Logged in as {st.session_state.user['email']}")
        return True

    if st.session_state.forgot_mode:
        st.subheader("🔐 Forgot Password")
        with st.form("forgot_password_form"):
            forgot_email = st.text_input("Enter your registered email")
            reset_btn = st.form_submit_button("Send Reset Link")
        if reset_btn:
            if forgot_email:
                st.success(f"Password reset link sent to {forgot_email} (simulated).")
                st.session_state.forgot_mode = False
            else:
                st.error("Please enter your email.")
        if st.button("🔙 Back to Login"):
            st.session_state.forgot_mode = False
        return False

    st.subheader("Login using Google")

    # ✅ Pass redirect_uri HERE instead
    token = oauth.authorize_button(
        name="Continue with Google",
        icon="🌐",
        redirect_uri=redirect_uri,
        use_container_width=True
    )

    if token:
        userinfo = oauth.get_user_info(token)
        if userinfo and "email" in userinfo:
            st.session_state.user = userinfo
            st.success(f"✅ Logged in as {userinfo['email']}")
            return True
        else:
            st.error("Login failed. Could not fetch user info.")

    st.markdown("🔒 Forgot your password?")
    if st.button("Reset via Email"):
        st.session_state.forgot_mode = True

    return False
