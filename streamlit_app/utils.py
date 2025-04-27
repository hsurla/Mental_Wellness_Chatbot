# streamlit_app/utils.py

import time
import streamlit as st

def typing_animation(text):
    for word in text.split():
        st.write(word, end=" ", unsafe_allow_html=True)
        time.sleep(0.2)

def show_loading(message="Thinking..."):
    with st.spinner(message):
        time.sleep(2)
