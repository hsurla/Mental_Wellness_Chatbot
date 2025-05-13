# streamlit_app/chatbot.py


from database.database import log_chat, log_mood, flag_crisis
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('punkt_tab')
nltk.download('vader_lexicon')
from datetime import datetime
import text2emotion as te
import random

sia = SentimentIntensityAnalyzer()

def detect_emotion(user_message):
    #detects emotion from the user's message.
    emotion_scores = te.get_emotion(user_message)

    if not emotion_scores or all(score == 0 for score in emotion_scores.values()):
        return "neutral"

    #Get emotion with highest score
    raw_emotion = max(emotion_scores, key=emotion_scores.get).lower()

    emotion_map = {
        "happy": "happy",
        "sad": "sad",
        "angry": "angry",
        "fear": "anxious",
        "surprise": "neutral"
    }

    return emotion_map.get(raw_emotion, "neutral")

#intent detection (simple rule-based)
def detect_intent(user_message):
    msg = user_message.lower()
    if any(word in msg for word in ["help", "advice", "suggest", "what should", "how can", "recommend", "guide", "tips"]):
        return "seeking advice"

    elif any(word in msg for word in ["angry", "annoyed", "frustrated", "hate", "rage", "furious", "pissed"]):
        return "venting"

    elif any(word in msg for word in ["thank you", "thanks", "grateful", "appreciate", "gratitude"]):
        return "gratitude"

    elif any(word in msg for word in ["happy", "excited", "joy", "amazing", "feeling great", "positive"]):
        return "sharing joy"

    elif any(word in msg for word in ["hi", "hello", "hey", "yo", "greetings"]):
        return "greeting"

    elif any(word in msg for word in ["alone", "tired", "done", "exhausted", "no one", "overwhelmed", "can't take"]):
        return "venting"

    # Fallback
    return "casual"

#response map (emotion + intent -> list of responses)
response_map = {
    ("sad", "venting"): [
        "I'm here for you. Want to talk more about it?",
        "It's okay to feel this way. Let's work through it together.",
        "That must be really hard. I'm listening whenever you're ready.",
        "You don't have to go through this alone. I'm here with you.",
        "It's totally valid to feel low sometimes. Let's talk it out."
    ],
    ("sad", "seeking advice"): [
        "I'm here to help. Would it help to explore some coping strategies?",
        "You've taken the first step by talking about it. Let's find a way forward.",
        "Can I share some self-care techniques that might help?",
        "Let's take it one step at a time — I've got you."
    ],
    ("anxious", "venting"):[
        "Anxiety can be overwhelming. Want to share what's on your mind?",
        "Would it help if we slowed down and talked through it?",
        "I'm here — no pressure. You can tell me everything or nothing.",
        "That sounds tough. I'm proud of you for opening up.",
        "We can handle it together. Start from wherever you feel comfortable."
    ],
    ("anxious", "seeking advice"): [
        "Would you like to try a calming exercise together?",
        "Let's take a few deep breaths. I can guide you if you'd like.",
        "Do grounding techniques sound helpful right now?",
        "Let's focus on one small thing at a time — that often helps."
    ],
    ("happy", "gratitude"): [
        "That's wonderful to hear! I'm glad you're feeling good. 😊",
        "You deserve every bit of joy you're feeling today!",
        "I'm happy to hear that — let's keep that energy going!",
        "That made my day too. 💛"
    ],
    ("angry", "venting"): [
        "It's okay to feel angry. I'm here to listen without judgment.",
        "Want to talk about what triggered your anger?",
        "Anger is a valid emotion — we can unpack it together.",
        "You're allowed to feel this way. I'm with you.",
        "Would it help to express your thoughts openly? I'm all ears.",
        "Let it out - I'm here for you."
    ],
    ("happy", "sharing joy"):[
        "Tell me more — I love hearing about good moments!",
        "Let's celebrate that win together! 🎉",
        "I'm smiling with you! What made it special?",
        "That sounds amazing! Keep the good vibes coming."
    ],
    ("neutral", "casual"): [
        "Tell me more about how you're feeling today.",
        "I'm here for anything you'd like to share.",
        "Whether it's big or small, I'm listening.",
        "How has your day been so far?",
        "I'm ready to talk about whatever's on your mind."
    ],
    ("neutral", "greeting"): [
        "Hi there 👋 How are you feeling today?",
        "Hey! I'm here if you want to chat.",
        "Hello! What would you like to talk about today?",
        "Welcome! Feel free to share whatever's on your mind."
    ],
    ("sad", "gratitude"): [
        "Thank you for trusting me — I'm here whenever you need.",
        "I'm really glad to be here with you.",
        "That means a lot. Let's keep going together."
    ],
    ("anxious", "gratitude"): [
        "I'm proud of you for expressing gratitude despite the anxiety.",
        "That says a lot about your strength. I'm here for you.",
        "It's inspiring to see you hold onto hope — keep going!"
    ]
}

