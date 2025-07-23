import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import secrets
from datetime import datetime, timedelta

# Configuration
CLIENT_ID = "your-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "your-client-secret"
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

# User database
USERS_DB = {
    "demo_user": {
        "password": "demo_pass",
        "email": "demo@example.com"
    }
}

# Password reset tokens
RESET_TOKENS = {}

def generate_reset_token(email):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    RESET_TOKENS[token] = {
        "email": email,
        "expires_at": expires_at
    }
    return token

def show_forgot_password_form():
    with st.form("forgot_password_form"):
        st.subheader("🔒 Reset Your Password")
        email = st.text_input("Enter your registered email address")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_reset = st.form_submit_button("Send Reset Link")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_forgot_password = False
                st.rerun()
        
        if submit_reset and email:
            user_exists = any(user["email"] == email for user in USERS_DB.values())
            if user_exists:
                token = generate_reset_token(email)
                reset_link = f"{REDIRECT_URI}?token={token}"
                st.success(f"Password reset link generated (demo): {reset_link}")
                st.session_state.show_forgot_password = False
                st.rerun()
            else:
                st.error("No account found with this email")

def handle_password_reset():
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
    if not st.session_state.get("password_reset_done", False):
        handle_password_reset()
    
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")

    # Custom CSS for the login form footer
    st.markdown("""
    <style>
    .login-form-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
    }
    .forgot-password-link {
        color: #666;
        text-decoration: none;
        font-size: 0.9em;
        cursor: pointer;
    }
    .forgot-password-link:hover {
        color: #444;
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Form footer with both elements in one line
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("""
            <div class="login-form-footer">
                <span class="forgot-password-link" onclick="document.getElementById('forgot-btn').click()">
                    Forgot password?
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            login_clicked = st.form_submit_button("Login")
        
        # Hidden button for forgot password functionality
        forgot_clicked = st.form_submit_button(" ", key="forgot-btn")
        
        if forgot_clicked:
            st.session_state.show_forgot_password = True
            st.rerun()
        
        if login_clicked:
            user = USERS_DB.get(username)
            if user and user["password"] == password:
                st.session_state.user_email = user["email"]
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Show forgot password form if triggered
    if st.session_state.get("show_forgot_password", False):
        with st.expander("Reset Password", expanded=True):
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