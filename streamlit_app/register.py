# streamlit_app/register.py

import streamlit as st
from database.database import add_user, find_user_by_email
import bcrypt

def registration_page():
    st.title("Create an Account")
    
    with st.form(key="register_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif find_user_by_email(email):
                st.error("❌ Username already exists.")
            else:
                # Hash password before storing
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                add_user(email=email, password=hashed.decode(),username=username)
                st.success("✅ Account created successfully! Please login.")
                st.session_state.user_email = email
                st.session_state.user_data = find_user_by_email(email)
                st.rerun()