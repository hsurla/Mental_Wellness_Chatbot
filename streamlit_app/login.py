# streamlit_app/login.py

import streamlit as st
import requests
import bcrypt
from urllib.parse import urlencode
from database.database import find_user, add_user

# Google OAuth2 credentials
CLIENT_ID ="639432204726-af4d4q5v8a82cs67uo33djmhdgqujsf1.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"  # Or your deployed Streamlit URL

def login_page():
    # Step 1: Handle Google OAuth2 redirect
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
                st.success(f"✅ Logged in as: {email}")
                st.session_state["username"] = email
                st.session_state["logged_in"] = True

                if not find_user(email):
                    add_user(email, "")  # Register Google user with blank password

                return  # Skip showing the manual login form
            else:
                st.error("❌ Failed to retrieve user info.")
                return
        else:
            st.error("❌ Failed to get access token.")
            return

    # Step 2: Google Sign-In Button (if not logged in via redirect)
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

    # Step 3: Manual Login Section
    st.title("Login with Username and Password")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Step 4: Google reCAPTCHA
    st.components.v1.html("""
    <html>
      <head>
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
      </head>
      <body>
        <form action="?" method="POST">
          <div class="g-recaptcha" data-sitekey="6LcSOU4rAAAAAGphyafMH1TIE7TuoGiaMB9GKwAP"></div>
          <br/>
        </form>
      </body>
    </html>
""", height=150)

    recaptcha_token = st.query_params.get("g-recaptcha-response", [None])[0]

    if not recaptcha_token:
        st.warning("Please complete the reCAPTCHA.")
        return

    recaptcha_secret = "6LcSOU4rAAAAAFTf5LUY429GMWEC1m3egehwsUs8"
    recaptcha_response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": recaptcha_secret, "response": recaptcha_token}
    ).json()

    if not recaptcha_response.get("success"):
        st.error("reCAPTCHA verification failed.")
        return

    # Step 5: Handle manual login
    if st.button("Login"):
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
