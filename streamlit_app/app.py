import streamlit as st
import pyrebase
from datetime import datetime
from .login import login_page
from streamlit_app.register import registration_page as legacy_registration_page  # legacy, not used
from streamlit_app.chatbot import chat_with_bot
from streamlit_app.sidebar import sidebar
from streamlit_app.wellness import wellness_page
from streamlit_app.profile import profile_page
from database.database import (
    get_chat_history,
    save_journal_entry,
    get_journal_entries,
    update_journal_entry,
    delete_journal_entry
)
from streamlit_app.firebase_config import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def google_auth_page():
    st.title("🔐 Login with Firebase")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success("Login successful!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = email
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")

    st.markdown("---")
    st.caption("Don't have an account? Please register on Firebase or use an admin tool to create users.")

def main():
    st.set_page_config(page_title="Mental Wellness Chatbot", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        google_auth_page()
    else:
        page = sidebar()

        if page == "Chatbot":
            st.markdown("## 💬 Your Mental Wellness Chatbot")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
                
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

            st.markdown("<br>", unsafe_allow_html=True)

            if st.session_state.get("clear_input", False):
                st.session_state["chat_input"] = ""
                st.session_state["clear_input"] = False

            st.markdown("### 👇 Type your message")
            user_message = st.text_input("Type here", key="chat_input", label_visibility="collapsed")

            if st.button("📤 Send Message", use_container_width=True):
                if user_message.strip():
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.chat_history.append(("You", user_message, current_time))
                    response, emotion, current_time = chat_with_bot(st.session_state['username'], user_message)
                    st.session_state.chat_history.append(("Bot", f"{response} *(Mood: {emotion})*", current_time))
                    st.session_state["clear_input"] = True
                    st.rerun()

        elif page == "Wellness":
            wellness_page()

        elif page == "Chat History":
            st.title("🕒 Your Chat History")
            chat_logs = get_chat_history(st.session_state['username'])

            if not chat_logs:
                st.info("No chat history available.")
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
            profile_page(st.session_state["username"])

        elif page == "Journal":
            st.title("📔 Your Personal Journal")
            st.markdown("Write down anything you're feeling or thinking.")
            journal_text = st.text_area("New Entry", placeholder="Start writing here...")

            if st.button("Save Entry"):
                if journal_text.strip():
                    save_journal_entry(st.session_state["username"], journal_text.strip())
                    st.success("Entry saved successfully!")
                    st.rerun()
                else:
                    st.warning("Entry cannot be empty.")

            st.markdown("### 📚 Previous Entries")
            entries = get_journal_entries(st.session_state["username"])

            if not entries:
                st.info("No journal entries yet.")
            else:
                for entry in reversed(entries):
                    entry_id = str(entry.get("_id"))
                    time = entry.get("timestamp", "")
                    text = entry.get("text", "")

                    with st.expander(f"🕒 {time}"):
                        edited_text = st.text_area("Edit entry", value=text, key=entry_id)

                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Update", key=f"update_{entry_id}"):
                                update_journal_entry(st.session_state["username"], entry_id, edited_text)
                                st.success("Entry updated.")
                                st.rerun()
                        with col2:
                            if st.button("Delete", key=f"delete_{entry_id}"):
                                delete_journal_entry(st.session_state["username"], entry_id)
                                st.warning("Entry deleted.")
                                st.rerun()

        elif page == "Logout":
            if st.button("Confirm Logout", help="Click to log out"):
                st.session_state['logged_in'] = False
                st.success("You have been logged out.")
                st.rerun()

if __name__ == "__main__":
    main()
