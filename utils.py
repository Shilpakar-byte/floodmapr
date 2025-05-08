import numpy as np

def calculate_flood_area(mask, pixel_size=10):
    flooded_pixels = np.sum(mask)
    flooded_area_km2 = flooded_pixels * (pixel_size ** 2) / 1e6
    return round(flooded_area_km2, 2)
