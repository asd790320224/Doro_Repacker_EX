import os
import shutil
from Config_path import *

# Function to log errors to the ERRORS.txt file
def log_error(message):
    with open(error_log_path, "a") as error_file:
        error_file.write(message + "\n")

def main():
    try:
        # Step 1: Gather all subfolders in "Repacked" and move files to the root
        for root, dirs, files in os.walk(REPACKED_FOLDER):
            for file in files:
                source_file_path = os.path.join(root, file)  # Source file path
                destination_file_path = os.path.join(REPACKED_FOLDER, file)  # Destination path

                try:
                    # Handle name conflicts by appending an index if needed
                    index = 1
                    while os.path.exists(destination_file_path):
                        base_name, ext = os.path.splitext(file)
                        destination_file_path = os.path.join(REPACKED_FOLDER, f"{base_name}_{index}{ext}")
                        index += 1

                    shutil.move(source_file_path, destination_file_path)
                    print(f"Moved {source_file_path} to {destination_file_path}")

                except Exception as e:
                    error_message = f"Failed to move {source_file_path} to {destination_file_path}: {e}"
                    print(error_message)
                    log_error(error_message)

        # Step 2: Delete empty subfolders
        for root, dirs, files in os.walk(REPACKED_FOLDER, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_path)  # Remove the directory
                    print(f"Deleted empty folder: {dir_path}")

                except OSError as e:
                    error_message = f"Failed to delete folder {dir_path}: {e}"
                    print(error_message)
                    log_error(error_message)

        # Step 3: Rename files by removing "_1" from the filenames
        for file in os.listdir(REPACKED_FOLDER):
            file_path = os.path.join(REPACKED_FOLDER, file)

            # Check if the file name ends with "_1" before the extension
            if file.endswith("_1"):
                try:
                    new_file_name = file[:-2] + os.path.splitext(file)[1]  # Remove "_1"
                    new_file_path = os.path.join(REPACKED_FOLDER, new_file_name)
                    
                    os.rename(file_path, new_file_path)  # Rename the file
                    print(f"Renamed {file_path} to {new_file_path}")

                except Exception as e:
                    error_message = f"Failed to rename {file_path} to {new_file_path}: {e}"
                    print(error_message)
                    log_error(error_message)

    except Exception as e:
        # Log any unexpected error and keep the terminal open
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        log_error(error_message)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()