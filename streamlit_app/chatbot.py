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
from typing import Dict, List, Tuple, Optional

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
        """Simple noun extraction"""
        words = re.findall(r"\b\w+\b", text.lower())
        return [w for w in words if w in ['work', 'family', 'school', 'friend', 'sleep', 'exam', 'job', 'relationship']]

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
            elif sentiment['compound'] > 0.5:
                return "happy"
            return "neutral"

        raw_emotion = max(emotion_scores, key=emotion_scores.get).lower()
        
        emotion_map = {
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "fear": "anxious",
            "surprise": "neutral",
            "disgust": "angry"  # Map disgust to anger
        }
        return emotion_map.get(raw_emotion, "neutral")
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return "neutral"

def detect_intent(user_message: str) -> str:
    """Rule-based intent detection with enhanced patterns"""
    msg = user_message.lower()
    
    intent_patterns = {
        "seeking advice": [
            r"\b(help|advice|suggest|what should|how can|recommend|guide|tips)\b",
            r"what (would|should) you (suggest|recommend)",
            r"how (do|can) I (handle|deal with)"
        ],
        "venting": [
            r"\b(angry|annoyed|frustrated|hate|rage|furious|pissed)\b",
            r"\b(alone|tired|done|exhausted|no one|overwhelmed)\b",
            r"can('|no)t take (it|this|anymore)"
        ],
        "gratitude": [
            r"\b(thank you|thanks|grateful|appreciate|gratitude)\b",
            r"i (really )?appreciate",
            r"that('s| is) helpful"
        ],
        "sharing joy": [
            r"\b(happy|excited|joy|amazing|feeling great|positive)\b",
            r"i('m| am) (so )?(happy|excited)",
            r"(good|great) news"
        ],
        "greeting": [
            r"\b(hi|hello|hey|yo|greetings)\b",
            r"good (morning|afternoon|evening)",
            r"how(('s| is) it )?going"
        ]
    }
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, msg):
                return intent
                
    return "casual"

def _extract_slot(text: str, pattern: str) -> Optional[str]:
    """Extracts a slot value from text using regex"""
    match = re.search(pattern, text.lower())
    return match.group(0) if match else None

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
        follow_ups = {
            "sad": "You've mentioned this feeling before - would coping strategies help?",
            "anxious": "I remember this anxiety - shall we try a new approach?",
            "angry": "This anger seems familiar - want to explore its roots?"
        }
        response += " " + follow_ups.get(emotion, "Let's explore this together.")
    
    # Add contextual follow-up 30% of the time
    if random.random() < 0.3:
        follow_ups = {
            "sad": [
                "What happened to make you feel this way?",
                "Would describing it in more detail help?",
                "How is this affecting your daily life?"
            ],
            "anxious": [
                "What part feels most overwhelming?",
                "Can we break this down into smaller pieces?",
                "Would ranking your worries help prioritize?"
            ],
            "angry": [
                "What specifically triggered this reaction?",
                "Would expressing it differently help?",
                "How might you want this situation to change?"
            ],
            "happy": [
                "What made this so positive for you?",
                "How can you build on this good feeling?",
                "Who could you share this joy with?"
            ]
        }
        if emotion in follow_ups:
            response += " " + random.choice(follow_ups[emotion])
    
    return response

