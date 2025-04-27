# streamlit_app/app.py

import streamlit as st
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.chatbot import chat_with_bot
from streamlit_app.sidebar import sidebar
from streamlit_app.utils import typing_animation

def main():
    st.set_page_config(page_title="Mental Wellness Chatbot")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        choice = st.selectbox("Login / Register", ["Login", "Register"])
        if choice == "Login":
            login_page()
        else:
            registration_page()
    else:
        page = sidebar()

        if page == "Chatbot":
            st.title("Your Mental Wellness Chatbot 💬")
            user_message = st.text_input("You: ", key="user_message")
            if st.button("Send"):
                if user_message:
                    response, emotion = chat_with_bot(st.session_state['username'], user_message)
                    typing_animation(response)
        elif page == "Profile":
            st.subheader("Profile Page (Coming Soon!)")
        elif page == "Logout":
            st.session_state['logged_in'] = False
            st.success("You have been logged out!")

if __name__ == "__main__":
    main()
