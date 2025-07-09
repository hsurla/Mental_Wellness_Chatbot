import streamlit as st
import requests
import bcrypt
from database.database import find_user, add_user
from google_auth_oauthlib.flow import Flow
from requests_oauthlib import OAuth2Session

# ---- Google OAuth2 Setup ----
CLIENT_ID = "95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Must match your Google Cloud Console settings
SCOPES = ["openid", "email", "profile"]

def init_google_oauth():
    return Flow.from_client_secrets_file(
        'client_secrets.json',  # You'll need to create this file
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

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

    # ---- Google OAuth Section ----
    st.subheader("🔐 Sign in with Google")
    
    if 'google_auth_code' not in st.session_state:
        flow = init_google_oauth()
        authorization_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Login with Google]({authorization_url})")
        
        st.session_state.google_auth_code = st.text_input("Enter the authorization code from Google:")
        if st.session_state.google_auth_code:
            try:
                flow = init_google_oauth()
                flow.fetch_token(code=st.session_state.google_auth_code)
                credentials = flow.credentials
                
                # Get user info
                userinfo_response = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {credentials.token}"}
                )
                
                if userinfo_response.status_code == 200:
                    user_info = userinfo_response.json()
                    email = user_info.get("email")

                    # Register Google user if not already in DB
                    if not find_user(email):
                        add_user(email, "")  # Empty password for OAuth users

                    show_login_success(email)
                    return
                else:
                    st.error("❌ Failed to retrieve user info from Google.")
            except Exception as e:
                st.error(f"❌ Authentication failed: {str(e)}")

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