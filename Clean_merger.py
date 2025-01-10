import os
import subprocess
import sys
from tqdm import tqdm

def execute_command(command):
    try:
        print(f"Executing command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        sys.exit(1)

def main(base_file):
    # Ensure the base file exists
    if not os.path.exists(base_file):
        print(f"Base file does not exist: {base_file}")
        sys.exit(1)

    # Define the list of commands to execute
    commands = [
        f"python utils/clean_house.py \"{base_file}\"",
        f"python utils/clean_svi.py \"{base_file}\"",
        f"python utils/clean_neighbor.py \"{base_file}\"",
        f"python utils/merge.py --base_file \"{base_file}\"",
        f"python utils/merge_fliter.py --base_file \"{base_file}\""
    ]

    # Execute each command in sequence with a progress bar
    for command in tqdm(commands, desc="Executing commands", unit="command"):
        execute_command(command)

if __name__ == "__main__":
    # Check for proper usage
    if len(sys.argv) != 2:
        print("Usage: python Clean_merger.py \"Data/filename.jsonl\"")
        sys.exit(1)

    base_file = sys.argv[1]
    main(base_file)