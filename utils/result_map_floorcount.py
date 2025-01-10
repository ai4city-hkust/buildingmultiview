import pandas as pd
import folium
from branca.colormap import linear
import os
import argparse

def process_floor_count_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_FloorCount.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'Floor_Count_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert Floor_Count_Prediction to numeric and filter valid data
    data['Floor_Count_Prediction'] = pd.to_numeric(data['Floor_Count_Prediction'], errors='coerce')
    data = data.dropna(subset=['Floor_Count_Prediction'])

    # Get min and max floor counts
    min_floor = int(data['Floor_Count_Prediction'].min())
    max_floor = int(data['Floor_Count_Prediction'].max())

    # Define continuous color mapping (blue gradient)
    colormap = linear.Blues_09.scale(min_floor, max_floor)
    colormap.caption = "Floor Count"

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add colorbar
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        floor_count = row['Floor_Count_Prediction']
        color = colormap(floor_count)

        popup_text = f"Floor Count: {int(floor_count)}"

        folium.CircleMarker(
            location=(row['lat'], row['lon']),
            radius=5,
            color='none',
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            popup=popup_text
        ).add_to(m)

    # Save the map
    m.save(output_file)
    print(f"Floor Count map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Floor Count from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_floor_count_map(args.base_file)
