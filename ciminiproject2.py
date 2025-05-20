import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import tempfile

st.set_page_config(page_title="SmartSight - Low Light Enhancer", layout="centered")

st.title("🔆 SmartSight: Real-Time Low-Light Image Enhancer")

st.markdown("""
Upload or capture a photo taken in poor lighting. The image will be enhanced using computational imaging.  
Choose optional actions like sending an alert or uploading to cloud storage.
""")

# Enhancement method selector (Zero-DCE placeholder for future)
method = st.radio("Choose Enhancement Method", ["CLAHE (Classical)"], horizontal=True)

# File upload or camera input
image_file = st.camera_input("📸 Take a photo (optional)") or st.file_uploader("📁 Or upload a low-light image", type=["jpg", "png", "jpeg"])

# Enhance image function using CLAHE
def enhance_low_light_image_clahe(img):
    # Convert to LAB color space (L = lightness)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to the L-channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Merge the CLAHE enhanced L-channel back with A and B channels
    enhanced_lab = cv2.merge((cl, a, b))
    
    # Convert back to RGB color space
    enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    
    return enhanced_img
    
# Process and show
if image_file:
    image = Image.open(image_file)
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing image..."):
            enhanced_image =  enhance_low_light_image_clahe(image)
            st.image(enhanced_image, caption="Enhanced Image", use_container_width=True)

        # Optional alert
        if st.checkbox("📢 Simulate Alert to Safety Team"):
            st.success("✅ Alert has been dispatched to safety team!")

        # Optional save to cloud
        if st.checkbox("☁️ Save Enhanced Image to Google Drive (Simulated)"):
            # Placeholder logic
            st.info("🛠️ This feature is a placeholder. Add real upload logic if needed.")
            # To implement:
            # save_image_to_drive(enhanced_image)
