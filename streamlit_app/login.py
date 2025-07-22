import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import time

# Google OAuth2 Configuration
client_id = "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
client_secret = "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"
auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
redirect_uri = "http://localhost:8501"

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

    # --- Manual Login Form ---
    with st.form("manual_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state.user_email = f"{username}@localapp"
                st.success("Logged in successfully!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Invalid username or password.")

    # --- Stylish Divider ---
    st.markdown("""<div style="margin: 20px 0; text-align: center;"><hr style="opacity:0.3;"><span style="color:gray;">or</span></div>""", unsafe_allow_html=True)

    # --- Google Styled Login Button ---
    with st.container():
        custom_html = """
        <style>
            .google-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                background-color: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                text-align: center;
                transition: background-color 0.3s;
            }
            .google-btn:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            .google-btn img {
                height: 18px;
            }
        </style>
        <div class="google-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png">
            <span>Log in with Google</span>
        </div>
        """
        st.markdown(custom_html, unsafe_allow_html=True)

        # OAuth2 Button (Invisible to customize placement)
        token = oauth2.authorize_button(
            name=" ",  # name blank so we don't show Streamlit button text
            redirect_uri=redirect_uri,
            scope="openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
        )

    # --- Token Handling ---
    if token and 'token' in token and 'access_token' in token['token']:
        access_token = token['token']['access_token']
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        if "email" in userinfo:
            st.session_state.user_email = userinfo["email"]
            st.toast(f"✅ Logged in as {userinfo['email']}", icon="👤")
            time.sleep(2)
            st.rerun()
        else:
            st.error("Failed to fetch user info.")

    return False
