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
</style>
""", unsafe_allow_html=True)

st.title("🔍 SmartSight")
st.markdown("---")

# ----------------- Upload Section -----------------
upload_method = st.radio("Select Image Input Method", ("📸 Camera", "📁 Upload from device"))

uploaded_image = None
if upload_method == "📸 Camera":
    uploaded_image = st.camera_input("Capture an image")
else:
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Initialize session state for enhanced image buffer
if "enhanced_image_bytes" not in st.session_state:
    st.session_state.enhanced_image_bytes = None

# ----------------- Police station mapping -----------------
SECTOR_TO_POLICE_STATION = {
    "Tech Park": "Tech Park Police Station",
    "Central Mall": "Central Mall Police Station",
    "City Center": "City Center Police Station",
    "Greenwood": "Greenwood Police Station",
    "Lakeside": "Lakeside Police Station"
}

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

if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)

    # Enhance image button
    if st.button("✨ Enhance Image"):
        # Convert to OpenCV format
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # CLAHE enhancement
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        enhanced_image = Image.fromarray(enhanced_rgb)
        st.session_state.enhanced_image_bytes = io.BytesIO()
        enhanced_image.save(st.session_state.enhanced_image_bytes, format="PNG")
        st.session_state.enhanced_image_bytes.seek(0)
        st.success("Image enhanced successfully!")

    # If enhanced image exists, show it + download
    if st.session_state.enhanced_image_bytes:
        enhanced_img = Image.open(st.session_state.enhanced_image_bytes)
        st.image(enhanced_img, caption="🔆 Enhanced Image", use_container_width=True)

        st.download_button(
            label="📥 Download Enhanced Image",
            data=st.session_state.enhanced_image_bytes,
            file_name="enhanced_image.png",
            mime="image/png"
        )

        st.markdown("---")
        st.markdown("🚀 Save Space! Upload to Cloud")
        st.markdown(
            '<a class="stLink" href="https://drive.google.com/drive/my-drive" target="_blank">Click here to open your Drive</a>',
            unsafe_allow_html=True
        )

        # Police alert section
        st.subheader("🚨 Police Alert System")

        selected_sector = st.selectbox("Select your sector/location:", list(SECTOR_TO_POLICE_STATION.keys()))
        police_station = SECTOR_TO_POLICE_STATION.get(selected_sector, "Unknown Police Station")
        st.write(f"Nearest Police Station: **{police_station}**")

        # Prepare log data
        log_data = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Image Name": "enhanced_image.png",
            "Location": selected_sector,
            "Police Station": police_station,
        }

        # Display log table
        st.markdown("### Real-time Capture Log")
        st.table(log_data)

        # Send alert button
        if st.button("🚨 Send Alert to Police"):
            if not email_config:
                st.error("Email config missing or invalid.")
            else:
                try:
                    msg = EmailMessage()
                    msg["Subject"] = f"Alert: Suspicious Activity at {selected_sector}"
                    msg["From"] = email_config.get("EMAIL_USERNAME")
                    msg["To"] = email_config.get("RECEIVER_EMAIL")
                    msg.set_content(f"""
Dear Officer,

An alert has been triggered by SmartSight.

Details:
Sector: {selected_sector}
Police Station: {police_station}
Timestamp: {log_data['Timestamp']}

Please find attached the enhanced image and the alert log.

Regards,
SmartSight System
                    """)

                    # Attach enhanced image
                    st.session_state.enhanced_image_bytes.seek(0)
                    msg.add_attachment(st.session_state.enhanced_image_bytes.read(), maintype="image", subtype="png", filename="enhanced_image.png")

                    # Attach log as txt
                    log_text = "\n".join([f"{k}: {v}" for k,v in log_data.items()])
                    msg.add_attachment(log_text.encode("utf-8"), maintype="text", subtype="plain", filename="alert_log.txt")

                    # SMTP connection
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
                    st.error(f"Failed to send alert: {e}")
