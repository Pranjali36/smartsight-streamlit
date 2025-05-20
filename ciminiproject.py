import streamlit as st
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite

# Load TFLite model with caching
@st.cache_resource
def load_model():
    interpreter = tflite.Interpreter(model_path="zero_dce_model.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    return interpreter, input_details, output_details

def preprocess_image(image, input_shape):
    # Resize image to model input size (height, width)
    img = image.resize((input_shape[2], input_shape[1]))
    img = np.array(img).astype(np.float32) / 255.0
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    return img

def postprocess_image(output):
    # Output expected shape: (1, H, W, C)
    img = np.clip(output[0] * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(img)

def enhance_image(image, interpreter, input_details, output_details):
    input_tensor = preprocess_image(image, input_details[0]['shape'])
    interpreter.set_tensor(input_details[0]['index'], input_tensor)
    interpreter.invoke()
    output_tensor = interpreter.get_tensor(output_details[0]['index'])
    return postprocess_image(output_tensor)

st.title("SmartSight: Low-Light Image Enhancer")
st.markdown("Enhance your low-light images using a deep learning model (Zero-DCE) powered by TensorFlow Lite.")

uploaded_file = st.file_uploader("Upload a low-light image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("Enhance Image"):
        with st.spinner("Enhancing..."):
            interpreter, input_details, output_details = load_model()
            enhanced_image = enhance_image(image, interpreter, input_details, output_details)
        st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)
        st.success("Image enhancement complete!")

st.markdown("---")
st.markdown("Developed as part of the SmartSight project for Computational Imaging.")
