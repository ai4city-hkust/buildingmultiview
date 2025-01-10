import pandas as pd
import folium
from branca.colormap import StepColormap
import os
import argparse

def process_swimming_pool_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_SwimmingPool.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'Swimming_Pool_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert Swimming_Pool_Prediction to numeric and filter valid data
    data['Swimming_Pool_Prediction'] = pd.to_numeric(data['Swimming_Pool_Prediction'], errors='coerce')
    data = data.dropna(subset=['Swimming_Pool_Prediction'])

    # Define color mappings
    pool_colors = {
        0: 'gray',  # No swimming pool
        1: '#19AFFF'  # Has swimming pool
    }

    pool_labels = {
        0: "No",
        1: "Yes"
    }

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add StepColormap
    colormap = StepColormap(
        colors=['gray', '#19AFFF'],
        index=[0, 0.5, 1],
        vmin=0, vmax=1,
        caption="Swimming Pool Prediction: No (0), Yes (1)"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        pool_value = int(row['Swimming_Pool_Prediction'])
        color = pool_colors.get(pool_value, 'gray')  # Default to gray
        pool_label = pool_labels.get(pool_value, "Unknown")

        popup_text = f"Swimming Pool: {pool_label}"

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
    print(f"Swimming Pool map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Swimming Pool Prediction from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_swimming_pool_map(args.base_file)
