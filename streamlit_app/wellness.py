import streamlit as st
import time
import random
import requests
from streamlit_app.fun_support import get_fun_activity, get_healthy_snack

# Constants
FALLBACK_TIPS = [
    "Take a deep breath — you're doing your best.",
    "Let yourself rest without guilt.",
    "Drink a glass of water and stretch.",
    "Focus on what you can control — and let the rest go.",
    "You deserve kindness — especially from yourself.",
    "Small steps forward are still progress.",
    "It's okay to pause. You don't have to rush.",
    "Celebrate small wins today."
]

MINDFULNESS_VIDEO = "https://www.youtube.com/watch?v=inpok4MKVLM"

def wellness_center_page():
    """Main wellness center page with all wellness features"""
    st.title("🧈 Wellness Center")

    # Initialize session state variables if they don't exist
    if 'current_activity' not in st.session_state:
        st.session_state.current_activity = get_fun_activity()
    
    if 'current_snack' not in st.session_state:
        st.session_state.current_snack = get_healthy_snack()
    
    # Activity and snack suggestions
    col1, col2 = st.columns(2)
    with col1:
        activity_suggestion()
    
    with col2:
        snack_suggestion()

    # Wellness activities
    with st.expander("🧘 Breathing Exercise", expanded=False):
        breathing_exercise()
        
    with st.expander("🧘‍♂️ Meditation Suggestions", expanded=False):
        meditation_suggestions()
        
    with st.expander("🌟 Daily Wellness Tips", expanded=False):
        daily_tip()
    
    # Mindfulness video
    st.markdown("---")
    st.header("Mindfulness Exercise")
    st.video(MINDFULNESS_VIDEO)

def activity_suggestion():
    """Display a fun activity suggestion"""
    st.header("Activity Suggestion")
    
    # Display activity using st.empty() placeholder
    activity_placeholder = st.empty()
    activity_placeholder.info(st.session_state.current_activity)
    
    # Button to update activity
    if st.button("Get new activity", key="wellness_activity_btn"):
        st.session_state.current_activity = get_fun_activity()
        activity_placeholder.info(st.session_state.current_activity)

def snack_suggestion():
    """Display a healthy snack idea"""
    st.header("Healthy Snack Idea")
    
    # Display snack using st.empty() placeholder
    snack_placeholder = st.empty()
    snack_placeholder.success(st.session_state.current_snack)
    
    # Button to update snack
    if st.button("Get new snack", key="wellness_snack_btn"):
        st.session_state.current_snack = get_healthy_snack()
        snack_placeholder.success(st.session_state.current_snack)

def breathing_exercise():
    """Guided breathing exercise"""
    st.subheader("🧘 Breathing Exercise")
    st.write("Let's do a quick calming breath together. Inhale... Hold... Exhale...")
    duration = st.slider("Select duration (in seconds):", 10, 60, 30, 10, key="breathing_duration_slider")

    if st.button("Start Breathing", key="breathing_start_btn"):
        placeholder = st.empty()
        progress_bar = st.progress(0)
        
        for i in range(0, duration, 5):
            # Update progress
            progress = min(1.0, i / duration)
            progress_bar.progress(progress)
            
            # Breathing phases
            for phase in [
                ("🌬️ Inhale...", 2),
                ("😮‍💨 Hold...", 1),
                ("🌬️ Exhale...", 2)
            ]:
                placeholder.markdown(
                    f"<div style='text-align: center; padding: 20px;'>"
                    f"<h1>{phase[0]}</h1>"
                    f"<p>Time remaining: {duration-i}s</p>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                time.sleep(phase[1])
                
        placeholder.empty()
        progress_bar.empty()
        st.success("Done! Hope you're feeling calmer.")

def meditation_suggestions():
    """Provide meditation suggestions"""
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

    category = st.selectbox(
        "Choose a meditation style", 
        list(categories.keys()), 
        key="meditation_style_select"
    )

    suggestion = random.choice(categories[category])
    st.write(f"🧘 Try this: *{suggestion}*")

    if st.button("🔁 Need Another Suggestion?", key="meditation_refresh_btn"):
        st.rerun()

    st.markdown("---")
    st.markdown("🕒 **Want to set a 1-minute mindfulness timer?**")

    if st.button("Start 1-Minute Timer", key="meditation_timer_btn"):
        countdown = st.empty()
        progress_bar = st.progress(0)
        
        for i in range(60, 0, -1):
            progress = (60 - i) / 60
            countdown.markdown(f"⏳ **Time left: {i} seconds**")
            progress_bar.progress(progress)
            time.sleep(1)
            
        countdown.markdown("✅ **Time's up!** Hope you're feeling more relaxed.")
        progress_bar.empty()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_daily_tips():
    """Get daily wellness tips with API fallback"""
    tips = []
    try:
        for _ in range(3):
            response = requests.get("https://www.affirmations.dev/", timeout=3)
            data = response.json()
            if tip := data.get("affirmation"):
                tips.append(tip)
    except:
        pass
    
    return tips if tips else random.sample(FALLBACK_TIPS, 3)

def daily_tip():
    """Display daily wellness tips"""
    st.subheader("🌟 Daily Wellness Tips")

    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔁", key="daily_tip_refresh_btn"):
            st.cache_data.clear()
            st.rerun()

    tips = get_daily_tips()

    for i, tip in enumerate(tips, 1):
        st.success(f"{i}. {tip}")