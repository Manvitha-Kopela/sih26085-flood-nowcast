import geopandas as gpd

grid = gpd.read_file("data/processed/chennai_grid_elevation.geojson")
waterways = gpd.read_file("data/raw/chennai_waterways.geojson")

# Work in meters so length is in meters, not degrees
grid_m = grid.to_crs("EPSG:32644")
waterways_m = waterways.to_crs("EPSG:32644")

# Only keep actual drainage-relevant line features (not water body polygons)
waterways_lines = waterways_m[waterways_m.geometry.geom_type.isin(["LineString", "MultiLineString"])]

# Intersect waterway lines with each grid cell, sum length per cell
joined = gpd.overlay(
    waterways_lines[["geometry"]],
    grid_m[["grid_id", "geometry"]],
    how="intersection"
)
joined["length_m"] = joined.geometry.length
drainage_by_cell = joined.groupby("grid_id")["length_m"].sum().reset_index()
drainage_by_cell = drainage_by_cell.rename(columns={"length_m": "drainage_length_m"})

grid = grid.merge(drainage_by_cell, on="grid_id", how="left")
grid["drainage_length_m"] = grid["drainage_length_m"].fillna(0)

print("cells with any drainage feature:", (grid["drainage_length_m"] > 0).sum(), "/", len(grid))
print("drainage length range:", grid["drainage_length_m"].min(), "-", grid["drainage_length_m"].max())

grid.to_file("data/processed/chennai_grid_drainage.geojson", driver="GeoJSON")