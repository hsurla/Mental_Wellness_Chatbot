import streamlit as st
from streamlit_oauth import OAuth2Component

# OAuth2 Configuration (replace with your credentials)
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
oauth = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

def login_page():
    st.set_page_config(page_title="Login", layout="centered")
    st.markdown("""
        <h2 style='text-align: left;'>🔒 Login</h2>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_clicked = st.form_submit_button("Login")

    if login_clicked:
        if username == "admin" and password == "admin":
            st.success("Login successful!")
            st.session_state.user = username
        else:
            st.error("Invalid username or password")

    # Small link styled 'Forgot Password'
    st.markdown(
        """
        <p style='font-size: 0.85rem; text-align: left; margin-top: -10px;'>
            <a href='?show_reset=true' style='color: #1a73e8;'>🔑 Forgot Password?</a>
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Handle Forgot Password Form
    if st.query_params.get("show_reset") == ["true"]:
        with st.form("reset_form"):
            st.markdown("### 🔄 Reset Password")
            user = st.text_input("Enter your username")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            reset = st.form_submit_button("Reset Password")
        if reset:
            if new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                st.success("Password reset successful (simulated)")

    # Divider and Google OAuth Button
    st.markdown("""<hr style='margin-top:30px; margin-bottom:10px;'>""", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>or</p>", unsafe_allow_html=True)

    token = oauth.authorize_button(
        "Continue with Google",
        redirect_uri="http://localhost:8501",
        scope=["profile", "email"],
    )

    if token:
        st.success("Google Login successful!")
        st.session_state.user = token.get("userinfo", {}).get("email", "Google User")

    return st.session_state.get("user")
