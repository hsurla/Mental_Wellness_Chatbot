# streamlit_app/sidebar.py

import streamlit as st

def sidebar():
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Chatbot", "Wellness", "Chat History", "Profile", "Logout"])
<<<<<<< HEAD
=======

>>>>>>> dc1e2a6372059eb605d1a96ab06f0758d0a857b5
    return page

