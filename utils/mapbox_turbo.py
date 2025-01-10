import os
import json
import math
import time
import requests
from tqdm import tqdm
import sys


class MapboxImageDownloader:
    def __init__(self, api_key, jsonl_path, house_zoom, neighbor_zoom, house_dim_meters, neighbor_dim_meters):
        self.api_key = api_key
        self.jsonl_path = jsonl_path
        self.house_zoom = house_zoom
        self.neighbor_zoom = neighbor_zoom
        self.house_dim_meters = house_dim_meters
        self.neighbor_dim_meters = neighbor_dim_meters

        # Prepare output folder paths
        base_folder_name = os.path.splitext(os.path.basename(self.jsonl_path))[0]
        self.house_folder = os.path.join('mapboxhouse', base_folder_name)
        self.neighbor_folder = os.path.join('mapboxneighbor', base_folder_name)
        self.error_log_file = 'check.txt'

        # Create output directories
        os.makedirs(self.house_folder, exist_ok=True)
        os.makedirs(self.neighbor_folder, exist_ok=True)

    @staticmethod
    def ground_resolution(latitude, zoom):
        """Calculate the ground resolution in meters per pixel at a given latitude and zoom level."""
        return (40075017 * math.cos(math.radians(latitude))) / (256 * (2 ** zoom))

    @staticmethod
    def get_pixel_dimensions(target_width_meters, resolution):
        """Calculate the pixel dimensions for a given width in meters and resolution."""
        pixels = int(target_width_meters / resolution)
        return pixels, pixels

    @staticmethod
    def download_image(url, output_file, retries=3):
        """Download an image from a URL and save it to a file."""
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(output_file, 'wb') as file:
                        file.write(response.content)
                    return True
                elif response.status_code == 422:
                    return False
            except requests.RequestException as e:
                print(f"Error: {e}, retrying {attempt + 1}/{retries}")
            time.sleep(2)
        return False

    def process_location(self, location, error_log):
        """Process a single location to download house and neighbor images."""
        latitude = location['lat']
        longitude = location['lon']
        location_id = location['id']

        # File paths for output images
        house_file = os.path.join(self.house_folder, f"mapbox_image_{location_id}_house.png")
        neighbor_file = os.path.join(self.neighbor_folder, f"mapbox_image_{location_id}_neighbor.png")

        # Download house image
        if not os.path.exists(house_file):
            house_res = self.ground_resolution(latitude, self.house_zoom)
            width, height = self.get_pixel_dimensions(self.house_dim_meters, house_res)
            house_url = (
                f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
                f"{longitude},{latitude},{self.house_zoom}/{width}x{height}?access_token={self.api_key}"
            )
            if not self.download_image(house_url, house_file):
                error_log.write(f"House image failed - Lat: {latitude}, Lon: {longitude}\n")

        # Download neighbor image
        if not os.path.exists(neighbor_file):
            neighbor_res = self.ground_resolution(latitude, self.neighbor_zoom)
            width, height = self.get_pixel_dimensions(self.neighbor_dim_meters, neighbor_res)
            neighbor_url = (
                f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
                f"{longitude},{latitude},{self.neighbor_zoom}/{width}x{height}?access_token={self.api_key}"
            )
            if not self.download_image(neighbor_url, neighbor_file):
                error_log.write(f"Neighbor image failed - Lat: {latitude}, Lon: {longitude}\n")

    def process_all_locations(self):
        """Process all locations from the input JSONL file."""
        with open(self.error_log_file, 'a') as error_log, open(self.jsonl_path, 'r', encoding='utf-8') as file:
            locations = [json.loads(line) for line in file]
            for location in tqdm(locations, desc="Downloading Progress", unit="image"):
                self.process_location(location, error_log)


if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python mapbox_turbo.py <JSONL_PATH> <API_KEY>")
        sys.exit(1)

    JSONL_PATH = sys.argv[1]
    MAPBOX_API_KEY = sys.argv[2]

    # Configuration parameters
    HOUSE_ZOOM = 20
    NEIGHBOR_ZOOM = 17
    HOUSE_DIM_METERS = 100
    NEIGHBOR_DIM_METERS = 500

    # Initialize and run the downloader
    downloader = MapboxImageDownloader(
        api_key=MAPBOX_API_KEY,
        jsonl_path=JSONL_PATH,
        house_zoom=HOUSE_ZOOM,
        neighbor_zoom=NEIGHBOR_ZOOM,
        house_dim_meters=HOUSE_DIM_METERS,
        neighbor_dim_meters=NEIGHBOR_DIM_METERS
    )
    downloader.process_all_locations()
