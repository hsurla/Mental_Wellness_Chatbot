# streamlit_app/sidebar.py

import streamlit as st

def sidebar():
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio("Go to", ["Chatbot", "Wellness", "Chat History", "Profile", "Journal","Logout"])

        st.markdown("---")
        st.subheader("🎨 Chatbot Tone")

        tone = st.radio(
            "Choose a tone for the chatbot:",
            ["Calm 🧘", "Motivational 💪", "Friendly 🤝"],
            index=["Calm 🧘", "Motivational 💪", "Friendly 🤝"].index(
                st.session_state.get("tone_ui", "Calm 🧘")
            )
        )

        # Store clean tone string in session_state for use in chatbot
        tone_mapping = {
            "Calm 🧘": "calm",
            "Motivational 💪": "motivational",
            "Friendly 🤝": "friendly"
        }

        st.session_state["tone_ui"] = tone
        st.session_state["tone"] = tone_mapping[tone]
    return page