# Response maps with added dynamic slots
response_map = {
    ("sad", "venting"): [
        "I'm here for you about [topic]. Want to talk more?",
        "It's okay to feel this way. Let's work through [topic] together.",
        "That must be really hard. I'm listening whenever you're ready.",
        "You don't have to go through [topic] alone. I'm here with you.",
        "It's valid to feel low about [topic]. Let's talk it out."
    ],
    ("sad", "seeking advice"): [
        "I'm here to help with [topic]. Would coping strategies help?",
        "You've taken the first step. Let's find a way forward with [topic].",
        "Can I share self-care techniques for [topic]?",
        "Let's take [topic] one step at a time."
    ],
    ("anxious", "venting"): [
        "[Topic] anxiety can be overwhelming. Want to share more?",
        "Would slowing down about [topic] help?",
        "I'm here — no pressure about [topic].",
        "That sounds tough. I'm proud of you for opening up.",
        "We can handle [topic] together."
    ],
    ("anxious", "seeking advice"): [
        "Would a calming exercise help with [topic]?",
        "Let's breathe through [topic] together.",
        "Do grounding techniques for [topic] sound helpful?",
        "Let's focus on one small part of [topic]."
    ],
    ("happy", "gratitude"): [
        "That's wonderful to hear! I'm glad you're feeling good. 😊",
        "You deserve every bit of joy you're feeling today!",
        "I'm happy to hear that — let's keep that energy going!",
        "That made my day too. 💛"
    ],
    ("angry", "venting"): [
        "It's okay to feel angry about [topic]. I'm listening.",
        "Want to talk about what triggered your anger?",
        "Anger about [topic] is valid — let's unpack it.",
        "You're allowed to feel this way. I'm with you.",
        "Would expressing thoughts about [topic] help?"
    ],
    ("happy", "sharing joy"): [
        "Tell me more about [topic]! I love hearing good news!",
        "Let's celebrate that [topic] win together! 🎉",
        "I'm smiling with you about [topic]!",
        "That [topic] news sounds amazing!"
    ],
    ("neutral", "casual"): [
        "Tell me more about [topic].",
        "I'm here for anything about [topic] you'd like to share.",
        "Whether it's [topic] or something else, I'm listening.",
        "How has [topic] been going for you?"
    ],
    ("neutral", "greeting"): [
        "Hi there 👋 How are you feeling today?",
        "Hey! I'm here if you want to chat.",
        "Hello! What would you like to talk about today?",
        "Welcome back! Feel free to share what's on your mind."
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
            "It's okay to feel sad — you're doing your best."
        ],
        "anxious": [
            "Breathe deeply. You're doing okay. 🧘",
            "Let's pause for a moment together.",
            "We can take things one step at a time.",
            "Just rest here with me for a moment.",
            "Let's allow ourselves a slow, calm reset."
        ],
        "angry": [
            "Anger is okay. Let's explore it calmly.",
            "I'm right here with you, no pressure. 🧘",
            "Let's channel that energy into understanding.",
            "Take your time to express it. I'm listening.",
            "Let's breathe through this storm together."
        ],
        "happy": [
            "That's peaceful to hear. Stay centered and joyful.",
            "So nice to hear positivity. 🧘",
            "Keep your calm joy flowing today!",
            "That's a gentle ray of sunshine — thank you.",
            "Glad you're feeling good inside. 😊"
        ],
        "neutral": [
            "I'm here with a calm space for you. 🧘",
            "Let's take today slow. How are you feeling?",
            "You can always share what's on your mind.",
            "Whatever you're feeling — it's welcome here.",
            "We don't need to rush. I'm here with you."
        ]
    },
    "motivational": {
        "sad": [
            "You're stronger than you think — keep going 💪",
            "Every day is a new chance to grow.",
            "I'm here cheering you on — you're not alone.",
            "Even storms pass — you've got this.",
            "You're making progress, even when it's hard."
        ],
        "anxious": [
            "You've got this — take a breath and push forward!",
            "Even small steps matter. Let's take one together. 💪",
            "Courage isn't the absence of fear, it's moving through it.",
            "We rise through the challenges — one breath at a time.",
            "Let's turn this worry into momentum. You're capable."
        ],
        "angry": [
            "Let's turn that fire into power! 💪",
            "Speak your truth — it's valid and important.",
            "Let it out, and let's rebuild stronger.",
            "That energy can fuel your next move.",
            "Anger means you care — and that matters."
        ],
        "happy": [
            "That's the energy we love! Keep it up! 💪",
            "You're absolutely glowing today — keep going!",
            "Success starts with this kind of mindset!",
            "Let's ride that wave — amazing energy!",
            "You're unstoppable today — love to see it!"
        ],
        "neutral": [
            "Let's find what fires you up today 💪",
            "Every moment is a chance to grow.",
            "What's one thing we can tackle today?",
            "Even ordinary days hold great potential.",
            "Let's make today count together!"
        ]
    },
    "friendly": {
        "sad": [
            "Hey, I've got your back 💛",
            "Rough days happen, but I'm always here.",
            "Wanna talk it out like pals?",
            "It's okay, buddy — I'm listening.",
            "You can vent here anytime, friend."
        ],
        "anxious": [
            "Deep breaths, buddy. You're not alone. 🤝",
            "We're in this together. Let's chill and chat.",
            "Just you and me, let's talk it out!",
            "You've got a friend in me — always.",
            "I'm here, like a true friend would be."
        ],
        "angry": [
            "Let it all out, friend. No judgment. 🤝",
            "We all have our days — I'm here to hear you.",
            "Hit me with it — I'm listening like a friend.",
            "I've got your back, even on the hard days.",
            "Say what you need — I'll still be here."
        ],
        "happy": [
            "Woohoo! Love hearing that! 🤗",
            "That's awesome, buddy! High five! ✋",
            "Good vibes only — tell me more!",
            "You made my day too!",
            "Your joy is contagious 😄"
        ],
        "neutral": [
            "Hey there! What's up? 🤝",
            "Feel like chatting today?",
            "Let's catch up on how you're feeling.",
            "I'm here, friend — anytime you wanna talk.",
            "Want to share something from your day?"
        ]
    }
}

