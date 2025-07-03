import streamlit as st
from datetime import datetime
import time
import random
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.chatbot import chat_with_bot
from streamlit_app.sidebar import sidebar
from database.database import get_chat_history
from streamlit_app.wellness import wellness_page
from streamlit_app.profile import profile_page

# Added fun activities directly in the main file
def get_fun_activity():
    """Returns random fun activity (joke/trivia/boredom buster)"""
    activities = {
        "bored": [
            "Try a 5-minute yoga flow",
            "Doodle something abstract",
            "Learn a TikTok dance",
            "Organize your phone photos",
            "Try a new recipe with ingredients you have"
        ],
        "trivia": [
            "Bananas are berries, but strawberries aren't!",
            "The shortest war in history was 38 minutes (Britain vs. Zanzibar, 1896)",
            "A group of flamingos is called a 'flamboyance'",
            "The Eiffel Tower grows 6 inches in summer due to thermal expansion"
        ],
        "joke": [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call fake spaghetti? An impasta!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "How do you organize a space party? You planet!"
        ]
    }
    category = random.choice(list(activities.keys()))
    return f"💡 {random.choice(activities[category])}"

def get_healthy_snack():
    """Returns random healthy snack suggestion"""
    snacks = [
        "Apple slices with almond butter",
        "Greek yogurt with berries",
        "Handful of mixed nuts",
        "Carrot sticks with hummus",
        "Rice cakes with avocado",
        "Hard-boiled eggs with sea salt"
    ]
    return random.choice(snacks)

def main():
    st.set_page_config(page_title="Mental Wellness Chatbot", layout="wide")

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
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for sender, msg, *rest in st.session_state.chat_history:
            time_sent = rest[0] if rest else "Unknown time"
            st.markdown(f"**{'🧑 You' if sender == 'You' else '🤖 Bot'}:** {msg}  \n<sub>{time_sent}</sub>", 
                       unsafe_allow_html=True)

        user_message = st.text_input("Type your message", key="chat_input", label_visibility="collapsed")
        if st.button("📤 Send") and user_message.strip():
            current_time = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(("You", user_message, current_time))
            response, emotion, _ = chat_with_bot(st.session_state['username'], user_message)
            st.session_state.chat_history.append(("Bot", f"{response} (Mood: {emotion})", current_time))
            st.rerun()

    elif page == "Wellness":
        wellness_page()
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎲 Activity Suggestion")
            st.info(get_fun_activity())
            if st.button("🔀 Get Another Activity"):
                st.rerun()
                
        with col2:
            st.subheader("🥗 Healthy Snack")
            st.success(get_healthy_snack())
            if st.button("🔀 Get Another Snack"):
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