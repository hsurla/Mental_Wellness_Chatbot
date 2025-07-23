import streamlit as st
from streamlit_oauth import OAuth2Component
import os

# Google OAuth2 credentials
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"

oauth = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

redirect_uri = "http://localhost:8501"

# Dummy user database for email/password (for example/demo only)
dummy_users = {
    "user@example.com": "password123",
    "test@wellness.com": "mental123"
}

def login_page():
    st.title("🧠 Mental Wellness Chatbot Login")

    if "user" not in st.session_state:
        st.session_state.user = None
    if "forgot_mode" not in st.session_state:
        st.session_state.forgot_mode = False

    # ✅ Already logged in
    if st.session_state.user:
        st.success(f"✅ Logged in as {st.session_state.user['email']}")
        return True

    # 🔐 Forgot Password Mode
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

    # 🔵 Google OAuth Login
    st.subheader("Login with Google")
    token = oauth.authorize_button(
        name="Continue with Google",
        icon="🌐",
        redirect_uri=redirect_uri,
        scope="openid email profile",
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

    # 🔶 Manual Email/Password Login
    st.subheader("Or login manually")

    with st.form("manual_login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        if email in dummy_users and dummy_users[email] == password:
            st.success(f"✅ Logged in as {email}")
            st.session_state.user = {"email": email, "method": "manual"}
            return True
        else:
            st.error("Invalid email or password.")

    # Forgot password link
    st.markdown("🔒 Forgot your password?")
    if st.button("Reset via Email"):
        st.session_state.forgot_mode = True

    return False
