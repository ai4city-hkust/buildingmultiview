import pandas as pd
import folium
from branca.colormap import StepColormap
import os
import argparse

def process_land_use_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_LandUse.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'Land_Use_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert Land_Use_Prediction to numeric and filter valid data
    data['Land_Use_Prediction'] = pd.to_numeric(data['Land_Use_Prediction'], errors='coerce')
    data = data.dropna(subset=['Land_Use_Prediction'])

    # Define color mappings
    land_use_colors = {
        0: '#ADFF2F',  # Light Green (Agricultural Land)
        1: '#DEB887',  # Light Brown (Bare Land)
        2: '#1E90FF',  # Blue (Educational Land)
        3: '#228B22',  # Dark Green (Greenspace)
        4: '#8A2BE2',  # Purple (Industrial Land)
        5: '#FFA500',  # Orange (Public Commercial Land)
        6: '#A9A9A9',  # Gray (Residential Land)
        7: '#FFD700',  # Yellow (Transportation Land)
        8: '#00BFFF',  # Light Blue (Waterbody)
        9: '#556B2F'   # Dark Olive Green (Woodland)
    }

    land_use_labels = {
        0: "Agricultural",
        1: "Bare",
        2: "Educational",
        3: "Greenspace",
        4: "Industrial",
        5: "Public Commercial",
        6: "Residential",
        7: "Transportation",
        8: "Waterbody",
        9: "Woodland"
    }

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # HTML caption for the colorbar
    html_caption = (
        "Land Use Categories:<br>"
        "0: Agricultural, 1: Bare, 2: Educational, 3: Greenspace, 4: Industrial,<br>"
        "5: Public Commercial, 6: Residential, 7: Transportation, 8: Waterbody, 9: Woodland"
    )

    # Add StepColormap
    colormap = StepColormap(
        colors=list(land_use_colors.values()),
        index=list(land_use_colors.keys()),
        vmin=0, vmax=9,
        caption=html_caption  # HTML format for line breaks
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        land_use_value = int(row['Land_Use_Prediction'])
        color = land_use_colors.get(land_use_value, 'gray')  # Default to gray
        land_use_label = land_use_labels.get(land_use_value, "Unknown")

        popup_text = f"Land Use: {land_use_label}"

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
    print(f"Land Use map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Land Use from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_land_use_map(args.base_file)
