import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import argparse

def export_results(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate export folder path
    export_folder = os.path.join("export", base_name)
    os.makedirs(export_folder, exist_ok=True)

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns for GeoDataFrame
    if not {'lat', 'lon'}.issubset(data.columns):
        print("The file is missing required columns: 'lat' and 'lon'. Cannot export GeoJSON or Shapefile.")
        return

    # Create GeoDataFrame
    data['geometry'] = data.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    gdf = gpd.GeoDataFrame(data, geometry='geometry', crs='EPSG:4326')

    # Export to CSV
    csv_path = os.path.join(export_folder, f"{base_name}.csv")
    data.to_csv(csv_path, index=False)
    print(f"CSV exported to: {csv_path}")

    # Export to GeoJSON
    geojson_path = os.path.join(export_folder, f"{base_name}.geojson")
    gdf.to_file(geojson_path, driver='GeoJSON')
    print(f"GeoJSON exported to: {geojson_path}")

    # Export to Shapefile
    shapefile_folder = os.path.join(export_folder, f"{base_name}_shapefile")
    os.makedirs(shapefile_folder, exist_ok=True)
    gdf.to_file(os.path.join(shapefile_folder, f"{base_name}.shp"))
    print(f"Shapefile exported to: {shapefile_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export processed data to CSV, GeoJSON, and Shapefile.")
    parser.add_argument("--base_file", required=True, help="Path to the input base JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    export_results(args.base_file)
