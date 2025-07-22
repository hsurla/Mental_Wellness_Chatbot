import streamlit as st
from streamlit_oauth import OAuth2Component
import requests

# Configuration
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
redirect_uri = "http://localhost:8502"

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
