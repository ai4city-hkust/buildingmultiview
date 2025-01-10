import os
import json
import requests
from tqdm import tqdm
import sys

class GoogleStreetViewDownloader:
    def __init__(self, jsonl_path, api_key):
        self.jsonl_path = jsonl_path
        self.api_key = api_key

        # Prepare output folder
        base_folder = "GoogleStreetViewImages"
        jsonl_filename = os.path.basename(jsonl_path).split('.')[0]
        self.save_folder = os.path.join(base_folder, jsonl_filename)
        os.makedirs(self.save_folder, exist_ok=True)

    def check_street_view_availability(self, lat, lon):
        """Check if Street View is available for the given latitude and longitude."""
        base_metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
        params = {
            'location': f"{lat},{lon}",
            'radius': 30,
            'key': self.api_key
        }
        response = requests.get(base_metadata_url, params=params)
        if response.status_code == 200:
            metadata = response.json()
            return metadata.get('status') == 'OK'
        return False

    def download_street_views(self):
        """Download Street View images for locations with availability."""
        # Read JSONL file
        with open(self.jsonl_path, 'r', encoding='utf-8') as file:
            locations = [json.loads(line) for line in file]

        filtered_locations = []
        pbar = tqdm(total=len(locations), desc="Checking Street View Availability")
        for location in locations:
            lat, lon = location['lat'], location['lon']
            if self.check_street_view_availability(lat, lon):
                filtered_locations.append(location)
            else:
                print(f"No Street View available for location {location['id']}. Removing from list.")
            pbar.update(1)
        pbar.close()

        # Update JSONL file with filtered locations
        with open(self.jsonl_path, 'w', encoding='utf-8') as file:
            for location in filtered_locations:
                file.write(json.dumps(location) + '\n')

        # Download images for filtered locations
        base_url = "https://maps.googleapis.com/maps/api/streetview"
        params = {
            'size': '600x300',
            'radius': 30,
            'key': self.api_key
        }

        pbar = tqdm(total=len(filtered_locations), desc="Downloading Street Views")
        for location in filtered_locations:
            params['location'] = f"{location['lat']},{location['lon']}"

            response = requests.get(base_url, params=params, stream=True)
            if response.status_code == 200:
                image_path = os.path.join(self.save_folder, f"{location['id']}.jpg")
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Image saved for Location {location['id']} - {image_path}")
            else:
                print(f"Failed to fetch image for location {location['id']}. Status code: {response.status_code}")

            pbar.update(1)
        pbar.close()

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python Google_svi_turbo.py <JSONL_PATH> <API_KEY>")
        sys.exit(1)

    JSONL_PATH = sys.argv[1]
    API_KEY = sys.argv[2]

    # Initialize and run the downloader
    downloader = GoogleStreetViewDownloader(jsonl_path=JSONL_PATH, api_key=API_KEY)
    downloader.download_street_views()
