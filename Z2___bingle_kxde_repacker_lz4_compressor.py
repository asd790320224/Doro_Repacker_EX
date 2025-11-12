from PIL import Image
import os
import UnityPy
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from Config_path import *
import base64
from pathlib import Path


class ModClassifier:
    """Classifies mod types based on folder naming patterns."""

    # Pre-compiled patterns
    NORMAL_PATTERN = re.compile(r"^(c\d{3})[_-](\d{2})[_-](standing|aim|cover)")
    BURST_PATTERN = re.compile(r"^(c\d{3})[_-](\d{2})[_-](lobby|burst)")
    EVENT_PATTERN = re.compile(r"^([A-Za-z0-9_-]+-lobby)")

    @classmethod
    @lru_cache(maxsize=1024)
    def classify_mod(cls, folder_name: str) -> Tuple[str, Optional[str]]:
        """Classify mod type and extract base bundle name.

        Returns: (mod_type, base_bundle_name)
        Example: 'c016_00_standing_catalyzer_rapisummerB1' -> ('normal', 'c016_00_standing')
        Example: 'c016_00_burst_Yuk11...' -> ('burst', 'c016-00-burst') <--- ĐÃ SỬA
        """
        match = cls.NORMAL_PATTERN.match(folder_name)
        if match:
            # Rebuild the name with the CORRECT separator for this type
            # 'normal' mods use underscores, so we rebuild with underscores.
            base_bundle_name = f"{match.group(1)}_{match.group(2)}_{match.group(3)}"
            return 'normal', base_bundle_name

        match = cls.BURST_PATTERN.match(folder_name)
        if match:
            # Rebuild the name with the CORRECT separator for this type
            # 'burst' mods use hyphens, so we REBUILD with hyphens.
            base_bundle_name = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            return 'burst', base_bundle_name

        match = cls.EVENT_PATTERN.match(folder_name)
        if match:
            # Event mods seem to use hyphens, this is fine.
            return 'event', match.group(1)

        return 'unknown', folder_name

    @classmethod
    def get_bundle_folder(cls, mod_type: str) -> Path:
        """Get the appropriate original bundle folder based on mod type."""
        folders = {
            'normal': ORIGINAL_BUNDLES_FOLDER,
            'burst': ORIGINAL_LOBBY_BURST_FOLDER,
            'event': ORIGINAL_EVENT_FOLDER,
            'unknown': ORIGINAL_OTHER_FOLDER
        }
        return folders.get(mod_type)


