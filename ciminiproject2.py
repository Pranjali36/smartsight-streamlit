import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="SmartSight", layout="centered")

# Google Drive uploader
def upload_to_gdrive(image_bytes, filename):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "smart_service_account.json",
            scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        service = build('drive', 'v3', credentials=credentials)
        media = MediaIoBaseUpload(image_bytes, mimetype='image/jpeg', resumable=True)

        file_metadata = {
            'name': filename,
            'parents': ['appDataFolder']  # Change this to your folder ID if needed
        }
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        return f"https://drive.google.com/uc?id={file_id}"
    except Exception as e:
        st.error(f"Google Drive upload failed: {e}")
        return None

# CLAHE Enhancement
def enhance_image_clahe(pil_image):
    img = np.array(pil_image.convert('RGB'))
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    return Image.fromarray(enhanced)

# UI
st.title("🔍 SmartSight - Low-Light Image Enhancer")
st.markdown("Enhance low-light images in real-time and upload to cloud for safety monitoring.")

input_method = st.radio("Choose input method:", ["📤 Upload Image", "📷 Camera Capture"])

image = None

if input_method == "📤 Upload Image":
    uploaded_file = st.file_uploader("Upload a low-light image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
elif input_method == "📷 Camera Capture":
    camera_img = st.camera_input("Capture an image")
    if camera_img:
        image = Image.open(camera_img)

if image:
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("✨ Enhance and Upload"):
        with st.spinner("Enhancing..."):
            enhanced_img = enhance_image_clahe(image)
            st.image(enhanced_img, caption="Enhanced Image", use_container_width=True)

            buffer = io.BytesIO()
            enhanced_img.save(buffer, format="JPEG")
            buffer.seek(0)

            with st.spinner("Uploading to Google Drive..."):
                drive_link = upload_to_gdrive(buffer, "enhanced_image.jpg")
                if drive_link:
                    st.success("✅ Image uploaded successfully!")
                    st.markdown(f"[View in Google Drive]({drive_link})")
