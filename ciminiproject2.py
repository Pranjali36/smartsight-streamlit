import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# Page title
st.set_page_config(page_title="SmartSight - Real-Time Low-Light Enhancement", layout="centered")
st.title("🔆 SmartSight: Real-Time Low-Light Enhancement")

# CLAHE Enhancement Function
def enhance_with_clahe(image):
    img_array = np.array(image.convert('RGB'))
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    return Image.fromarray(enhanced)

# Google Drive Upload
def upload_to_gdrive(image_file, filename):
    credentials_path = "smart_client_config.json"
    if not os.path.exists(credentials_path):
        st.error("OAuth credentials not found.")
        return None

    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)

    file_drive = drive.CreateFile({'title': filename})
    file_drive.SetContentString(image_file.getvalue().decode("ISO-8859-1"))
    file_drive.Upload()
    return file_drive['alternateLink']

# Simulated Alert System
def log_alert(filename):
    st.info(f"🚨 Simulated Alert: Enhanced image '{filename}' uploaded and alert triggered.")

# Image Upload UI
image_source = st.radio("Select input method:", ["📁 Upload Image", "📷 Use Camera"])

if image_source == "📁 Upload Image":
    uploaded_file = st.file_uploader("Upload a low-light image", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_container_width=True)

elif image_source == "📷 Use Camera":
    captured_image = st.camera_input("Capture an image")
    if captured_image:
        image = Image.open(captured_image)
        st.image(image, caption="Captured Image", use_container_width=True)

# Enhance and Upload
if 'image' in locals():
    if st.button("✨ Enhance and Upload"):
        with st.spinner("Enhancing image with CLAHE..."):
            enhanced = enhance_with_clahe(image)
            st.image(enhanced, caption="Enhanced Image", use_container_width=True)

        # Save to in-memory buffer
        buffer = io.BytesIO()
        enhanced.save(buffer, format="JPEG")
        buffer.seek(0)

        # Upload to Google Drive
        st.info("📤 Uploading to Google Drive...")
        gdrive_link = upload_to_gdrive(buffer, "enhanced_image.jpg")
        if gdrive_link:
            st.success(f"✅ Image uploaded successfully! [View in Drive]({gdrive_link})")

        # Simulate alert
        log_alert("enhanced_image.jpg")
