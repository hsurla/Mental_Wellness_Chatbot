# streamlit_app/login.py

import streamlit as st
import requests
import bcrypt
from urllib.parse import urlencode
from streamlit.components.v1 import html
from database.database import find_user, add_user

# Google OAuth2 credentials
CLIENT_ID ="Client :95879444252-71052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "Client secret :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"
REDIRECT_URI = "http://localhost:8501"  # Or your deployed Streamlit URL

def show_login_success():
    """Show login success animation and redirect to chat page"""
    st.balloons()
    st.success("✅ Login successful!")

    # Redirect using JavaScript
    js_redirect = """
    <script>
        setTimeout(function() {
            window.location.href = window.location.origin;
        }, 1000);
    </script>
    """
    st.markdown(js_redirect, unsafe_allow_html=True)

def login_page():
    # Check if already logged in
    if st.session_state.get("logged_in"):
        show_login_success()
        return
    
    code = st.query_params.get("code")
    if code:
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        if token_response.status_code == 200:
            tokens = token_response.json()
            access_token = tokens.get("access_token")

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
                    add_user(email, "")  # Register Google user with blank password

                
                show_login_success()
                return  # Skip showing the manual login form
            else:
                st.error("❌ Failed to retrieve user info.")
        else:
            st.error("❌ Failed to get access token.")

    # Google Sign-In Button (if not logged in via redirect)
    st.markdown("### 🔐 Sign in with Google")
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    google_login_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    st.markdown(f"[👉 Click here to Sign in with Google]({google_login_url})")

    #Manual Login Section
    st.title("Login")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = find_user(username)
            if user:
                if bcrypt.checkpw(password.encode(), user["password"].encode()):
                    st.success(f"✅ Welcome, {username}!")
                    st.session_state["username"] = username
                    st.session_state["logged_in"] = True
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")