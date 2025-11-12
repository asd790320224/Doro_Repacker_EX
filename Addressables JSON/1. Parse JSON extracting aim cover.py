import json
import re
import os

# Function to load JSON while handling BOM
def load_json_without_bom(file_path):
    with open(file_path, 'rb') as f:
        content = f.read().decode('utf-8-sig')  # This removes any BOM
    return json.loads(content)

# Get the current script's directory (assumed to be Addressables JSON)
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory

# Define relative paths
input_directory = script_dir  # Use the script's directory as input

# Print current working directory for debugging
print(f"Current script directory: {script_dir}")
print(f"Looking for files in: {input_directory}")

# Find a JSON file that starts with "catalog_"
input_json_path = None
for filename in os.listdir(input_directory):
    if filename.startswith("catalog_db") and filename.endswith(".json"):
        input_json_path = os.path.join(input_directory, filename)
        break  # Stop after finding the first matching file

# Check if a JSON file was found
if input_json_path is None:
    print(f"Error: No JSON file starting with 'catalog_' found in {input_directory}")
else:
    # Try to load the JSON file while handling BOM and encoding issues
    try:
        data = load_json_without_bom(input_json_path)
    except json.JSONDecodeError as e:
        print(f"Error loading JSON file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    else:
        # Create a new structure
        transformed_data = []

        # Iterate through the original data and restructure it
        for key, value in data.items():
            # Use regex to extract file_code, skin_code, and type from the key, including 'aim', 'cover', and 'hd' only, while skipping 'sd'
            match = re.search(r'combat/c(\d{3})/(\d{2})/(aim|cover|hd)', key)
            if match and 'sd' not in key:
                file_code = "c" + match.group(1)  # Add "c" at the beginning of file_code
                skin_code = match.group(2)
                file_type = match.group(3)

                # Create a new entry
                transformed_entry = {
                    "file_code": file_code,
                    "skin_code": skin_code,
                    "type": file_type,
                    "hashed_name": value
                }

                # Add the entry to the transformed data
                transformed_data.append(transformed_entry)

        # Define output JSON path in the same directory
        output_json_path = os.path.join(input_directory, "structured_data_aim_cover.json")

        # Save the transformed data to a new JSON file
        with open(output_json_path, 'w', encoding='utf-8') as output_file:
            json.dump(transformed_data, output_file, indent=4)

        print(f"Transformed JSON has been saved to {output_json_path}")
