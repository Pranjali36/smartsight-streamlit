import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import smtplib
from email.message import EmailMessage
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

uploaded_image = None
if upload_method == "📸 Camera":
    uploaded_image = st.camera_input("Capture an image")
else:
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# ----------------- Session State -----------------
if "enhanced_image" not in st.session_state:
    st.session_state["enhanced_image"] = None
if "log_entry" not in st.session_state:
    st.session_state["log_entry"] = None

# ----------------- Enhancement Logic -----------------
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

        st.session_state["enhanced_image"] = enhanced_image

        st.image(enhanced_image, caption="🔆 Enhanced Image", use_container_width=True)

        buffer = io.BytesIO()
        enhanced_image.save(buffer, format="PNG")
        st.download_button(
            label="📥 Download Enhanced Image",
            data=buffer.getvalue(),
            file_name="enhanced_image.png",
            mime="image/png",
            key="download_btn"
        )

        st.markdown("---")
        st.markdown("🚀 Save Space! Upload to Cloud")
        st.markdown(
            '<a class="stLink" href="https://drive.google.com/drive/my-drive" target="_blank">Click here to open your Drive</a>',
            unsafe_allow_html=True
        )

# ----------------- Police Alert System -----------------
st.markdown("---")
st.subheader("🚨 Police Alert System")

sector_map = {
    "Sector 1": "Central Police Station",
    "Sector 2": "West End Police Station",
    "Sector 3": "East Zone Station",
    "Sector 4": "South Hill Police HQ",
    "Sector 5": "North Gate Station"
}

selected_sector = st.selectbox("Select Sector", list(sector_map.keys()))

if selected_sector:
    matched_station = sector_map[selected_sector]
    st.success(f"📍 Mapped to: {matched_station}")

    if st.session_state["enhanced_image"] is not None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "Timestamp": timestamp,
            "Image Name": "enhanced_image.png",
            "Location": selected_sector,
            "Mapped Station": matched_station
        }
        st.session_state["log_entry"] = log_entry

        st.markdown("### 🧾 Image Alert Log")
        st.table([log_entry])

        if st.button("📨 Send Alert Log to Police"):
            try:
                email_config = {}
                with open("email_config.txt", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            email_config[key.strip()] = value.strip()

                # Prepare log file
                log_text = "\n".join([f"{k}: {v}" for k, v in log_entry.items()])
                log_bytes = io.BytesIO(log_text.encode("utf-8"))

                # Prepare image
                image_buffer = io.BytesIO()
                st.session_state["enhanced_image"].save(image_buffer, format="PNG")
                image_buffer.seek(0)

                # Compose email
                msg = EmailMessage()
                msg["Subject"] = f"🚨 Alert: Incident Captured at {selected_sector}"
                msg["From"] = email_config["EMAIL_ADDRESS"]
                msg["To"] = email_config["EMAIL_RECEIVER"]
                msg.set_content(f"Incident reported in {selected_sector}.\n\nDetails:\n{log_text}")

                msg.add_attachment(image_buffer.read(), maintype="image", subtype="png", filename="enhanced_image.png")
                msg.add_attachment(log_bytes.read(), maintype="text", subtype="plain", filename="alert_log.txt")

                with smtplib.SMTP(email_config["SMTP_SERVER"], int(email_config["SMTP_PORT"])) as server:
                    server.starttls()
                    server.login(email_config["EMAIL_ADDRESS"], email_config["EMAIL_PASSWORD"])
                    server.send_message(msg)

                st.success("✅ Alert sent successfully to the police station.")
            except Exception as e:
                st.error(f"Failed to send alert: {e}")
    else:
        st.warning("⚠️ Please enhance an image first before sending an alert.")
