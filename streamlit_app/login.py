# streamlit_app/login.py

import streamlit as st
from database.database import find_user

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = find_user(username)
        if user and user["password"] == password:
            st.success(f"Welcome, {username}!")
            st.session_state['username'] = username
            st.session_state['logged_in'] = True
        else:
            st.error("Invalid Username or Password")
