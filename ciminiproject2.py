import streamlit as st
import numpy as np
from PIL import Image
import cv2
import io
import logging
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Write service account json from secrets (if using secrets)
if not os.path.exists('service_account_key.json'):
    with open('service_account_key.json', 'w') as f:
        json.dump(st.secrets["gcp_service_account"], f)

SERVICE_ACCOUNT_FILE = 'service_account_key.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '13JMycYo85qfzDu3fa57c9Wlryd-A3stT'  # your folder ID

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
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return enhanced_img

st.title("SmartSight: Real-Time Low-Light Enhancement & Alert System")

uploaded_file = st.file_uploader("Upload a low-light image", type=['jpg', 'jpeg', 'png'])
camera_image = st.camera_input("Or capture an image using your camera")

if camera_image:
    image = Image.open(camera_image).convert('RGB')
elif uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
else:
    image = None

if image:
    st.image(image, caption="Original Image", use_container_width=True)
    if st.button("Enhance Image"):
        with st.spinner("Enhancing..."):
            img_array = np.array(image)
            enhanced_img = enhance_low_light_image_clahe(img_array)
            enhanced_pil = Image.fromarray(enhanced_img)
            st.image(enhanced_pil, caption="Enhanced Image", use_container_width=True)

            buf = io.BytesIO()
            enhanced_pil.save(buf, format='JPEG')
            buf.seek(0)

            try:
                drive_link = upload_to_gdrive(buf, "enhanced_image.jpg")
                st.success("Image uploaded to Google Drive!")
                st.markdown(f"[View in Google Drive]({drive_link})")

                logging.info(f"Alert: Enhanced image uploaded. Link: {drive_link}")
                st.info("Alert simulated: Notification logged.")
            except Exception as e:
                st.error(f"Google Drive upload failed: {e}")
else:
    st.info("Please upload or capture an image to get started.")
