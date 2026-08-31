import geopandas as gpd
import rasterio
import numpy as np

grid = gpd.read_file("data/processed/chennai_grid.geojson")
dem = rasterio.open("data/raw/chennai_dem.tif")

dem_arr = dem.read(1).astype(float)
dem_arr[dem_arr < -3] = np.nan  # mask coastal artifacts

# SRTM GL3 true resolution is 90m — use this directly instead of the
# degree-based transform, which gives nonsense slope values
pixel_size = 90  # meters
dzdy, dzdx = np.gradient(np.nan_to_num(dem_arr, nan=0), pixel_size, pixel_size)
slope_arr = np.sqrt(dzdx**2 + dzdy**2)

# Reproject only for centroid calc to silence the CRS warning and get accurate centroids
grid_m = grid.to_crs("EPSG:32644")
centroids_m = grid_m.geometry.centroid
centroids = centroids_m.to_crs("EPSG:4326")  # back to lon/lat for DEM lookup

elevations, slopes = [], []
for pt in centroids:
    row, col = dem.index(pt.x, pt.y)
    if 0 <= row < dem_arr.shape[0] and 0 <= col < dem_arr.shape[1]:
        elevations.append(dem_arr[row, col])
        slopes.append(slope_arr[row, col])
    else:
        elevations.append(np.nan)
        slopes.append(np.nan)

grid["elevation"] = elevations
grid["slope"] = slopes

print("cells with valid elevation:", grid["elevation"].notna().sum(), "/", len(grid))
print("elevation range:", grid["elevation"].min(), "-", grid["elevation"].max())
print("slope range:", grid["slope"].min(), "-", grid["slope"].max())

grid.to_file("data/processed/chennai_grid_elevation.geojson", driver="GeoJSON")