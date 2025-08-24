# App.py

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()

def get_api_key():
    """
    Retrieve the Google API key.
    Priority: Streamlit Secrets -> Local .env -> OS Environment
    """
    api_key = None

    # Try Streamlit Cloud Secrets
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]

    # Fallback to .env / system
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")

    return api_key


# --------------------------
# Initialize API Key
# --------------------------
GOOGLE_API_KEY = get_api_key()

if not GOOGLE_API_KEY:
    st.error("🚨 GOOGLE_API_KEY is missing! Please set it in Streamlit Secrets (on Cloud) or in a local .env file.")
    st.stop()

# Initialize OpenAI Client with Google API key
client = OpenAI(api_key=GOOGLE_API_KEY)


# --------------------------
# Streamlit App UI
# --------------------------
st.set_page_config(page_title="Image Segmentation + Chatbot", layout="wide")

st.title("🖼️ Image Segmentation + 💬 Chatbot")

# Conversation state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Image upload
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Save user input
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call API (replace with your actual Google Gemini / OpenAI request)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 👈 swap for Gemini model if using Google
            messages=st.session_state.messages
        )
        bot_reply = response.choices[0].message.content

    except Exception as e:
        bot_reply = f"⚠️ API Error: {str(e)}"

    # Save bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# Render conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

