import streamlit as st
from datetime import datetime
import time
import random
import requests
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.sidebar import sidebar
from database.database import get_chat_history
from streamlit_app.wellness import wellness_page
from streamlit_app.profile import profile_page
from streamlit_app.fun_support import get_fun_activity, get_healthy_snack

# Import chatbot functions after other dependencies are loaded
def get_chatbot_functions():
    from streamlit_app.chatbot import chat_with_bot
    return chat_with_bot

# API Functions (moved to top level to avoid circular imports)
def get_joke():
    """Fetch a joke from JokeAPI"""
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
    
    # Get chatbot functions after all other imports are done
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
        # Remove the badge flag after showing once
        del st.session_state.show_login_badge

    page = sidebar()

    if page == "Chatbot":
        st.markdown("## 💬 Your Mental Wellness Chatbot")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for sender, msg, *rest in st.session_state.chat_history:
            time_sent = rest[0] if rest else "Unknown time"
            st.markdown(f"**{'🧑 You' if sender == 'You' else '🤖 Bot'}:** {msg}  \n<sub>{time_sent}</sub>", 
                       unsafe_allow_html=True)

        # Reverted to original button style
        def handle_user_message():

            user_message = st.session_state.chat_input.strip()
            if user_message:
                 current_time = datetime.now().strftime("%H:%M")
                 st.session_state.chat_history.append(("You", user_message, current_time))
                 response, emotion, _ = chat_with_bot(st.session_state['username'], user_message)
                 st.session_state.chat_history.append(("Bot", f"{response} (Mood: {emotion})", current_time))
                 st.session_state.chat_input = ""  # ✅ safe here because we're inside the callback
                 st.rerun()

# Render input box with callback
st.text_input("Type your message", key="chat_input", label_visibility="collapsed", on_change=handle_user_message)


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

    elif page == "Profile":
        profile_page(st.session_state["username"])

    elif page == "Journal":
        st.title("📔 Journal")
        journal_text = st.text_area("New Entry", placeholder="Write your thoughts...")
        if st.button("Save Entry") and journal_text.strip():
            # Add your journal saving logic here
            st.success("Entry saved!")
            st.rerun()

    elif page == "Logout":
        st.session_state.clear()
        st.success("Logged out successfully")
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()