def chitchat_response(user_message: str) -> Optional[str]:
    """Handles simple predefined chats with enhanced patterns"""
    msg = user_message.lower().strip()
    
    chitchat_map = {
        # Greetings
        r"\b(hi|hello|hey)\b": "Hi there! 😊 How are you feeling today?",
        r"how are you": "I'm just a chatbot, but I'm here and happy to help you!",
        
        # Identity
        r"who are you": "I'm your Mental Wellness Chatbot, always ready to listen.",
        r"what('s| is) your name": "You can call me your Wellbeing Buddy. 💬",
        r"are you real": "I'm virtual, but I'm really here for you. 🤝",
        
        # Gratitude
        r"\b(thank you|thanks)\b": "You're welcome! Always here for you. 💛",
        r"i (really )?appreciate": "That means a lot to me. I'm glad I could help.",
        
        # Crisis
        r"\b(hurt myself|kill myself|end my life)\b": 
            "I'm really concerned. Please talk to someone you trust. You're not alone. 💛",
        r"nobody cares": "I care. You're important, and I'm here for you. 💙",
        
        # Miscellaneous
        r"what are you doing": "I'm here to listen and chat with you. 🧘",
        r"where do you live": "I'm a virtual assistant — I live in your browser!",
        r"i (like|love) you": "I'm here to support you as your wellness companion. 💬",
        r"marry me": "Haha, I'm flattered, but I'm just here to help. 🧘",
        r"you('re| are) (cute|stupid|dumb)": "I'm here to help however I can. Let's focus on you."
    }
    
    for pattern, response in chitchat_map.items():
        if re.fullmatch(pattern, msg):
            return response
            
    return None

def chat_with_bot(username: str, user_message: str) -> Tuple[str, str, str]:
    """Main chatbot function with enhanced dynamic responses"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Step 1: Check for casual/chitchat
    chitchat = chitchat_response(user_message)
    if chitchat:
        emotion = detect_emotion(user_message)
        
        # Crisis detection
        crisis_phrases = [
            "hurt myself", "want to die", "kill myself", 
            "end my life", "suicide", "can't go on"
        ]
        if any(phrase in user_message.lower() for phrase in crisis_phrases):
            flag_crisis(username, "Detected self-harm or suicidal message")
            chitchat = "I'm deeply concerned. Please reach out to a trusted person or helpline. You matter so much. 💛"
        
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