import streamlit as st
import numpy as np
import cv2
from PIL import Image

st.title("SmartSight: Real-Time Low-Light Image Enhancement")

def enhance_low_light_image_clahe(img_rgb: np.ndarray) -> np.ndarray:
    """Enhance low-light image using CLAHE on the L channel of LAB color space."""
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    return enhanced_img

# Capture image from camera
image = st.camera_input("Capture low-light image")

if image is not None:
    # Convert PIL Image to RGB NumPy array
    img_array = np.array(image.convert('RGB'))

    st.image(img_array, caption="Original Image", use_container_width=True)

    with st.spinner("Enhancing image..."):
        enhanced_img = enhance_low_light_image_clahe(img_array)

    st.image(enhanced_img, caption="Enhanced Image (CLAHE)", use_container_width=True)
else:
    st.info("Please capture an image using your device camera.")
