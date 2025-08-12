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

# Email configuration (using Gmail SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")  # Your Gmail address
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Your Gmail app password

# Initialize OAuth
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

def send_reset_email(email, reset_link):
    """Send password reset email to the user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Password Reset Request"
        
        # Email body
        body = f"""
        <html>
            <body>
                <p>Hello,</p>
                <p>You have requested to reset your password. Please click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,</p>
                <p>Your App Team</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def generate_reset_token(email):
    """Generate a reset token and store it in the database"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    reset_tokens_collection.insert_one({
        "token": token,
        "email": email,
        "expires_at": expires_at
    })
    return token

def show_forgot_password_form():
    """Show the forgot password form"""
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
                
                # Send email with reset link
                if send_reset_email(email, reset_link):
                    st.success("Password reset link has been sent to your email!")
                    st.session_state.show_forgot_password = False
                    st.rerun()
            else:
                st.error("No account found with this email")

def handle_password_reset():
    """Handle the password reset process"""
    if "token" in st.query_params:
        token = st.query_params["token"]
        token_data = reset_tokens_collection.find_one({"token": token})
        
        if token_data:
            if datetime.now() < token_data["expires_at"]:
                email = token_data["email"]
                with st.form("reset_password_form"):
                    st.subheader("🔄 Reset Your Password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Update Password"):
                        if new_password == confirm_password:
                            # Hash the new password
                            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                            update_password(email, hashed_password)
                            reset_tokens_collection.delete_one({"token": token})
                            st.success("Password updated successfully! Please login.")
                            st.session_state.password_reset_done = True
                            st.rerun()
                        else:
                            st.error("Passwords do not match")
            else:
                st.error("Reset link has expired")
                reset_tokens_collection.delete_one({"token": token})
        else:
            st.error("Invalid reset link")

# ... rest of your existing login_page() function remains the same ...