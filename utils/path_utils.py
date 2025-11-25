"""
Path utilities for ComfyUI_Detonate.

Helper functions for file path resolution and discovery.
"""

import os
from typing import List


def get_comfyui_input_dir(current_file: str) -> str:
    """
    Get the ComfyUI input directory path.

    Args:
        current_file: __file__ from calling module

    Returns:
        Absolute path to ComfyUI/input/ directory

    Directory structure:
        ComfyUI/
        ├── input/                  <- Returns this
        ├── output/
        ├── models/
        └── custom_nodes/
            └── ComfyUI_Detonate/
                └── nodes/
                    └── (calling module)
    """
    current_dir = os.path.dirname(os.path.abspath(current_file))

    # Navigate up from nodes/category/ -> nodes/ -> ComfyUI_Detonate/ -> custom_nodes/ -> ComfyUI/
    detonate_root = os.path.dirname(os.path.dirname(current_dir))  # Up to ComfyUI_Detonate/
    custom_nodes_dir = os.path.dirname(detonate_root)  # Up to custom_nodes/
    comfyui_root = os.path.dirname(custom_nodes_dir)  # Up to ComfyUI/
    input_dir = os.path.join(comfyui_root, "input")

    return input_dir


def get_exr_files(current_file: str) -> List[str]:
    """
    Discover EXR files in ComfyUI's input directory.

    Args:
        current_file: __file__ from calling module

    Returns:
        List of relative paths to .exr files (sorted alphabetically)
        Returns ["[No EXR files in input folder]"] if no files found
    """
    input_dir = get_comfyui_input_dir(current_file)
    exr_files = []

    if os.path.exists(input_dir):
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.exr'):
                    # Store relative path from input directory for cleaner display
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, input_dir)
                    exr_files.append(relative_path)

    # Sort alphabetically for better UX
    exr_files.sort()

    # Return placeholder if no files found (prevents ComfyUI errors)
    if not exr_files:
        return ["[No EXR files in input folder]"]

    return exr_files


def resolve_input_path(current_file: str, relative_path: str) -> str:
    """
    Resolve relative path from ComfyUI input directory to absolute path.

    Args:
        current_file: __file__ from calling module
        relative_path: Relative path from input directory (e.g., "render.exr" or "shots/shot01/beauty.exr")

    Returns:
        Absolute path to file

    Raises:
        FileNotFoundError: If relative_path is placeholder text or file doesn't exist
    """
    # Check for placeholder
    if relative_path.startswith("[No"):
        raise FileNotFoundError("No files found in ComfyUI input directory. Please add files to the input folder.")

    input_dir = get_comfyui_input_dir(current_file)
    absolute_path = os.path.join(input_dir, relative_path)

    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"File not found: {absolute_path}")

    return absolute_path
