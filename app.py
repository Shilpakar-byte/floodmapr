import streamlit as st
from flood_detection import detect_flood
from utils import calculate_flood_area
import matplotlib.pyplot as plt
import tempfile
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

st.title("🌊 Flood Detection from Satellite Images")

image_type = st.selectbox("Select Image Type", options=["SAR", "Optical"])
uploaded_file = st.file_uploader("Upload a GeoTIFF image", type=["tif", "tiff"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        mask, profile, bands = detect_flood(tmp_path, image_type=image_type.lower())
        area = calculate_flood_area(mask)

        # Display flood mask
        st.subheader("🗺️ Flood Map")
        fig, ax = plt.subplots()
        ax.imshow(mask, cmap='Blues')
        ax.set_title("Detected Flood Zones")
        st.pyplot(fig)

        # Display raw image (optional)
        if bands.shape[0] >= 3:
            st.subheader("🛰️ Original Image (RGB Composite)")
            rgb = np.stack([bands[2], bands[1], bands[0]], axis=-1)  # R, G, B
            rgb = np.clip((rgb - rgb.min()) / (rgb.max() - rgb.min()), 0, 1)
            fig2, ax2 = plt.subplots()
            ax2.imshow(rgb)
            ax2.set_title("RGB Composite")
            ax2.axis("off")
            st.pyplot(fig2)

        st.success(f"Estimated Flooded Area: {area:.2f} sq.km")

        if st.button("Download Flood Map as PDF"):
            os.makedirs("output", exist_ok=True)
            pdf_path = "output/flood_report.pdf"
            with PdfPages(pdf_path) as pdf:
                # Flood Map
                fig, ax = plt.subplots()
                ax.imshow(mask, cmap="Blues")
                ax.set_title("Detected Flood Zones")
                pdf.savefig(fig)
                plt.close()

                # Area Info
                fig, ax = plt.subplots()
                ax.axis("off")
                ax.text(0.1, 0.5, f"Estimated Flooded Area:\n{area:.2f} sq.km", fontsize=14)
                pdf.savefig(fig)
                plt.close()

            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF Report", f, "flood_report.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Error during flood detection: {str(e)}")
