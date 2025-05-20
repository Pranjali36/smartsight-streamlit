import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import base64

# Set page configuration (must be first Streamlit command)
st.set_page_config(page_title="SmartSight", layout="centered")

# ----------------- Styling -----------------
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        color: #003366;
        text-align: center;
    }
    .stButton > button {
        background-color: #004080;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6em 1.2em;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #0059b3;
        color: white;
    }
    .stLink {
        color: #004080;
        font-weight: bold;
        text-decoration: none;
    }
    .stLink:hover {
        color: #0073e6;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Header -----------------
st.title("🔍 SmartSight - Low Light Image Enhancer")

# ----------------- Upload Section -----------------
upload_method = st.radio("Select Image Input Method", ("📸 Camera", "📁 Upload from device"))

uploaded_image = None
if upload_method == "📸 Camera":
    uploaded_image = st.camera_input("Capture an image")
else:
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

enhanced_image = None

# ----------------- Enhancement -----------------
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("✨ Enhance Image"):
        # Convert to OpenCV format
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Convert to LAB color space and apply CLAHE
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        enhanced_image = Image.fromarray(enhanced_rgb)

        st.image(enhanced_image, caption="🔆 Enhanced Image", use_column_width=True)

        # Convert to downloadable format
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format="PNG")
        byte_data = buffer.getvalue()
        b64 = base64.b64encode(byte_data).decode()
        href = f'<a href="data:file/png;base64,{b64}" download="enhanced_image.png">📥 <b>Download Enhanced Image</b></a>'
        st.markdown(href, unsafe_allow_html=True)

        # Add Google Drive redirection link
        st.markdown("---")
        st.markdown("🚀 Want to save it to your Google Drive?")
        st.markdown('<a class="stLink" href="https://drive.google.com/drive/my-drive" target="_blank">Click here to open your Drive and upload manually</a>', unsafe_allow_html=True)
