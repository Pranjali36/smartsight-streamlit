import streamlit as st
import numpy as np
import cv2
from PIL import Image

# CLAHE Enhancement function
def enhance_with_clahe(pil_image):
    # Convert PIL image to OpenCV format (BGR)
    img = np.array(pil_image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

    # Split LAB channels
    l, a, b = cv2.split(img)

    # Apply CLAHE to the L-channel (lightness)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)

    # Merge the channels back and convert to RGB
    lab_enhanced = cv2.merge((l_enhanced, a, b))
    final = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

    return Image.fromarray(final)

# Streamlit App UI
st.title("SmartSight: Real Low-Light Image Enhancer")
st.markdown("Enhance low-light images using real-time processing with CLAHE (Contrast Limited Adaptive Histogram Equalization).")

uploaded_file = st.file_uploader("Upload a low-light image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("Enhance Image"):
        with st.spinner("Enhancing with CLAHE..."):
            enhanced_image = enhance_with_clahe(image)
        st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)
        st.success("Image enhancement complete!")

st.markdown("---")
st.markdown("Developed as part of the SmartSight project.")
