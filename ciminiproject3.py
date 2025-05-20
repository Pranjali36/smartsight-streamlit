import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import pandas as pd
from datetime import datetime

# ----------------- Page Config -----------------
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
st.title("🔍 SmartSight")
st.markdown("<div style='text-align: center; font-size: 24px; font-weight: 600;'>Real-Time Image Enhancement and Alert System</div>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- Upload Section -----------------
upload_method = st.radio("Select Image Input Method", ("📸 Camera", "📁 Upload from device"))
uploaded_image = st.camera_input("Capture an image") if upload_method == "📸 Camera" else st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

enhanced_image = None
log_entries = []

# ----------------- Enhancement Logic -----------------
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("✨ Enhance Image"):
        # Convert to OpenCV format
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Apply CLAHE
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        # Display
        enhanced_image = Image.fromarray(enhanced_rgb)
        st.image(enhanced_image, caption="🔆 Optimized Visual Output", use_container_width=True)

        # Download Button
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format="PNG")
        st.download_button(
            label="📥 Download Enhanced Image",
            data=buffer.getvalue(),
            file_name="enhanced_image.png",
            mime="image/png",
            key="download_btn"
        )

        # Drive Link
        st.markdown("---")
        st.markdown("🚀 Save Space! Upload to Cloud")
        st.markdown(
            '<a class="stLink" href="https://drive.google.com/drive/my-drive" target="_blank">Click here to open your Drive</a>',
            unsafe_allow_html=True
        )

        # ----------------- Police Alert Mechanism -----------------
        st.markdown("---")
        st.subheader("🚨 Alert Routing System")

        # Static police stations database
        stations = {
            "Central Mall": "Sector 17 Police Station",
            "Tech Park": "Cyber City Police Station",
            "Green Garden": "North Zone Police HQ",
            "River Bridge": "Eastside Police Post",
            "City Hospital": "Metro Police Center"
        }

        landmark = st.text_input("Enter landmark (e.g. Tech Park, Central Mall, etc.):")
        if landmark and st.button("📡 Route Alert"):
            matched_station = stations.get(landmark.strip(), "No matching station found")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_data = {
                "Timestamp": timestamp,
                "Location (Landmark)": landmark,
                "Image Name": "enhanced_image.png",
                "Routed Station": matched_station,
                "Coordinates": "Auto-fetch unavailable"
            }

            st.success(f"Alert routed to: **{matched_station}**")

            # Display log
            log_df = pd.DataFrame([log_data])
            st.markdown("### 📋 Real-Time Capture Log")
            st.dataframe(log_df, use_container_width=True)
