import streamlit as st
import numpy as np
import cv2
from PIL import Image

st.title("SmartSight: Low-Light Image Enhancer (CLAHE)")
st.markdown("Enhance low-light images using real-time processing with CLAHE (Contrast Limited Adaptive Histogram Equalization).")

uploaded_file = st.file_uploader("Upload a low-light image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_container_width=True)

    if st.button("Enhance Image"):
        with st.spinner("Enhancing..."):
            # Convert PIL image to OpenCV format (BGR)
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Convert to LAB color space
            lab = cv2.cvtColor(image_cv, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)

            # Merge channels and convert back to BGR
            limg = cv2.merge((cl, a, b))
            enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

            # Convert back to PIL (RGB) for display
            enhanced_image = Image.fromarray(cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB))

        st.image(enhanced_image, caption="Enhanced Image", use_container_width=True)
        st.success("Image enhancement complete!")

st.markdown("---")
st.markdown("Developed as part of the SmartSight project.")
