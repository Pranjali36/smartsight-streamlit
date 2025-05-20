import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import smtplib
from email.message import EmailMessage
import datetime

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
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1em;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    th {
        background-color: #004080;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Header -----------------
st.title("🔍 SmartSight")
st.markdown("<div style='text-align: center; font-size: 24px; font-weight: 600;'>Real-Time Image Enhancement and Alert System</div>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- Upload Section -----------------
upload_method = st.radio("Select Image Input Method", ("📸 Camera", "📁 Upload from device"))

uploaded_image = None
if upload_method == "📸 Camera":
    uploaded_image = st.camera_input("Capture an image")
else:
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

enhanced_image = None

# ----------------- Police station mapping -----------------
SECTOR_TO_POLICE_STATION = {
    "Tech Park": "Tech Park Police Station",
    "Central Mall": "Central Mall Police Station",
    "City Center": "City Center Police Station",
    "Greenwood": "Greenwood Police Station",
    "Lakeside": "Lakeside Police Station"
}

# ----------------- Load email config -----------------
def load_email_config():
    config = {}
    try:
        with open("email_config.txt", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    config[key.strip()] = val.strip()
    except Exception as e:
        st.error(f"Error loading email_config.txt: {e}")
    return config

email_config = load_email_config()

# ----------------- Enhancement Logic -----------------
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("✨ Enhance Image"):
        # Convert to OpenCV format
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Apply CLAHE in LAB color space
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        # Display Enhanced Image
        enhanced_image = Image.fromarray(enhanced_rgb)
        st.image(enhanced_image, caption="🔆 Enhanced Image", use_container_width=True)

        # Download Button for Enhanced Image
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format="PNG")
        st.download_button(
            label="📥 Download Enhanced Image",
            data=buffer.getvalue(),
            file_name="enhanced_image.png",
            mime="image/png",
            key="download_btn"
        )

        # Link to Google Drive for Manual Upload
        st.markdown("---")
        st.markdown("🚀 Save Space! Upload to Cloud")
        st.markdown(
            '<a class="stLink" href="https://drive.google.com/drive/my-drive" target="_blank">Click here to open your Drive</a>',
            unsafe_allow_html=True
        )

        # ----------------- Police Alert Mechanism -----------------
        st.markdown("---")
        st.subheader("🚨 Police Alert System")

        # Sector dropdown
        selected_sector = st.selectbox("Select your sector/location:", list(SECTOR_TO_POLICE_STATION.keys()))

        # Show mapped police station
        police_station = SECTOR_TO_POLICE_STATION.get(selected_sector, "Unknown Police Station")
        st.write(f"Nearest Police Station: **{police_station}**")

        # Real-time capture log data
        log_data = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Image Name": "enhanced_image.png",
            "Location": selected_sector,
            "Police Station": police_station,
        }

        # Button to send alert
        if st.button("🚨 Send Alert to Police"):
            # Prepare email with image and log attachments
            if not email_config:
                st.error("Email configuration missing or failed to load.")
            else:
                try:
                    msg = EmailMessage()
                    msg["Subject"] = f"Alert: Suspicious Activity Detected at {selected_sector}"
                    msg["From"] = email_config.get("EMAIL_USERNAME")
                    msg["To"] = email_config.get("RECEIVER_EMAIL")
                    msg.set_content(f"""
Dear Officer,

An alert has been triggered by SmartSight at the following location:

Sector: {selected_sector}
Nearest Police Station: {police_station}
Timestamp: {log_data['Timestamp']}

Please find attached the enhanced image and the alert log.

Regards,
SmartSight System
                    """)

                    # Attach enhanced image
                    buffer.seek(0)
                    msg.add_attachment(buffer.getvalue(), maintype="image", subtype="png", filename="enhanced_image.png")

                    # Attach log file as text
                    log_text = "\n".join([f"{k}: {v}" for k,v in log_data.items()])
                    msg.add_attachment(log_text.encode("utf-8"), maintype="text", subtype="plain", filename="alert_log.txt")

                    # Send email via Mailtrap SMTP
                    smtp_host = email_config.get("EMAIL_HOST")
                    smtp_port = int(email_config.get("EMAIL_PORT", 587))
                    smtp_user = email_config.get("EMAIL_USERNAME")
                    smtp_pass = email_config.get("EMAIL_PASSWORD")

                    with smtplib.SMTP(smtp_host, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        server.send_message(msg)

                    st.success(f"Alert sent successfully to {police_station}!")
                except Exception as e:
                    st.error(f"Failed to send alert email: {e}")