class UnityBundleRepacker:
    """Handles repacking of Unity bundles with modded assets."""

    def __init__(self):
        self.error_log = ERROR_LOG_FILE
        self.processed_count = 0
        self.success_count = 0

    def setup_directories(self) -> bool:
        """Create required directories if they don't exist."""
        required_dirs = [
            (ORIGINAL_BUNDLES_FOLDER, "original bundles (normal mods)"),
            (ORIGINAL_PORTRAITS_FOLDER, "original portraits"),
            (ORIGINAL_LOBBY_BURST_FOLDER, "original lobby/burst bundles"),
            (ORIGINAL_EVENT_FOLDER, "original event bundles"),
            (ORIGINAL_OTHER_FOLDER, "original other bundles")
        ]

        missing_dirs = []
        for dir_path, description in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                missing_dirs.append(f"{dir_path} ({description})")

        if missing_dirs:
            print("Created the following directories:")
            for dir_name in missing_dirs:
                print(f"  - {dir_name}")
            print("\nPlease add the required bundles and rerun the script.")
            return False

        return True

    def get_mod_variations(self) -> List[Dict[str, str]]:
        """Get all mod variations from Extracted Assets folder with their types."""
        if not MODDED_ASSETS_FOLDER.exists():
            return []

        variations = []
        for folder in MODDED_ASSETS_FOLDER.iterdir():
            if folder.is_dir():
                mod_type, base_bundle = ModClassifier.classify_mod(folder.name)
                variations.append({
                    'name': folder.name,
                    'type': mod_type,
                    'base_bundle': base_bundle,
                    'path': folder
                })

        return variations

    def build_modded_assets_map(self, variation_folder: Path) -> Tuple[Dict[str, Path], Set[str]]:
        """Build a map of modded asset filenames and set of base names for quick lookup."""
        assets_map = {}
        base_names = set()

        for file_path in variation_folder.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(variation_folder)
                key = str(rel_path).replace(os.sep, "/")
                assets_map[key] = file_path

                # Remove extension and add to base_names
                if "." in key:
                    stem = key.rsplit('.', 1)[0]
                else:
                    stem = key

                base_names.add(stem)
        return assets_map, base_names

    def find_target_bundles(self, bundle_folder: Path, base_bundle_name: str) -> List[Path]:
        """Find bundles that match the base bundle name.

        Example: For 'c016_00_standing', will find:
        - c016_00_standing.bundle (exact match)
        - Any other bundles in subdirectories that match
        """
        if not base_bundle_name:
            return []

        target_bundles = []

        # Tìm file bundle chính xác
        exact_bundle = bundle_folder / f"{base_bundle_name}.bundle"
        if exact_bundle.exists():
            target_bundles.append(exact_bundle)

        # Tìm trong subdirectories (nếu có cấu trúc thư mục)
        for bundle_path in bundle_folder.rglob("*.bundle"):
            if bundle_path.stem == base_bundle_name and bundle_path not in target_bundles:
                target_bundles.append(bundle_path)

        return target_bundles

    def log_error(self, bundle_name: str, variation_name: str, customError = ""):
        """Log bundle errors to the error file."""
        with open(self.error_log, "a") as f:
            if customError:
                f.write(f"{bundle_name} (variation: {variation_name}) - {customError}\n")
            else:
                f.write(f"{bundle_name} (variation: {variation_name}) needs to be repacked manually\n")

    def replace_texture(self, obj, modded_file_path: Path) -> bool:
        """Replace a Texture2D object with a modded image."""
        try:
            data = obj.read()
            pil_img = Image.open(modded_file_path)

            if pil_img.mode != "RGBA":
                pil_img = pil_img.convert("RGBA")

            data.m_Width, data.m_Height = pil_img.size
            data.m_TextureFormat = 4  # RGBA32 format
            data.image = pil_img
            data.save()

            return True
        except Exception as e:
            print(f"    Error replacing texture '{modded_file_path.name}': {e}")
            return False

    def replace_text_asset(self, obj, modded_file_path: Path) -> bool:
        """
        Replace a TextAsset object with modded text/binary content.
        """
        try:
            print(f"replace_text_asset (V19 - Final) for: {modded_file_path.name}")
            with open(modded_file_path, "rb") as f:
                mod_bytes = f.read()

            data = obj.read()
            try:
                data.m_Script = mod_bytes.decode("utf-8", "surrogateescape")
            except Exception as e_decode:
                print(f"    -> WARNING: surrogateescape failed: {e_decode}. Falling back to latin-1.")
                data.m_Script = mod_bytes.decode("latin-1")
            data.save()
            return True

        except Exception as e:
            print(f"    Error replacing text asset '{modded_file_path.name}': {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_bundle_object(self, obj, assets_map: Dict[str, Path],
                              base_names: Set[str]) -> Tuple[bool, str]:
        """
        Process a single object. (V7 - Real version)
        Returns (modified, filename).
        """
        try:
            data = obj.read()
            file_name = data.m_Name
            file_name_with_ext = None

            # 1. 检查资产名 (m_Name) 是否在我们的 mod 文件列表里
            if file_name in assets_map:
                file_name_with_ext = file_name

            # 2. 如果(1)失败了, 尝试去掉扩展名再找
            elif file_name in base_names:
                possible_exts = ['.png', '.skel', '.atlas', '.json', '.txt', '.bytes', '.wav', '.ogg']
                for ext in possible_exts:
                    potential_key = file_name + ext
                    if potential_key in assets_map:
                        file_name_with_ext = potential_key
                        break

            # 3. 如果(1)和(2)都失败了，尝试反向操作
            else:
                if "." in file_name:
                    stem = file_name.rsplit('.', 1)[0]
                    if stem in base_names:
                        # (这个逻辑和 2 重复了, 但为了保险)
                        possible_exts = ['.png', '.skel', '.atlas', '.json', '.txt', '.bytes', '.wav', '.ogg']
                        for ext in possible_exts:
                            potential_key = stem + ext
                            if potential_key in assets_map:
                                file_name_with_ext = potential_key
                                break

            # 4. 如果还是没找到, 放弃
            if file_name_with_ext is None or file_name_with_ext not in assets_map:
                return False, None
            # ---  查找结束 ️ ---

            modded_file_path = assets_map[file_name_with_ext]

            # Handle different asset types
            if obj.type.name == "Texture2D":
                success = self.replace_texture(obj, modded_file_path)
            elif obj.type.name == "TextAsset":
                # 关键函数，增强写入能力
                success = self.replace_text_asset(obj, modded_file_path)
            elif obj.type.name == "AudioClip":
                success = self.replace_audio_asset(obj, modded_file_path)
            else:
                success = False  # Did not handle this type

            return success, file_name_with_ext if success else None

        except Exception:
            return False, None

    def save_repacked_bundle(self, env, bundle_path: Path, variation_name: str,
                            bundle_source_folder: Path) -> bool:
        """Save the modified bundle to the repacked folder."""
        try:
            # Determine output path
            relative_path = bundle_path.relative_to(bundle_source_folder)
            output_path = REPACKED_FOLDER / variation_name / variation_name
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write bundle data
            bundle_data = env.file.save(packer="lz4")

            with open(output_path, "wb") as f:
                f.write(bundle_data)

                # Add padding if configured
                if ADD_PADDING:
                    current_size = len(bundle_data)
                    padding_needed = (0x10 - (current_size % 0x10)) % 0x10
                    if padding_needed:
                        f.write(b'\x00' * padding_needed)

            return True

        except Exception as e:
            print(f"    ✗ Error saving bundle: {e}")
            return False

    def process_bundle(self, bundle_path: Path, variation_name: str,
                      assets_map: Dict[str, Path], base_names: Set[str],
                      bundle_source_folder: Path) -> Tuple[bool, int]:
        """Process a single bundle file. Returns (success, modified_count)."""
        bundle_name = bundle_path.name

        try:
            print("process_bundle running")
            print(f"load bundle at: {bundle_path}")
            env = UnityPy.load(str(bundle_path))

            edited = False
            modified_files = []

            # Process each object in the bundle
            for obj in env.objects:

                was_modified, filename = self.process_bundle_object(obj, assets_map, base_names)
                if was_modified:
                    edited = True
                    if filename:
                        modified_files.append(filename)

            # Save if modifications were made
            if edited:
                if self.save_repacked_bundle(env, bundle_path, variation_name, bundle_source_folder):
                    return True, len(modified_files)
                else:
                    self.log_error(bundle_path.stem, variation_name, "Cannot save repacked mod, there may be a file with the same name in the Repacked folder")
                    return False, 0

            return False, 0

        except Exception as e:
            print(f"    ✗ Error loading bundle {bundle_name}: {e}")
            self.log_error(bundle_path.stem, variation_name)
            return False, 0

    def process_variation(self, variation: Dict[str, str]):
        """Process all bundles for a single mod variation."""
        variation_name = variation['name']
        variation_type = variation['type']
        variation_path = variation['path']
        base_bundle_name = variation['base_bundle']

        print(f"\n{'='*60}")
        print(f"Processing variation: {variation_name}")
        print(f"Type: {variation_type}")
        if base_bundle_name:
            print(f"Target bundle: {base_bundle_name}.bundle")
        print(f"{'='*60}")


        # Get the appropriate bundle folder
        bundle_folder = ModClassifier.get_bundle_folder(variation_type)
        if not bundle_folder or not bundle_folder.exists():
            print(f"  ⚠ Bundle folder not found for type '{variation_type}', skipping...")
            return

        # Build modded assets map
        assets_map, base_names = self.build_modded_assets_map(variation_path)
        if not assets_map:
            print(f"  ⚠ No modded assets found in {variation_name}")
            return

        print(f"  Found {len(assets_map)} modded asset(s)")

        # Find target bundles based on base bundle name
        if base_bundle_name:
            bundle_files = self.find_target_bundles(bundle_folder, base_bundle_name)
        else:
            # Fallback: process all bundles if we can't determine target
            print(f"  ⚠ Cannot determine target bundle, processing all bundles...")
            bundle_files = [f for f in bundle_folder.rglob("*.bundle") if f.is_file()]

        if not bundle_files:
            print(f"  ⚠ No matching bundle files found")
            print(f"     Looking for: {base_bundle_name}.bundle in {bundle_folder}")
            return

        print(f"  Processing {len(bundle_files)} target bundle(s)...")

        # Process bundles with threading
        variation_success = 0
        variation_processed = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(
                    self.process_bundle,
                    bundle_path,
                    variation_name,
                    assets_map,
                    base_names,
                    bundle_folder
                ): bundle_path
                for bundle_path in bundle_files
            }

            for future in as_completed(futures):
                bundle_path = futures[future]
                try:
                    success, modified_count = future.result()
                    print(f"success = {success}")
                    variation_processed += 1

                    if success:
                        variation_success += 1
                        print(f"  ✓ {bundle_path.name} - Modified {modified_count} asset(s)")
                    else:
                        if modified_count == 0:
                            print(f"  - {bundle_path.name} - No matching assets")

                except Exception as e:
                    print(f"  ✗ Error processing {bundle_path.name}: {e}")

        self.processed_count += variation_processed
        self.success_count += variation_success

        print(f"\n  Variation summary: {variation_success}/{variation_processed} bundles repacked")

    def run(self):
        """Main execution method."""
        try:
            print("Unity Bundle Repacker - Starting...")
            print("="*60)

            # Setup directories
            if not self.setup_directories():
                return

            # Get mod variations
            variations = self.get_mod_variations()
            if not variations:
                print("\n⚠ No mod variations found in 'Extracted Assets' folder.")
                print("Please make sure you have extracted your mods first.")
                return

            print(f"\nFound {len(variations)} mod variation(s):")
            for var in variations:
                bundle_info = f" -> {var['base_bundle']}.bundle" if var['base_bundle'] else ""
                print(f"  - {var['name']} (type: {var['type']}){bundle_info}")

            # Process each variation
            for variation in variations:
                self.process_variation(variation)

            # Summary
            print(f"\n{'='*60}")
            print(f"Processing complete!")
            print(f"Total bundles processed: {self.processed_count}")
            print(f"Successfully repacked: {self.success_count}")

            if self.error_log.exists():
                print(f"\n⚠ Some bundles had errors. Check {self.error_log} for details.")

            print(f"{'='*60}")

        except Exception as e:
            print(f"\n✗ An error occurred: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")

def main():
    repacker = UnityBundleRepacker()
    repacker.run()

# 主要是有的mod作者的skel和atlas设置很难写入official bundle中并被存储，想了贼久才搞定

if __name__ == "__main__":
    main()