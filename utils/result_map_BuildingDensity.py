import pandas as pd
import folium
from branca.colormap import LinearColormap
import os
import argparse

def process_building_density_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_BuildingDensity.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'BD'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert BD to numeric and filter valid data
    data['BD'] = pd.to_numeric(data['BD'], errors='coerce')
    data = data.dropna(subset=['BD'])

    # Define color mappings
    bd_colors = {
        0: '#00FF00',  # Green (0 - 10%)
        1: '#FFA500',  # Orange (10 - 25%)
        2: '#FF0000'   # Red (25 - 100%)
    }
    bd_labels = {0: "0 - 10%", 1: "10 - 25%", 2: "25 - 100%"}

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add colorbar
    colormap = LinearColormap(
        colors=['#00FF00', '#FFA500', '#FF0000'],
        vmin=0, vmax=2,
        caption="Building Density: 0-10%, 10-25%, 25-100%"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        bd_value = int(row['BD'])
        color = bd_colors.get(bd_value, 'gray')  # Default to gray
        bd_label = bd_labels.get(bd_value, "Unknown")

        popup_text = f"Building Density: {bd_label}"

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
    print(f"Building Density map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Building Density from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_building_density_map(args.base_file)
