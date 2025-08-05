#streamlit_app/profile.py

import streamlit as st
import pandas as pd
from database.database import (
  get_latest_mood, 
  get_total_chat_count, 
  get_total_journal_count,
  get_mood_history
)

def profile_page(username):
  st.title("👤 Your Profile Summary")

  latest_mood, mood_time = get_latest_mood(username)
  total_chats = get_total_chat_count(username)
  total_journals = get_total_journal_count(username)

  st.markdown(f"""
  ### 🧠 Latest Mood
  **Mood:** `{latest_mood}`
  _Last recorded on: {mood_time if mood_time else "N/A"}_

  ---
  ### 💬 Total Chat Sessions
  `{total_chats}` conversations stored

  ---
  ### 📓 Total Journal Entries
  `{total_journals}` personal reflections saved
  """)

  st.markdown("---")
  st.subheader("📈 Mood Tracker")

  mood_data = get_mood_history(username)

  if mood_data:
    df = pd.DataFrame(mood_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['mood'] = df['mood'].str.capitalize()

    mood_to_score = {
      "Happy": 5,
      "Neutral": 3,
      "Anxious": 2,
      "Sad": 1,
      "Angry": 0
      }
    df['mood_score'] = df['mood'].map(mood_to_score)
    df = df.sort_values("timestamp")

    st.line_chart(data=df, x="timestamp", y="mood_score", use_container_width=True)

    mood_labels = ", ".join([f"{k}({v})" for k, v in mood_to_score.items()])
    st.caption(f"Mood Scores: {mood_labels}")
  else:
    st.info("No mood history availables to display chart.")

  st.success("Keep up the great work on your wellness journey! 🌿")