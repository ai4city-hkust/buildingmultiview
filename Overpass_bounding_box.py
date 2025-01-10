import requests
import random
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(filename='building_data_errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

def fetch_building_data(south, west, north, east, max_elements=100):
    """
    Fetches a random sample of building IDs and their coordinates from OpenStreetMap within a specified bounding box, categorized by building types.

    Parameters:
        south (float): Southern latitude of the bounding box.
        west (float): Western longitude of the bounding box.
        north (float): Northern latitude of the bounding box.
        east (float): Eastern longitude of the bounding box.
        max_elements (int): Maximum number of building elements to fetch.

    Returns:
        dict: Dictionary containing lists of dictionaries with building IDs and their coordinates, categorized by building types.
    """
    # Overpass API query
    query = f"""
    [out:json][timeout:25];
    (
      way["building"]({south},{west},{north},{east});
    );
    out center;
    """
    try:
        response = requests.get("http://overpass-api.de/api/interpreter", params={'data': query})
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        print(f"Fetched {len(data['elements'])} buildings")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching building data: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response for building data: {e}")
        print(f"Response content: {response.text}")
        return None

    # Extract building way IDs and their coordinates
    all_buildings = []
    for element in data['elements']:
        if element['type'] == 'way' and 'tags' in element and 'building' in element['tags'] and 'center' in element:
            building_info = {
                'id': element['id'],
                'lat': element['center']['lat'],
                'lon': element['center']['lon'],
                'type': element['tags']['building']
            }
            all_buildings.append(building_info)

    # Check if we have any buildings
    if not all_buildings:
        print("No buildings found")
        return None

    print(f"Total buildings extracted: {len(all_buildings)}")

    # Randomly sample buildings if more than max_elements are fetched
    if len(all_buildings) > max_elements:
        sampled_buildings = random.sample(all_buildings, max_elements)
    else:
        sampled_buildings = all_buildings

    def fetch_details(building, retries=3, backoff_factor=1):
        """
        Fetch details for a specific building with retry logic.

        Parameters:
            building (dict): Building information.
            retries (int): Number of retry attempts.
            backoff_factor (int): Exponential backoff factor for retries.

        Returns:
            dict: Updated building information with additional details (if available).
        """
        building_id = building['id']
        details_query = f"""
        [out:json][timeout:25];
        way({building_id});
        out body;
        >;
        out skel qt;
        """
        for attempt in range(retries):
            try:
                response = requests.get("http://overpass-api.de/api/interpreter", params={'data': details_query}, timeout=30)
                response.raise_for_status()  # Check if the request was successful
                details_data = response.json()
                if details_data['elements']:
                    element = details_data['elements'][0]
                    building['addr_street'] = element['tags'].get('addr:street', 'N/A')
                    building['height'] = element['tags'].get('height', 'N/A')
                else:
                    building['addr_street'] = 'N/A'
                    building['height'] = 'N/A'
                return building
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching details for building ID {building_id} (Attempt {attempt + 1}): {e}")
                time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
            except ValueError as e:
                logging.error(f"Error parsing JSON for building ID {building_id} (Attempt {attempt + 1}): {e}")
                return building
        # If all retries fail, log and skip the building
        logging.error(f"Skipping building ID {building_id} after {retries} retries.")
        building['addr_street'] = 'Error'
        building['height'] = 'Error'
        return building

    # Fetch details for each sampled building in parallel
    building_data = {
        "yes": [],
        "house": [],
        "commercial": []
    }
    with ThreadPoolExecutor(max_workers=5) as executor:  # Reduce the number of concurrent requests
        futures = [executor.submit(fetch_details, building) for building in sampled_buildings]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching building details"):
            building = future.result()
            building_type = building['type']
            building_info = {
                'id': building['id'],
                'lat': building['lat'],
                'lon': building['lon'],
                'addr_street': building['addr_street'],
                'height': building['height'],
                'building_type': building_type
            }
            if building_type == 'yes':
                building_data["yes"].append(building_info)
            elif building_type == 'house':
                building_data["house"].append(building_info)
            elif building_type == 'commercial':
                building_data["commercial"].append(building_info)
            if len(building_data["yes"]) + len(building_data["house"]) + len(building_data["commercial"]) >= max_elements:
                break
            time.sleep(0.5)  # Add a delay between requests to avoid hitting rate limits

    return building_data

def save_to_jsonl(data, city_name, max_elements, south, west, north, east):
    """
    Saves the building data to a JSONL file.

    Parameters:
        data (dict): The building data to save.
        city_name (str): Name of the city.
        max_elements (int): Maximum number of building elements.
        south (float): Southern latitude of the bounding box.
        west (float): Western longitude of the bounding box.
        north (float): Northern latitude of the bounding box.
        east (float): Eastern longitude of the bounding box.
    """
    filename = f"Data/{city_name}_{max_elements}_{south}_{west}_{north}_{east}.jsonl"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        for btype, buildings in data.items():
            for building in buildings:
                json.dump(building, f, ensure_ascii=False)
                f.write('\n')
    print(f"Data saved to {filename}")

# Specify bounding box coordinates
south = 40.4459
west = -112.3853
north = 40.8917
east = -111.3073

# Specify city name
city_name = "SLC"

# Specify maximum number of elements
max_elements = 4000

# Fetch building data for the specified bounding box
building_data = fetch_building_data(south, west, north, east, max_elements)
if building_data:
    save_to_jsonl(building_data, city_name, max_elements, south, west, north, east)
