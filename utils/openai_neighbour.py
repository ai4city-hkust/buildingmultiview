import openai
import base64
import os
import json
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Load API Keys from config.json
def load_api_keys():
    with open("config.json", "r") as file:
        config = json.load(file)
    return config["OPENAI_API_KEYS"]

# Configuration: Model IDs
BUILDING_MODEL = "ft:gpt-4o-2024-08-06:personal:footprint:AXIKicCz"
LAND_USE_MODEL = "ft:gpt-4o-2024-08-06:personal:landuse:AWDBTGjs"
ROAD_MODEL = "ft:gpt-4o-2024-08-06:personal:road:AZER1efc"

# Function to set API key in a round-robin fashion
api_keys = load_api_keys()
api_key_index = 0
def set_next_api_key():
    global api_key_index
    openai.api_key = api_keys[api_key_index]
    api_key_index = (api_key_index + 1) % len(api_keys)

# Function to encode an image as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Generalized prediction function
def predict(image_path, filename, model, system_prompt):
    set_next_api_key()
    base64_image = encode_image(image_path)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Classify the image '{filename}'."},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
    ]
    response = openai.ChatCompletion.create(model=model, messages=messages)
    return response.choices[0].message["content"]

# Wrapper functions for predictions
def predict_building_footprint(image_path, filename):
    system_prompt = (
            "Classify some building footprint types for a remote sensing image considering the following parameters: "
            "Building Density 0 (0-10%), 1 (10-25%), 2 (25%-100%); Large Building Count: 0(0), 1(1-5), 2(5-20), 3(20 and more than); "
            "Building Distribution Patterns: 0 (clustered), 1(random), 2 (uniform). "
            "Output format: Filename: <filename>, BD: <density_class>, LB: <building_count_class>, BDP: <Patterns_class>."
    )
    return predict(image_path, filename, BUILDING_MODEL, system_prompt)

def predict_land_use(image_path, filename):
    system_prompt = (
                "Classify the land use type for a remote sensing image. Possible classes: 0 (agriculturalland), 1 (bareland), 2 (educationalland), "
                "3 (greenspace), 4 (industrialland), 5 (publiccommercialland), 6 (residentialland), 7 (transportationland), 8 (waterbody), 9 (woodland). "
                "Output: 'Filename: <filename>, Type_Class: <class>'. Each image can have multiple classes."
    )
    return predict(image_path, filename, LAND_USE_MODEL, system_prompt)

def predict_road_network(image_path, filename):
    system_prompt = (
        "Classify some Road Network types for a remote sensing image considering the following parameters: "
        "Road Coverage Ratio (RCR) 0 (0%-10%), 1 (10%-30%), 2 (30%-50%), 3 (Above 50%); Fractal Dimension FD (Road Network Complexity): "
        "0 (Simple), 1 (Mildly Complex), 2 (Moderately Complex), 3 (Highly Complex). "
        "Output format: 'Filename: <filename>, RCR: <rcr_class>, FD: <fd_class>'."
    )
    return predict(image_path, filename, ROAD_MODEL, system_prompt)

# Worker function to process a single image
def process_single_image(filename, input_dir, completed_files, output_jsonl, lock):
    if filename in completed_files:
        print(f"Skipping {filename}, already processed.")
        return

    image_path = os.path.join(input_dir, filename)

    building_prediction = predict_building_footprint(image_path, filename)
    land_use_prediction = predict_land_use(image_path, filename)
    road_prediction = predict_road_network(image_path, filename)

    record = {
        "Filename": filename,
        "Building_Footprint_Prediction": building_prediction,
        "Land_Use_Prediction": land_use_prediction,
        "Road_Prediction": road_prediction
    }

    with lock:
        with open(output_jsonl, 'a') as jsonl_file:
            jsonl_file.write(json.dumps(record) + "\n")
        print(f"Processed {filename} - Building Footprint: {building_prediction}, Land Use: {land_use_prediction}, Road: {road_prediction}")

# Main function to process images
def process_images(input_dir, output_jsonl):
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png'))]

    completed_files = set()
    if os.path.exists(output_jsonl):
        with open(output_jsonl, 'r') as jsonl_file:
            for line in jsonl_file:
                record = json.loads(line)
                completed_files.add(record["Filename"])

    from threading import Lock
    lock = Lock()
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_single_image, filename, input_dir, completed_files, output_jsonl, lock)
            for filename in image_files
        ]
        for future in tqdm(futures, desc="Processing Images"):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process images and export predictions.")
    parser.add_argument("--input_dir", required=True, help="Directory containing input images.")
    parser.add_argument("--output_jsonl", required=True, help="Path to save output JSONL file.")
    args = parser.parse_args()

    process_images(args.input_dir, args.output_jsonl)
