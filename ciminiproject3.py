import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

def enhance_image_clahe(image):
    # Convert to LAB and apply CLAHE
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    return enhanced_image

def main():
    st.title("SmartSight - Low-Light Enhancer")
    st.write("Upload an image or capture one using your camera:")

    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    camera_capture = st.camera_input("Or take a picture with your camera")

    image_file = uploaded_file or camera_capture

    if image_file is not None:
        input_image = Image.open(image_file).convert("RGB")
        st.image(input_image, caption="Original Image", use_column_width=True)

        img_array = np.array(input_image)
        enhanced_image = enhance_image_clahe(img_array)

        st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        enhanced_pil = Image.fromarray(enhanced_image)
        enhanced_pil.save(temp_file.name)

        # Download button
        with open(temp_file.name, "rb") as f:
            st.download_button("Download Enhanced Image", f.read(), file_name="enhanced_image.png", mime="image/png")

        # Drive upload note
        drive_link = st.text_input("Paste your Google Drive folder link (optional)")
        if drive_link:
            st.success("You can now manually upload the downloaded image to your Drive folder.")
    else:
        st.info("Please upload or capture an image to proceed.")

if __name__ == "__main__":
    main()
