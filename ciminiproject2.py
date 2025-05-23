import streamlit as st
from PIL import Image, ImageEnhance
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import cv2
import numpy as np

# --- DEBUG: Check private_key reading from secrets ---

service_account_info = dict(st.secrets["gcp_service_account"])

st.write("### Raw private_key from secrets (first 200 chars):")
st.text(service_account_info["private_key"][:200])

st.write("### After replace('\\n', '\\\\n') (first 200 chars):")
st.text(service_account_info["private_key"].replace("\\n", "\n")[:200].replace("\n", "\\n"))

# --- Google Drive upload setup ---

def get_drive_service():
    # Replace literal '\\n' with actual newlines in private_key
    service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

def upload_file_to_drive(filepath, filename):
    drive_service = get_drive_service()
    try:
        file_metadata = {'name': filename}
        media = MediaFileUpload(filepath, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        st.success(f"File uploaded successfully! File ID: {file.get('id')}")
    except Exception as e:
        st.error(f"Google Drive upload failed: {e}")

# --- Enhancement function with CLAHE ---

def enhance_image(image: Image.Image) -> Image.Image:
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced_cv = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    enhanced_pil = Image.fromarray(enhanced_cv)
    return enhanced_pil

# --- Streamlit UI ---

st.title("SmartSight - Low Light Enhancement & Upload")

input_method = st.radio("Select input method", ("Upload image", "Use camera"))

img = None
if input_method == "Upload image":
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
elif input_method == "Use camera":
    captured_img = st.camera_input("Take a picture")
    if captured_img:
        img = Image.open(captured_img)

if img:
    st.image(img, caption="Original Image", use_container_width=True)

    if st.button("Enhance Image"):
        enhanced_img = enhance_image(img)
        st.image(enhanced_img, caption="Enhanced Image", use_container_width=True)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            enhanced_img.save(tmp_file.name)
            st.session_state['tmp_file_path'] = tmp_file.name

if 'tmp_file_path' in st.session_state:
    if st.button("Upload Enhanced Image to Google Drive"):
        upload_file_to_drive(st.session_state['tmp_file_path'], "enhanced_image.png")
