import json
import os
import argparse

def find_house_file(base_path):
    """
    Find the corresponding _house file path based on the input path.
    :param base_path: Input path, e.g., Data/NewYork_United States_100.jsonl
    :return: The matched _house file path
    """
    base_name = os.path.splitext(os.path.basename(base_path))[0]
    folder_name = os.path.join("output", base_name)

    if os.path.exists(folder_name) and os.path.isdir(folder_name):
        for file_name in os.listdir(folder_name):
            if file_name.endswith("_house.jsonl"):
                return os.path.join(folder_name, file_name)
    raise FileNotFoundError(f"No matching _house file found in {folder_name}")

# Custom cleaning function
# Extract core values and remove unnecessary fields
def clean_record(record):
    cleaned_record = {}

    # Extract id from Filename
    if 'Filename' in record:
        cleaned_record['id'] = record['Filename'].split('_')[2]

    # Extract core prediction values
    if 'Swimming_Pool_Prediction' in record:
        cleaned_record['Swimming_Pool_Prediction'] = record['Swimming_Pool_Prediction'].split(':')[-1].strip()

    if 'Roof_Type_Prediction' in record:
        cleaned_record['Roof_Type_Prediction'] = record['Roof_Type_Prediction'].split(':')[-1].strip()

    if 'Green_Prediction' in record:
        cleaned_record['Green_Prediction'] = record['Green_Prediction'].split(':')[-1].strip()

    return cleaned_record

# Read the input file and clean it
def process_file(base_path):
    # Find the actual input file path
    input_file = find_house_file(base_path)

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
    parser = argparse.ArgumentParser(description="Clean _house JSONL files.")
    parser.add_argument("input_base_path", type=str, help="Path to the input JSONL file to locate the _house file.")

    args = parser.parse_args()
    process_file(args.input_base_path)
