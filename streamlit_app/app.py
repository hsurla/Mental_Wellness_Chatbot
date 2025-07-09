import streamlit as st
from datetime import datetime
import time
import requests
import os
from login import login_page
from database.database import get_chat_history
import random

# Set page config
st.set_page_config(
    page_title="Mental Wellness Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample wellness functions (replace with your actual implementations)
def get_fun_activity():
    activities = [
        "Go for a 10-minute walk in nature",
        "Try 5 minutes of deep breathing",
        "Write down 3 things you're grateful for",
        "Listen to your favorite song and dance",
        "Do a quick 5-minute stretching routine"
    ]
    return random.choice(activities)

def get_healthy_snack():
    snacks = [
        "A handful of almonds and an apple",
        "Greek yogurt with berries",
        "Carrot sticks with hummus",
        "Whole grain toast with avocado",
        "A smoothie with spinach and banana"
    ]
    return random.choice(snacks)

def chatbot_response(user_message):
    """Mock chatbot - replace with your actual implementation"""
    responses = [
        ("I understand how you're feeling. Have you tried deep breathing?", "calm"),
        ("That sounds challenging. Would you like to talk more about it?", "concerned"),
        ("Great to hear you're feeling positive today!", "happy"),
        ("Let me suggest some relaxation techniques...", "neutral")
    ]
    return random.choice(responses)

def profile_page(username):
    st.title("👤 Your Profile")
    st.write(f"Logged in as: **{username}**")
    
    with st.expander("Account Settings"):
        st.text_input("Change display name", value=username.split("@")[0])
        st.button("Save Changes")
    
    with st.expander("Wellness Preferences"):
        st.multiselect(
            "Your interests",
            ["Mindfulness", "Exercise", "Nutrition", "Sleep", "Relationships"],
            default=["Mindfulness"]
        )

def main():
    # Authentication check
    if not login_page():
        return
    
    # Main app content - only shown when logged in
    username = st.session_state.user_email
    
    # Sidebar navigation
    with st.sidebar:
        st.title(f"Hello, {username.split('@')[0]}!")
        st.image("https://cdn-icons-png.flaticon.com/512/2965/2965300.png", width=100)
        
        page = st.radio(
            "Menu",
            ["💬 Chatbot", "🧘 Wellness", "📚 Chat History", "👤 Profile", "🚪 Logout"],
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
    
    # Page routing
    if page == "💬 Chatbot":
        st.title("💬 Mental Wellness Chatbot")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for sender, message, timestamp in st.session_state.chat_history:
            avatar = "🧑" if sender == "You" else "🤖"
            st.chat_message(sender, avatar=avatar).write(message)
            st.caption(timestamp)
        
        # Chat input
        if prompt := st.chat_input("How are you feeling today?"):
            # Add user message to history
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(("You", prompt, timestamp))
            
            # Get bot response
            with st.spinner("Thinking..."):
                response, emotion = chatbot_response(prompt)
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.chat_history.append(("Bot", f"{response} (Mood: {emotion})", timestamp))
                st.rerun()
    
    elif page == "🧘 Wellness":
        st.title("🧘 Wellness Center")
        
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
        st.title("📚 Your Chat History")
        if history := get_chat_history(username):
            for entry in history:
                st.write(f"**You:** {entry['user_message']}")
                st.write(f"**Bot:** {entry['bot_response']} *(Mood: {entry['emotion_detected']})*")
                st.caption(entry['timestamp'])
                st.markdown("---")
        else:
            st.info("No chat history yet")
    
    elif page == "👤 Profile":
        profile_page(username)
    
    elif page == "🚪 Logout":
        st.session_state.clear()
        st.success("Logged out successfully!")
        time.sleep(1)
        st.experimental_set_query_params()
        st.rerun()

if __name__ == "__main__":
    # For local development only
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    main()