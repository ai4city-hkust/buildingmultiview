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
WWR_MODEL = "ft:gpt-4o-2024-08-06:personal:wwr:AVPiC3pY"
PROPERTYTYPE_MODEL = "ft:gpt-4o-2024-08-06:personal:property:AYsChkwR"
FLOORCOUNT_MODEL = "ft:gpt-4o-2024-08-06:personal:floorcount:AdozFsk8"

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
def predict_wwr(image_path, filename):
    system_prompt = (
        "You are given a street view image. Determine the WWR class for the image based on its window-to-wall ratio (WWR). "
        "The WWR classes are as follows: 0 (0-20%), 1 (20-40%), 2 (40-60%), 3 (60-100%). "
        "Output format: 'Filename: <filename>, WWR_Class: <class>'. Only output the filename and WWR class."
    )
    return predict(image_path, filename, WWR_MODEL, system_prompt)

def predict_propertyType(image_path, filename):
    system_prompt = (
        "You are given a streetview image. Determine the Building Property type class for the image. "
        "The Building Property type classes are as follows: Single Family 0, Apartment 1, Multi-Family 2, Manufactured 3, Condo, 4 Townhouse 5, other 6. "
        "Output format: 'Filename: <filename>, Type_Class: <class>'. Only output the filename and Type class."
    )
    return predict(image_path, filename, PROPERTYTYPE_MODEL, system_prompt)

def predict_floorcount(image_path, filename):
    system_prompt = (
        "You are given a street view image. Determine the floor count of the building in the image. "
        "Output format: 'Filename: <filename>, FloorCount: <Count>'. Only output the filename and floorcount."
    )
    return predict(image_path, filename, FLOORCOUNT_MODEL, system_prompt)

# Worker function to process a single image
def process_single_image(filename, input_dir, completed_files, output_jsonl, lock):
    if filename in completed_files:
        print(f"Skipping {filename}, already processed.")
        return

    image_path = os.path.join(input_dir, filename)

    # Get predictions for all models
    wwr_prediction = predict_wwr(image_path, filename)
    propertyType_prediction = predict_propertyType(image_path, filename)
    floorcount_prediction = predict_floorcount(image_path, filename)

    # Log predictions
    record = {
        "Filename": filename,
        "WWR_Prediction": wwr_prediction,
        "Property_Type_Prediction": propertyType_prediction,
        "Floor_Count_Prediction": floorcount_prediction
    }

    with lock:
        with open(output_jsonl, 'a') as jsonl_file:
            jsonl_file.write(json.dumps(record) + "\n")
        print(f"Processed {filename} - WWR: {wwr_prediction}, Property Type: {propertyType_prediction}, Floor Count: {floorcount_prediction}")

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
    parser = argparse.ArgumentParser(description="Process street view images and export predictions.")
    parser.add_argument("--input_dir", required=True, help="Directory containing input images.")
    parser.add_argument("--output_jsonl", required=True, help="Path to save output JSONL file.")
    args = parser.parse_args()

    process_images(args.input_dir, args.output_jsonl)
