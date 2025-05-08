import streamlit as st
from flood_detection import detect_flood
from utils import calculate_flood_area
import matplotlib.pyplot as plt
import tempfile
import os

st.title("🌊 Flood Detection from Satellite Images")
uploaded_file = st.file_uploader("Upload a Sentinel-1 GeoTIFF", type=["tif", "tiff"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    mask, profile = detect_flood(tmp_path)
    area = calculate_flood_area(mask)

    st.subheader("🗺️ Flood Map")
    plt.imshow(mask, cmap='Blues')
    plt.title("Detected Flood Zones")
    st.pyplot(plt)

    st.success(f"Estimated Flooded Area: {area} sq.km")

    if st.button("Download Flood Map"):
        plt.imsave("output/flood_map.png", mask, cmap="Blues")
        with open("output/flood_map.png", "rb") as img:
            st.download_button("Download PNG", img, "flood_map.png")
