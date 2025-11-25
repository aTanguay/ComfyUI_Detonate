#!/usr/bin/env python3
"""
Diagnostic script to verify Load EXR and Cryptomatte nodes are loading correctly.
Run this from the ComfyUI_Detonate directory.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("ComfyUI_Detonate Node Loading Diagnostic")
print("=" * 60)
print()

# Test 1: Load path_utils
print("Test 1: Loading path_utils...")
try:
    from utils.path_utils import get_exr_files, resolve_input_path, get_comfyui_input_dir
    print("✓ path_utils loaded successfully")
except Exception as e:
    print(f"✗ Failed to load path_utils: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 2: Load Load EXR node
print("Test 2: Loading Load EXR node...")
try:
    from nodes.io.load_exr import DetonateLoadEXR
    print("✓ DetonateLoadEXR loaded successfully")

    # Check INPUT_TYPES
    input_types = DetonateLoadEXR.INPUT_TYPES()
    print(f"✓ INPUT_TYPES method works")

    # Check if exr_file is a COMBO (list)
    exr_file_input = input_types["required"]["exr_file"]
    if isinstance(exr_file_input[0], list):
        print(f"✓ exr_file is a COMBO dropdown with {len(exr_file_input[0])} options")
        print(f"  Options: {exr_file_input[0]}")
    else:
        print(f"✗ exr_file is NOT a COMBO! Type: {type(exr_file_input[0])}")
        print(f"  Value: {exr_file_input}")

except Exception as e:
    print(f"✗ Failed to load Load EXR node: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 3: Load Cryptomatte Extract node
print("Test 3: Loading Cryptomatte Extract node...")
try:
    from nodes.cryptomatte.cryptomatte_extract import DetonateCryptomatteExtract
    print("✓ DetonateCryptomatteExtract loaded successfully")

    # Check INPUT_TYPES
    input_types = DetonateCryptomatteExtract.INPUT_TYPES()
    print(f"✓ INPUT_TYPES method works")

    # Check if exr_file is a COMBO (list)
    exr_file_input = input_types["required"]["exr_file"]
    if isinstance(exr_file_input[0], list):
        print(f"✓ exr_file is a COMBO dropdown with {len(exr_file_input[0])} options")
        print(f"  Options: {exr_file_input[0]}")
    else:
        print(f"✗ exr_file is NOT a COMBO! Type: {type(exr_file_input[0])}")
        print(f"  Value: {exr_file_input}")

except Exception as e:
    print(f"✗ Failed to load Cryptomatte Extract node: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 4: Check __init__.py mappings
print("Test 4: Checking __init__.py node mappings...")
try:
    import __init__ as detonate_init

    if "DetonateLoadEXR" in detonate_init.NODE_CLASS_MAPPINGS:
        print("✓ DetonateLoadEXR registered in NODE_CLASS_MAPPINGS")
        node_class = detonate_init.NODE_CLASS_MAPPINGS["DetonateLoadEXR"]
        input_types = node_class.INPUT_TYPES()
        exr_file_input = input_types["required"]["exr_file"]
        if isinstance(exr_file_input[0], list):
            print(f"✓ Registered node has COMBO dropdown")
        else:
            print(f"✗ Registered node does NOT have COMBO dropdown")
    else:
        print("✗ DetonateLoadEXR NOT registered in NODE_CLASS_MAPPINGS")

    if "DetonateCryptomatteExtract" in detonate_init.NODE_CLASS_MAPPINGS:
        print("✓ DetonateCryptomatteExtract registered in NODE_CLASS_MAPPINGS")
        node_class = detonate_init.NODE_CLASS_MAPPINGS["DetonateCryptomatteExtract"]
        input_types = node_class.INPUT_TYPES()
        exr_file_input = input_types["required"]["exr_file"]
        if isinstance(exr_file_input[0], list):
            print(f"✓ Registered node has COMBO dropdown")
        else:
            print(f"✗ Registered node does NOT have COMBO dropdown")
    else:
        print("✗ DetonateCryptomatteExtract NOT registered in NODE_CLASS_MAPPINGS")

except Exception as e:
    print(f"✗ Failed to check __init__.py: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("Diagnostic Complete")
print("=" * 60)
print()
print("If you see ✓ for all tests, the nodes should work correctly in ComfyUI.")
print("If you see ✗, there's an issue that needs fixing.")
print()
print("Next steps:")
print("1. Delete __pycache__ folders: find . -type d -name __pycache__ -exec rm -rf {} +")
print("2. Restart ComfyUI completely")
print("3. Check ComfyUI console for import errors")
print("4. Try creating a NEW workflow (don't load old saved workflow)")
