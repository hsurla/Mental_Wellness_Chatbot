import streamlit as st
from datetime import datetime
import time
import requests
import random
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.sidebar import sidebar
from database.database import get_chat_history
from streamlit_app.wellness import wellness_page
from streamlit_app.profile import profile_page
from streamlit_app.fun_support import get_fun_activity, get_healthy_snack

def get_chatbot_functions():
    from streamlit_app.chatbot import chat_with_bot
    return chat_with_bot

def get_joke():
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")
        if response.status_code == 200:
            data = response.json()
            if data["type"] == "twopart":
                return f"{data['setup']}... {data['delivery']}"
            return data["joke"]
        return "Why don't scientists trust atoms? Because they make up everything!"
    except:
        return "Failed to fetch joke - here's one: What do you call a fake noodle? An impasta!"

def main():
    st.set_page_config(page_title="Mental Wellness Chatbot", layout="wide")

    chat_with_bot = get_chatbot_functions()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state.get("logged_in"):
        choice = st.selectbox("Login / Register", ["Login", "Register"])
        if choice == "Login":
            login_page()
        else:
            registration_page()
        return

    # Login badge
    if st.session_state.get("show_login_badge"):
        st.markdown(
            f"""<div style='position:fixed; top:15px; right:20px; background:#def1de; 
                padding:10px 16px; border-radius:12px; font-size:14px; color:green; z-index:1000;'>
                ✅ Logged in as <b>{st.session_state['username']}</b>
            </div>""",
            unsafe_allow_html=True
        )
        del st.session_state.show_login_badge

    page = sidebar()

    # ---------------------- CHATBOT ----------------------
    if page == "Chatbot":
        st.markdown("## 💬 Your Mental Wellness Chatbot")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_emoji = "🧑"
        bot_emoji = "🤖"

        # Show message history
        for sender, msg, *rest in st.session_state.chat_history:
            time_sent = rest[0] if rest else "Unknown time"
            prefix = user_emoji if sender == "You" else bot_emoji
            st.markdown(f"**{prefix} {sender}:** {msg}  \n<sub>{time_sent}</sub>", unsafe_allow_html=True)

        st.markdown("---")

        # Chat input form
        with st.form("chat_form", clear_on_submit=True):
            user_message = st.text_input("Type your message", key="chat_input", label_visibility="collapsed")
            send_clicked = st.form_submit_button("📤 Send", use_container_width=True)

            # Enlarge button styling
            st.markdown("""
                <style>
                button[kind="primary"] {
                    padding-top: 0.75rem !important;
                    padding-bottom: 0.75rem !important;
                    font-size: 1.1rem !important;
                    border-radius: 8px !important;
                }
                </style>
            """, unsafe_allow_html=True)

        # If user sends message
        if send_clicked and user_message.strip():
            current_time = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(("You", user_message.strip(), current_time))

            # Typing animation using HTML/CSS
            with st.empty():
                typing_placeholder = st.empty()
                typing_placeholder.markdown("""
                    <style>
                    .typing-dots {
                        display: inline-block;
                        position: relative;
                        width: 80px;
                        height: 24px;
                    }
                    .typing-dots div {
                        position: absolute;
                        top: 0;
                        width: 16px;
                        height: 16px;
                        border-radius: 50%;
                        background: #aaa;
                        animation-timing-function: cubic-bezier(0, 1, 1, 0);
                    }
                    .typing-dots div:nth-child(1) {
                        left: 8px;
                        animation: dots1 0.6s infinite;
                    }
                    .typing-dots div:nth-child(2) {
                        left: 32px;
                        animation: dots2 0.6s infinite;
                    }
                    .typing-dots div:nth-child(3) {
                        left: 56px;
                        animation: dots3 0.6s infinite;
                    }
                    @keyframes dots1 {
                        0% { transform: scale(0); }
                        100% { transform: scale(1); }
                    }
                    @keyframes dots2 {
                        0% { transform: scale(0); }
                        50% { transform: scale(1); }
                        100% { transform: scale(0); }
                    }
                    @keyframes dots3 {
                        0% { transform: scale(1); }
                        100% { transform: scale(0); }
                    }
                    </style>
                    <div class="typing-dots">
                        <div></div><div></div><div></div>
                    </div>
                """, unsafe_allow_html=True)

                time.sleep(1.5)  # Simulate typing delay
                response, emotion, _ = chat_with_bot(st.session_state['username'], user_message)
                typing_placeholder.empty()

                st.session_state.chat_history.append(("Bot", f"{response} (Mood: {emotion})", current_time))
                st.rerun()

        # Scroll to bottom
        st.markdown(
            """<script>
            var chatDiv = window.parent.document.querySelector('section.main');
            if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
            </script>""",
            unsafe_allow_html=True
        )

    # ---------------------- WELLNESS ----------------------
    elif page == "Wellness":
        wellness_page()
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎲 Activity Suggestion")
            st.info(get_fun_activity())
            if st.button("🔀 Get Another Activity", key="new_activity"):
                if 'current_activity' in st.session_state:
                    del st.session_state.current_activity
                st.rerun()
        with col2:
            st.subheader("🥗 Healthy Snack")
            st.success(get_healthy_snack())
            if st.button("🔀 Get Another Snack", key="new_snack"):
                if 'current_snack' in st.session_state:
                    del st.session_state.current_snack
                st.rerun()

    # ---------------------- CHAT HISTORY ----------------------
    elif page == "Chat History":
        st.title("🕒 Chat History")
        if chat_logs := get_chat_history(st.session_state['username']):
            for entry in chat_logs:
                st.markdown(f"""
                **🧑 You:** {entry.get("user_message", "")}  
                **🤖 Bot:** {entry.get("bot_response", "")} *(Mood: {entry.get("emotion_detected", "unknown")})*  
                <sub>{entry.get("timestamp", "unknown")}</sub>
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No chat history yet")

    # ---------------------- PROFILE ----------------------
    elif page == "Profile":
        profile_page(st.session_state["username"])

    # ---------------------- JOURNAL ----------------------
    elif page == "Journal":
        st.title("📔 Journal")
        journal_text = st.text_area("New Entry", placeholder="Write your thoughts...")
        if st.button("Save Entry") and journal_text.strip():
            st.success("Entry saved!")
            st.rerun()

    # ---------------------- LOGOUT ----------------------
    elif page == "Logout":
        st.session_state.clear()
        st.success("Logged out successfully")
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()
