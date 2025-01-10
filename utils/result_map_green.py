import pandas as pd
import folium
from branca.colormap import LinearColormap
import os
import argparse

def process_green_cover_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_GreenCover.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'Green_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert Green_Prediction to numeric and filter valid data
    data['Green_Prediction'] = pd.to_numeric(data['Green_Prediction'], errors='coerce')
    data = data.dropna(subset=['Green_Prediction'])

    # Define color mappings
    green_colors = {
        0: '#ADFF2F',  # Light Green (0 - 10%)
        1: '#7CFC00',  # Pale Green (10 - 30%)
        2: '#32CD32',  # Medium Green (30 - 60%)
        3: '#006400'   # Dark Green (60%+)
    }
    green_labels = {0: "0 - 10%", 1: "10 - 30%", 2: "30 - 60%", 3: "60%+"}

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add colorbar
    colormap = LinearColormap(
        colors=['#ADFF2F', '#7CFC00', '#32CD32', '#006400'],
        vmin=0, vmax=3,
        caption="Green Cover Density: 0-10%, 10-30%, 30-60%, 60%+"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        green_value = int(row['Green_Prediction'])
        color = green_colors.get(green_value, 'gray')  # Default to gray
        green_label = green_labels.get(green_value, "Unknown")

        popup_text = f"Green Cover Density: {green_label}"

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
    print(f"Green Cover Density map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Green Cover Density from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_green_cover_map(args.base_file)
