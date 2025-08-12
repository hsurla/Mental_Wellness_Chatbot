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
import re

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

def is_valid_gmail(email):
    """Check if email is a valid Gmail address"""
    pattern = r"^[a-zA-Z0-9_.+-]+@gmail\.com$"
    return re.match(pattern, email) is not None

def send_gmail(sender_email, sender_password, recipient_email, subject, body):
    """Universal Gmail sender function"""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def send_reset_email(recipient_email, reset_link):
    """Send password reset email using the recipient's own Gmail"""
    if not is_valid_gmail(recipient_email):
        st.error("Only Gmail addresses are supported for password reset")
        return False
    
    subject = "Password Reset Request"
    body = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Click below to reset your password:</p>
            <p><a href="{reset_link}" style="
                background: #4285F4;
                color: white;
                padding: 10px 15px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            ">Reset Password</a></p>
            <p><small>Link expires in 1 hour</small></p>
        </body>
    </html>
    """
    
    # Use the recipient's own Gmail credentials (would need to be provided)
    # In a real app, you'd need to securely collect these or use OAuth
    sender_email = recipient_email
    sender_password = st.secrets.get("USER_GMAPPASSWORD", "default_password")
    
    return send_gmail(sender_email, sender_password, recipient_email, subject, body)

def generate_reset_token(email):
    """Generate and store reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    reset_tokens_collection.insert_one({
        "token": token,
        "email": email,
        "expires_at": expires_at
    })
    return token

def show_forgot_password_form():
    """Forgot password form that works for any Gmail"""
    with st.form("forgot_password_form"):
        st.subheader("🔒 Reset Your Password")
        email = st.text_input("Enter your Gmail address")
        
        submitted = st.form_submit_button("Send Reset Link")
        if st.form_submit_button("Cancel"):
            st.session_state.show_forgot_password = False
            st.rerun()
        
        if submitted and email:
            if not is_valid_gmail(email):
                st.error("Please enter a valid Gmail address")
                return
                
            token = generate_reset_token(email)
            reset_link = f"{REDIRECT_URI}?token={token}"
            
            if send_reset_email(email, reset_link):
                st.success("Password reset link sent to your Gmail!")
                st.session_state.show_forgot_password = False
                st.rerun()

# [Rest of your existing code (handle_password_reset, login_page) remains unchanged]