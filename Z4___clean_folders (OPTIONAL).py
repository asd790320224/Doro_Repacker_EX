import os
import shutil

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the folder paths relative to the current script's directory
modded_bundles_folder = os.path.join(script_dir, "Modded Bundles")
original_bundles_folder = os.path.join(script_dir, "Original Bundles")
extracted_assets_folder = os.path.join(script_dir, "Extracted Assets")
original_lobby_burst_bundles_path = os.path.join(script_dir, "Original lobby burst bundles")
original_even_bundles_path = os.path.join(script_dir, "Original event bundles")
original_portraits_path = os.path.join(script_dir, "Original Portraits")
original_other_path = os.path.join(script_dir, "Original other bundles")

# Function to delete files inside a folder and optionally recreate the folder
def delete_files_in_folder(folder_path, recreate=False):
    if os.path.exists(folder_path):
        print(f"Deleting files in {folder_path}...")
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Optionally delete subfolders too
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        if recreate:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Recreated folder: {folder_path}")
    else:
        print(f"{folder_path} does not exist.")
        if recreate:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")

# Delete files in each folder and recreate if needed
#delete_files_in_folder(extracted_portrait_folder, recreate=True)
delete_files_in_folder(original_even_bundles_path, recreate=True)
delete_files_in_folder(original_lobby_burst_bundles_path, recreate=True)
delete_files_in_folder(original_portraits_path, recreate=True)

# 旧mod要不要删除？
# delete_files_in_folder(modded_bundles_folder, recreate=True)

delete_files_in_folder(original_bundles_folder, recreate=True)   # Clean "Original Bundles"
delete_files_in_folder(extracted_assets_folder, recreate=True)   # Clean "Extracted Assets"

print("All specified files have been deleted.")
