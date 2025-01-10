import pandas as pd
import folium
from branca.colormap import StepColormap
import os
import argparse

def process_wall_window_ratio_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_WallWindowRatio.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'WWR_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert WWR_Prediction to numeric and filter valid data
    data['WWR_Prediction'] = pd.to_numeric(data['WWR_Prediction'], errors='coerce')
    data = data.dropna(subset=['WWR_Prediction'])

    # Define color mappings
    wwr_colors = {
        0: '#F5DEB3',  # Wheat (0% - 20%)
        1: '#FFA07A',  # Light Salmon (20% - 40%)
        2: '#FF7F50',  # Coral (40% - 60%)
        3: '#CD5C5C'   # Indian Red (60% - 100%)
    }

    wwr_labels = {
        0: "0% - 20%",
        1: "20% - 40%",
        2: "40% - 60%",
        3: "60% - 100%"
    }

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add StepColormap
    colormap = StepColormap(
        colors=['#F5DEB3', '#FFA07A', '#FF7F50', '#CD5C5C'],
        index=[0, 1, 2, 3],
        vmin=0, vmax=3,
        caption="Wall Window Ratio: 0% - 20%, 20% - 40%, 40% - 60%, 60% - 100%"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        wwr_value = int(row['WWR_Prediction'])
        color = wwr_colors.get(wwr_value, 'gray')  # Default to gray
        wwr_label = wwr_labels.get(wwr_value, "Unknown")

        popup_text = f"Wall Window Ratio: {wwr_label}"

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
    print(f"Wall Window Ratio map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Wall Window Ratio from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_wall_window_ratio_map(args.base_file)
