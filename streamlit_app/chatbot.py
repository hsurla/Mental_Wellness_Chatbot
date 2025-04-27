# streamlit_app/chatbot.py

import random
import nltk
from database.database import log_chat, log_mood, flag_crisis

# Dummy emotion detection (later we improve)
def detect_emotion(user_message):
    emotions = ['happy', 'sad', 'angry', 'anxious', 'neutral']
    return random.choice(emotions)

# Simple chatbot response
def chatbot_response(user_message):
    responses = [
        "I understand how you feel.",
        "It's okay to feel that way.",
        "Remember to take deep breaths.",
        "You are stronger than you think.",
        "I'm here to listen."
    ]
    return random.choice(responses)

def chat_with_bot(username, user_message):
    emotion = detect_emotion(user_message)
    response = chatbot_response(user_message)

    log_chat(username, user_message, response, emotion)

    if emotion in ['sad', 'angry', 'anxious']:
        log_mood(username, emotion)

    if emotion == 'anxious':
        flag_crisis(username, "Detected signs of anxiety")

    return response, emotion
