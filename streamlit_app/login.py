import streamlit as st
from streamlit_oauth import OAuth2Component
import requests

# Configuration
client_id = "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
client_secret = "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"
auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
redirect_uri = "http://localhost:8501"

# Initialize
oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint=auth_url,
    token_endpoint=token_url
)

USER_CREDENTIALS = {
    "demo_user": "demo_pass"
}

def login_page():
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")

    # Manual login
    with st.form("manual_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Forgot password section (hidden by default)
        if st.session_state.get("show_forgot_password", False):
            st.markdown("---")
            st.subheader("🔒 Password Recovery")
            recovery_email = st.text_input("Enter your email")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Send Reset Link"):
                    # Mock password reset functionality
                    st.success(f"Reset link sent to {recovery_email} (demo)")
                    st.session_state.show_forgot_password = False
            with col2:
                if st.button("Cancel"):
                    st.session_state.show_forgot_password = False
        else:
            # Forgot password link
            st.markdown(
                """<div style="text-align: right; margin-top: -15px;">
                <a href="#" onclick="window.streamlitSessionState.set('show_forgot_password', true); return false;">
                Forgot password?</a></div>""",
                unsafe_allow_html=True
            )
        
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state.user_email = f"{username}@local"
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown("---")
    st.subheader("Or sign in with Google")

    # Display styled wrapper
    st.markdown("""
        <style>
        .google-button-container button {
            background-color: #111 !important;
            color: white !important;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            border: 1px solid #555;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .forgot-password-link {
            color: #888;
            font-size: 0.9em;
            cursor: pointer;
        }
        </style>
        <div class="google-button-container">
    """, unsafe_allow_html=True)

    # Place OAuth2 button inside styled container
    token = oauth2.authorize_button(
        name="Log in with Google",
        redirect_uri=redirect_uri,
        scope="openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if token:
        if 'token' in token and 'access_token' in token['token']:
            access_token = token['token']['access_token']
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
            st.error("Google login failed.")
            if "error" in token:
                st.error(f"OAuth Error: {token['error']}")

    return False