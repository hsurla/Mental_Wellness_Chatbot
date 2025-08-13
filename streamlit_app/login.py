# streamlit_app/login.py
import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import secrets
import os
from datetime import datetime, timedelta
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

from database.database import (
    find_user_by_email,
    find_user_by_google_id,
    add_user,
    update_password,
    add_google_id,
    reset_tokens_collection
)

# Configuration
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"

# Initialize OAuth
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

def send_reset_email(email, reset_link):
    """Send password reset email using Gmail SMTP"""
    try:
        # Configuration (use environment variables)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("GMAIL_EMAIL", "your.app.email@gmail.com")
        app_password = os.getenv("GMAIL_APP_PASSWORD", "your-app-password")
        app_name = "Your App Name"
        
        # Create email content
        subject = f"Password Reset Request for {app_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <h2 style="color: #333;">Password Reset Request</h2>
                    <p>Hello,</p>
                    <p>You've requested to reset your password for {app_name}.</p>
                    <p>Please click the button below to reset your password:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="
                            display: inline-block;
                            padding: 12px 24px;
                            background-color: #4285F4;
                            color: white;
                            text-decoration: none;
                            border-radius: 4px;
                            font-weight: bold;
                        ">Reset Password</a>
                    </p>
                    <p>This link will expire in 15 minutes.</p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                    <p>Best regards,<br>{app_name} Team</p>
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                    <p style="font-size: 12px; color: #777;">
                        For security reasons, please do not share this email with anyone.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Create text version
        text_content = f"""\
Password Reset Request
----------------------
Hello,
You've requested to reset your password for {app_name}.
Please visit this link to reset your password: {reset_link}
This link expires in 15 minutes.
If you didn't request this, please ignore this email.
"""
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        # Create secure SSL context
        context = ssl.create_default_context()
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email, msg.as_string())
        
        st.success("Password reset email sent! Please check your inbox.")
        return True
            
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        # Fallback to showing link in app
        st.warning(f"Reset link: {reset_link}")
        return False

def generate_reset_token(email):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=15)  # Shorter expiration
    reset_tokens_collection.insert_one({
        "token": token,
        "email": email,
        "expires_at": expires_at,
        "used": False  # Track if token has been used
    })
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
            user = find_user_by_email(email)
            if user:
                token = generate_reset_token(email)
                reset_link = f"{REDIRECT_URI}?token={token}"
                send_reset_email(email, reset_link)  # Send actual email
                st.session_state.show_forgot_password = False
                st.rerun()
            else:
                # Show generic message to prevent email enumeration
                st.success("If an account exists with this email, a reset link will be sent")
                st.session_state.show_forgot_password = False
                st.rerun()

def handle_password_reset():
    if "token" in st.query_params:
        token = st.query_params["token"]
        token_data = reset_tokens_collection.find_one({"token": token})
        
        if token_data and not token_data.get("used", False):
            if datetime.now() < token_data["expires_at"]:
                email = token_data["email"]
                with st.form("reset_password_form"):
                    st.subheader("🔄 Reset Your Password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Update Password"):
                        if new_password == confirm_password:
                            update_password(email, new_password)
                            # Mark token as used instead of deleting
                            reset_tokens_collection.update_one(
                                {"token": token},
                                {"$set": {"used": True}}
                            )
                            # Clear token from URL
                            st.experimental_set_query_params()
                            st.success("Password updated successfully! Please login.")
                            st.session_state.password_reset_done = True
                            st.rerun()
                        else:
                            st.error("Passwords do not match")
            else:
                st.error("Reset link has expired")
                reset_tokens_collection.delete_one({"token": token})
        else:
            st.error("Invalid or expired reset link")

def login_page():
    if not st.session_state.get("password_reset_done", False):
        handle_password_reset()
    
    if 'user_email' in st.session_state:
        return True

    st.title("🔐 Login")

    # Initialize session state
    if "show_forgot_password" not in st.session_state:
        st.session_state.show_forgot_password = False

    # Main login form
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        # Login button
        login_clicked = st.form_submit_button("Login")
        
        if login_clicked:
            user = find_user_by_email(email)
            if user and "password" in user and bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.session_state.user_email = user["email"]
                st.session_state.user_data = user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Forgot password button
    if st.button("Forgot password?"):
        st.session_state.show_forgot_password = True
        st.rerun()

    # Show forgot password form if triggered
    if st.session_state.get("show_forgot_password", False):
        with st.container():
            st.markdown("---")
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
                email = userinfo["email"]
                google_id = userinfo["sub"]
                
                # Check if user exists by Google ID
                user = find_user_by_google_id(google_id)
                if not user:
                    # Check if user exists by email (manual registration)
                    user = find_user_by_email(email)
                    if user:
                        # Link Google ID to existing account
                        add_google_id(email, google_id)
                    else:
                        # Create new account
                        add_user(
                            email=email,
                            google_id=google_id,
                            username=userinfo.get("name", "")
                        )
                        #flag that user needs to set up password
                        st.session_state.needs_password_setup = True

                #set session state
                st.session_state.user_email = email
                st.session_state.user_data = user or find_user_by_email(email)

                #only rerun if not in password setup mode
                if not st.session_state.get("needs_password_setup", False):
                    st.success(f"Logged in as {email}")
                    st.rerun()
        except Exception as e:
            st.error(f"Google login failed: {str(e)}")

    return False