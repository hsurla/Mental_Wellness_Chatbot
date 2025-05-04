# streamlit_app/app.py

import streamlit as st
from datetime import datetime
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.chatbot import chat_with_bot
from streamlit_app.sidebar import sidebar
from database.database import get_chat_history

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
                for item in st.session_state.chat_history:
                    if len(item) == 3:
                        sender, msg, time = item
                    else:
                        sender, msg = item
                        time = "Time not available"

                    if sender == "You":
                        st.markdown(f"**🧑 You:** {msg}  \n<sub>{time}</sub>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**🤖 Bot:** {msg}  \n<sub>{time}</sub>", unsafe_allow_html=True)

            # Spacer
            st.markdown("----")

            #Clear the input before rendering the widget
            if st.session_state.get("clear_input", False):
                st.session_state["chat_input"] = ""
                st.session_state["clear_input"] = False

            # Input field and button (bottom)
            input_col1, input_col2 = st.columns([5, 1])
            with input_col1:
                user_message = st.text_input("Type your message:", key="chat_input", label_visibility="collapsed")
            with input_col2:
                if st.button("Send"):
                    if user_message.strip():
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        st.session_state.chat_history.append(("You", user_message, current_time))
                        response, emotion, current_time = chat_with_bot(st.session_state['username'], user_message)
                        st.session_state.chat_history.append(("Bot", f"{response} *(Mood: {emotion})*", current_time))

                        #flag to clear input next run
                        st.session_state["clear_input"] = True
                        st.rerun()
        elif page == "Chat History":
            st.title("🕒 Your Chat History")

            chat_logs = get_chat_history(st.session_state['username'])

            if not chat_logs:
                st.info("No chat history avaiable.")
            else:
                for entry in chat_logs:
                    user_msg = entry.get("user_message", "")
                    bot_msg = entry.get("bot_response", "")
                    mood = entry.get("emotion_detected", "unknown")
                    time = entry.get("timestamp", "unknown")

                    st.markdown(f"""
                    **🧑 You:** {user_msg}  
                    **🤖 Bot:** {bot_msg} *(Mood: {mood})*  
                    <sub>{time}</sub>
                    """, unsafe_allow_html=True)
                    st.markdown("---")

        elif page == "Profile":
            st.subheader("Profile Page (Coming Soon!)")

        elif page == "Logout":
            st.session_state['logged_in'] = False
            st.success("You have been logged out!")

if __name__ == "__main__":
    main()
