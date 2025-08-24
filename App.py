import os
import io
import base64
import uuid
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("🚨 GOOGLE_API_KEY is missing! Please set it in Streamlit Secrets or .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

# -------------------------
# App Config
# -------------------------
st.set_page_config(page_title="Image Segmentation + Chatbot", layout="wide")

# -------------------------
# Initialize session state
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "images" not in st.session_state:
    st.session_state.images = {}
if "active_image" not in st.session_state:
    st.session_state.active_image = None

# -------------------------
# Helper Functions
# -------------------------
def encode_image(image_file) -> str:
    img = Image.open(image_file).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def safe_generate_content(prompt, image=None):
    try:
        if image:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": f"data:{image['mime_type']};base64,{image['data']}"}
                    ]}
                ]
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# -------------------------
# Sidebar (Image Upload)
# -------------------------
st.sidebar.header("📂 Upload Images")
uploaded_files = st.sidebar.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

for uploaded_file in uploaded_files:
    img_key = uploaded_file.name
    if img_key not in st.session_state.images:
        st.session_state.images[img_key] = {
            "data": encode_image(uploaded_file),
            "mime_type": "image/jpeg"
        }

if st.session_state.images:
    st.sidebar.subheader("🖼️ Uploaded Images")
    for img_key in list(st.session_state.images.keys()):
        if st.sidebar.button(f"Select {img_key}"):
            st.session_state.active_image = img_key
    if st.sidebar.button("Clear Images"):
        st.session_state.images.clear()
        st.session_state.active_image = None

# -------------------------
# Main Layout
# -------------------------
st.title("🤖 Image Segmentation & Chatbot")

col1, col2 = st.columns([1, 2])

# ---- Left: Active Image Preview ----
with col1:
    st.subheader("Active Image")
    if st.session_state.active_image:
        img_obj = st.session_state.images[st.session_state.active_image]
        st.image(base64.b64decode(img_obj["data"]), caption=st.session_state.active_image, use_container_width=True)
    else:
        st.info("No image selected.")

# ---- Right: Chat ----
with col2:
    st.subheader("💬 Conversation")

    chat_container = st.container()
    with chat_container:
        for sender, msg in st.session_state.chat_history:
            st.markdown(f"**{sender}:** {msg}")

    # Safe input box (auto clears)
    temp_key = str(uuid.uuid4())  # unique key per render
    user_msg = st.text_input("Type your message...", key=temp_key)

    if st.button("Send", key="send-btn") and user_msg.strip():
        msg = user_msg.strip()
        st.session_state.chat_history.append(("You", msg))

        if st.session_state.active_image is not None:
            img_obj = st.session_state.images[st.session_state.active_image]
            bot_reply = safe_generate_content(msg, img_obj)
        else:
            bot_reply = safe_generate_content(msg)

        st.session_state.chat_history.append(("Bot", bot_reply))

        st.experimental_rerun()  # rerun clears the input box
