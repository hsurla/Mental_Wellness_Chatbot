# streamlit_app/sidebar.py

import streamlit as st

def sidebar():
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Chatbot", "Wellness", "Chat History", "Profile", "Journal","Logout"])

    return page

