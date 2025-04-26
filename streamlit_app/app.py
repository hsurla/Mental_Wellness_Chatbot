import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="🧠 Mental Wellness Chatbot", page_icon="💬", layout="wide")

# --- Initialize Session State for Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- App Title ---
st.title("🧠 Mental Wellness Chatbot")
st.subheader("Your friendly companion for mental wellness 🌸")

st.markdown("---")

# --- Display Existing Chat Messages ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User Input ---
user_input = st.chat_input("How are you feeling today?")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate bot response (dummy response for now)
    bot_response = f"I'm here for you. Tell me more about how you're feeling. 🌼"

    # Save bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display bot message
    with st.chat_message("assistant"):
        st.markdown(bot_response)
