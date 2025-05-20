import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import datetime
import smtplib
from email.message import EmailMessage

# ----------- Load email config from txt file -----------
def load_email_config(path="email_config.txt"):
    config = {}
    try:
        with open(path, "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    config[key.strip()] = val.strip()
    except Exception as e:
        st.error(f"Error loading email config: {e}")
    return config

email_config = load_email_config()

# ----------- Police stations static mapping -----------
SECTOR_TO_POLICE = {
    "Downtown": "Downtown Police Station",
    "Tech Park": "Tech Park Police Station",
    "Central Mall": "Central Mall Police Station",
    "Harbor Area": "Harbor Police Station",
    "Greenfield": "Greenfield Police Station"
}

# ----------- Page Config -----------
st.set_page_config(page_title="SmartSight", layout="centered")

# ----------- Styling -----------
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
        margin: 4px 0;
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
    .centered {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ----------- Header -----------
st.title("🔍 SmartSight")
st.markdown("<div class='centered' style='font-size: 24px; font-weight: 600;'>Real-Time Image Enhancement and Alert System</div>", unsafe_allow_html=True)
st.markdown("---")

# ----------- Upload Section -----------
upload_method = st.radio("Select Image Input Method", ("📸 Camera", "📁 Upload from device"))

uploaded_image = None
if upload_method == "📸 Camera":
    uploaded_image = st.camera_input("Capture an image")
else:
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

enhanced_image = None

if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)

    # Enhance Button
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

        # Convert back to PIL
        enhanced_image = Image.fromarray(enhanced_rgb)
        st.image(enhanced_image, caption="🔆 Enhanced Image", use_container_width=True)

        # Save enhanced image bytes in session for reuse
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format="PNG")
        buffer.seek(0)
        st.session_state.enhanced_image_bytes = buffer

        # Download button
        st.download_button(
            label="📥 Download Enhanced Image",
            data=buffer.getvalue(),
            file_name="enhanced_image.png",
            mime="image/png"
        )

        # Link to open Google Drive for manual upload
        st.markdown("---")
        st.markdown("🚀 Save Space! Upload to Cloud")
        st.markdown(
            '<a class="stLink" href="https://drive.google.com/drive/my-drive" target="_blank">Click here to open your Drive</a>',
            unsafe_allow_html=True
        )

        # ----------- Alert mechanism -----------

        st.markdown("---")
        st.subheader("🚨 Police Alert System")

        # Sector dropdown
        selected_sector = st.selectbox("Select Sector", options=list(SECTOR_TO_POLICE.keys()))
        police_station = SECTOR_TO_POLICE.get(selected_sector, "Unknown")

        # Display mapped police station
        st.markdown(f"Nearest Police Station: **{police_station}**")

        # Prepare log data
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_data = {
            "Timestamp": timestamp,
            "Sector": selected_sector,
            "Police Station": police_station,
            "Image Name": "enhanced_image.png"
        }

        # Show log on button click
        if st.button("Show Alert Log"):
            st.table([log_data])

        # Send alert email
        def send_alert_email(log_data):
            try:
                msg = EmailMessage()
                msg["Subject"] = f"Alert: Suspicious Activity at {selected_sector}"
                msg["From"] = email_config.get("EMAIL_USERNAME")
                msg["To"] = email_config.get("RECEIVER_EMAIL")

                # Email body with details
                email_body = f"""
Dear Officer,

An alert has been triggered by SmartSight.

Details:
Sector: {log_data['Sector']}
Police Station: {log_data['Police Station']}
Timestamp: {log_data['Timestamp']}

Please find attached the enhanced image and the alert log.

Regards,
SmartSight System
"""
                msg.set_content(email_body)

                # Attach enhanced image
                st.session_state.enhanced_image_bytes.seek(0)
                msg.add_attachment(
                    st.session_state.enhanced_image_bytes.read(),
                    maintype="image",
                    subtype="png",
                    filename="enhanced_image.png"
                )

                # Attach log details as text file
                log_text = "\n".join([f"{k}: {v}" for k, v in log_data.items()])
                msg.add_attachment(
                    log_text.encode("utf-8"),
                    maintype="text",
                    subtype="plain",
                    filename="alert_log.txt"
                )

                # Connect and send email via Mailtrap SMTP
                with smtplib.SMTP(email_config.get("SMTP_HOST"), int(email_config.get("SMTP_PORT"))) as smtp:
                    smtp.starttls()
                    smtp.login(email_config.get("EMAIL_USERNAME"), email_config.get("EMAIL_PASSWORD"))
                    smtp.send_message(msg)

                st.success(f"Alert email sent to {email_config.get('RECEIVER_EMAIL')} successfully!")

            except Exception as e:
                st.error(f"Failed to send alert email: {e}")

        if st.button("Send Alert to Police"):
            if "enhanced_image_bytes" not in st.session_state:
                st.warning("Please enhance the image first!")
            else:
                send_alert_email(log_data)
else:
    st.info("Please capture or upload an image to start.")
