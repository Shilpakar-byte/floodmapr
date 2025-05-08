import rasterio
import numpy as np

def detect_flood(input_path, image_type='sar', threshold=-15, optical_threshold=0.3):
    with rasterio.open(input_path) as src:
        profile = src.profile
        bands = src.read()

        if image_type == 'sar':
            band = bands[0]
            flood_mask = band < threshold

        elif image_type == 'optical':
            if bands.shape[0] < 4:
                raise ValueError("Optical image must have at least 4 bands (e.g. Blue, Green, Red, NIR)")

            green = bands[3].astype(np.float32)
            nir = bands[8].astype(np.float32)

            ndwi = (green - nir) / (green + nir + 1e-6)
            flood_mask = ndwi > optical_threshold

        else:
            raise ValueError("Invalid image_type. Choose 'sar' or 'optical'.")

        return flood_mask.astype(np.uint8), profile
