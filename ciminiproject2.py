import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="SmartSight", layout="centered")
st.title("📷 SmartSight: Real-Time Low-Light Enhancement")

# === Low-Light Enhancement Function ===
def enhance_low_light_image_clahe(image):
    img_array = np.array(image.convert('RGB'))
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return Image.fromarray(final)

# === Google Drive Upload (OAuth2 User Flow) ===
def upload_to_gdrive_oauth(image_buffer, filename):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    token_path = 'token.pkl'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('smart_client_config.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': filename}
    media = MediaIoBaseUpload(image_buffer, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return link

# === Email Alert Function (Simulation) ===
def simulate_alert():
    try:
        st.info("🚨 Simulating alert dispatch...")
        msg = MIMEText("SmartSight has captured and enhanced a low-light image. Please review immediately.")
        msg['Subject'] = 'SmartSight Safety Alert'
        msg['From'] = 'smartsight@app.com'
        msg['To'] = 'authority@example.com'
        # For real use: smtplib.SMTP_SSL('smtp.gmail.com', 465) with login
        st.success("✅ Alert simulated successfully (not actually sent).")
    except Exception as e:
        st.error(f"Alert simulation failed: {e}")

# === Image Upload or Camera ===
st.subheader("1. Upload or Capture a Low-Light Image")
input_type = st.radio("Select input method:", ("Upload File", "Use Camera"))
image = None

if input_type == "Upload File":
    uploaded_file = st.file_uploader("Choose a low-light image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
else:
    camera_image = st.camera_input("Capture Image")
    if camera_image:
        image = Image.open(camera_image)

# === Enhance Button ===
if image:
    st.image(image, caption="Original Image", use_container_width=True)
    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing with CLAHE..."):
            enhanced_image = enhance_low_light_image_clahe(image)
            st.image(enhanced_image, caption="Enhanced Image", use_container_width=True)

            # Save image buffer
            buffer = io.BytesIO()
            enhanced_image.save(buffer, format="JPEG")
            buffer.seek(0)

            # Upload to Google Drive
            try:
                gdrive_link = upload_to_gdrive_oauth(buffer, "enhanced_image.jpg")
                st.success(f"✅ Uploaded to Google Drive: [View Image]({gdrive_link})")
            except Exception as e:
                st.error(f"Google Drive upload failed: {e}")

            # Simulate Alert
            simulate_alert()
else:
    st.info("Please upload or capture an image to begin.")
