import streamlit as st
from flood_detection import detect_flood
from utils import calculate_flood_area
import matplotlib.pyplot as plt
import tempfile
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import rasterio

st.title("🌊 Flood Detection from Satellite Images")

image_type = st.selectbox("Select Image Type", options=["SAR", "Optical"])
uploaded_file = st.file_uploader("Upload a GeoTIFF image", type=["tif", "tiff"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # Detect flood using the adjusted function
        mask, profile = detect_flood(tmp_path, image_type=image_type.lower())
        area = calculate_flood_area(mask)

        # Show flood mask
        st.subheader("🗺️ Flood Map")
        with rasterio.open(tmp_path) as src:
            transform = src.transform

            height, width = mask.shape
            left, top = transform * (0, 0)
            right, bottom = transform * (width, height)

            extent = [left, right, bottom, top]

            fig1, ax1 = plt.subplots()
            ax1.imshow(mask, cmap='Blues', extent=extent, origin='upper')
            ax1.set_title("Detected Water")
            ax1.axis("off")  # Remove axis labels and ticks
            st.pyplot(fig1)

        # Show estimated area in smaller font just below map
        st.markdown(f"<p style='font-size: 18px;'>🌍 <b>Estimated Flooded Area:</b> {area:.2f} sq.km</p>", unsafe_allow_html=True)

        # Try to show original image (RGB or first band)
        with rasterio.open(tmp_path) as src:
            bands = src.read()
            fig2, ax2 = plt.subplots()
            if bands.shape[0] >= 3:
                rgb = np.stack([bands[2], bands[1], bands[0]], axis=-1)
                rgb = np.clip((rgb - rgb.min()) / (rgb.max() - rgb.min()), 0, 1)
                ax2.imshow(rgb)
                ax2.set_title("Original Image (RGB Composite)")
            else:
                ax2.imshow(bands[0], cmap='gray')
                ax2.set_title("Original Image (Single Band)")
            ax2.axis("off")
            st.pyplot(fig2)

        # Download PDF Report Button
        if st.button("Download PDF Report"):
            os.makedirs("output", exist_ok=True)
            pdf_path = "output/flood_report.pdf"

            with PdfPages(pdf_path) as pdf:
                # Page 1: Flood mask
                fig, ax = plt.subplots()
                ax.imshow(mask, cmap="Blues")
                ax.set_title("Detected Flood Zones")
                ax.axis("off")
                pdf.savefig(fig)
                plt.close(fig)

                # Page 2: Area info
                fig, ax = plt.subplots()
                ax.axis("off")
                ax.text(0.1, 0.5, f"Estimated Flooded Area:\n{area:.2f} sq.km", fontsize=16)
                pdf.savefig(fig)
                plt.close(fig)

            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF Report", f, "flood_report.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Error during flood detection: {str(e)}")
