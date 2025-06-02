# streamlit_app/register.py

import streamlit as st
import requests
from streamlit.components.v1 import html
from database.database import add_user, find_user
import bcrypt

# reCAPTCHA credentials
RECAPTCHA_SITE_KEY = "6LcjG1IrAAAAAGqJbpWsE8tGX-QHebp-xt1CaDUS"
RECAPTCHA_SECRET_KEY = "6LcjG1IrAAAAAN0OKNJVoHiIdtEiIdXsg79GXz3D"

def registration_page():
    st.title("Create an Account")
    
    recaptcha_token = None
    with st.form(key="register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")

        # reCAPTCHA
        html(f"""
        <div class="g-recaptcha" data-sitekey="{RECAPTCHA_SITE_KEY}"></div>
        <script src="https://www.google.com/recaptcha/api.js"></script>
        """, height=150)
        
        if submitted:
            recaptcha_token = st.query_params.get("g-recaptcha-response", "")

    if recaptcha_token:
        result = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
            "secret": RECAPTCHA_SECRET_KEY,
            "response": recaptcha_token
        }).json()

        if not result.get("success"):
            st.error("❌ reCAPTCHA verification failed.")
        else:
            if password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif find_user(username):
                st.error("❌ Username already exists.")
            else:
                # Hash password before storing
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                add_user(username, hashed.decode())
                st.success("✅ Account created successfully! Please login.")