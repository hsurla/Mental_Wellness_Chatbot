import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import secrets
from datetime import datetime, timedelta

CLIENT_ID = "95879444252-7t052beum9527nbj32qbcan2h8i1caan.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501"
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# Initialize OAuth
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTH_URL,
    token_endpoint=TOKEN_URL
)

# User database (in production, use a real database)
USERS_DB = {
    "demo_user": {
        "password": "demo_pass",
        "email": "demo@example.com",
        "verified": True
    }
}

# Password reset tokens (in production, use a database)
RESET_TOKENS = {}

def generate_reset_token(email):
    """Create a secure token with expiration"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    RESET_TOKENS[token] = {
        "email": email,
        "expires_at": expires_at
    }
    return token

def send_password_reset_email(email, token):
    """Mock email sending function"""
    reset_link = f"{REDIRECT_URI}?token={token}"
    print(f"Password reset link for {email}: {reset_link}")
    # In production, implement real email sending here
    # using smtplib or a service like SendGrid

def show_forgot_password_form():
    """Display the forgot password form"""
    with st.form("forgot_password_form"):
        st.subheader("🔒 Password Recovery")
        email = st.text_input("Enter your email address")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Send Reset Link")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_forgot_password = False
                st.rerun()
        
        if submit and email:
            # Check if email exists in database
            user_exists = any(user["email"] == email for user in USERS_DB.values())
            
            if user_exists:
                token = generate_reset_token(email)
                send_password_reset_email(email, token)
                st.success("Password reset link sent! Check your email.")
                st.session_state.show_forgot_password = False
                st.rerun()
            else:
                st.error("No account found with this email")

def handle_password_reset():
    """Process password reset from URL token"""
    if "token" in st.query_params:
        token = st.query_params["token"]
        
        if token in RESET_TOKENS:
            token_data = RESET_TOKENS[token]
            
            if datetime.now() < token_data["expires_at"]:
                email = token_data["email"]
                
                with st.form("reset_password_form"):
                    st.subheader("🔄 Reset Your Password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    
                    if st.form_submit_button("Update Password"):
                        if new_password == confirm_password:
                            # Update password in database
                            for username, user_data in USERS_DB.items():
                                if user_data["email"] == email:
                                    USERS_DB[username]["password"] = new_password
                                    break
                            
                            del RESET_TOKENS[token]
                            st.success("Password updated successfully! Please login.")
                            st.session_state.password_reset_done = True
                            st.rerun()
                        else:
                            st.error("Passwords do not match")
            else:
                st.error("Reset link has expired")
                del RESET_TOKENS[token]
        else:
            st.error("Invalid reset link")

def login_page():
    """Main login page with authentication"""
    # Handle password reset if token exists in URL
    if not st.session_state.get("password_reset_done", False):
        handle_password_reset()
    
    # Check if already logged in
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")

    # Manual login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Forgot password link
        st.markdown(
            """<style>
            .forgot-password-link {
                text-align: right;
                margin-top: -15px;
                margin-bottom: 15px;
            }
            </style>
            <div class="forgot-password-link">
                <a href="#" onclick="window.streamlitSessionState.set('show_forgot_password', true); return false;">
                Forgot password?</a>
            </div>""",
            unsafe_allow_html=True
        )
        
        submitted = st.form_submit_button("Login")

        if submitted:
            user = USERS_DB.get(username)
            if user and user["password"] == password:
                st.session_state.user_email = user["email"]
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Show forgot password form if triggered
    if st.session_state.get("show_forgot_password", False):
        show_forgot_password_form()
        return False

    # Google OAuth login
    st.markdown("---")
    st.subheader("Or sign in with Google")

    token = oauth2.authorize_button(
        name="Continue with Google",
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
            st.error(f"Google login failed: {str(e)}")

    return False

