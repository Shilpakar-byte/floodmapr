import rasterio
import numpy as np

def detect_flood(input_path, threshold=-15):
    with rasterio.open(input_path) as src:
        band = src.read(1)
        profile = src.profile

        # Basic thresholding for water (SAR backscatter logic)
        flood_mask = band < threshold

        return flood_mask.astype(np.uint8), profile
