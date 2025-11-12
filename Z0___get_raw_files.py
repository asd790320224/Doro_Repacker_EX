from pathlib import Path
import re
import argparse
from typing import List, Set
import os, sys
import json
import requests
from Config_path import *

import subprocess
import shutil

try:
    _SCRIPT_DIR = SCRIPT_DIR
except NameError:
    print("Warning: SCRIPT_DIR not found in Config_path.py. Using fallback...")
    try:
        _SCRIPT_DIR = Path(__file__).resolve().parent
    except NameError:
        _SCRIPT_DIR = Path.cwd()

NAU_EXE_PATH = _SCRIPT_DIR / "NAU" / "NAU.exe"


def decrypt_folder(folder_path: Path):
    """使用 NAU.exe 解密整个文件夹 (d -i 'folder_path')"""

    folder_path = Path(folder_path)

    if not NAU_EXE_PATH.exists():
        print(f"  [ERROR] NAU.exe not found at: {NAU_EXE_PATH}")
        print(f"  Please make sure NAU.exe is in the NAU folder.")
        return

    if not folder_path.exists():
        print(f"  [ERROR] Cannot decrypt, folder not found: {folder_path}")
        return

    print(f"\n  -> Decrypting folder with NAU: {folder_path}")
    try:
        # 命令: "NAU/NAU.exe" d -i "path/to/folder"
        command = [str(NAU_EXE_PATH), "d", "-i", str(folder_path)]

        # NAU.exe 正在等待 "Press enter to continue."
        # 使用 input='\n' 来自动发送一个回车键 (newline)
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            input='\n'  # <-- 自动“按下回车”
        )

        if result.stdout:
            output_lines = [
                line for line in result.stdout.splitlines()
                if "press enter" not in line.lower()
            ]
            clean_output = "\n".join(output_lines)
            if clean_output.strip():
                print(f"  [NAU Output]:\n{clean_output}")

        print(f"  [SUCCESS] Decryption complete for {folder_path.name}")

    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] NAU failed to run on folder {folder_path.name}.")
        print(f"  Return Code: {e.returncode}")
        if e.stdout:
            print(f"  [NAU Stdout]:\n{e.stdout}")
        if e.stderr:
            print(f"  [NAU Stderr]:\n{e.stderr}")
    except Exception as e:
        print(f"  [ERROR] An unexpected error occurred during decryption: {e}")


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None


PATTERNS = [
    re.compile(r"^c\d{3}_\d{2}_(standing|aim|cover|icons)$"),
    re.compile(r"^c\d{3}[_-]\d{2}[_-](lobby|burst)$"),
    re.compile(r"^[A-Za-z0-9_-]+-lobby$")
]


# ... [所有 normalize_name, classify, analyze_... 函数保持不变] ...
def keep_up_to_third_separator(name: str) -> str:
    count = 0
    for i, ch in enumerate(name):
        if ch == '-' or ch == '_':
            count += 1
            if count == 3:
                return name[:i]
    return name


def trim_after_lobby_prefix(name: str) -> str:
    m = re.match(r"^(.*?-lobby)\b", name)
    if m:
        return m.group(1)
    return name


def normalize_name(orig: str) -> str:
    name = orig
    if re.match(r"^c\d{3}_", name) or re.match(r"^c\d{3}-", name):
        name = keep_up_to_third_separator(name)
    elif re.match(r"^[A-Za-z0-9_-]+-lobby", name):
        name = trim_after_lobby_prefix(name)
    return name


def collect_unique_names(folder: Path) -> Set[str]:
    s: Set[str] = set()
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    for p in folder.iterdir():
        if p.is_file():
            stem = p.stem  # tên file không có extension
            normalized = normalize_name(stem)
            s.add(normalized)
    return s


def classify(names: Set[str]) -> tuple[List[str], List[str], List[str], List[str]]:
    list1: List[str] = []
    list2: List[str] = []
    list3: List[str] = []
    list4: List[str] = []
    for n in sorted(names):
        if PATTERNS[0].fullmatch(n):
            list1.append(n)
        elif PATTERNS[1].fullmatch(n):
            list2.append(n)
        elif PATTERNS[2].fullmatch(n):
            list3.append(n)
        else:
            list4.append(n)
    return list1, list2, list3, list4


