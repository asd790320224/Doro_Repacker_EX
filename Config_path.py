# file: config.py
from pathlib import Path
import os, sys

def get_base_dir():
    """
    Lấy thư mục chứa .exe hoặc script chính
    Kiểm tra nhiều cách để đảm bảo hoạt động với Nuitka
    """
    # Cách 1: Kiểm tra sys.frozen (PyInstaller, cx_Freeze, Nuitka thường set)
    is_frozen = getattr(sys, 'frozen', False)
    
    # Cách 2: Kiểm tra nếu đang chạy từ .exe
    # Nếu sys.executable không phải python.exe/pythonw.exe
    is_executable = not sys.executable.lower().endswith(('python.exe', 'pythonw.exe', 'python'))
    
    # Cách 3: Kiểm tra __file__ có phải trong thư mục TEMP không
    in_temp = 'temp' in __file__.lower() or 'tmp' in __file__.lower()
    
    print(f"Debug info:")
    print(f"  sys.frozen: {is_frozen}")
    print(f"  is_executable: {is_executable}")
    print(f"  in_temp: {in_temp}")
    print(f"  sys.executable: {sys.executable}")
    print(f"  __file__: {__file__}")
    
    # Nếu một trong các điều kiện này đúng = đang chạy .exe
    if is_frozen or is_executable or in_temp:
        base = os.path.dirname(os.path.abspath(sys.executable))
        print(f"Running as EXE, base dir: {base}")
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        print(f"Running as script, base dir: {base}")
    
    return base

script_dir = get_base_dir()

# Các thư mục chính
json_path = os.path.join(script_dir, "Addressables JSON")
original_bundles_path = os.path.join(script_dir, "Original Bundles")
original_portraits_path = os.path.join(script_dir, "Original Portraits")
original_lobby_burst_bundles_path = os.path.join(script_dir, "Original lobby burst bundles")
original_even_bundles_path = os.path.join(script_dir, "Original event bundles")
original_other_bundles_path = os.path.join(script_dir, "Original other bundles")

bundles_folder = os.path.join(script_dir, "Modded Bundles")
export_folder = os.path.join(script_dir, "Extracted Assets")
error_log_path = os.path.join(script_dir, "ERRORS.txt")

# Đảm bảo thư mục tồn tại
for folder in [
    original_bundles_path,
    original_portraits_path,
    original_lobby_burst_bundles_path,
    original_even_bundles_path,
    original_other_bundles_path,
    bundles_folder,
    export_folder,
]:
    os.makedirs(folder, exist_ok=True)

# --- REPACK SCRIPT SETTINGS ---
MODDED_ASSETS_FOLDER = Path(script_dir, "Extracted Assets")
ORIGINAL_BUNDLES_FOLDER = Path(script_dir, "Original Bundles")
ORIGINAL_PORTRAITS_FOLDER = Path(script_dir, "Original Portraits")
ORIGINAL_LOBBY_BURST_FOLDER = Path(script_dir, "Original lobby burst bundles")
ORIGINAL_EVENT_FOLDER = Path(script_dir, "Original event bundles")
ORIGINAL_OTHER_FOLDER = Path(script_dir, "Original other bundles")
REPACKED_FOLDER = Path(script_dir, "Repacked")
ERROR_LOG_FILE = Path(script_dir, "ERRORS.txt")

# Tạo thư mục Repacked nếu chưa có
REPACKED_FOLDER.mkdir(exist_ok=True)
MODDED_ASSETS_FOLDER.mkdir(exist_ok=True)

ADD_PADDING = False
MAX_WORKERS = 4