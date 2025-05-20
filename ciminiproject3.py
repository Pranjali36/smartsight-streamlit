import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import base64

# ------------------------ Set Page Config FIRST ------------------------
st.set_page_config(page_title="SmartSight", layout="centered")

# ------------------------ Custom Styling ------------------------
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f8f9fa;
        padding: 2rem;
    }

    h1, h2, h3, h4 {
        color: #1e3a5f;
        font-weight: 600;
    }

    .block-container {
        padding-top: 2rem;
    }

    .stButton button {
        background-color: #2c6ef2;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: 0.3s ease;
    }

    .stButton button:hover {
        background-color: #154ec1;
        transform: scale(1.03);
    }

    .stImage > img {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    a {
        text-decoration: none;
        font-weight: 500;
    }

    .stMarkdown a {
        color: #2c6ef2;
    }

    </style>
    """, unsafe_allow_html=True)

# ------------------------ Core Enhancer ------------------------
def enhance_image_clahe(image):
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return enhanced_img

# ------------------------ Download Link Generator ------------------------
st.markdown("---")
st.subheader("✨ Refined Image")

# Display enhanced image
st.image(enhanced_img, caption="Your enhanced image is ready!", use_column_width=True)

# Convert to download-ready format
_, buffer = cv2.imencode(".png", enhanced_img)
image_bytes = buffer.tobytes()

# 📥 Download button
st.download_button(
    label="📥 Download Enhanced Image",
    data=image_bytes,
    file_name="enhanced_image.png",
    mime="image/png",
    use_container_width=True
)
# ------------------------ Streamlit UI ------------------------
local_css()

st.title("🔍 SmartSight")
st.subheader("Real-Time Low-Light Enhancement and Alert System")

input_method = st.radio("Choose input method:", ("Upload Image", "Capture from Camera"))

image_np = None
img = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload a low-light image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(img)

elif input_method == "Capture from Camera":
    camera_image = st.camera_input("Capture image using your device")
    if camera_image:
        img = Image.open(camera_image).convert("RGB")
        image_np = np.array(img)

if image_np is not None:
    st.subheader("📸 Original Image")
    st.image(image_np, channels="RGB", use_container_width=True)

    if st.button("✨ Enhance Image"):
        enhanced_np = enhance_image_clahe(image_np)
        enhanced_img = Image.fromarray(enhanced_np)

        st.subheader("Optimized Image")
        st.image(enhanced_img, channels="RGB", use_container_width=True)

        st.markdown(get_image_download_link(enhanced_img), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("💾 Save space! Upload to Cloud")
        st.markdown(
            """
            <a href="https://drive.google.com/drive/my-drive" target="_blank">
                🚀 Drive upload
            </a>
            """, unsafe_allow_html=True
        )

st.markdown("---")
st.markdown("🔐 This tool runs fully on-device. No images are stored or shared.")
