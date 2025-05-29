# streamlit_app/register.py

import streamlit as st
import requests
from database.database import add_user, find_user

def registration_page():
    st.title("Create an Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    #recaptcha
    st.markdown("""
                <script src='https://www.google.com/recaptcha/api.js'></script>
                <form action="?" method="POST">
                <div class="g-recaptcha" data-sitekey="6LcSOU4rAAAAAGphyafMH1TIE7TuoGiaMB9GKwAP"></div>
                <br/>
                </form>
                """, unsafe_allow_html=True)
    
    # Get the recaptcha token from query params (Streamlit workaround)
    query_params = st.experimental_get_query_params()
    recaptcha_token = query_params.get("g-recaptcha-response", [None])[0]

    if not recaptcha_token:
        st.warning("⚠️ Please complete the reCAPTCHA.")
        return

    # Verify the token with Google
    recaptcha_secret = "6LcSOU4rAAAAAFTf5LUY429GMWEC1m3egehwsUs8"
    response = requests.post(
    "https://www.google.com/recaptcha/api/siteverify",
    data={"secret": recaptcha_secret, "response": recaptcha_token}
    )
    result = response.json()

    if not result.get("success"):
        st.error("❌ reCAPTCHA verification failed.")
        return

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif find_user(username):
            st.error("Username already exists!")
        else:
            add_user(username, password)
            st.success("Account created successfully! Please Login.")
