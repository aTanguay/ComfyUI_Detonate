"""
ComfyUI_Detonate - Professional Compositing Nodes for ComfyUI

Brings Nuke and Fusion-style compositing workflows to ComfyUI.
"""

# Version info
__version__ = "0.1.0"
__author__ = "ComfyUI_Detonate Contributors"

# Node mappings - will be populated as nodes are implemented
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


# Import nodes as they are implemented

# Priority 1 Nodes - Implemented ✓
try:
    from .nodes.channel.premultiply import DetonatePremultiply, DetonateUnpremultiply
    NODE_CLASS_MAPPINGS["DetonatePremultiply"] = DetonatePremultiply
    NODE_CLASS_MAPPINGS["DetonateUnpremultiply"] = DetonateUnpremultiply
    NODE_DISPLAY_NAME_MAPPINGS["DetonatePremultiply"] = "Premultiply (Detonate)"
    NODE_DISPLAY_NAME_MAPPINGS["DetonateUnpremultiply"] = "Unpremultiply (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Premult nodes: {e}")

try:
    from .nodes.channel.shuffle import DetonateShuffle
    NODE_CLASS_MAPPINGS["DetonateShuffle"] = DetonateShuffle
    NODE_DISPLAY_NAME_MAPPINGS["DetonateShuffle"] = "Shuffle (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Shuffle node: {e}")

try:
    from .nodes.filter.blur import DetonateBlur
    NODE_CLASS_MAPPINGS["DetonateBlur"] = DetonateBlur
    NODE_DISPLAY_NAME_MAPPINGS["DetonateBlur"] = "Blur (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Blur node: {e}")

try:
    from .nodes.compositing.merge import DetonateMerge
    NODE_CLASS_MAPPINGS["DetonateMerge"] = DetonateMerge
    NODE_DISPLAY_NAME_MAPPINGS["DetonateMerge"] = "Merge (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Merge node: {e}")

# try:
#     from .nodes.transform.transform import DetonateTransform
#     NODE_CLASS_MAPPINGS["DetonateTransform"] = DetonateTransform
#     NODE_DISPLAY_NAME_MAPPINGS["DetonateTransform"] = "Transform (Detonate)"
# except ImportError:
#     pass

# try:
#     from .nodes.color.colorcorrect import DetonateColorCorrect
#     NODE_CLASS_MAPPINGS["DetonateColorCorrect"] = DetonateColorCorrect
#     NODE_DISPLAY_NAME_MAPPINGS["DetonateColorCorrect"] = "ColorCorrect (Detonate)"
# except ImportError:
#     pass

# try:
#     from .nodes.color.grade import DetonateGrade
#     NODE_CLASS_MAPPINGS["DetonateGrade"] = DetonateGrade
#     NODE_DISPLAY_NAME_MAPPINGS["DetonateGrade"] = "Grade (Detonate)"
# except ImportError:
#     pass

# try:
#     from .nodes.matte.erode_dilate import DetonateErode, DetonateDilate
#     NODE_CLASS_MAPPINGS["DetonateErode"] = DetonateErode
#     NODE_CLASS_MAPPINGS["DetonateDilate"] = DetonateDilate
#     NODE_DISPLAY_NAME_MAPPINGS["DetonateErode"] = "Erode (Detonate)"
#     NODE_DISPLAY_NAME_MAPPINGS["DetonateDilate"] = "Dilate (Detonate)"
# except ImportError:
#     pass


# Export for ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]


# Print debug info on load
print("\n" + "="*60)
print("ComfyUI_Detonate - Professional Compositing Nodes")
print(f"Version: {__version__}")
print(f"Loaded {len(NODE_CLASS_MAPPINGS)} nodes")
if NODE_CLASS_MAPPINGS:
    print("\nRegistered nodes:")
    for name in sorted(NODE_CLASS_MAPPINGS.keys()):
        display_name = NODE_DISPLAY_NAME_MAPPINGS.get(name, name)
        print(f"  - {display_name}")
else:
    print("\nNo nodes loaded yet - nodes will be added in development")
    print("This is expected for initial setup.")
print("="*60 + "\n")
