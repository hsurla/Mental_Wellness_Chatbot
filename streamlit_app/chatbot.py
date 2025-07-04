from database.database import log_chat, log_mood, flag_crisis
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('punkt_tab')
nltk.download('vader_lexicon')
from datetime import datetime
import text2emotion as te
import random

# Initialize analyzer
sia = SentimentIntensityAnalyzer()

class ChatBot:
    def __init__(self):
        self.response_map = self._initialize_response_map()
        self.tone_response_map = self._initialize_tone_response_map()
        self.default_response_map = self._initialize_default_response_map()
        
    def detect_emotion(self, user_message):
        """Detects emotion from the user's message."""
        emotion_scores = te.get_emotion(user_message)

        if not emotion_scores or all(score == 0 for score in emotion_scores.values()):
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

    def detect_intent(self, user_message):
        """Simple rule-based intent detection"""
        msg = user_message.lower()
        if any(word in msg for word in ["help", "advice", "suggest", "what should", "how can"]):
            return "seeking advice"
        elif any(word in msg for word in ["angry", "annoyed", "frustrated", "hate"]):
            return "venting"
        elif any(word in msg for word in ["thank you", "thanks", "grateful"]):
            return "gratitude"
        elif any(word in msg for word in ["happy", "excited", "joy"]):
            return "sharing joy"
        elif any(word in msg for word in ["hi", "hello", "hey"]):
            return "greeting"
        elif any(word in msg for word in ["alone", "tired", "done"]):
            return "venting"
        return "casual"

    def _initialize_response_map(self):
        """Initialize the main response mapping"""
        return {
            ("sad", "venting"): ["I'm here for you. Want to talk more about it?"],
            # ... [rest of your response mappings] ...
        }

    def _initialize_tone_response_map(self):
        """Initialize tone-specific responses"""
        return {
            "calm": {
                "sad": ["I'm here with you. Let's take a deep breath together."],
                # ... [rest of tone mappings] ...
            },
            # ... [other tones] ...
        }

    def _initialize_default_response_map(self):
        """Initialize default responses"""
        return {
            "sad": ["I'm here for you. Take your time."],
            # ... [rest of default mappings] ...
        }

    def chitchat_response(self, user_message):
        """Handle simple chitchat interactions"""
        msg = user_message.lower().strip()
        chitchat_map = {
            "hi": "Hi there! 😊",
            # ... [rest of your chitchat mappings] ...
        }
        return chitchat_map.get(msg)

    def generate_response(self, username, user_message):
        """Main method to generate bot response"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check for chitchat first
        chitchat = self.chitchat_response(user_message)
        if chitchat:
            emotion = self.detect_emotion(user_message)
            self._log_interaction(username, user_message, chitchat, emotion, "chitchat")
            return chitchat, "neutral", timestamp

        # Process emotion and intent
        emotion = self.detect_emotion(user_message)
        intent = self.detect_intent(user_message)

        # Get appropriate response
        responses = self.response_map.get((emotion, intent))
        if not responses:
            tone = "calm"  # Default tone
            tone_fallbacks = self.tone_response_map.get(tone, self.default_response_map)
            responses = tone_fallbacks.get(emotion, self.default_response_map.get(emotion, 
                ["I'm here to listen. Take your time."]))

        response = random.choice(responses)
        self._log_interaction(username, user_message, response, emotion, intent)
        return response, emotion, timestamp

    def _log_interaction(self, username, user_message, response, emotion, intent):
        """Handle all logging operations"""
        log_chat(username, user_message, response, emotion, intent)
        if emotion in ['sad', 'angry', 'anxious']:
            log_mood(username, emotion)
        if emotion == 'anxious':
            flag_crisis(username, "Detected signs of anxiety")
        if any(keyword in user_message.lower() for keyword in ["hurt myself", "want to die"]):
            flag_crisis(username, "Detected self-harm message")

# Create a singleton instance
chatbot_instance = ChatBot()

def chat_with_bot(username, user_message):
    """Public interface for the chatbot"""
    return chatbot_instance.generate_response(username, user_message)