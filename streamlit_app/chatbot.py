# streamlit_app/chatbot.py

from nltk.sentiment import SentimentIntensityAnalyzer
from database.database import log_chat, log_mood, flag_crisis
import nltk
nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

def detect_emotion(user_message):
    scores = sia.polarity_scores(user_message)
    compound = scores["compound"]
    if compound >= 0.5:
        return "happy"
    elif compound <= -0.5:
        return "sad"
    elif "anxious" in user_message.lower():
        return "anxious"
    elif "angry" in user_message.lower():
        return "angry"
    else:
        return "neutral"

def chatbot_response(user_message):
    responses = [
        "I understand how you feel.",
        "It's okay to feel that way.",
        "Remember to take deep breaths.",
        "You are stronger than you think.",
        "I'm here to listen."
    ]
    return responses[len(user_message) % len(responses)]

def chat_with_bot(username, user_message):
    emotion = detect_emotion(user_message)
    response = chatbot_response(user_message)

    log_chat(username, user_message, response, emotion)

    if emotion in ['sad', 'angry', 'anxious']:
        log_mood(username, emotion)
    if emotion == 'anxious':
        flag_crisis(username, "Detected signs of anxiety")

    return response, emotion
