#!/usr/bin/python3

import argparse
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Pack the Blender addon into a zip file."
    )
    parser.add_argument("version", help="Version of the addon (e.g., 1.0.0).")
    args = parser.parse_args()

    addon_name = "uma-tools"

    # The script is in scripts/, so project root is one level up.
    project_root = Path(__file__).resolve().parent.parent
    zip_filename = project_root / f"{addon_name}-v{args.version}.zip"

    # List of files and directories to include in the zip, relative to project_root
    files_and_dirs_to_include = [
        "__init__.py",
        "config",
        "operators",
        "ui",
    ]

    print(f"Creating archive: {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        for item_name in files_and_dirs_to_include:
            item_path = project_root / item_name
            # This is the root of the path inside the zip file
            archive_root = Path(addon_name)

            if item_path.is_file():
                archive_path = archive_root / item_path.name
                zf.write(item_path, arcname=archive_path)
            elif item_path.is_dir():
                for file_path in item_path.rglob("*"):
                    if file_path.is_file() and "__pycache__" not in file_path.parts:
                        relative_path = file_path.relative_to(project_root)
                        archive_path = archive_root / relative_path
                        zf.write(file_path, arcname=archive_path)

    print(f"Successfully created {zip_filename}")


if __name__ == "__main__":
    main()
