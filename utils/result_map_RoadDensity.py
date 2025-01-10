import pandas as pd
import folium
from branca.colormap import StepColormap
import os
import argparse

def process_road_density_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_RoadDensity.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'RCR'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert RCR to numeric and filter valid data
    data['RCR'] = pd.to_numeric(data['RCR'], errors='coerce')
    data = data.dropna(subset=['RCR'])

    # Define color mappings
    rcr_colors = {
        0: '#ADD8E6',  # Light Blue (0% - 10%)
        1: '#87CEEB',  # Sky Blue (10% - 30%)
        2: '#6A5ACD',  # Blue Violet (30% - 50%)
        3: '#4B0082'   # Indigo (Above 50%)
    }

    rcr_labels = {
        0: "0% - 10%",
        1: "10% - 30%",
        2: "30% - 50%",
        3: "Above 50%"
    }

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add StepColormap
    colormap = StepColormap(
        colors=['#ADD8E6', '#87CEEB', '#6A5ACD', '#4B0082'],
        index=[0, 1, 2, 3],
        vmin=0, vmax=3,
        caption="Road Density: 0% - 10%, 10% - 30%, 30% - 50%, Above 50%"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        rcr_value = int(row['RCR'])
        color = rcr_colors.get(rcr_value, 'gray')  # Default to gray
        rcr_label = rcr_labels.get(rcr_value, "Unknown")

        popup_text = f"Road Density: {rcr_label}"

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
    print(f"Road Density map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Road Density from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_road_density_map(args.base_file)
