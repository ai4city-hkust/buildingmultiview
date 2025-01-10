import pandas as pd
import folium
from branca.colormap import StepColormap
import os
import argparse

def process_property_type_map(base_file):
    # Generate the actual file to process based on input file
    base_name = os.path.splitext(os.path.basename(base_file))[0]
    actual_file = os.path.join("output", base_name, f"{base_name}_final.jsonl")

    if not os.path.exists(actual_file):
        print(f"Expected file {actual_file} does not exist. Please ensure it is generated.")
        return

    # Generate output file path based on input file
    output_folder = os.path.join("maps", base_name)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{base_name}_PropertyType.html")

    # Read the JSONL file
    data = pd.read_json(actual_file, lines=True)

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'Property_Type_Prediction'}
    if not required_columns.issubset(data.columns):
        print(f"File {actual_file} is missing required columns, skipping.")
        return

    # Convert Property_Type_Prediction to numeric and filter valid data
    data['Property_Type_Prediction'] = pd.to_numeric(data['Property_Type_Prediction'], errors='coerce')
    data = data.dropna(subset=['Property_Type_Prediction'])

    # Define color mappings
    property_colors = {
        0: '#ADFF2F',  # Light Green (Single Family)
        1: '#87CEEB',  # Sky Blue (Apartment)
        2: '#1E90FF',  # Deep Blue (Multi-Family)
        3: '#FFA500',  # Orange (Manufactured)
        4: '#8A2BE2',  # Purple (Condo)
        5: '#228B22',  # Dark Green (Townhouse)
        6: '#A9A9A9'   # Gray (Other)
    }

    property_labels = {
        0: "Single Family",
        1: "Apartment",
        2: "Multi-Family",
        3: "Manufactured",
        4: "Condo",
        5: "Townhouse",
        6: "Other"
    }

    # Create Folium map
    m = folium.Map(
        location=[data['lat'].mean(), data['lon'].mean()],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add StepColormap
    colormap = StepColormap(
        colors=['#ADFF2F', '#87CEEB', '#1E90FF', '#FFA500', '#8A2BE2', '#228B22', '#A9A9A9'],
        index=[0, 1, 2, 3, 4, 5, 6],
        vmin=0, vmax=6,
        caption=("Property Type:<br>"
                 "0: Single Family, 1: Apartment, 2: Multi-Family, 3: Manufactured,<br>"
                 "4: Condo, 5: Townhouse, 6: Other")
    )
    colormap.add_to(m)

    # Add data points to the map
    for _, row in data.iterrows():
        prop_value = int(row['Property_Type_Prediction'])
        color = property_colors.get(prop_value, 'gray')  # Default to gray
        prop_label = property_labels.get(prop_value, "Unknown")

        popup_text = f"Property Type: {prop_label}"

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
    print(f"Property Type map saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for Property Type from a JSONL file.")
    parser.add_argument("--base_file", required=True, help="Path to the input JSONL file (e.g., Data/base.jsonl).")
    args = parser.parse_args()

    process_property_type_map(args.base_file)
