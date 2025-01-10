import os
import sys
import subprocess
import json

def load_config():
    """Load configuration if needed in the future."""
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

def run_script(script_name, input_dir, output_jsonl):
    """Run a script with the given input directory and output JSONL."""
    try:
        subprocess.run([
            "python", script_name, "--input_dir", input_dir, "--output_jsonl", output_jsonl
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

def main():
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python Annotation_processor.py <JSONL_PATH>")
        sys.exit(1)

    jsonl_path = sys.argv[1]

    # Validate the input JSONL path
    if not os.path.exists(jsonl_path):
        print(f"JSONL file not found: {jsonl_path}")
        sys.exit(1)

    # Derive the base name from the JSONL file
    base_name = os.path.splitext(os.path.basename(jsonl_path))[0]

    # Define input directories
    street_view_dir = os.path.join("GoogleStreetViewImages", base_name)
    mapbox_house_dir = os.path.join("mapboxhouse", base_name)
    mapbox_neighbor_dir = os.path.join("mapboxneighbor", base_name)

    # Validate input directories
    for folder in [street_view_dir, mapbox_house_dir, mapbox_neighbor_dir]:
        if not os.path.exists(folder):
            print(f"Input folder not found: {folder}")
            sys.exit(1)

    # Define output directory
    output_dir = os.path.join("output", base_name)
    os.makedirs(output_dir, exist_ok=True)

    # Define output JSONL files
    svi_output_jsonl = os.path.join(output_dir, f"{base_name}_svi.jsonl")
    neighbor_output_jsonl = os.path.join(output_dir, f"{base_name}_neighbor.jsonl")
    house_output_jsonl = os.path.join(output_dir, f"{base_name}_house.jsonl")

    # Run the scripts in sequence
    print("Running openai_svi.py...")
    run_script("utils/openai_svi.py", street_view_dir, svi_output_jsonl)

    print("Running openai_neighbour.py...")
    run_script("utils/openai_neighbour.py", mapbox_neighbor_dir, neighbor_output_jsonl)

    print("Running openai_house.py...")
    run_script("utils/openai_house.py", mapbox_house_dir, house_output_jsonl)

    print(f"Processing complete. Results saved in {output_dir}")

if __name__ == "__main__":
    main()
