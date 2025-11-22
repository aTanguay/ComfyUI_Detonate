"""
ComfyUI_Detonate - Professional Compositing Nodes for ComfyUI

Brings Nuke and Fusion-style compositing workflows to ComfyUI.
"""

# Version info
__version__ = "0.5.0"
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

try:
    from .nodes.color.colorcorrect import DetonateColorCorrect
    NODE_CLASS_MAPPINGS["DetonateColorCorrect"] = DetonateColorCorrect
    NODE_DISPLAY_NAME_MAPPINGS["DetonateColorCorrect"] = "ColorCorrect (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load ColorCorrect node: {e}")

try:
    from .nodes.color.grade import DetonateGrade
    NODE_CLASS_MAPPINGS["DetonateGrade"] = DetonateGrade
    NODE_DISPLAY_NAME_MAPPINGS["DetonateGrade"] = "Grade (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Grade node: {e}")

try:
    from .nodes.matte.erode_dilate import DetonateErode, DetonateDilate
    NODE_CLASS_MAPPINGS["DetonateErode"] = DetonateErode
    NODE_CLASS_MAPPINGS["DetonateDilate"] = DetonateDilate
    NODE_DISPLAY_NAME_MAPPINGS["DetonateErode"] = "Erode (Detonate)"
    NODE_DISPLAY_NAME_MAPPINGS["DetonateDilate"] = "Dilate (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Erode/Dilate nodes: {e}")

try:
    from .nodes.transform.transform import DetonateTransform
    NODE_CLASS_MAPPINGS["DetonateTransform"] = DetonateTransform
    NODE_DISPLAY_NAME_MAPPINGS["DetonateTransform"] = "Transform (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Transform node: {e}")


# Tier 2 Nodes - Essential Utilities ✓
try:
    from .nodes.color.clamp import DetonateClamp
    NODE_CLASS_MAPPINGS["DetonateClamp"] = DetonateClamp
    NODE_DISPLAY_NAME_MAPPINGS["DetonateClamp"] = "Clamp (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Clamp node: {e}")

try:
    from .nodes.color.invert import DetonateInvert
    NODE_CLASS_MAPPINGS["DetonateInvert"] = DetonateInvert
    NODE_DISPLAY_NAME_MAPPINGS["DetonateInvert"] = "Invert (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Invert node: {e}")

try:
    from .nodes.generator.constant import DetonateConstant
    NODE_CLASS_MAPPINGS["DetonateConstant"] = DetonateConstant
    NODE_DISPLAY_NAME_MAPPINGS["DetonateConstant"] = "Constant (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Constant node: {e}")

try:
    from .nodes.color.saturation import DetonateSaturation
    NODE_CLASS_MAPPINGS["DetonateSaturation"] = DetonateSaturation
    NODE_DISPLAY_NAME_MAPPINGS["DetonateSaturation"] = "Saturation (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Saturation node: {e}")

try:
    from .nodes.matte.mattecontrol import DetonateMatteControl
    NODE_CLASS_MAPPINGS["DetonateMatteControl"] = DetonateMatteControl
    NODE_DISPLAY_NAME_MAPPINGS["DetonateMatteControl"] = "MatteControl (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load MatteControl node: {e}")

try:
    from .nodes.channel.channelcopy import DetonateChannelCopy
    NODE_CLASS_MAPPINGS["DetonateChannelCopy"] = DetonateChannelCopy
    NODE_DISPLAY_NAME_MAPPINGS["DetonateChannelCopy"] = "ChannelCopy (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load ChannelCopy node: {e}")

try:
    from .nodes.filter.edgedetect import DetonateEdgeDetect
    NODE_CLASS_MAPPINGS["DetonateEdgeDetect"] = DetonateEdgeDetect
    NODE_DISPLAY_NAME_MAPPINGS["DetonateEdgeDetect"] = "EdgeDetect (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load EdgeDetect node: {e}")


# IO Nodes - File Loaders ✓
try:
    from .nodes.io.load_exr import DetonateLoadEXR
    NODE_CLASS_MAPPINGS["DetonateLoadEXR"] = DetonateLoadEXR
    NODE_DISPLAY_NAME_MAPPINGS["DetonateLoadEXR"] = "Load EXR (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load LoadEXR node: {e}")


# Cryptomatte Nodes - Object/Material ID Mattes ✓
try:
    from .nodes.cryptomatte.cryptomatte_extract import DetonateCryptomatteExtract
    NODE_CLASS_MAPPINGS["DetonateCryptomatteExtract"] = DetonateCryptomatteExtract
    NODE_DISPLAY_NAME_MAPPINGS["DetonateCryptomatteExtract"] = "Cryptomatte Extract (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Cryptomatte Extract node: {e}")


# Tier 3 Nodes - Effects & Color ✓
try:
    from .nodes.filter.glow import DetonateGlow
    NODE_CLASS_MAPPINGS["DetonateGlow"] = DetonateGlow
    NODE_DISPLAY_NAME_MAPPINGS["DetonateGlow"] = "Glow (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Glow node: {e}")

try:
    from .nodes.filter.sharpen import DetonateSharpen
    NODE_CLASS_MAPPINGS["DetonateSharpen"] = DetonateSharpen
    NODE_DISPLAY_NAME_MAPPINGS["DetonateSharpen"] = "Sharpen (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Sharpen node: {e}")

try:
    from .nodes.filter.defocus import DetonateDefocus
    NODE_CLASS_MAPPINGS["DetonateDefocus"] = DetonateDefocus
    NODE_DISPLAY_NAME_MAPPINGS["DetonateDefocus"] = "Defocus (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Defocus node: {e}")

try:
    from .nodes.filter.zdefocus import DetonateZDefocus
    NODE_CLASS_MAPPINGS["DetonateZDefocus"] = DetonateZDefocus
    NODE_DISPLAY_NAME_MAPPINGS["DetonateZDefocus"] = "ZDefocus (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load ZDefocus node: {e}")

try:
    from .nodes.compositing.zmerge import DetonateZMerge
    NODE_CLASS_MAPPINGS["DetonateZMerge"] = DetonateZMerge
    NODE_DISPLAY_NAME_MAPPINGS["DetonateZMerge"] = "ZMerge (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load ZMerge node: {e}")

try:
    from .nodes.color.colorcurves import DetonateColorCurves
    NODE_CLASS_MAPPINGS["DetonateColorCurves"] = DetonateColorCurves
    NODE_DISPLAY_NAME_MAPPINGS["DetonateColorCurves"] = "ColorCurves (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load ColorCurves node: {e}")

try:
    from .nodes.generator.ramp import DetonateRamp
    NODE_CLASS_MAPPINGS["DetonateRamp"] = DetonateRamp
    NODE_DISPLAY_NAME_MAPPINGS["DetonateRamp"] = "Ramp (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Ramp node: {e}")

try:
    from .nodes.generator.noise import DetonateNoise
    NODE_CLASS_MAPPINGS["DetonateNoise"] = DetonateNoise
    NODE_DISPLAY_NAME_MAPPINGS["DetonateNoise"] = "Noise (Detonate)"
except ImportError as e:
    print(f"Warning: Could not load Noise node: {e}")


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
