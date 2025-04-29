# streamlit_app/app.py

import streamlit as st
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.chatbot import chat_with_bot
from streamlit_app.sidebar import sidebar

def main():
    st.set_page_config(page_title="Mental Wellness Chatbot", layout="centered")

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
            st.title("💬 Your Mental Wellness Chatbot")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Display chat history (top)
            chat_container = st.container()
            with chat_container:
                for sender, msg in st.session_state.chat_history:
                    if sender == "You":
                        st.markdown(f"**🧑 You:** {msg}")
                    else:
                        st.markdown(f"**🤖 Bot:** {msg}")

            # Spacer
            st.markdown("----")

            # Input field and button (bottom)
            input_col1, input_col2 = st.columns([5, 1])
            with input_col1:
                user_message = st.text_input("Type your message:", key="chat_input", label_visibility="collapsed")
            with input_col2:
                if st.button("Send"):
                    if user_message.strip():
                        st.session_state.chat_history.append(("You", user_message))
                        response, emotion = chat_with_bot(st.session_state['username'], user_message)
                        st.session_state.chat_history.append(("Bot", f"{response} *(Mood: {emotion})*"))
                        st.rerun()

        elif page == "Profile":
            st.subheader("Profile Page (Coming Soon!)")

        elif page == "Logout":
            st.session_state['logged_in'] = False
            st.success("You have been logged out!")

if __name__ == "__main__":
    main()
