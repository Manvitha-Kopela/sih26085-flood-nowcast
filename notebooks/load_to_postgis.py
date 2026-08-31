import os
import geopandas as gpd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

# Boundary
boundary = gpd.read_file("data/raw/chennai_boundary.geojson")
boundary = boundary[boundary["geometry"].geom_type == "Polygon"]
boundary.to_postgis("chennai_boundary", engine, if_exists="replace")
print("boundary loaded:", len(boundary))

# Roads — filtered to major classes, chunked to avoid timeout
roads = gpd.read_file("data/raw/chennai_roads.geojson")
print("full roads count:", len(roads))
major_classes = ["motorway", "trunk", "primary", "secondary", "tertiary", "residential"]
roads_filtered = roads[roads["highway"].isin(major_classes)]
print("filtered roads count:", len(roads_filtered))
roads_filtered.to_postgis("chennai_roads", engine, if_exists="replace", chunksize=500)
print("roads loaded:", len(roads_filtered))

# Waterways
waterways = gpd.read_file("data/raw/chennai_waterways.geojson")
waterways.to_postgis("chennai_waterways", engine, if_exists="replace", chunksize=500)
print("waterways loaded:", len(waterways))