import pandas as pd
import folium
from branca.colormap import LinearColormap
import os
import argparse

def process_large_building_count_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_LargeBuildingCount.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'LB'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert LB to numeric and filter valid data
    data['LB'] = pd.to_numeric(data['LB'], errors='coerce')
    data = data.dropna(subset=['LB'])

    # Define color mappings
    lb_colors = {
        0: '#00FF00',  # Green (0)
        1: '#FFA500',  # Orange (1-5)
        2: '#FF0000',  # Red (5-20)
        3: '#8B0000'   # Dark Red (20+)
    }
    lb_labels = {0: "0", 1: "1-5", 2: "5-20", 3: "20+"}

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add colorbar
    colormap = LinearColormap(
        colors=['#00FF00', '#FFA500', '#FF0000', '#8B0000'],
        vmin=0, vmax=3,
        caption="Large Building Count: 0, 1-5, 5-20, 20+"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        lb_value = int(row['LB'])
        color = lb_colors.get(lb_value, 'gray')  # Default to gray
        lb_label = lb_labels.get(lb_value, "Unknown")

        popup_text = f"Large Building Count: {lb_label}"

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
    print(f"Large Building Count map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Large Building Count from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_large_building_count_map(args.base_file)
