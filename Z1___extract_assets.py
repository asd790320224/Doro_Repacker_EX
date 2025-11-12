import os
import UnityPy
import subprocess
from Config_path import *

# Function to log errors to the ERRORS.txt file
def log_error(bundle_name, e):
    with open(error_log_path, "a") as error_file:
        error_file.write(f"{bundle_name} needs to be repacked manually\nERROR: {e}\n")

def run_cli_extractor(bundle_path, bundle_export_folder, bundle_name):
    print(f"    -> Retrying with AssetStudioModCLI...")
    cli_path = "AssetStudioModCLI\AssetStudioModCLI.exe"

    command = [
        cli_path,
        bundle_path,
        "-o", bundle_export_folder,
        "--unity-version", "2021.3.36f1",   # 解决了Na0h的mod无法被提取的困难
        "--log-level", "verbose",
        "--asset-type", "tex2d,textAsset"
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True)
        if b"Exported" in result.stdout or b"Converted" in result.stdout:
            print(f"    ✅ [CLI] Successfully extracted {bundle_name}")
            print(f"    -> Cleaning up unwanted files...")
            allowed_extensions = {'.atlas', '.skel', '.png'}
            for root, dirs, files in os.walk(bundle_export_folder):
                for filename in files:
                    try:
                        file_path = os.path.join(root, filename)
                        ext = os.path.splitext(filename)[1].lower()
                        if ext not in allowed_extensions:
                            os.remove(file_path)
                    except OSError as e_remove:
                        print(f"      -> ⚠️ Could not remove {filename}: {e_remove}")
            print(f"    -> Cleanup complete.")

        else:
            stdout_str = result.stdout.decode('gbk', errors='replace')
            print(f"    ⚠️ [CLI] Succeeded (Code 0) but NO assets were exported for {bundle_name}.")
            print("    -> Check CLI output:", stdout_str)
            log_error(bundle_name, f"CLI Succeeded (Code 0) but exported 0 files.\nCLI Output: {stdout_str}")

        return True

    except subprocess.CalledProcessError as e:
        stdout_str = e.stdout.decode('gbk', errors='replace')
        stderr_str = e.stderr.decode('gbk', errors='replace')
        print(f"    ❌ [CLI] FAILED (Code {e.returncode}) even with CLI.")
        log_error(bundle_name, f"UnityPy AND CLI failed.\nCLI Error: {stderr_str}\nCLI Output: {stdout_str}")
        return False

    except FileNotFoundError:
        print(f"    ❌ [CLI] Error: 'AssetStudioModCLI.exe' not found at path: {cli_path}")
        log_error(bundle_name, f"CLI Error: 'AssetStudioModCLI.exe' not found at path: {cli_path}")
        return False

    except Exception as e:
        print(f"    ❌ [CLI] An unexpected error occurred: {e}")
        log_error(bundle_name, f"CLI Error: {e}")
        return False


def main():
    try:
        for bundle_filename in os.listdir(bundles_folder):
            bundle_path = os.path.join(bundles_folder, bundle_filename)
            if os.path.isfile(bundle_path):
                if bundle_filename.endswith(".bundle"):
                    bundle_name = bundle_filename[:-7]
                else:
                    bundle_name = bundle_filename
                bundle_export_folder = os.path.join(export_folder, bundle_name)

                if not os.path.exists(bundle_export_folder):
                    os.makedirs(bundle_export_folder)

                # === ⬇ATTEMPT 1: Fast UnityPy ===
                try:
                    print(f"[UnityPy] Processing {bundle_filename}")
                    env = UnityPy.load(bundle_path)
                    for obj in env.objects:
                        try:
                            if obj.type.name == "Texture2D":
                                data = obj.read()
                                texture_path = os.path.join(bundle_export_folder, f"{data.m_Name}.png")
                                data.image.save(texture_path)
                            elif obj.type.name == "TextAsset":
                                data = obj.read()
                                text_path = os.path.join(bundle_export_folder, data.m_Name)
                                with open(text_path, "wb") as f:
                                    f.write(data.m_Script.encode("utf-8", "surrogateescape"))
                            elif obj.type.name == "AudioClip":
                                data = obj.read()
                                for name, audio_bytes in data.samples.items():
                                    audio_path = os.path.join(bundle_export_folder, name)
                                    with open(audio_path, "wb") as f:
                                        f.write(audio_bytes)
                        except Exception as e_obj:
                            log_error(bundle_name, f"Failed to extract object {obj.type.name}: {e_obj}")

                    print(f"  -> ✅ [UnityPy] Successfully extracted {bundle_filename}")

                # === ATTEMPT 1 FAILED, TRY ATTEMPT 2 ===
                except Exception as e_unitypy:
                    print(f"  ->  [UnityPy] Failed for {bundle_filename}: {e_unitypy}")
                    # 调用辅助函数，使用 CLI 重试
                    run_cli_extractor(bundle_path, bundle_export_folder, bundle_name)

    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")

# 用了AS CLI版本做顽固mod的处理，哎头疼

if __name__ == "__main__":
    main()