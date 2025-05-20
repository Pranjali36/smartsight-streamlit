import streamlit as st
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import io

# Load the Zero-DCE model
@st.cache_resource
def load_zero_dce_model():
    model = load_model("zero_dce_model.h5", compile=False)
    return model

model = load_zero_dce_model()

# Enhance the image using Zero-DCE
def enhance_image(img):
    input_img = cv2.resize(img, (512, 512))  # Resize to model input
    input_img = input_img / 255.0  # Normalize
    input_tensor = np.expand_dims(input_img, axis=0).astype(np.float32)

    output = model.predict(input_tensor)[0]
    output = np.clip(output, 0, 1) * 255.0
    output = output.astype(np.uint8)
    return output

# Streamlit GUI
st.set_page_config(page_title="SmartSight - Low Light Enhancer", layout="centered")
st.title("🌙 SmartSight: Real-Time Low-Light Image Enhancement")
st.markdown("Enhance low-light images using deep learning on the fly.")

uploaded_file = st.file_uploader("📤 Upload a low-light image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    st.subheader("🔍 Original Image")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("✨ Enhance Image"):
        with st.spinner("Enhancing..."):
            enhanced = enhance_image(img_np)
            st.subheader("🚀 Enhanced Image")
            st.image(enhanced, caption="Enhanced Output", use_column_width=True)

            # Download Button
            enhanced_pil = Image.fromarray(enhanced)
            buf = io.BytesIO()
            enhanced_pil.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="📥 Download Enhanced Image",
                data=byte_im,
                file_name="enhanced_image.png",
                mime="image/png"
            )
