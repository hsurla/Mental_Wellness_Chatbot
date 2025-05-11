# streamlit_app/wellness.py

import streamlit as st
import time
import random
import requests

def breathing_exercise():
    st.subheader("🧘 Breathing Exercise")
    st.write("Let's do a quick calming breath together. Inhale... Hold... Exhale...")
    duration = st.slider("Select duration (in seconds):", 10, 60, 30, 10)

    if st.button("Start Breathing"):
        for i in range(0, duration, 5):
            st.write("🌬️ Inhale...")
            time.sleep(2)
            st.write("😮‍💨 Hold...")
            time.sleep(1)
            st.write("🌬️ Exhale...")
            time.sleep(2)
        st.success("Done! Hope you're feeling calmer.")

def meditation_suggestions():
    st.subheader("🧘‍♂️ Meditation Suggestions")
    meditations = [
        "Focus on your breath for 2 minutes.",
        "Try a body scan meditation.",
        "Listen to calming nature sounds for 5 minutes.",
        "Repeat a simple mantra like 'I am calm and safe.'",
        "Try mindful observation — pick an object and study it silently."
    ]
    st.write(random.choice(meditations))

def journaling_prompt():
    st.subheader("📓 Journaling Prompt")
    prompts = [
        "What are three things you're grateful for today?",
        "Describe a recent moment that made you smile.",
        "What’s been weighing on your mind lately?",
        "Write a letter to your future self.",
        "Describe a safe space — real or imagined."
    ]
    st.write(random.choice(prompts))
    response = st.text_area("Write your thoughts here:")
    if st.button("Save Entry"):
        st.success("Entry saved! (Note: You can enhance this by saving to MongoDB later.)")

def daily_tip():
    st.subheader("🌟 Daily Wellness Tip")
    try:
        # Replace with actual API if available
        tip = requests.get("https://zenquotes.io/api/random").json()[0]['q']
        st.info(tip)
    except:
        st.info("Take a few deep breaths and remind yourself that you're doing your best. 💙")

def wellness_page():
    st.title("🌿 Wellness Corner")
    activity = st.selectbox("Choose a Wellness Activity", [
        "Breathing Exercise", "Meditation", "Journaling", "Daily Tip"
    ])

    if activity == "Breathing Exercise":
        breathing_exercise()
    elif activity == "Meditation":
        meditation_suggestions()
    elif activity == "Journaling":
        journaling_prompt()
    elif activity == "Daily Tip":
        daily_tip()
