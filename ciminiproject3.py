import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import base64

# Enhance image using CLAHE
def enhance_image_clahe(image):
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return enhanced_img

# Create download link for enhanced image
def get_image_download_link(img, filename='enhanced_image.png'):
    buffered = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(buffered.name, format='PNG')
    with open(buffered.name, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="{filename}">📥 Download Enhanced Image</a>'
    return href

# Streamlit UI
st.set_page_config(page_title="SmartSight", layout="centered")
st.title("🔍 SmartSight: Low-Light Image Enhancer")

input_method = st.radio("Select input method:", ("Upload Image", "Capture from Camera"))

image_np = None
img = None
if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(img)
elif input_method == "Capture from Camera":
    camera_image = st.camera_input("Capture an image")
    if camera_image is not None:
        img = Image.open(camera_image).convert("RGB")
        image_np = np.array(img)

if image_np is not None:
    st.subheader("📸 Original Image")
    st.image(image_np, channels="RGB", use_container_width=True)

    # Button to enhance image
    if st.button("✨ Enhance Image"):
        enhanced_np = enhance_image_clahe(image_np)
        enhanced_img = Image.fromarray(enhanced_np)

        st.subheader("🔧 Enhanced Image")
        st.image(enhanced_img, channels="RGB", use_container_width=True)

        # Download link
        st.markdown(get_image_download_link(enhanced_img), unsafe_allow_html=True)

        # Redirect to Google Drive
        st.markdown("---")
        st.markdown("After downloading, you can upload the image to your Google Drive:")
        st.markdown(
            """
            <a href="https://drive.google.com/drive/my-drive" target="_blank">
                🚀 Cloud Upload
            </a>
            """,
            unsafe_allow_html=True
        )
