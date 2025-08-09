# streamlit_app/chat_history.py
import streamlit as st
import pandas as pd
from database.database import get_chat_history

def chat_history_page(username):
    st.subheader("🗨️ Chat History")
    
    try:
        # Load chat history
        chat_data = get_chat_history(username)
        if not chat_data:
            st.info("No chat history found.")
            return
            
        # Convert timestamps to datetime for proper sorting
        for chat in chat_data:
            chat['datetime'] = pd.to_datetime(chat['timestamp'])
        
        # Sort by datetime in ascending order (oldest first)
        chat_data.sort(key=lambda x: x['datetime'])
        
        # --- SEARCH FUNCTIONALITY ---
        search_term = st.text_input("🔍 Search your chat history", 
                                   placeholder="Type a keyword to search...")
        
        if search_term:
            filtered_data = []
            for chat in chat_data:
                user_msg = chat.get('user_message', '').lower()
                bot_res = chat.get('bot_response', '').lower()
                
                if search_term.lower() in user_msg or search_term.lower() in bot_res:
                    filtered_data.append(chat)
            chat_data = filtered_data
            
        # Show results count
        result_count = len(chat_data)
        st.caption(f"Found {result_count} conversation{'s' if result_count != 1 else ''}")
        
        # --- EXPORT OPTION ---
        if result_count > 0:
            if st.button("📤 Export to CSV"):
                # Create a DataFrame
                df = pd.DataFrame(chat_data)
                
                # Clean up and select relevant columns
                export_cols = ['timestamp', 'user_message', 'bot_response', 
                              'emotion_detected', 'intent_detected']
                
                # Filter columns that actually exist
                export_df = df[[col for col in export_cols if col in df.columns]]
                
                # Generate CSV
                csv = export_df.to_csv(index=False).encode('utf-8')
                
                # Create download button
                st.download_button(
                    label="💾 Download CSV Now",
                    data=csv,
                    file_name=f"{username}_chat_history.csv",
                    mime="text/csv",
                    key='download-csv'
                )
        
        # --- PAGINATION ---
        items_per_page = 10
        total_pages = max(1, (result_count + items_per_page - 1) // items_per_page)
        page = st.selectbox("Page", range(1, total_pages+1), index=0)
        start_idx = (page-1) * items_per_page
        end_idx = min(start_idx + items_per_page, result_count)
        
        # --- PROPERLY SORTED DISPLAY ---
        if chat_data:
            # Display in chronological order (oldest first)
            for chat in chat_data[start_idx:end_idx]:
                with st.expander(f"💬 {chat.get('timestamp', 'Unknown date')}", expanded=False):
                    # User message
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        st.markdown("**You**")
                        st.markdown("🧑")
                    with col2:
                        st.markdown(f"```\n{chat.get('user_message', 'No message recorded')}\n```")
                    
                    # Bot response
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        st.markdown("**Bot**")
                        st.markdown("🤖")
                    with col2:
                        st.markdown(f"```\n{chat.get('bot_response', 'No response recorded')}\n```")
                    
                    # Metadata
                    if 'emotion_detected' in chat or 'intent_detected' in chat:
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col1:
                            if emotion := chat.get('emotion_detected'):
                                st.caption(f"🎭 **Emotion:** {emotion}")
                        with col2:
                            if intent := chat.get('intent_detected'):
                                st.caption(f"🎯 **Intent:** {intent}")
        else:
            st.info("No conversations match your search criteria")
            
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        st.info("Please try again later or contact support")