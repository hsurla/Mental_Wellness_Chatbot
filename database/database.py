# database/database.py
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt
import os

# MongoDB Atlas Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["mental_wellness_db"]
users_collection = db["users"]
reset_tokens_collection = db["reset_tokens"]

# Add a new user during registration
def add_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users_collection.insert_one({
        "username": username,
        "password": hashed_pw,
        "mood_history": [],
        "crisis_flags": [],
        "chat_logs": [],
        "journal_entries": []
    })

# Find a user during login
def find_user(username):
    return users_collection.find_one({"username": username})

# Add chat message to user's history
def log_chat(username, message, bot_response, emotion_detected, intent_detected):
    users_collection.update_one(
        {"username": username},
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
def log_mood(username, mood):
    users_collection.update_one(
        {"username": username},
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
def flag_crisis(username, reason):
    users_collection.update_one(
        {"username": username},
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
def get_chat_history(username):
    user = users_collection.find_one({"username": username})
    if user and "chat_logs" in user:
        return user["chat_logs"]
    return []


def save_journal_entry(username, text):
    users_collection.update_one(
        {"username": username},
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

def get_journal_entries(username):
    user = users_collection.find_one({"username": username})
    if user and "journal_entries" in user:
        return user["journal_entries"]
    return []

def update_journal_entry(username, entry_id, new_text):
    users_collection.update_one(
        {"username": username, "journal_entries._id": ObjectId(entry_id)},
        {
            "$set": {
                "journal_entries.$.text": new_text
            }
        }
    )

def delete_journal_entry(username, entry_id):
    users_collection.update_one(
        {"username": username},
        {
            "$pull": {
                "journal_entries": {"_id": ObjectId(entry_id)}
            }
        }
    )


def get_latest_mood(username):
    user = users_collection.find_one({"username": username})
    if user and "mood_history" in user and user["mood_history"]:
        return user["mood_history"][-1]["mood"], user["mood_history"][-1]["timestamp"]
    return "No mood data", None

def get_total_chat_count(username):
    user = users_collection.find_one({"username": username})
    return len(user.get("chat_logs", [])) if user else 0

def get_total_journal_count(username):
    user = users_collection.find_one({"username": username})
    return len(user.get("journal_entries", [])) if user else 0

def get_mood_history(username):
    user = users_collection.find_one({"username": username})
    if user and "mood_history" in user:
        return user["mood_history"]
    return []
