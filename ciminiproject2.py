import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="SmartSight", layout="centered")
st.title("SmartSight: Real-Time Low-Light Enhancement")
st.markdown("Enhance low-light images and upload to Google Drive for safety monitoring.")

# ----------------------
# CLAHE Enhancement Function
# ----------------------
def enhance_low_light_image_clahe(img_pil):
    img = np.array(img_pil.convert("RGB"))
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))

    enhanced_img = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    return Image.fromarray(enhanced_img)

# ----------------------
# Upload to Google Drive Function (Service Account)
# ----------------------
def upload_to_gdrive(image_bytes, filename):
    scope = ['https://www.googleapis.com/auth/drive']
    credentials_path = 'smart_service_account.json'  # Must be in your GitHub repo

    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {'name': filename}
        media = MediaIoBaseUpload(image_bytes, mimetype='image/jpeg')

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        return f"https://drive.google.com/file/d/{file_id}/view"
    except Exception as e:
        return f"Google Drive upload failed: {e}"

# ----------------------
# Streamlit App Logic
# ----------------------
image = st.camera_input("Capture a low-light image")

if image:
    st.image(image, caption="Captured Image", use_container_width=True)
    with st.spinner("Enhancing image..."):
        img_pil = Image.open(image)
        enhanced_img = enhance_low_light_image_clahe(img_pil)

    st.image(enhanced_img, caption="Enhanced Image", use_container_width=True)

    # Save to buffer for upload
    buffer = io.BytesIO()
    enhanced_img.save(buffer, format="JPEG")
    buffer.seek(0)

    st.success("Enhancement complete!")
    if st.button("Upload to Google Drive"):
        gdrive_link = upload_to_gdrive(buffer, "enhanced_image.jpg")
        st.markdown(f"✅ [View Uploaded Image in Google Drive]({gdrive_link})")
