import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
import tempfile
import os

# ----------------------------
# Load the Zero-DCE model
# ----------------------------
@st.cache_resource
def load_zero_dce_model():
    model_path = "zero_dce_model.h5"  # Ensure this is uploaded in your GitHub repo
    model = load_model(model_path, compile=False)
    return model

# ----------------------------
# Enhance the image using the model
# ----------------------------
def enhance_image(img, model):
    input_img = cv2.resize(img, (224, 224)) / 255.0
    input_tensor = tf.convert_to_tensor(np.expand_dims(input_img, axis=0), dtype=tf.float32)
    enhanced_tensor = model(input_tensor)
    enhanced_img = tf.squeeze(enhanced_tensor).numpy()
    enhanced_img = (enhanced_img * 255).astype(np.uint8)
    enhanced_img = cv2.resize(enhanced_img, (img.shape[1], img.shape[0]))
    return enhanced_img

# ----------------------------
# Simulate danger alert
# ----------------------------
def simulate_alert(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    if brightness < 50:
        st.error("⚠️ Alert: Very low visibility detected!")
    else:
        st.success("✅ Visibility levels are normal.")

# ----------------------------
# Simulate cloud upload
# ----------------------------
def upload_to_cloud(img):
    filename = "enhanced_image.jpg"
    cv2.imwrite(filename, img)
    st.info("✅ Image saved locally (simulated cloud upload).")
    return filename

# ----------------------------
# Main Streamlit app
# ----------------------------
def main():
    st.title("SmartSight: Low-Light Image Enhancer 🌙")
    st.subheader("A Real-Time Safety Monitoring System")
    st.write("Upload a low-light image to enhance it using Zero-DCE and receive safety alerts.")

    model = load_zero_dce_model()

    uploaded_file = st.file_uploader("Upload a Low-Light Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        bgr_image = cv2.imdecode(file_bytes, 1)
        st.image(cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB), caption="Original Image", use_column_width=True)

        if st.button("Enhance Image"):
            enhanced = enhance_image(bgr_image, model)
            st.image(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB), caption="Enhanced Image", use_column_width=True)

            simulate_alert(enhanced)
            upload_to_cloud(enhanced)

if __name__ == "__main__":
    main()
