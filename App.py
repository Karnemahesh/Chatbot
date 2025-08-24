import os
import io
import streamlit as st
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()

# Prefer Streamlit secrets on Cloud, fallback to .env locally
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("🚨 GOOGLE_API_KEY is missing! Please set it in Streamlit Secrets or in a local .env file.")
    st.stop()

# --------------------------
# OpenAI Client
# --------------------------
client = OpenAI(api_key=GOOGLE_API_KEY)

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Image + Chat Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI Assistant with Image + Chat")

# --------------------------
# Session State Initialization
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------
# Sidebar: Upload Image
# --------------------------
st.sidebar.header("📂 Upload an Image")
uploaded_image = st.sidebar.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_image:
    img = Image.open(uploaded_image)
    st.sidebar.image(img, caption="Uploaded Image", use_column_width=True)

# --------------------------
# Chat Display
# --------------------------
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --------------------------
# Chat Input (auto-clear)
# --------------------------
if prompt := st.chat_input("Type your message..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --------------------------
    # Bot Response
    # --------------------------
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        st.markdown(reply)

    # Save bot reply to history
    st.session_state.messages.append({"role": "assistant", "content": reply})
