import streamlit as st
from extra_streamlit_components import OAuth2Component
import requests
import os
import base64

# Initialize OAuth2Component with correct parameters
oauth2 = OAuth2Component(
    client_id="95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com",
    client_secret="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",
    authroize_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://accounts.google.com/o/oauth2/token",
    refresh_token_url="https://accounts.google.com/o/oauth2/token",
    revoke_token_url="https://accounts.google.com/o/oauth2/revoke",
    scope="openid email profile"
)

def login_page():
    if st.session_state.get("logged_in"):
        st.success(f"Already logged in as {st.session_state['username']}")
        return

    st.title("Login to Mental Wellness Chatbot")

    # Google OAuth Button
    result = oauth2.authorize_button(
        name="Continue with Google",
        redirect_uri="http://localhost:8501",  # Must match your Google Cloud Console settings
        scope="openid email profile",
        key="google"
    )

    if result:
        # Get user info from Google
        id_token = result.get("token").get("id_token")
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {result.get('token').get('access_token')}"}
        )
        
        if userinfo_response.status_code == 200:
            user_info = userinfo_response.json()
            email = user_info.get("email")
            st.session_state["username"] = email
            st.session_state["logged_in"] = True
            st.success(f"Logged in as {email}")
            st.rerun()

    # Manual login fallback
    st.markdown("---")
    st.subheader("Or login manually")
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # Your existing manual login logic here
            pass