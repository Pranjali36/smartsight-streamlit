import streamlit as st
import numpy as np
from PIL import Image
import cv2
import io
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Google Drive setup
SERVICE_ACCOUNT_FILE = 'service_account_key.json'  # your service account json file in repo
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '13JMycYo85qfzDu3fa57c9Wlryd-A3stT'  # your shared folder ID

def authenticate_gdrive():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

def upload_to_gdrive(image_buffer, filename):
    drive_service = authenticate_gdrive()

    file_metadata = {
        'name': filename,
        'parents': [FOLDER_ID]
    }
    media = MediaIoBaseUpload(image_buffer, mimetype='image/jpeg')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')
    return f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'

def enhance_low_light_image_clahe(img: np.ndarray) -> np.ndarray:
    # Convert RGB to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Merge channels back
    limg = cv2.merge((cl, a, b))

    # Convert back to RGB
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return enhanced_img

st.title("SmartSight: Low-Light Image Enhancement & Alert System")

uploaded_file = st.file_uploader("Upload a low-light image", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image)

    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("Enhance Image"):
        with st.spinner("Enhancing..."):
            enhanced_img = enhance_low_light_image_clahe(img_array)
            enhanced_pil = Image.fromarray(enhanced_img)

            st.image(enhanced_pil, caption="Enhanced Image", use_container_width=True)

            # Save to in-memory buffer
            buf = io.BytesIO()
            enhanced_pil.save(buf, format='JPEG')
            buf.seek(0)

            try:
                drive_link = upload_to_gdrive(buf, "enhanced_image.jpg")
                st.success("Image uploaded to Google Drive!")
                st.markdown(f"[View in Google Drive]({drive_link})")

                # Simulate alert email - for now just log it
                logging.info(f"Alert: Enhanced image uploaded. Link: {drive_link}")
                st.info("Alert simulated: Notification logged.")
            except Exception as e:
                st.error(f"Google Drive upload failed: {e}")
