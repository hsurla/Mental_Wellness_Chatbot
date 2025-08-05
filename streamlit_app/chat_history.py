# streamlit_app/chat_history.py
import streamlit as st
from database.database import get_chat_history

def chat_history_page(username):
    st.subheader("🗨️ Chat History")
    
    try:
        chat_data = get_chat_history(username)
        if not chat_data:
            st.info("No chat history found.")
            return
            
        st.info(f"Found {len(chat_data)} chat records")
        
        # Pagination
        items_per_page = 10
        total_pages = (len(chat_data) //items_per_page) + 1
        page = st.selectbox("Page", range(1, total_pages+1), index=0)
        start_idx = (page-1) * items_per_page
        end_idx = start_idx + items_per_page
        
        for chat in reversed(chat_data[start_idx:end_idx]):
            with st.container():
                st.markdown(f"**{chat.get('timestamp', 'No timestamp')}**")
                
                user_message = chat.get('user_message', 'No message recorded')
                st.markdown(f"**You:** {user_message}")
                
                bot_response = chat.get('bot_response', 'No response recorded')
                st.markdown(f"**Bot:** {bot_response}")
                
                # Optional fields
                if emotion := chat.get('emotion_detected'):
                    st.markdown(f"*Detected emotion: {emotion}*")
                if intent := chat.get('intent_detected'):
                    st.markdown(f"*Intent: {intent}*")
                    
                st.markdown("---")
                
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        st.info("Please try again later or contact support")