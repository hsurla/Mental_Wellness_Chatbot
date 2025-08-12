# database/database.py
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# MongoDB Atlas Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set")
client = MongoClient(MONGO_URI)
db = client["mental_wellness_db"]
users_collection = db["users"]
reset_tokens_collection = db["reset_tokens"]

# Add a new user during registration
def add_user(email, password=None, username=None, google_id=None):
    user_data = {
        "email": email,
        "username": username,
        "mood_history": [],
        "crisis_flags": [],
        "chat_logs": [],
        "journal_entries": []
    }
    if password:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_data["password"] = hashed_pw
    if google_id:
        user_data["google_id"] = google_id
    
    users_collection.insert_one(user_data)

# Find a user by email
def find_user_by_email(email):
    return users_collection.find_one({"email": email})

# Find a user by username
def find_user_by_username(username):
    return users_collection.find_one({"username": username})

# Find a user by Google ID
def find_user_by_google_id(google_id):
    return users_collection.find_one({"google_id": google_id})

# Update user password
def update_password(email, new_password):
    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    users_collection.update_one(
        {"email": email},
        {"$set": {"password": hashed_pw}}
    )

# Add Google ID to an existing user
def add_google_id(email, google_id):
    users_collection.update_one(
        {"email": email},
        {"$set": {"google_id": google_id}}
    )

# Add chat message to user's history
def log_chat(email, message, bot_response, emotion_detected, intent_detected):
    users_collection.update_one(
        {"email": email},
        {
            "$push": {
                "chat_logs": {
                    "user_message": message,
                    "bot_response": bot_response,
                    "emotion_detected": emotion_detected,
                    "intent_detected": intent_detected,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    )

# Update mood history
def log_mood(email, mood):
    users_collection.update_one(
        {"email": email},
        {
            "$push": {
                "mood_history": {
                    "mood": mood,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    )

# Raise crisis alert if needed
def flag_crisis(email, reason):
    users_collection.update_one(
        {"email": email},
        {
            "$push": {
                "crisis_flags": {
                    "reason": reason,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    )

#get past chats
def get_chat_history(email):
    user = users_collection.find_one({"email": email})
    if user and "chat_logs" in user:
        return user["chat_logs"]
    return []

#save journal entry
def save_journal_entry(email, text):
    users_collection.update_one(
        {"email": email},
        {
            "$push": {
                "journal_entries": {
                    "_id": ObjectId(),
                    "text": text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    )

#get journal entries
def get_journal_entries(email):
    user = users_collection.find_one({"email": email})
    if user and "journal_entries" in user:
        return user["journal_entries"]
    return []

#update journal entry
def update_journal_entry(email, entry_id, new_text):
    users_collection.update_one(
        {"email": email, "journal_entries._id": ObjectId(entry_id)},
        {
            "$set": {
                "journal_entries.$.text": new_text
            }
        }
    )

#delete journal entry
def delete_journal_entry(email, entry_id):
    users_collection.update_one(
        {"email": email},
        {
            "$pull": {
                "journal_entries": {"_id": ObjectId(entry_id)}
            }
        }
    )

#get latest mood
def get_latest_mood(email):
    user = users_collection.find_one({"email": email})
    if user and "mood_history" in user and user["mood_history"]:
        return user["mood_history"][-1]["mood"], user["mood_history"][-1]["timestamp"]
    return "No mood data", None

#get total chat count
def get_total_chat_count(email):
    user = users_collection.find_one({"email": email})
    return len(user.get("chat_logs", [])) if user else 0

#get total journal count
def get_total_journal_count(email):
    user = users_collection.find_one({"email": email})
    return len(user.get("journal_entries", [])) if user else 0

#get mood history
def get_mood_history(email):
    user = users_collection.find_one({"email": email})
    if user and "mood_history" in user:
        return user["mood_history"]
    return []
