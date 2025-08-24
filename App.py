import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import os, io
from PIL import Image

# --- CONFIG ---
st.set_page_config(page_title="Multi-Image Chat with Gemini", layout="wide")

# Read API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ GOOGLE_API_KEY environment variable not set.")
    st.stop()
genai.configure(api_key=api_key)

# --- INIT SESSION STATE ---
if "images" not in st.session_state:
    st.session_state.images = []
if "active_image" not in st.session_state:
    st.session_state.active_image = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SAFE GEMINI CALL WITH OFFLINE MODE ---
def safe_generate_content(prompt, image_data=None):
    try:
        if image_data:
            return genai.GenerativeModel("gemini-1.5-flash").generate_content(
                [prompt, image_data]
            ).text
        else:
            return genai.GenerativeModel("gemini-1.5-flash").generate_content(
                prompt
            ).text
    except ResourceExhausted:
        st.warning("⚠️ Gemini API quota exceeded — running in offline mode.")
        return f"[Offline Mode] (Simulated answer) {prompt[:100]}..."

# --- IMAGE ANALYSIS ---
def analyze_image(image_bytes, name):
    image_data = {
        "mime_type": "image/jpeg",
        "data": image_bytes
    }
    description = safe_generate_content(
        "Describe this image in detail, include context and objects you see.", image_data
    )
    caption = safe_generate_content(
        "Write a short catchy caption for this image.", image_data
    )
    tags = safe_generate_content(
        "Generate a list of 5 short tags for this image.", image_data
    )
    story = safe_generate_content(
        "Write a short 3-sentence fictional story inspired by this image.", image_data
    )

    return {
        "DESCRIPTION": description,
        "CAPTION": caption,
        "TAGS": tags,
        "STORY": story
    }

# --- SIDEBAR: UPLOAD & IMAGE LIST ---
with st.sidebar:
    st.header("📂 Upload Images")
    uploaded_files = st.file_uploader(
        "Upload images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True
    )
    if uploaded_files:
        for file in uploaded_files:
            img_bytes = file.read()
            analysis = analyze_image(img_bytes, file.name)
            st.session_state.images.append({
                "name": file.name,
                "data": img_bytes,
                "analysis": analysis
            })
            st.session_state.active_image = len(st.session_state.images) - 1  # select latest

    st.markdown("### 🖼 Images")
    if st.session_state.images:
        with st.container():
            for idx, img in enumerate(st.session_state.images):
                if st.button(img["name"], key=f"img-{idx}"):
                    st.session_state.active_image = idx

# --- MAIN UI ---
st.title("💬 Multi-Image Conversational Chatbot with Gemini")

if st.session_state.active_image is not None:
    img_obj = st.session_state.images[st.session_state.active_image]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(io.BytesIO(img_obj["data"]), caption=img_obj["name"], width=300)
    with col2:
        st.subheader("Image Analysis")
        st.markdown(f"**Description:** {img_obj['analysis']['DESCRIPTION']}")
        st.markdown(f"**Caption:** {img_obj['analysis']['CAPTION']}")
        st.markdown(f"**Tags:** {img_obj['analysis']['TAGS']}")
        st.markdown(f"**Story:** {img_obj['analysis']['STORY']}")

# --- CHAT ---
st.subheader("💬 Conversation")
for sender, msg in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {msg}")

user_msg = st.text_input("Type your message...")
if st.button("Send") and user_msg:
    st.session_state.chat_history.append(("You", user_msg))

    if st.session_state.active_image is not None:
        img_obj = st.session_state.images[st.session_state.active_image]
        bot_reply = safe_generate_content(user_msg, {
            "mime_type": "image/jpeg",
            "data": img_obj["data"]
        })
    else:
        bot_reply = safe_generate_content(user_msg)

    st.session_state.chat_history.append(("Bot", bot_reply))
    st.rerun()  # ✅ Updated for Streamlit 1.32+
