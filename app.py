import streamlit as st
from flood_detection import detect_flood
from utils import calculate_flood_area
import matplotlib.pyplot as plt
import tempfile
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import rasterio
from fpdf import FPDF
from datetime import datetime

st.title("🌊 Flood Detection from Satellite Images")

image_type = st.selectbox("Select Image Type", options=["SAR", "Optical"])
uploaded_file = st.file_uploader("Upload a GeoTIFF image", type=["tif", "tiff"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # Detect flood and calculate area
        mask, profile = detect_flood(tmp_path, image_type=image_type.lower())
        area = calculate_flood_area(mask)

        # Load image to get geospatial extent
        with rasterio.open(tmp_path) as src:
            transform = src.transform
            height, width = mask.shape
            left, top = transform * (0, 0)
            right, bottom = transform * (width, height)
            extent = [left, right, bottom, top]

        # Display flood mask
        st.subheader("🗺️ Flood Map")
        fig1, ax1 = plt.subplots()
        ax1.imshow(mask, cmap='Blues', extent=extent, origin='upper')
        ax1.set_title("Detected Water")
        ax1.axis("off")
        st.pyplot(fig1)

        # Show estimated flooded area
        st.markdown(f"<p style='font-size: 18px;'>🌍 <b>Estimated Flooded Area:</b> {area:.2f} sq.km</p>", unsafe_allow_html=True)

        # Display original image (RGB or grayscale)
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

        # Generate Bonus PDF Report with metadata and image
        if st.button("📥 Download Bonus PDF Report"):
            os.makedirs("output", exist_ok=True)
            map_image_path = "output/flood_map.png"

            # Save map with lat/lon grid
            fig, ax = plt.subplots()
            ax.imshow(mask, cmap="Blues", extent=extent, origin='upper')
            ax.set_title("Detected Flood Zones")
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.grid(True, color='white', linestyle='--', linewidth=0.5)
            plt.tight_layout()
            fig.savefig(map_image_path, dpi=150)
            plt.close(fig)

            # Create PDF
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Flood Detection Report", ln=True, align='C')

            pdf.set_font("Arial", size=12)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pdf.ln(10)
            pdf.cell(0, 10, f"🕒 Timestamp: {timestamp}", ln=True)
            pdf.cell(0, 10, f"🌍 Estimated Flooded Area: {area:.2f} sq.km", ln=True)

            # Add flood map image
            pdf.ln(10)
            pdf.image(map_image_path, x=10, y=60, w=180)

            pdf_path = "output/flood_report_bonus.pdf"
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF", f, "flood_report_bonus.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Error during flood detection: {str(e)}")
