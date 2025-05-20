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
def enhance_with_clahe(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    merged = cv2.merge((cl, a, b))
    final_img = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    final_rgb = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(final_rgb)

# Process and show
if image_file:
    image = Image.open(image_file)
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing image..."):
            enhanced_image = enhance_with_clahe(image)
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