def download_file_normalMod_burstMod(url, mod, output_folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        if mod['type'] in ["lobby", "burst"]:
            filename = f"{mod['character_ID']}-{mod['skin_ID']}-{mod['type']}.bundle"
        else:
            filename = f"{mod['character_ID']}_{mod['skin_ID']}_{mod['type']}.bundle"
        file_path = os.path.join(output_folder, filename)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded and saved: {filename} to {output_folder}")
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")


def download_file_eventMod(url, mod, output_folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        filename = f"{mod}-lobby.bundle"
        file_path = os.path.join(output_folder, filename)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {filename} to {output_folder}")
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")


def download_file_otherMod(url, mod, output_folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        filename = mod
        file_path = os.path.join(output_folder, filename)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {filename} to {output_folder}")
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")


def analyze_normalMod_filename(name: str):
    attribute = name.split("_")
    character_ID = attribute[0]
    skin_ID = attribute[1]
    type = attribute[2]
    return character_ID, skin_ID, type


def analyze_burstMod_filename(name: str):
    standard_name = name.replace("_", "-")
    attribute = standard_name.split("-")
    character_ID = attribute[0]
    skin_ID = attribute[1]
    type = attribute[2]
    return character_ID, skin_ID, type


def analyze_eventMod_filename(name: str):
    event_ID = name.split("-")[0]
    return event_ID


def parse_file_name_to_dicts_normalMod(
        listMod):  # make a list list[dict{str:str,str:str,str:str}] to store character id, skin id, type of every mod into one list
    element_list = []
    for name in listMod:
        character_ID, skin_ID, type = analyze_normalMod_filename(name)
        dict1 = {'character_ID': character_ID, 'skin_ID': skin_ID, "type": type}
        element_list.append(dict1)
    return element_list


def parse_file_name_to_dicts_burstMod(
        listMod):  # make a list list[dict{str:str,str:str,str:str}] to store character id, skin id, type of every mod into one list
    element_list = []
    for name in listMod:
        character_ID, skin_ID, type = analyze_burstMod_filename(name)
        dict1 = {'character_ID': character_ID, 'skin_ID': skin_ID, "type": type}
        element_list.append(dict1)
    return element_list


def parse_file_name_to_dicts_eventMod(listMod):  # just a list[str]
    element_list = []
    for name in listMod:
        event_ID = analyze_eventMod_filename(name)
        element_list.append(event_ID)
    return element_list


def download_matched_file_normalMod(element_list):
    try:
        transformed_catalog = load_json(os.path.join(json_path, "structured_data_aim_cover_URL.json"))
        structured_data = load_json(os.path.join(json_path, "structured_data_standing_URL.json"))
        structured_data_portrait = load_json(os.path.join(json_path, "structured_data_portraits_URL.json"))

        if transformed_catalog is None or structured_data is None or structured_data_portrait is None:
            print("error: Empty catalog")
            return False

        jsonData = transformed_catalog + structured_data + structured_data_portrait

        for mod in element_list:
            for data in jsonData:
                if (
                        data.get('file_code') == mod["character_ID"] and
                        data.get('skin_code') == mod["skin_ID"] and
                        data.get('type') == mod["type"]
                ):
                    url = data.get('hashed_name')
                    if url:
                        print(f"Downloading file from URL: {url}")
                        if data in structured_data_portrait:
                            output_folder = original_portraits_path
                        else:
                            output_folder = original_bundles_path

                        download_file_normalMod_burstMod(url, mod, output_folder)

    except Exception as e:
        print(f"error: {e}")


def download_matched_file_burstMod(element_list):
    try:
        lobby_burst_catalog = load_json(os.path.join(json_path, "lobby_burst_merged_data_URL.json"))

        if lobby_burst_catalog is None:
            print("error: Empty catalog")
            return False

        for mod in element_list:
            for data in lobby_burst_catalog:
                if (
                        data.get('ID') == mod["character_ID"] and
                        data.get('skin_code') == mod["skin_ID"]
                ):
                    if mod["type"] == "burst":
                        url = data.get('burst_id')
                    elif mod["type"] == "lobby":
                        url = data.get("lobby_id")
                    else:
                        print("error: WRONG TYPE")
                        return False
                    output_folder = original_lobby_burst_bundles_path
                    download_file_normalMod_burstMod(url, mod, output_folder)

    except Exception as e:
        print(f"error: {e}")


def download_matched_file_eventMod(element_list):
    try:
        lobby_event_catalog = load_json(os.path.join(json_path, "lobby_event_data_URL.json"))

        if lobby_event_catalog is None:
            print("error: Empty catalog")
            return False

        for mod in element_list:
            for data in lobby_event_catalog:
                if (data.get("ID") == mod):
                    url = data.get("lobby_id")
                    output_folder = original_even_bundles_path
                    download_file_eventMod(url, mod, output_folder)

    except Exception as e:
        print(f"error: {e}")


def create_reverse_dict(data):
    """
    Create reverse dict (value -> key) from non-nested JSON file.
    Used to look up name from hash.
    """
    if not isinstance(data, dict):
        raise ValueError("JSON data must be a top-level object (dict).")

    reverse_map = {value: key for key, value in data.items()}
    return reverse_map


def write_mod_name_log(dir_path: str, text1: str, text2: str) -> bool:
    try:
        # Tạo thư mục nếu chưa có
        os.makedirs(dir_path, exist_ok=True)

        # Đường dẫn tới file log
        file_path = os.path.join(dir_path, "hash_to_name.txt")

        # Ghi nội dung vào file (append)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{text1} --> {text2}\n")

        return True
    except Exception as e:
        print(f"Lỗi khi ghi log: {e}")
        return False


def download_matched_file_otherMod(element_list):
    try:
        reverse_mother_catalog_path = os.path.join(json_path, "reverse_mother_catalog_db.json")
        reverse_core_other_catalog_path = os.path.join(json_path, "reverse_core_other_catalog.json")
        mother_catalog = load_json(os.path.join(json_path, "catalog_db.json"))
        mother_catalog_URL = load_json(os.path.join(json_path, "catalog_db_URL.json"))
        core_other_catalog = load_json(os.path.join(json_path, "core_other.json"))
        core_other_catalog_URL = load_json(os.path.join(json_path, "core_other_URL.json"))

        if mother_catalog is None or mother_catalog_URL is None or core_other_catalog is None or core_other_catalog_URL is None:
            print("error: Empty catalog")
            return False

        if not os.path.exists(reverse_mother_catalog_path):
            reverse_map = create_reverse_dict(mother_catalog)
            with open(reverse_mother_catalog_path, 'w', encoding='utf-8') as f:
                json.dump(reverse_map, f, ensure_ascii=False, indent=4)
        if not os.path.exists(reverse_core_other_catalog_path):
            reverse_map = create_reverse_dict(core_other_catalog)
            with open(reverse_core_other_catalog_path, 'w', encoding='utf-8') as f:
                json.dump(reverse_map, f, ensure_ascii=False, indent=4)

        reverse_mother_catalog = load_json(reverse_mother_catalog_path)
        reverse_core_other_catalog = load_json(reverse_core_other_catalog_path)

        hash2name_catalog = {}
        if isinstance(reverse_mother_catalog, dict):
            hash2name_catalog.update(reverse_mother_catalog)
        if isinstance(reverse_core_other_catalog, dict):
            hash2name_catalog.update(reverse_core_other_catalog)

        name2URL_catalog = {}
        if isinstance(mother_catalog_URL, dict):
            name2URL_catalog.update(mother_catalog_URL)
        if isinstance(core_other_catalog_URL, dict):
            name2URL_catalog.update(core_other_catalog_URL)

        hashMod = []
        nameMod = []

        for mod in element_list:
            print(f"mod name: {mod}")
            if mod in hash2name_catalog:
                hashMod.append(mod)
                write_mod_name_log(original_other_bundles_path, mod, hash2name_catalog[mod])
                continue

            if not mod.endswith(".bundle"):
                modNameFix = f"{mod}.bundle"

            if modNameFix in name2URL_catalog:
                nameMod.append(modNameFix)
            else:
                print(f"Cannot find original file of the mod: {mod} check ")

        output_folder = original_other_bundles_path

        for mod in hashMod:
            modName = hash2name_catalog[mod]
            url = name2URL_catalog[modName]
            modAddExtention = f"{mod}.bundle"
            download_file_otherMod(url, modAddExtention, output_folder)

        for mod in nameMod:
            url = name2URL_catalog[mod]
            download_file_otherMod(url, mod, output_folder)

    except Exception as e:
        print(f"error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Normalize and classify mod filenames in a folder")
    parser.add_argument("--dir", dest="dir", default="Modded Bundles",
                        help="Folder chứa files (mặc định: 'Modded Bundles')")
    args = parser.parse_args()

    folder = Path(args.dir)
    try:
        unique = collect_unique_names(folder)
    except FileNotFoundError as e:
        print(e)
        return

    print(f"Found {len(unique)} unique normalized names")

    normalMod, burstMod, evenMod, otherMod = classify(unique)

    parsed_data_normalMod = parse_file_name_to_dicts_normalMod(normalMod)
    parsed_data_burstMod = parse_file_name_to_dicts_burstMod(burstMod)
    parsed_data_evenMod = parse_file_name_to_dicts_eventMod(evenMod)

    # --- 1. 下载 Normal Mods ---
    print("\n--- Downloading Normal Mods (standing, aim, cover, portraits) ---")
    download_matched_file_normalMod(parsed_data_normalMod)

    # --- 2. 下载 Burst/Lobby Mods (不解密) ---
    print("\n--- Downloading Burst/Lobby Mods ---")
    download_matched_file_burstMod(parsed_data_burstMod)

    # --- 3. 下载 Event Mods ---
    print("\n--- Downloading Event Mods ---")
    download_matched_file_eventMod(parsed_data_evenMod)

    # --- 4. 下载 Other Mods ---
    print("\n--- Downloading Other Mods ---")
    download_matched_file_otherMod(otherMod)

    # --- 5. 在所有下载完成后，运行批量解密 ---
    print("\n--- Running Batch Decryption ---")

    # 解密 Normal Mods (standing, aim, cover)
    if normalMod:
        decrypt_folder(original_bundles_path)
        # decrypt_folder(original_portraits_path)

    # 解密 Event Mods
    # if evenMod:
        # decrypt_folder(original_even_bundles_path)

    # 解密 Other Mods
    # if otherMod:
        # decrypt_folder(original_other_bundles_path)

    print("\n--- All operations complete. ---")


if __name__ == '__main__':
    main()