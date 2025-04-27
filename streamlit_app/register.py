# streamlit_app/register.py

import streamlit as st
from database.database import add_user, find_user

def registration_page():
    st.title("Create an Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif find_user(username):
            st.error("Username already exists!")
        else:
            add_user(username, password)
            st.success("Account created successfully! Please Login.")
