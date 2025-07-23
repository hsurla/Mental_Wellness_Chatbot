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

# Mock user database
USER_CREDENTIALS = {
    "demo_user": {
        "password": "demo_pass",
        "email": "user@example.com",
        "reset_tokens": {}
    }
}

RESET_TOKENS = {}

def generate_reset_token(email):
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=1)
    RESET_TOKENS[token] = {
        "email": email,
        "expires": expires
    }
    return token

def send_reset_email(email, token):
    reset_link = f"{REDIRECT_URI}?token={token}"
    print(f"[DEMO] Password reset link for {email}: {reset_link}")

def show_forgot_password():
    with st.form("forgot_password_form"):
        st.subheader("🔒 Reset Your Password")
        email = st.text_input("Enter your registered email")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("Send Reset Link")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_forgot_password = False
                st.rerun()
        
        if submit and email:
            user_exists = any(user["email"] == email for user in USER_CREDENTIALS.values())
            if user_exists:
                token = generate_reset_token(email)
                send_reset_email(email, token)
                st.success(f"Reset link sent to {email} (check console for demo link)")
                st.session_state.show_forgot_password = False
                st.rerun()
            else:
                st.error("No account found with that email")

def handle_password_reset():
    # Updated to use st.query_params instead of st.experimental_get_query_params
    if "token" in st.query_params:
        token = st.query_params["token"]
        
        if token in RESET_TOKENS:
            if datetime.now() < RESET_TOKENS[token]["expires"]:
                email = RESET_TOKENS[token]["email"]
                
                with st.form("reset_password_form"):
                    st.subheader("🔄 Create New Password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    
                    if st.form_submit_button("Update Password"):
                        if new_password == confirm_password:
                            for username, data in USER_CREDENTIALS.items():
                                if data["email"] == email:
                                    USER_CREDENTIALS[username]["password"] = new_password
                                    break
                            
                            del RESET_TOKENS[token]
                            st.success("Password updated successfully! Please login.")
                            st.session_state.password_reset_done = True
                            st.rerun()
                        else:
                            st.error("Passwords don't match")
            else:
                st.error("Reset link has expired")
                del RESET_TOKENS[token]
        else:
            st.error("Invalid reset link")

def login_page():
    if not st.session_state.get("password_reset_done", False):
        handle_password_reset()
    
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")

    with st.form("manual_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        st.markdown(
            """<div style="text-align: right; margin-top: -15px;">
            <a href="#" onclick="window.streamlitSessionState.set('show_forgot_password', true); return false;">
            Forgot password?</a></div>""",
            unsafe_allow_html=True
        )
        
        submitted = st.form_submit_button("Login")

        if submitted:
            user = USER_CREDENTIALS.get(username)
            if user and user["password"] == password:
                st.session_state.user_email = user["email"]
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    if st.session_state.get("show_forgot_password", False):
        show_forgot_password()
        return False

    st.markdown("---")
    st.subheader("Or sign in with Google")

    token = oauth2.authorize_button(
        name="Log in with Google",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile"
    )

    if token and "token" in token:
        try:
            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token['token']['access_token']}"}
            ).json()
            
            if "email" in userinfo:
                st.session_state.user_email = userinfo["email"]
                st.success(f"Logged in as {userinfo['email']}")
                st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

    return False