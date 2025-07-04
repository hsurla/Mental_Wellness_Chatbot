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

# Lazy import to prevent circular imports
def get_chatbot():
    from streamlit_app.chatbot import chat_with_bot
    return chat_with_bot

# API Functions
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

# ... [other API functions remain the same] ...

def main():
    st.set_page_config(page_title="Mental Wellness Chatbot", layout="wide")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_input_value' not in st.session_state:
        st.session_state.chat_input_value = ""

    # Google login handling
    if st.query_params.get("google_login_success") and not st.session_state.get("logged_in"):
        email = st.query_params.get("email", "user@example.com")
        st.session_state.update({
            'logged_in': True,
            'username': email,
            'login_time': time.time()
        })
        st.experimental_set_query_params()
        st.rerun()

    if not st.session_state.get("logged_in"):
        choice = st.selectbox("Login / Register", ["Login", "Register"])
        if choice == "Login":
            login_page()
        else:
            registration_page()
        return

    # Login badge
    if st.session_state.get("logged_in") and time.time() - st.session_state.get("login_time", 0) < 3:
        st.markdown(
            f"""<div style='position:fixed; top:15px; right:20px; background:#def1de; 
                padding:10px 16px; border-radius:12px; font-size:14px; color:green; z-index:1000;'>
                ✅ Logged in as <b>{st.session_state['username']}</b>
            </div>""",
            unsafe_allow_html=True
        )

    page = sidebar()

    if page == "Chatbot":
        st.markdown("## 💬 Your Mental Wellness Chatbot")
        
        # Display chat history
        for sender, msg, *rest in st.session_state.chat_history:
            time_sent = rest[0] if rest else "Unknown time"
            st.markdown(f"**{'🧑 You' if sender == 'You' else '🤖 Bot'}:** {msg}  \n<sub>{time_sent}</sub>", 
                       unsafe_allow_html=True)

        # Chat input with proper state management
        def clear_chat_input():
            """Callback to clear the input after sending"""
            st.session_state.chat_input_value = ""
            st.session_state.chat_input_key = str(time.time())  # Force widget reset

        # Create a unique key for the text input to force reset when cleared
        if 'chat_input_key' not in st.session_state:
            st.session_state.chat_input_key = "chat_input_default"

        # The text input widget
        user_message = st.text_input(
            "Type your message",
            value=st.session_state.chat_input_value,
            key=st.session_state.chat_input_key,
            label_visibility="collapsed",
            on_change=clear_chat_input
        )

        # Update the session state with current input
        st.session_state.chat_input_value = user_message

        # Send button - centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            send_button = st.button("📤 Send Message", use_container_width=True)

        # Handle message sending
        if send_button or st.session_state.get("enter_pressed", False):
            if user_message.strip():
                # Get chatbot function
                chat_with_bot = get_chatbot()
                
                current_time = datetime.now().strftime("%H:%M")
                st.session_state.chat_history.append(("You", user_message, current_time))
                response, emotion, _ = chat_with_bot(st.session_state['username'], user_message)
                st.session_state.chat_history.append(("Bot", f"{response} (Mood: {emotion})", current_time))
                
                # Reset flags and force rerun
                st.session_state.enter_pressed = False
                st.session_state.chat_input_value = ""
                st.rerun()

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

    # ... [rest of your page handlers remain the same] ...

if __name__ == "__main__":
    main()