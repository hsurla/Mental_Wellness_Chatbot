# streamlit_app/app.py
import os
from pathlib import Path
from dotenv import load_dotenv

env_path=Path(__file__).parent.parent/'.env'
load_dotenv()

import streamlit as st
from datetime import datetime
import time
import requests
import random

from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.profile import profile_page
from streamlit_app.journal import journal_page
from streamlit_app.chat_history import chat_history_page
from streamlit_app.chatbot import chat_with_bot
from streamlit_app.fun_support import get_fun_activity, get_healthy_snack

# Set page config
st.set_page_config(
    page_title="Mental Wellness Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

def chatbot_response(user_message):
    return random.choice([
        ("I understand how you're feeling. Have you tried deep breathing?", "calm"),
        ("That sounds challenging. Would you like to talk more about it?", "concerned"),
        ("Great to hear you're feeling positive today!", "happy"),
        ("Let me suggest some relaxation techniques...", "neutral")
    ])

#def profile_page(username):
#    st.title("👤 Your Profile")
#    st.write(f"Logged in as: **{username}**")
#    with st.expander("Account Settings"):
 #       st.text_input("Change display name", value=username.split("@")[0])
#        st.button("Save Changes")
 #   with st.expander("Wellness Preferences"):
 #       st.multiselect(
#            "Your interests",
#            ["Mindfulness", "Exercise", "Nutrition", "Sleep", "Relationships"],
#            default=["Mindfulness"]
#        )

def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    #handle password setup after google signup
    if st.session_state.get("needs_password_setup"):
        email=st.session_state.user_email
        with st.form("password_setup_form"):
            st.title("🔐 Set Up Your Password")
            st.write(f"Email: {email}")
            password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Save Password"):
                if password == confirm_password:
                    from database.database import update_password
                    update_password(email, password)
                    st.success("Password set up successfully!")
                    st.session_state.needs_password_setup = False

                    # Ensure user data is refreshed
                    from database.database import find_user_by_email
                    user = find_user_by_email(email)
                    st.session_state.user_data = user or {"email": email}

                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Passwords do not match")
        return
    
    # Show login or registration page if not authenticated
    if 'user_email' not in st.session_state:
        st.sidebar.title("Account")
        auth_option = st.sidebar.radio(
            "Authentication",
            ["🔐 Login", "📝 Register"],
            label_visibility="collapsed"
        )
        
        if auth_option == "🔐 Login":
            if login_page():
                st.rerun()
        elif auth_option == "📝 Register":
            registration_page()
        return
    
    # Main app after login
    email = st.session_state.user_email
    
    # Ensure user_data exists in session state
    if 'user_data' not in st.session_state:
        # Import inside function where it's actually used
        from database.database import find_user_by_email
        user = find_user_by_email(email)
        if user:
            st.session_state.user_data = user
        else:
            # Fallback to minimal user data
            st.session_state.user_data = {"email": email}

    user_data = st.session_state.user_data
    display_name = user_data.get("username", email.split("@")[0])

    with st.sidebar:
        st.title(f"Hello, {display_name}!")
        page = st.radio(
            "Menu",
            ["💬 Chatbot", "🧈 Wellness", "📚 Chat History", "📔 Journal", "👤 Profile"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.write("Need help?")
        if st.button("Get a random joke"):
            joke = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode").json()
            if joke.get("setup"):
                st.write(f"{joke['setup']}\n\n{joke['delivery']}")
            else:
                st.write(joke.get("joke", "Why don't scientists trust atoms? Because they make up everything!"))
        
        # Add the logout button at the bottom of the sidebar
        st.markdown("---")
        st.markdown(
            """
            <style>
                .logout-button {
                    background-color: transparent !important;
                    border: none !important;
                    color: inherit !important;
                    width: 100%;
                    text-align: left;
                    padding: 0.5rem 1rem;
                    border-radius: 0.5rem;
                }
                .logout-button:hover {
                    background-color: rgba(250, 250, 250, 0.1) !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚪 Logout", key="logout", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully!")
            time.sleep(1)
            st.query_params.clear()
            st.rerun()

    if page == "💬 Chatbot":
        st.title("💬 Mental Wellness Chatbot")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for sender, message, timestamp in st.session_state.chat_history:
            avatar = "🧑" if sender == "You" else "🤖"
            st.chat_message(sender, avatar=avatar).write(message)
            st.caption(timestamp)

        if prompt := st.chat_input("How are you feeling today?"):
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(("You", prompt, timestamp))

            with st.spinner("Thinking..."):
                try:
                    response, emotion, timestamp = chat_with_bot(email,prompt)
                    timestamp = datetime.now().strftime("%H:%M")
                    st.session_state.chat_history.append(("Bot", f"{response} (Mood: {emotion})", timestamp))
                except Exception as e:
                    st.error("Chatbot is temporarily unavailable")
                    response = "I'm having trouble responding right now. Please try again later."
                    st.session_state.chat_history.append(
                    ("Bot", response, timestamp)
                    )
            st.rerun()

    elif page == "🧈 Wellness":
        st.title("🧈 Wellness Center")

        col1, col2 = st.columns(2)
        with col1:
            st.header("Activity Suggestion")
            st.info(get_fun_activity())
            if st.button("Get new activity", key="activity"):
                st.rerun()

        with col2:
            st.header("Healthy Snack Idea")
            st.success(get_healthy_snack())
            if st.button("Get new snack", key="snack"):
                st.rerun()

        st.markdown("---")
        st.header("Mindfulness Exercise")
        st.video("https://www.youtube.com/watch?v=inpok4MKVLM")

    elif page == "📚 Chat History":
        chat_history_page(email)

    elif page == "📔 Journal":
        journal_page(email)

    elif page == "👤 Profile":
        profile_page(email)

    elif page == "🚪 Logout":
        st.session_state.clear()
        st.success("Logged out successfully!")
        time.sleep(1)
        st.query_params.clear()
        st.rerun()

if __name__ == "__main__":
    main()
