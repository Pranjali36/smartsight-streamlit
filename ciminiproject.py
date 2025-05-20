import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import tempfile
import os

st.set_page_config(page_title="SmartSight - Low Light Enhancer", layout="centered")

st.title("🌙 SmartSight - Real-Time Low Light Image Enhancer")
st.write("Upload a low-light image to see the enhanced output using a TFLite model.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def preprocess_image(image: Image.Image) -> np.ndarray:
    img = np.array(image.resize((512, 512))) / 255.0  # Normalize to [0, 1]
    return np.expand_dims(img.astype(np.float32), axis=0)

def load_tflite_model(model_path: str):
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

def run_inference_tflite(interpreter, input_image):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], input_image)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    return output

if uploaded_file is not None:
    st.image(uploaded_file, caption='Original Image', use_column_width=True)

    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_img_path = temp_file.name

    # Preprocess and load model
    image = Image.open(temp_img_path).convert("RGB")
    input_tensor = preprocess_image(image)

    st.info("🔄 Running enhancement model...")

    try:
        model_path = os.path.join(os.path.dirname(__file__), "zero_dce_model.tflite")
        interpreter = load_tflite_model(model_path)
        enhanced_image = run_inference_tflite(interpreter, input_tensor)[0]
        enhanced_image = (enhanced_image * 255).astype(np.uint8)

        st.image(enhanced_image, caption="🌟 Enhanced Image", use_column_width=True)
        st.success("✅ Enhancement complete!")

    except Exception as e:
        st.error(f"⚠️ Model failed to run. Error: {str(e)}")

    os.remove(temp_img_path)
