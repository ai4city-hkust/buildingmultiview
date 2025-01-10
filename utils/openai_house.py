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
SWIMMING_POOL_MODEL = "ft:gpt-4o-2024-08-06:personal:swimmingpoolnew:AdCojiTM"
ROOF_TYPE_MODEL = "ft:gpt-4o-2024-08-06:personal:rooftype:AVZlEsqs"
GREEN_MODEL = "ft:gpt-4o-2024-08-06:personal:greenratio:AYqejz1M"

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
def predict_swimming_pool(image_path, filename):
    system_prompt = (
        "You are given a remote sensing image. Determine whether it has swimming pools (YES:1, NO:0). "
        "Output: 'Filename: <filename>, Type: <1or0>'."
    )
    return predict(image_path, filename, SWIMMING_POOL_MODEL, system_prompt)

def predict_roof_type(image_path, filename):
    system_prompt = (
        "You are given a remote sensing image. Determine the roof type (0: flat, 1: gabled, 2: hipped). "
        "Output: 'Filename: <filename>, Type_Class: <class>'."
    )
    return predict(image_path, filename, ROOF_TYPE_MODEL, system_prompt)

def predict_green(image_path, filename):
    system_prompt = (
        "You are given a remote sensing image. Determine the vegetation cover density class "
        "(0: 0-10%, 1: 10-30%, 2: 30-60%, 3: 60%+). Output: 'Filename: <filename>, Vegetation_Cover_Class: <class>'."
    )
    return predict(image_path, filename, GREEN_MODEL, system_prompt)

# Worker function to process a single image
def process_single_image(filename, input_dir, completed_files, output_jsonl, lock):
    if filename in completed_files:
        print(f"Skipping {filename}, already processed.")
        return

    image_path = os.path.join(input_dir, filename)

    swimming_pool_prediction = predict_swimming_pool(image_path, filename)
    roof_type_prediction = predict_roof_type(image_path, filename)
    green_prediction = predict_green(image_path, filename)

    record = {
        "Filename": filename,
        "Swimming_Pool_Prediction": swimming_pool_prediction,
        "Roof_Type_Prediction": roof_type_prediction,
        "Green_Prediction": green_prediction
    }

    with lock:
        with open(output_jsonl, 'a') as jsonl_file:
            jsonl_file.write(json.dumps(record) + "\n")
        print(f"Processed {filename} - Swimming Pool: {swimming_pool_prediction}, Roof Type: {roof_type_prediction}, Green: {green_prediction}")

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
