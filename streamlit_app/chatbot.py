# streamlit_app/chatbot.py


from database.database import log_chat, log_mood, flag_crisis
import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('punkt_tab')
nltk.download('vader_lexicon')
from datetime import datetime
import text2emotion as te
import random
import requests
from streamlit_app.login import login_page
from streamlit_app.register import registration_page
from streamlit_app.sidebar import sidebar
from database.database import get_chat_history
from streamlit_app.wellness import wellness_page
from streamlit_app.profile import profile_page
from streamlit_app.fun_support import get_fun_activity, get_healthy_snack

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

tone_response_map = {
    "calm": {
        "sad": [
            "I'm here with you. Let's take a deep breath together. 🧘",
            "Feel free to share, I'm here to listen with calm and care.",
            "You're safe. Let's work through this slowly.",
            "You're not alone. Let's gently navigate this together.",
            "It's okay to feel sad — you're doing your best.",
            "We don't have to rush. I'm here whenever you're ready.",
            "Even gentle steps forward matter. You're doing fine.",
            "Take all the time you need. I'm not going anywhere.",
            "Sometimes sitting with feelings is the bravest thing to do.",
            "This is a soft space to just be — no expectations."
        ],
        "anxious": [
            "Breathe deeply. You're doing okay. 🧘",
            "Let's pause for a moment together.",
            "We can take things one step at a time.",
            "Just rest here with me for a moment.",
            "Let's allow ourselves a slow, calm reset. 🧘",
            "It's okay to feel overwhelmed — you're still grounded.",
            "Let's take three slow breaths together. In... and out.",
            "You are safe here, just as you are.",
            "This too shall pass — let's wait it out gently.",
            "I'm here, offering calm when things feel stormy."
        ],
        "angry": [
            "Anger is okay. Let's explore it calmly.",
            "I'm right here with you, no pressure. 🧘",
            "Let's channel that energy into understanding.",
            "Take your time to express it. I'm listening.",
            "Let's breathe through this storm together.",
            "Anger means something matters deeply to you.",
            "We can unpack this together, slowly.",
            "Your feelings are welcome here — all of them.",
            "Even anger has a story. Let's listen to it.",
            "Let's settle the waves, one breath at a time."
        ],
        "happy": [
            "That's peaceful to hear. Stay centered and joyful.",
            "So nice to hear positivity. 🧘",
            "Keep your calm joy flowing today!",
            "That's a gentle ray of sunshine — thank you.",
            "Glad you're feeling good inside. 😊",
            "Cherish this moment — it's beautiful.",
            "Your light is warming — thank you for sharing it.",
            "I'm smiling with you in this calm joy.",
            "Hold onto that peace — it suits you.",
            "Let's preserve this good energy together."
        ],
        "neutral": [
            "I'm here with a calm space for you. 🧘",
            "Let's take today slow. How are you feeling?",
            "You can always share what's on your mind.",
            "Whatever you're feeling — it's welcome here.",
            "We don't need to rush. I'm here with you.",
            "Want to sit in silence or chat gently?",
            "Just being here is enough sometimes.",
            "Let's ease into the day together.",
            "You don't need a reason to speak. Just say hi.",
            "I'm here as a calm companion whenever you need."
        ]
    },

    "motivational": {
        "sad": [
            "You're stronger than you think — keep going 💪",
            "Every day is a new chance to grow.",
            "I'm here cheering you on — you're not alone.",
            "Even storms pass — you've got this.",
            "You're making progress, even when it's hard.",
            "This moment doesn't define you — your resilience does.",
            "You've come so far already — don't stop now!",
            "Let's rise together — one small victory at a time.",
            "Feel it, face it, and keep moving forward. 💪",
            "You're more powerful than this tough moment."
        ],
        "anxious": [
            "You've got this — take a breath and push forward!",
            "Even small steps matter. Let's take one together. 💪",
            "Courage isn't the absence of fear, it's moving through it.",
            "We rise through the challenges — one breath at a time.",
            "Let's turn this worry into momentum. You're capable.",
            "You're doing better than you think — keep breathing.",
            "Focus on what you *can* control — that's your power.",
            "This feeling is temporary — your strength isn't.",
            "You've faced worse — and you came through.",
            "Let's own this moment with confidence. 💪"
        ],
        "angry": [
            "Let's turn that fire into power! 💪",
            "Speak your truth — it's valid and important.",
            "Let it out, and let's rebuild stronger.",
            "That energy can fuel your next move.",
            "Anger means you care — and that matters.",
            "Use it to spark change. You can do that.",
            "This is your chance to grow beyond it.",
            "Power comes when we harness emotion wisely.",
            "I believe in your ability to overcome this.",
            "Even strong emotions can push us to level up."
        ],
        "happy": [
            "That's the energy we love! Keep it up! 💪",
            "You're absolutely glowing today — keep going!",
            "Success starts with this kind of mindset!",
            "Let's ride that wave — amazing energy!",
            "You're unstoppable today — love to see it!",
            "You're setting the tone — and it's powerful!",
            "Keep stacking those wins — one by one!",
            "Momentum is on your side — let's build it!",
            "Your joy is like rocket fuel — let's go!",
            "You're radiating strength and joy today!"
        ],
        "neutral": [
            "Let's find what fires you up today 💪",
            "Every moment is a chance to grow.",
            "What's one thing we can tackle today?",
            "Even ordinary days hold great potential.",
            "Let's make today count together!",
            "Stay open — today might surprise you.",
            "Let's set a small goal. Ready?",
            "You've got more in you than you know.",
            "Neutral is a launchpad — let's go higher.",
            "Let's create momentum from this moment!"
        ]
    },

    "friendly": {
        "sad": [
            "Hey, I've got your back 💛",
            "Rough days happen, but I'm always here.",
            "Wanna talk it out like pals?",
            "It's okay, buddy — I'm listening.",
            "You can vent here anytime, friend.",
            "Let's get through this together, like friends do.",
            "I'm just a chat away — always.",
            "No shame in sad days — we all have them.",
            "You're doing better than you think.",
            "We got this. One step at a time, friend."
        ],
        "anxious": [
            "Deep breaths, buddy. You're not alone. 🤝",
            "We're in this together. Let's chill and chat.",
            "Just you and me, let's talk it out!",
            "You've got a friend in me — always.",
            "I'm here, like a true friend would be.",
            "Let's sit through the worry — I've got snacks!",
            "Want to laugh a little to ease the tension?",
            "Nothing too big for us to handle together!",
            "I'm right here, pal. Keep breathing.",
            "One message at a time — we'll figure this out."
        ],
        "angry": [
            "Let it all out, friend. No judgment. 🤝",
            "We all have our days — I'm here to hear you.",
            "Hit me with it — I'm listening like a friend.",
            "I've got your back, even on the hard days.",
            "Say what you need — I'll still be here.",
            "Vent away! I won't take it personally.",
            "Friend to friend — let's cool off together.",
            "I'm still on your team, no matter what.",
            "You don't need to hold back here.",
            "Let's talk it out — or yell it out. Your call!"
        ],
        "happy": [
            "Woohoo! Love hearing that! 🤗",
            "That's awesome, buddy! High five! ✋",
            "Good vibes only — tell me more!",
            "You made my day too!",
            "Your joy is contagious 😄",
            "That's the spirit, my friend!",
            "Let's keep this good mood rolling!",
            "Tell me more — I love your energy!",
            "You're shining bright today! 🌟",
            "This calls for a virtual celebration!"
        ],
        "neutral": [
            "Hey there! What's up? 🤝",
            "Feel like chatting today?",
            "Let's catch up on how you're feeling.",
            "I'm here, friend — anytime you wanna talk.",
            "Want to share something from your day?",
            "Nothing's too boring to talk about here!",
            "Let's see where the chat takes us!",
            "We don't need a reason to hang out!",
            "You can say anything — no judgment zone.",
            "I'm all ears — what's on your mind?"
        ]
    }
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
        emotion = detect_emotion(user_message)

        if any(keyword in user_message.lower() for keyword in ["hurt myself", "want to die", "kill myself", "end my life"]):
            flag_crisis(username, "Detected self-harm or suicidal message")
        
        log_chat(username, user_message, chitchat, emotion_detected=emotion, intent_detected="chitchat")

        if emotion in ['sad', 'angry', 'anxious']:
            log_mood(username, emotion)
        if emotion == 'anxious':
            flag_crisis(username, "Detected signs of anxiety")
        return chitchat, "neutral", timestamp

    #step 2: proceed with emotion + intent logic
    emotion = detect_emotion(user_message)
    intent = detect_intent(user_message)
    

    # Try to get a response from the full (emotion, intent) pair
    responses = response_map.get((emotion, intent))

    if not responses:
        # Get tone (defaults to "calm" if not set)
        tone = st.session_state.get("tone", "calm").lower()
        tone_fallbacks = tone_response_map.get(tone, default_response_map)
        responses = tone_fallbacks.get(emotion, default_response_map.get(emotion, [
            "I'm here to listen. Take your time.",
            "Feel free to share anything you'd like. 🤝"
        ]))

    response = random.choice(responses)  # pick one randomly for natural variety

    #log the chat
    log_chat(username, user_message, response, emotion, intent)

    if emotion in ['sad', 'angry', 'anxious']:
        log_mood(username, emotion)
    if emotion == 'anxious':
        flag_crisis(username, "Detected signs of anxiety")

    return response, emotion, timestamp
