import streamlit as st

def sidebar():
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Chatbot", "Chat History", "Profile", "Logout"])

    return page
