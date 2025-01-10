import pandas as pd
import folium
from branca.colormap import LinearColormap
import os
import argparse

def process_building_group_pattern_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_BuildingGroupPattern.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'BDP'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert BDP to numeric and filter valid data
    data['BDP'] = pd.to_numeric(data['BDP'], errors='coerce')
    data = data.dropna(subset=['BDP'])

    # Define color mappings
    bdp_colors = {
        0: '#FF4500',  # Red (Clustered)
        1: '#A9A9A9',  # Gray (Random)
        2: '#228B22'   # Green (Uniform)
    }
    bdp_labels = {0: "Clustered", 1: "Random", 2: "Uniform"}

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add colorbar
    colormap = LinearColormap(
        colors=['#FF4500', '#A9A9A9', '#228B22'],
        vmin=0, vmax=2,
        caption="Building Group Pattern: Clustered (0), Random (1), Uniform (2)"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        bdp_value = int(row['BDP'])
        color = bdp_colors.get(bdp_value, 'gray')  # Default to gray
        bdp_label = bdp_labels.get(bdp_value, "Unknown")

        popup_text = f"Building Group Pattern: {bdp_label}"

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
    print(f"Building Group Pattern map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Building Group Pattern from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_building_group_pattern_map(args.base_file)
