# streamlit_app/login.py

import streamlit as st
import bcrypt
import streamlit.components.v1 as components
import requests
from streamlit_js_eval import streamlit_js_eval
from database.database import find_user, add_user

def login_page():
    st.markdown("### 🔐 Sign in with Google")

    components.html(f"""
<html>
  <head>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-auth-compat.js"></script>
  </head>
  <body>
    <button onclick="signInWithGoogle()">Sign in with Google</button>
    <input type="text" id="email_output" style="display:none"/>

    <script>
      const firebaseConfig = {{
        apiKey: "AIzaSyBQgmp214Gvi8PcmaX56NP7HjXPbXl0sws",
        authDomain: "mental-wellness-chatbot-a77b2.firebaseapp.com",
        projectId: "mental-wellness-chatbot-a77b2",
        storageBucket: "mental-wellness-chatbot-a77b2.firebasestorage.app",
        messagingSenderId: "639432204726",
        appId: "1:639432204726:web:e52557c4ef6e5a6987a117"
      }};
      firebase.initializeApp(firebaseConfig);

      function signInWithGoogle() {{
        const provider = new firebase.auth.GoogleAuthProvider();
        firebase.auth().signInWithPopup(provider).then((result) => {{
          const user = result.user;
          document.getElementById("email_output").value = user.email;
        }}).catch((error) => {{
          console.error(error);
        }});
      }}
    </script>
  </body>
</html>
""", height=250)

    # Listen for email from Firebase
    email = streamlit_js_eval(
    js_expressions="document.getElementById('email_output')?.value",
    key="google_email"
)


    if email:
        st.success(f"✅ Logged in as: {email}")
        st.session_state['username'] = email
        st.session_state['logged_in'] = True

        # Create Google user if new
        if not find_user(email):
            add_user(email, "")  # Password empty for Google login users

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

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


    if st.button("Login"):
        user = find_user(username)
        if user:
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.success(f"Welcome, {username}!")
                st.session_state["username"] = username
                st.session_state['logged_in'] = True
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")
