import pandas as pd
import folium
from branca.colormap import LinearColormap
import os
import argparse

def process_roof_type_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_RoofType.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'Roof_Type_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert Roof_Type_Prediction to numeric and filter valid data
    data['Roof_Type_Prediction'] = pd.to_numeric(data['Roof_Type_Prediction'], errors='coerce')
    data = data.dropna(subset=['Roof_Type_Prediction'])

    # Define color mappings
    roof_colors = {
        0: 'red',  # Flat
        1: 'green',  # Gabled
        2: 'blue'  # Hipped
    }

    roof_labels = {
        0: "Flat",
        1: "Gabled",
        2: "Hipped"
    }

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add LinearColormap
    colormap = LinearColormap(
        colors=['red', 'green', 'blue'],
        vmin=0, vmax=2,
        caption="Roof Type: Flat (0), Gabled (1), Hipped (2)"
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        roof_type = int(row['Roof_Type_Prediction'])
        color = roof_colors.get(roof_type, 'gray')  # Default to gray
        roof_label = roof_labels.get(roof_type, "Unknown")

        popup_text = f"Roof Type: {roof_label}"

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
    print(f"Roof Type map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Roof Type from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_roof_type_map(args.base_file)
