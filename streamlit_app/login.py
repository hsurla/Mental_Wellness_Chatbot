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

def send_reset_email(email, reset_code):
    """Send password reset email using Gmail SMTP"""
    try:
        # Configuration (use environment variables)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("GMAIL_EMAIL", "your.app.email@gmail.com")
        app_password = os.getenv("GMAIL_APP_PASSWORD", "your-app-password")
        app_name = "Mental Wellness Chatbot"
        
        # Create email content
        subject = f"Password Reset Code for {app_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
                    <p>Hello,</p>
                    <p>You've requested to reset your password for the <strong>{app_name}</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; margin: 25px 0;">
                        <p style="margin: 0; font-size: 18px; font-weight: bold;">Your Reset Code:</p>
                        <div style="font-size: 32px; font-weight: bold; letter-spacing: 3px; color: #4285F4; margin: 15px 0;">
                            {reset_code}
                        </div>
                        <p style="margin: 0; font-size: 14px; color: #666;">(This code expires in 15 minutes)</p>
                    </div>
                    
                    <p>Enter this code in the password reset form to proceed.</p>
                    
                    <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                        <p>Best regards,<br>
                        <strong>{app_name} Team</strong></p>
                        <p style="font-size: 12px; color: #777;">
                            For security reasons, please do not share this code with anyone.
                        </p>
                    </div>
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

Your reset code: {reset_code}
This code expires in 15 minutes.

Enter this code in the password reset form to proceed.

Best regards,
{app_name} Team
"""
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = f"{app_name} <{sender_email}>"
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
        
        return True
            
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def generate_reset_code(email):
    """Generate a 6-digit reset code"""
    code = ''.join(secrets.choice('0123456789') for i in range(6))
    expires_at = datetime.now() + timedelta(minutes=15)
    reset_tokens_collection.update_one(
        {"email": email},
        {"$set": {
            "code": code,
            "expires_at": expires_at,
            "used": False
        }},
        upsert=True
    )
    return code

def show_reset_form():
    """Show the password reset form with code verification"""
    with st.form("reset_password_form"):
        st.subheader("🔄 Reset Your Password")
        st.info(f"A 6-digit code has been sent to: **{st.session_state.reset_email}**")
        
        # Single input for 6-digit code
        reset_code = st.text_input("Enter 6-digit code", 
                                  max_chars=6,
                                  placeholder="123456",
                                  help="Check your email for the reset code")
        
        # Password fields
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Form submission
        submitted = st.form_submit_button("Update Password")
        
        if submitted:
            # Validate code format
            if not reset_code.isdigit() or len(reset_code) != 6:
                st.error("Please enter a valid 6-digit code")
                return
                
            # Validate password
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return
                
            if len(new_password) < 8:
                st.error("Password must be at least 8 characters")
                return
                
            # Check reset code
            token_data = reset_tokens_collection.find_one({"email": st.session_state.reset_email})
            if token_data:
                if datetime.now() > token_data["expires_at"]:
                    st.error("Reset code has expired")
                    return
                    
                if token_data.get("used", False):
                    st.error("This code has already been used")
                    return
                    
                if reset_code == token_data["code"]:
                    # Update password
                    update_password(st.session_state.reset_email, new_password)
                    
                    # Mark code as used
                    reset_tokens_collection.update_one(
                        {"email": st.session_state.reset_email},
                        {"$set": {"used": True}}
                    )
                    
                    st.success("Password updated successfully! Please login.")
                    st.session_state.password_reset_done = True
                    st.session_state.show_reset_form = False
                    st.session_state.show_forgot_password = False
                    if "reset_email" in st.session_state:
                        del st.session_state.reset_email
                    st.rerun()
                else:
                    st.error("Incorrect reset code")
            else:
                st.error("No reset request found for this email")

def show_forgot_password_form():
    """Show the forgot password workflow in a single tab"""
    # Step 1: Email input
    if "reset_email" not in st.session_state:
        with st.form("forgot_password_form"):
            st.subheader("🔒 Reset Your Password")
            email = st.text_input("Enter your registered email address")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_reset = st.form_submit_button("Send Reset Code")
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_forgot_password = False
                    st.rerun()
            
            if submit_reset and email:
                user = find_user_by_email(email)
                if user:
                    reset_code = generate_reset_code(email)
                    
                    # Try to send email
                    if send_reset_email(email, reset_code):
                        st.session_state.reset_email = email
                        st.rerun()
                    else:
                        st.warning("Email sending failed. Using demo code:")
                        st.code(f"Reset code: {reset_code}")
                        st.session_state.reset_email = email
                        st.rerun()
                else:
                    # Show generic message to prevent email enumeration
                    st.success("If an account exists with this email, a reset code will be sent")
                    st.session_state.show_forgot_password = False
                    st.rerun()
    
    # Step 2: Code verification and password reset
    else:
        show_reset_form()

def login_page():
    if not st.session_state.get("password_reset_done", False):
        # Handle password reset in the same tab
        pass
    
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