default_response_map = {
    "sad": [
        "I'm here for you. Take your time. 🧘",
        "You're not alone. I'm with you whenever you're ready to talk.",
        "It's completely okay to feel down sometimes.",
        "Talking can help. I'm here if you feel like sharing.",
        "You're doing better than you think. One step at a time. 💙"
    ],
    "anxious": [
        "Let's breathe together. You're doing okay. 🧘",
        "You're safe here. Let's take it one moment at a time.",
        "Would grounding techniques help? I can guide you through one.",
        "Whatever you're feeling is valid — let's sit with it for a moment.",
        "You've already taken the first step by opening up. That matters."
    ],
    "angry": [
        "It's okay to feel this way. Want to talk about it calmly?",
        "Let it out — I'm here without judgment.",
        "We all have tough moments. You're allowed to feel this.",
        "You deserve space to process. I'm here for you.",
        "Would expressing what made you feel this way help?"
    ],
    "happy": [
        "That's wonderful! 😊 What made your day better?",
        "I'm so glad to hear that! Want to tell me more?",
        "Hearing that brings me joy too. ✨",
        "Love the positivity! Let's keep that going!",
        "You're glowing today — keep it up! 💛"
    ],
    "neutral": [
        "How are you feeling right now? I'm here for anything. 🤝",
        "I'm listening. Tell me whatever's on your mind.",
        "Just checking in — how's your day going?",
        "I'm here to chat about anything, big or small.",
        "Want to talk or just sit together in silence? Either is okay."
    ]
}

def chitchat_response(user_message):
    msg = user_message.lower().strip()

    chitchat_map = {
        # Casual / Greeting
        "hi": "Hi there! 😊",
        "hello": "Hello! How can I support you today?",
        "hey": "Hey! How are you feeling?",
        "how are you": "I'm just a chatbot, but I'm here and happy to help you!",
        "what are you doing": "I'm here to listen and chat with you. 🧘",
        "who are you": "I'm your Mental Wellness Chatbot, always ready to listen.",
        "are you real": "I'm virtual, but I'm really here for you. 🤝",
        "what's your name": "You can call me your Wellbeing Buddy. 💬",
        "thank you": "You're welcome! Always here for you. 💛",
        "thanks": "Happy to help!",

        # Flirty / Childish
        "i like you": "I'm here to support you, not for romantic chats. 😊",
        "i love you": "That's kind of you, but I'm just a helpful bot. 💬",
        "will you marry me": "Haha, I'm flattered, but I'm just here to help. 🧘",
        "you're cute": "Thank you, but let's focus on how you're feeling today. 🤝",
        "where do you live": "I'm a virtual assistant — I live in your browser!",
        "you are stupid": "I'm here to help, not to be perfect. Let's refocus. 🧘",
        "i hate you": "That's okay — I'm still here to support you.",

        # Serious / Crisis
        "i'm going to hurt myself": "I'm really concerned. Please talk to someone you trust. You're not alone. 💛",
        "i want to die": "You're not alone. Please consider reaching out to a helpline. You matter. 🙏",
        "nobody cares about me": "I care. You're important, and I'm here for you. 💙"
    }

    return chitchat_map.get(msg)


def chat_with_bot(username, user_message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #step 1: check for casual/chitchat message
    chitchat = chitchat_response(user_message)
    if chitchat:
        # Flag if it's a crisis message
        if any(keyword in user_message.lower() for keyword in ["hurt myself", "want to die", "kill myself", "end my life"]):
            flag_crisis(username, "Detected self-harm or suicidal message")

        # Log as chitchat with default neutral emotion/intent
        log_chat(username, user_message, chitchat, emotion_detected="neutral", intent_detected="chitchat")
        return chitchat, "neutral", timestamp

    #step 2: proceed with emotion + intent logic
    emotion = detect_emotion(user_message)
    intent = detect_intent(user_message)
    

    # Try to get a response from the full (emotion, intent) pair
    responses = response_map.get((emotion, intent))

    if not responses:
        responses = default_response_map.get(emotion,[
            "I'm here to listen. Take your time.",
            "Feel free to share anything you'd like. 🤝"
        ])

    response = random.choice(responses)  # pick one randomly for natural variety

    #log the chat
    log_chat(username, user_message, response, emotion, intent)

    if emotion in ['sad', 'angry', 'anxious']:
        log_mood(username, emotion)
    if emotion == 'anxious':
        flag_crisis(username, "Detected signs of anxiety")

    return response, emotion, timestamp
