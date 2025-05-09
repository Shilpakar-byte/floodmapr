import rasterio
import numpy as np

def detect_flood(input_path, image_type='sar', threshold=-17, optical_threshold=0.3):
    with rasterio.open(input_path) as src:
        profile = src.profile
        bands = src.read()

        if image_type == 'sar':
            band = bands[0]
            flood_mask = band < threshold

        elif image_type == 'optical':
            if bands.shape[0] < 0.5:
                raise ValueError("Optical image must have at least 4 bands (e.g. Blue, Green, Red, NIR)")

            green = bands[1].astype(np.float32)
            # nir = bands[3].astype(np.float32)
            swir = bands[3].astype(np.float32)

            # ndwi = (green - nir) / (green + nir + 1e-6)
            mndwi = (green - swir) / (green + swir + 1e-6)
            flood_mask = mndwi > optical_threshold

        else:
            raise ValueError("Invalid image_type. Choose 'sar' or 'optical'.")

        return flood_mask.astype(np.uint8), profile
