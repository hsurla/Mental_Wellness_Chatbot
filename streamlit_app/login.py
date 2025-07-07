import streamlit as st
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript
import requests

CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"  # 🔁 Replace this with your actual Google client ID

def login_page():
    st.markdown("## 🔐 Login with Google")
    st.write("Please sign in to access your Mental Wellness Chatbot.")

    # HTML + JS for Google popup login
    html_code = f"""
    <div id="g_id_onload"
         data-client_id="{CLIENT_ID}"
         data-context="signin"
         data-ux_mode="popup"
         data-callback="handleCredentialResponse"
         data-auto_prompt="false">
    </div>
    <div class="g_id_signin"
         data-type="standard"
         data-shape="rectangular"
         data-theme="outline"
         data-text="sign_in_with"
         data-size="large"
         data-logo_alignment="left">
    </div>
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <script>
        function handleCredentialResponse(response) {{
            const token = response.credential;
            const iframe = parent.document.querySelector('iframe[title="streamlit_app"]');
            iframe.contentWindow.postMessage({{ type: "credential", token: token }}, "*");
        }}
    </script>
    """
    html(html_code, height=300)

    # JavaScript listener
    result = st_javascript("""
    window.token = null;
    window.addEventListener("message", (event) => {
        if (event.data.type === "credential") {
            window.token = event.data.token;
        }
    });
    window.token;
    """)

    # Token received, verify it with Google
    if result:
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={result}")
        if response.status_code == 200:
            info = response.json()
            st.session_state["username"] = info["email"]
            st.session_state["logged_in"] = True
            st.session_state["show_login_badge"] = True
            st.success(f"✅ Logged in as {info['email']}")
            st.rerun()
        else:
            st.error("❌ Invalid Google token. Please try again.")

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