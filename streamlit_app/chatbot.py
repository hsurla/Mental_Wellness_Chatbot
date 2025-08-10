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
import re
from collections import defaultdict
from typing import Dict, List, Tuple

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Dynamic response configuration
DYNAMIC_SLOTS = {
    "topic": r"\b(work|family|school|relationship|health)\b",
    "time_ref": r"\b(yesterday|today|last week|this month)\b"
}

class ConversationMemory:
    """Tracks conversation history and user patterns"""
    def __init__(self):
        self.history = []
        self.user_profile = defaultdict(list)
    
    def update(self, username: str, message: str, emotion: str, intent: str):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
            "emotion": emotion,
            "intent": intent
        }
        self.history.append(entry)
        
        # Track recurring emotions
        if emotion in ['sad', 'anxious', 'angry']:
            self.user_profile[f"recent_{emotion}_count"] = self.user_profile.get(f"recent_{emotion}_count", 0) + 1
            
        # Extract and store key topics
        nouns = self._extract_nouns(message)
        if nouns:
            self.user_profile["common_topics"].extend(nouns)
    
    def _extract_nouns(self, text: str) -> List[str]:
        """Simple noun extraction (can be enhanced with NLP later)"""
        words = re.findall(r"\b\w+\b", text.lower())
        return [w for w in words if w in ['work', 'family', 'school', 'friend', 'sleep']]

# Initialize conversation memory
memory = ConversationMemory()

def detect_emotion(user_message: str) -> str:
    """Enhanced emotion detection with sentiment fallback"""
    try:
        emotion_scores = te.get_emotion(user_message)
        
        if not emotion_scores or all(score == 0 for score in emotion_scores.values()):
            # Fallback to sentiment analysis
            sentiment = sia.polarity_scores(user_message)
            if sentiment['compound'] < -0.5:
                return "sad"
            return "neutral"

        raw_emotion = max(emotion_scores, key=emotion_scores.get).lower()
        
        emotion_map = {
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "fear": "anxious",
            "surprise": "neutral"
        }
        return emotion_map.get(raw_emotion, "neutral")
    except:
        return "neutral"  # Safe fallback

def detect_intent(user_message: str) -> str:
    """Rule-based intent detection"""
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
    return "casual"

def _extract_slot(text: str, pattern: str) -> str:
    """Extracts a slot value from text using regex"""
    match = re.search(pattern, text.lower())
    return match.group(1) if match else None

def enhance_response(response: str, user_message: str, emotion: str, username: str) -> str:
    """Adds dynamic personalization to responses"""
    # Extract dynamic slots from user message
    slots = {
        "topic": _extract_slot(user_message, DYNAMIC_SLOTS["topic"]),
        "time_ref": _extract_slot(user_message, DYNAMIC_SLOTS["time_ref"])
    }
    
    # Replace slots in response
    for slot, value in slots.items():
        if value and f"[{slot}]" in response:
            response = response.replace(f"[{slot}]", value)
    
    # Add memory-based follow-up
    if memory.user_profile.get(f"recent_{emotion}_count", 0) > 1:
        response += f" You've mentioned this feeling before - would you like to explore it differently today?"
    
    # Add contextual follow-up 30% of the time
    if random.random() < 0.3:
        follow_ups = {
            "sad": ["What happened to make you feel this way?", "Would describing it help?"],
            "anxious": ["What part feels most overwhelming?", "Can we break this down?"],
            "angry": ["What triggered this reaction?", "Would expressing it differently help?"]
        }
        if emotion in follow_ups:
            response += " " + random.choice(follow_ups[emotion])
    
    return response

# Original response maps remain unchanged
response_map = {
    ("sad", "venting"): [
        "I'm here for you. Want to talk more about [topic]?",
        "It's okay to feel this way about [topic]. Let's work through it together.",
        "That must be really hard. I'm listening whenever you're ready.",
        "You don't have to go through [topic] alone. I'm here with you.",
        "It's totally valid to feel low sometimes. Let's talk it out."
    ],
    # ... (keep all your original response_map entries)
}

default_response_map = {
    "sad": [
        "I'm here for you. Take your time. 🧘",
        # ... (keep all your original default_response_map entries)
    ],
    # ... (keep all other emotion entries)
}

tone_response_map = {
    "calm": {
        "sad": [
            "I'm here with you. Let's take a deep breath together. 🧘",
            # ... (keep all your original tone responses)
        ],
        # ... (keep all other tone entries)
    },
    # ... (keep motivational and friendly tones)
}

def chitchat_response(user_message: str) -> str:
    """Handles simple predefined chats"""
    msg = user_message.lower().strip()
    chitchat_map = {
        "hi": "Hi there! 😊",
        "hello": "Hello! How can I support you today?",
        # ... (keep all your original chitchat_map entries)
    }
    return chitchat_map.get(msg)

def chat_with_bot(username: str, user_message: str) -> Tuple[str, str, str]:
    """Main chatbot function with enhanced dynamic responses"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Step 1: Check for casual/chitchat
    chitchat = chitchat_response(user_message)
    if chitchat:
        emotion = detect_emotion(user_message)
        
        if any(keyword in user_message.lower() for keyword in ["hurt myself", "want to die", "kill myself", "end my life"]):
            flag_crisis(username, "Detected self-harm or suicidal message")
        
        log_chat(username, user_message, chitchat, emotion, "chitchat")
        
        if emotion in ['sad', 'angry', 'anxious']:
            log_mood(username, emotion)
            if emotion == 'anxious':
                flag_crisis(username, "Detected signs of anxiety")
        
        memory.update(username, user_message, emotion, "chitchat")
        return chitchat, "neutral", timestamp

    # Step 2: Process emotion and intent
    emotion = detect_emotion(user_message)
    intent = detect_intent(user_message)
    
    # Get base response
    responses = response_map.get((emotion, intent))
    
    if not responses:
        tone = st.session_state.get("tone", "calm").lower()
        tone_fallbacks = tone_response_map.get(tone, default_response_map)
        responses = tone_fallbacks.get(emotion, default_response_map.get(emotion, [
            "I'm here to listen. Take your time.",
            "Feel free to share anything you'd like. 🤝"
        ]))
    
    response = random.choice(responses)
    
    # Enhance with dynamic features
    response = enhance_response(response, user_message, emotion, username)
    
    # Log and update memory
    log_chat(username, user_message, response, emotion, intent)
    memory.update(username, user_message, emotion, intent)
    
    if emotion in ['sad', 'angry', 'anxious']:
        log_mood(username, emotion)
        if emotion == 'anxious':
            flag_crisis(username, "Detected signs of anxiety")
    
    return response, emotion, timestamp