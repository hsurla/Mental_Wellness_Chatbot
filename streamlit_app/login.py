import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import urllib.parse

# Google OAuth2 Configuration
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
redirect_uri = "http://localhost:8501"  # Must match in Google Cloud Console

# Initialize OAuth2 component
oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint=auth_url,
    token_endpoint=token_url
)

def login_page():
    if "user_email" in st.session_state:
        return True

    st.title("🔐 Login")

    # Manual login
    with st.form("manual_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "admin" and password == "pass":
                st.session_state.user_email = f"{username}@local"
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # Google login section
    st.markdown("---")
    st.subheader("Or login with Google")

    # Step 1: Generate the OAuth login URL
    login_url = (
        f"{auth_url}?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&scope={urllib.parse.quote('openid email profile')}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    # Step 2: Custom-styled button
    st.markdown(f"""
    <style>
        .google-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 10px 16px;
            background-color: transparent;
            color: white;
            font-weight: bold;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            text-decoration: none;
        }}
        .google-btn:hover {{
            background-color: rgba(255,255,255,0.05);
        }}
        .google-btn img {{
            width: 18px;
            height: 18px;
        }}
    </style>
    <div style="text-align: center; margin-top: 10px;">
        <a href="{login_url}" class="google-btn">
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg">
            Log in with Google
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Step 3: Handle redirected token
    token = oauth2.get_access_token(redirect_uri=redirect_uri)
    if token and "access_token" in token:
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token['access_token']}"}
        ).json()

        if "email" in userinfo:
            st.session_state.user_email = userinfo["email"]
            st.success(f"Logged in as {userinfo['email']}")
            st.rerun()
        else:
            st.error("Could not fetch Google user info.")

    return False
