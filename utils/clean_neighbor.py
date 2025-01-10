import json
import os
import argparse

def find_neighbor_file(base_path):
    """
    Find the corresponding _neighbor file path based on the input path.
    :param base_path: Input path, e.g., Data/NewYork_United States_100.jsonl
    :return: The matched _neighbor file path
    """
    base_name = os.path.splitext(os.path.basename(base_path))[0]
    folder_name = os.path.join("output", base_name)

    if os.path.exists(folder_name) and os.path.isdir(folder_name):
        for file_name in os.listdir(folder_name):
            if file_name.endswith("_neighbor.jsonl"):
                return os.path.join(folder_name, file_name)
    raise FileNotFoundError(f"No matching _neighbor file found in {folder_name}")

# Custom cleaning function
# Extract core values and remove unnecessary fields
def clean_record(record):
    cleaned_record = {}

    # Extract id from Filename
    if 'Filename' in record:
        filename_parts = record['Filename'].split('_')
        cleaned_record['id'] = filename_parts[2].split('.')[0] if len(filename_parts) > 2 else ''

    # Extract and parse Building_Footprint_Prediction values
    if 'Building_Footprint_Prediction' in record:
        lines = record['Building_Footprint_Prediction'].replace(',', '\n').split('\n')
        for line in lines:
            line = line.strip()
            if "BD:" in line:
                cleaned_record['BD'] = line.split("BD:")[1].split()[0].strip()
            elif "LB:" in line:
                cleaned_record['LB'] = line.split("LB:")[1].split()[0].strip()
            elif "BDP:" in line:
                cleaned_record['BDP'] = line.split("BDP:")[1].split()[0].strip()

    # Extract Land_Use_Prediction
    if 'Land_Use_Prediction' in record:
        if "Type_Class:" in record['Land_Use_Prediction']:
            cleaned_record['Land_Use_Prediction'] = record['Land_Use_Prediction'].split("Type_Class:")[1].split()[0].strip()

    # Extract and split Road_Prediction values
    if 'Road_Prediction' in record:
        road_parts = record['Road_Prediction'].split(',')
        for part in road_parts:
            key_value = part.split(':')
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].strip()
                if key == "RCR":
                    cleaned_record['RCR'] = value
                elif key == "FD":
                    cleaned_record['FD'] = value

    # Ensure all expected keys are present, even if missing in the input
    for key in ["id", "BD", "LB", "BDP", "Land_Use_Prediction", "RCR", "FD"]:
        if key not in cleaned_record:
            cleaned_record[key] = ""

    return cleaned_record

# Read the input file and clean it
def process_file(base_path):
    # Find the actual input file path
    input_file = find_neighbor_file(base_path)

    # Automatically generate the output file path
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_cleaned{ext}"

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            record = json.loads(line)  # Read JSON line by line
            cleaned_record = clean_record(record)  # Clean the record
            outfile.write(json.dumps(cleaned_record) + '\n')  # Write the cleaned record

    print(f"Cleaning completed. Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean _neighbor JSONL files.")
    parser.add_argument("input_base_path", type=str, help="Path to the input JSONL file to locate the _neighbor file.")

    args = parser.parse_args()
    process_file(args.input_base_path)
