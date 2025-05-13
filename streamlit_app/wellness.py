#streamlit_app/wellness.py

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

    categories = {
        "Breathing": [
            "Focus on your breath for 2 minutes.",
            "Inhale for 4 seconds, hold for 4, exhale for 4.",
            "Count 10 breaths slowly, restarting if you lose focus."
        ],
        "Visualization": [
            "Visualize a peaceful place — forest, beach, or mountain.",
            "Picture a calming light filling your body with warmth."
        ],
        "Mantra": [
            "Repeat a phrase like 'I am calm' for 3 minutes.",
            "Silently say 'Inhale calm, exhale tension' with each breath."
        ],
        "Body Scan": [
            "Mentally scan your body from toes to head, releasing tension.",
            "Focus on how each part of your body feels without judgment."
        ]
    }

    category = st.selectbox("Choose a meditation style", list(categories.keys()))

    suggestion = random.choice(categories[category])
    st.write(f"🧘 Try this: *{suggestion}*")

    if st.button("🔁 Need Another Suggestion?"):
        st.rerun()

    st.markdown("---")
    st.markdown("🕒 **Want to set a 1-minute mindfulness timer?**")

    if st.button("Start 1-Minute Timer"):
        countdown = st.empty()
        for i in range(60, 0, -1):
            countdown.markdown(f"⏳ Time left: **{i}** seconds")
            time.sleep(1)
        countdown.markdown("✅ Time's up! Hope you're feeling a bit more relaxed.")


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
