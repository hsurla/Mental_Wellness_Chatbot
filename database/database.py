# database/database.py

import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
from bson.objectid import ObjectId

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://rtxklaus1:9Oj0O6RmDeYZM5za@mental-wellness-chatbot.ta0sbvh.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["mental_wellness_db"]
users_collection = db["users"]

# Add a new user during registration
def add_user(username, password):
    users_collection.insert_one({
        "username": username,
        "password": password,
        "mood_history": [],
        "crisis_flags": [],
        "chat_logs": []
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