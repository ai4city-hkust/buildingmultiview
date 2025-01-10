import subprocess
import sys
from tqdm import tqdm
import argparse

def execute_commands(commands):
    for command in tqdm(commands, desc="Executing commands", unit="command"):
        try:
            print(f"Executing: {command}")
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute a series of map generation scripts.")
    parser.add_argument("--base_file", required=True, help="Path to the base file to be processed.")
    args = parser.parse_args()

    # List of commands to execute
    commands = [
        f"python utils/resullt_map_LargeBuildingCount.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_BuildingDensity.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_BuildingGroupPattern.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_floorcount.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_green.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_LandUSE.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_Property_Type.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_RoadDensity.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_rooftype.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_Swimmingpool.py --base_file \"{args.base_file}\"",
        f"python utils/result_map_wwr.py --base_file \"{args.base_file}\""
    ]

    execute_commands(commands)
