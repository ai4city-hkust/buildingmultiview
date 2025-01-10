import os
import sys
import subprocess
import json

def load_config():
    """Load API keys from the configuration file."""
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

def run_mapbox_turbo(jsonl_path, api_key):
    """Run the Mapbox Turbo script with the given JSONL path and API key."""
    try:
        subprocess.run([
            "python", "utils/mapbox_turbo.py", jsonl_path, api_key
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running mapbox_turbo.py: {e}")

def run_google_svi_turbo(jsonl_path, api_key):
    """Run the Google Street View Turbo script with the given JSONL path and API key."""
    try:
        subprocess.run([
            "python", "utils/Google_svi_turbo.py", jsonl_path, api_key
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Google_svi_turbo.py: {e}")

def main():
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python Image_downloader.py <JSONL_PATH>")
        sys.exit(1)

    jsonl_path = sys.argv[1]

    # Load API keys from config
    config = load_config()
    mapbox_api_key = config.get("MAPBOX_API_KEY")
    google_api_key = config.get("GOOGLE_API_KEY")

    if not mapbox_api_key or not google_api_key:
        print("API keys are missing in the configuration file.")
        sys.exit(1)

    # Run both scripts
    print("Running Google SVI Turbo...")
    run_google_svi_turbo(jsonl_path, google_api_key)

    print("Running Mapbox Turbo...")
    run_mapbox_turbo(jsonl_path, mapbox_api_key)

if __name__ == "__main__":
    main()
