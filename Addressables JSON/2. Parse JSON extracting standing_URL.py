import json
import re
import os
import codecs

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory

# Define input and output paths using the script's directory
input_directory = script_dir  # Use the script's directory as input
output_json_path = os.path.join(script_dir, "structured_data_standing_URL.json")  # Output path in the same directory

def convert_json(input_json_path, output_json_path):
    # Check if the input file exists
    if not os.path.exists(input_json_path):
        print(f"Error: File {input_json_path} not found!")
        return

    # Load the original JSON file while handling BOM and encoding issues
    try:
        with codecs.open(input_json_path, "r", encoding="utf-8-sig") as file:  # utf-8-sig removes BOM if present
            content = file.read().strip()  # Strip any whitespace to avoid empty content errors
            
            # Check if file is empty
            if not content:
                print("Error: The JSON file is empty.")
                return
            
            # Try to parse the JSON content
            data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return

    # Create a list to hold the new structured entries
    structured_data = []

    # Iterate over the original data to extract necessary fields
    for key, hashed_name in data.items():
        # Skip 'sd' results
        if 'sd' in key:
            continue
        
        # Only process entries with 'standing' and 'hd' in the key
        if 'standing' in key and 'hd' in key:
            # Regex to extract file_code and skin_code from keys like "/standing/c014/00_hd"
            match = re.search(r'/standing/c(\d{3})/(\d{2})_hd', key)
            
            if match:
                file_code = match.group(1)  # Extract the file_code (e.g., 014)
                skin_code = match.group(2)  # Extract the skin_code (e.g., 00)
                
                # Create the structured entry
                entry = {
                    "file_code": f"c{file_code}",
                    "skin_code": skin_code,
                    "type": "standing",  # Set type as 'standing'
                    "hashed_name": hashed_name
                }
                # Append the entry to the list
                structured_data.append(entry)

    # Check if there is any data to write
    if not structured_data:
        print("No 'standing_hd' entries found.")
        return

    # Write the new structured data to a JSON file
    try:
        with open(output_json_path, "w", encoding="utf-8") as outfile:
            json.dump(structured_data, outfile, indent=4)
        print(f"Structured JSON file generated at: {output_json_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

# Find a JSON file that starts with "catalog_"
input_json_path = None
for filename in os.listdir(input_directory):
    if filename.startswith("catalog_db_URL") and filename.endswith(".json"):
        input_json_path = os.path.join(input_directory, filename)
        break  # Stop after finding the first matching file

# Check if a JSON file was found
if input_json_path is None:
    print(f"Error: No JSON file starting with 'catalog_' found in {input_directory}")
else:
    # Call the function to convert JSON with the paths set above
    convert_json(input_json_path, output_json_path)
