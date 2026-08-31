import geopandas as gpd
from shapely.geometry import box

boundary = gpd.read_file("data/raw/chennai_boundary.geojson")
boundary = boundary[boundary.geometry.geom_type == "Polygon"]
boundary = boundary.set_crs("EPSG:4326")

# Project to UTM zone 44N so grid cells are real 200m squares, not degrees
boundary_m = boundary.to_crs("EPSG:32644")
minx, miny, maxx, maxy = boundary_m.total_bounds

cell_size = 200  # meters
cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        cells.append(box(x, y, x + cell_size, y + cell_size))
        y += cell_size
    x += cell_size

grid = gpd.GeoDataFrame({"geometry": cells}, crs="EPSG:32644")
grid = gpd.overlay(grid, boundary_m, how="intersection")
grid["grid_id"] = range(len(grid))
grid = grid.to_crs("EPSG:4326")

print("grid cells created:", len(grid))
grid.to_file("data/processed/chennai_grid.geojson", driver="GeoJSON")
print("saved to data/processed/chennai_grid.geojson")