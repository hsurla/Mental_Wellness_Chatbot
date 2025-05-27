# streamlit_app/login.py

import streamlit as st
import bcrypt
from database.database import find_user

def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = find_user(username)
        if user:
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.success(f"Welcome, {username}!")
                st.session_state["username"] = username
                st.session_state['logged_in'] = True
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")
