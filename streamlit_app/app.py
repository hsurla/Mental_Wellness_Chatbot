import streamlit as st
import random

# --- Page Config ---
st.set_page_config(page_title="🧠 Mental Wellness Chatbot", page_icon="💬", layout="wide")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Empathetic Response Generator ---
def generate_response(user_message):
    user_message = user_message.lower()

    # Keywords and possible responses
    responses = {
        "sad": [
            "I'm sorry you're feeling sad. 💙 I'm here to listen.",
            "It's okay to feel sad sometimes. Do you want to talk about it? 🌻"
        ],
        "happy": [
            "That's wonderful! 😊 Tell me what's making you happy!",
            "Your happiness is contagious! 🌟 Let's celebrate the good moments."
        ],
        "anxious": [
            "Anxiety can be tough. 🫶 Let's do some breathing exercises if you'd like.",
            "I'm here for you. Take a deep breath. 🌬️ You are stronger than you think."
        ],
        "stressed": [
            "Stress can feel overwhelming. 🌿 Would you like some tips to relax?",
            "I'm here to support you. Maybe we can try a small breathing exercise? 🌸"
        ],
        "angry": [
            "It's okay to feel angry. 😠 Want to talk about what's upsetting you?",
            "I hear you. Sometimes expressing your anger can help. 🧘"
        ],
        "lonely": [
            "You are not alone. 🫂 I'm here with you.",
            "Feeling lonely is hard. 🕊️ Talking helps — let's chat."
        ],
        "default": [
            "I'm here for you. Tell me more about how you're feeling. 🌼",
            "Feel free to share anything on your mind. 🧡"
        ]
    }

    # Match keywords
    for keyword, replies in responses.items():
        if keyword in user_message:
            return random.choice(replies)

    return random.choice(responses["default"])

# --- App Title ---
st.title("🧠 Mental Wellness Chatbot")
st.subheader("Your friendly companion for mental wellness 🌸")
st.markdown("---")

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User Input ---
user_input = st.chat_input("How are you feeling today?")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate bot response
    bot_response = generate_response(user_input)

    # Save bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display bot message
    with st.chat_message("assistant"):
        st.markdown(bot_response)
