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

def daily_tip():
    st.subheader("🌟 Daily Wellness Tips")

    # Create a two-column layout: [spacer, button]
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔁"):
            st.rerun()

    tips = []

    # Try to get tips from the API
    for _ in range(3):
        try:
            response = requests.get("https://www.affirmations.dev/")
            data = response.json()
            tip = data.get("affirmation")
            if tip and tip not in tips:
                tips.append(tip)
        except:
            break

    # Use fallback tips if needed
    if len(tips) < 3:
        offline_tips = [
            "Take a deep breath — you're doing your best.",
            "Let yourself rest without guilt.",
            "Drink a glass of water and stretch.",
            "Focus on what you can control — and let the rest go.",
            "You deserve kindness — especially from yourself.",
            "Small steps forward are still progress.",
            "It’s okay to pause. You don’t have to rush.",
            "Celebrate small wins today."
        ]
        tips.extend(random.sample(offline_tips, 3 - len(tips)))

    # Display the tips
    for i, tip in enumerate(tips, 1):
        st.success(f"{i}. {tip}")

def wellness_page():
    st.title("🌿 Wellness Corner")
    activity = st.selectbox("Choose a Wellness Activity", [
        "Breathing Exercise", "Meditation", "Journaling", "Daily Tip"
    ])

    if activity == "Breathing Exercise":
        breathing_exercise()
    elif activity == "Meditation":
        meditation_suggestions()
    elif activity == "Daily Tip":
        daily_tip()
