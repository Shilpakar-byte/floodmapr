import streamlit as st
from flood_detection import detect_flood
from utils import calculate_flood_area
import matplotlib.pyplot as plt
import tempfile
import os

st.title("🌊 Flood Detection from Satellite Images")

# Let user choose image type
image_type = st.selectbox("Select Image Type", options=["SAR", "Optical"])

uploaded_file = st.file_uploader("Upload a GeoTIFF image", type=["tif", "tiff"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        mask, profile = detect_flood(tmp_path, image_type=image_type.lower())
        area = calculate_flood_area(mask)

        st.subheader("🗺️ Flood Map")
        plt.imshow(mask, cmap='Blues')
        plt.title("Detected Flood Zones")
        st.pyplot(plt)

        st.success(f"Estimated Flooded Area: {area} sq.km")

        if st.button("Download Flood Map"):
            os.makedirs("output", exist_ok=True)
            output_path = "output/flood_map.png"
            plt.imsave(output_path, mask, cmap="Blues")
            with open(output_path, "rb") as img:
                st.download_button("Download PNG", img, "flood_map.png")
    except Exception as e:
        st.error(f"❌ Error during flood detection: {str(e)}")
