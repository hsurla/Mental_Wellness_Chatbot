import streamlit as st
from streamlit_oauth import OAuth2Component

# OAuth client credentials (replace with your values)
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"

# Configure Google OAuth2
oauth = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

redirect_uri = "http://localhost:8501"  # Update if hosted

# Dummy user data
dummy_users = {
    "jaswanth": "test123",
    "wellness_user": "calm456"
}

def login_page():
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)

    # Initialize session state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "show_reset" not in st.session_state:
        st.session_state.show_reset = False

    if st.session_state.user:
        st.success(f"✅ Logged in as {st.session_state.user['username']}")
        return True

    # Layout: Login (left) | Forgot password (right)
    col1, col2 = st.columns([2, 1])

    # 🔹 LEFT SIDE: Login form
    with col1:
        with st.form("login_form"):
            st.subheader("Login with Username")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

        if login_btn:
            if username in dummy_users and dummy_users[username] == password:
                st.success(f"✅ Logged in as {username}")
                st.session_state.user = {"username": username, "method": "manual"}
                return True
            else:
                st.error("❌ Invalid username or password.")

    # 🔹 RIGHT SIDE: Forgot Password Button + Optional Reset Form
    with col2:
        st.subheader("Forgot Password?")
        if not st.session_state.show_reset:
            if st.button("🔑 Forgot Password?"):
                st.session_state.show_reset = True
        else:
            with st.form("reset_form"):
                reset_username = st.text_input("Enter your username")
                reset_btn = st.form_submit_button("Send Reset Link")

            if reset_btn:
                if reset_username:
                    st.success(f"📧 Reset link sent to {reset_username} (simulated).")
                    st.session_state.show_reset = False  # hide again after submission
                else:
                    st.error("Please enter a valid username.")

    # 🔽 Divider + Google Login
    st.markdown("---")
    st.subheader("👇 Or Continue with Google")

    token = oauth.authorize_button(
        name="Continue with Google",
        icon="🌐",
        redirect_uri=redirect_uri,
        scope="openid email profile",
        use_container_width=True
    )

    if token:
        userinfo = oauth.get_user_info(token)
        if userinfo and "email" in userinfo:
            username = userinfo["email"].split("@")[0]
            st.session_state.user = {"username": username, "email": userinfo["email"], "method": "google"}
            st.success(f"✅ Logged in as {username}")
            return True
        else:
            st.error("Google login failed.")

    return False
