import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime
import os

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
st.title("🔍 SmartSight")
st.markdown("<div style='text-align: center; font-size: 24px; font-weight: 600;'>Real-Time Image Enhancement and Alert System</div>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- Upload Section -----------------
upload_method = st.radio("Select Image Input Method", ("📸 Camera", "📁 Upload from device"))
uploaded_image = st.camera_input("Capture an image") if upload_method == "📸 Camera" else st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

enhanced_image = None
log_entries = []

# ----------------- Enhancement -----------------
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("✨ Enhance Image"):
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        enhanced_image = Image.fromarray(enhanced_rgb)
        st.image(enhanced_image, caption="🔆 Enhanced Image", use_container_width=True)

        # Save buffer for download and alerting
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format="PNG")
        buffer.seek(0)

        # Download Button
        st.download_button(
            label="📥 Download Enhanced Image",
            data=buffer,
            file_name="enhanced_image.png",
            mime="image/png"
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
        st.subheader("🚨 Police Alert Mechanism")

        sector_options = {
            "Sector 1": "Central Police Station",
            "Sector 2": "South Zone Police Station",
            "Sector 3": "North Hill Police Station",
            "Sector 4": "Lakeview Police Station",
            "Sector 5": "Industrial Area Police Station"
        }

        selected_sector = st.selectbox("Select your location sector:", list(sector_options.keys()))

        if selected_sector:
            police_station = sector_options[selected_sector]
            st.success(f"Nearest police station identified: **{police_station}**")

            if st.button("🚨 Send Alert to Police"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                image_name = "enhanced_image.png"
                location = selected_sector

                # Log entry
                log_entries.append({
                    "Timestamp": timestamp,
                    "Location": location,
                    "Image": image_name,
                    "Police Station": police_station
                })

                # Create log file
                log_text = f"Timestamp: {timestamp}\nLocation: {location}\nImage: {image_name}\nPolice Station: {police_station}"
                log_file = io.BytesIO(log_text.encode())
                log_file.name = "incident_log.txt"

                # Email config from file
                try:
                    with open("email_config.txt", "r") as f:
                        lines = f.readlines()
                        config = dict(line.strip().split("=") for line in lines if "=" in line)
                        sender = config.get("EMAIL_ADDRESS")
                        password = config.get("EMAIL_PASSWORD")
                        receiver = config.get("RECEIVER_EMAIL")

                    msg = EmailMessage()
                    msg["Subject"] = "SmartSight Alert: Suspicious Image Captured"
                    msg["From"] = sender
                    msg["To"] = receiver
                    msg.set_content(f"Incident reported from {location}.\nNearest Police Station: {police_station}\nTime: {timestamp}")

                    msg.add_attachment(buffer.getvalue(), maintype="image", subtype="png", filename=image_name)
                    msg.add_attachment(log_file.getvalue(), maintype="text", subtype="plain", filename="incident_log.txt")

                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(sender, password)
                        server.send_message(msg)

                    st.success("🚨 Alert successfully sent to the helpline email.")
                except Exception as e:
                    st.error(f"Failed to send alert: {e}")

        # Display log table
        if log_entries:
            st.markdown("---")
            st.subheader("📑 Incident Log")
            st.table(log_entries)
