"""
LoadEXR node for ComfyUI_Detonate.

Load multi-channel/multi-layer EXR files from CG renders.
Supports reading specific AOV passes (beauty, diffuse, specular, etc.)

Essential for CG compositing workflows with render passes.

Reference: OpenImageIO Documentation
https://openimageio.readthedocs.io/en/latest/pythonbindings.html
"""

import torch
import numpy as np
import os

# Import utilities using relative import (works when loaded as ComfyUI package)
try:
    from ...utils.path_utils import get_exr_files, resolve_input_path
except ImportError:
    # Fallback for direct execution or testing
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from utils.path_utils import get_exr_files, resolve_input_path

try:
    import OpenImageIO as oiio
    OIIO_AVAILABLE = True
except ImportError:
    OIIO_AVAILABLE = False
    print("Warning: OpenImageIO not available. Install with: pip install OpenImageIO")


class DetonateLoadEXR:
    """
    Load multi-channel EXR files with AOV pass selection.

    Reads multi-layer EXR files from CG renders and allows selection
    of specific passes (Beauty, Diffuse, Specular, Reflection, etc.)

    Common uses:
    - Load CG render passes
    - Access specific AOVs from multi-layer EXR
    - Work with float HDR renders
    - CG compositing workflows

    Requires: OpenImageIO (industry-standard library)
    """

    CATEGORY = "detonate/io"

    @classmethod
    def INPUT_TYPES(cls):
        exr_files = get_exr_files(__file__)

        return {
            "required": {
                "exr_file": (exr_files, {
                    "default": exr_files[0] if exr_files else "",
                    "tooltip": "Select EXR file from ComfyUI input directory"
                }),
                "layer": ("STRING", {
                    "default": "RGBA",
                    "multiline": False,
                    "tooltip": "Layer name (RGBA, RGB, diffuse, specular, etc.)"
                }),
            },
            "optional": {
                "list_layers": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print available layers to console"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_exr"

    def load_exr(
        self,
        exr_file: str,
        layer: str = "RGBA",
        list_layers: bool = False
    ) -> tuple:
        """
        Load EXR file with specific layer/pass.

        Args:
            exr_file: Relative path to EXR file (from ComfyUI input directory)
            layer: Layer name to load (e.g., "RGBA", "diffuse", "specular")
                   For multi-layer EXRs, use names like "beauty.RGBA" or "diffuse.RGB"
            list_layers: If true, print available layers to console

        Returns:
            Tuple containing loaded image [B,H,W,C]

        Layer naming conventions:
        - "RGBA" or "RGB" - Default beauty pass
        - "diffuse.RGBA" - Diffuse pass RGBA
        - "specular.RGB" - Specular pass RGB
        - "Z" - Depth pass
        - Custom AOV names from your renderer

        Note: Values are NOT clamped - supports full HDR float range
        """
        if not OIIO_AVAILABLE:
            raise RuntimeError("OpenImageIO is required for EXR loading. Install with: pip install OpenImageIO")

        # Resolve full path from relative path
        exr_path = resolve_input_path(__file__, exr_file)

        # Open EXR file
        inp = oiio.ImageInput.open(exr_path)
        if not inp:
            raise RuntimeError(f"Failed to open EXR file: {exr_path}")

        try:
            spec = inp.spec()
            width = spec.width
            height = spec.height
            channels = spec.channelnames

            # List available layers if requested
            if list_layers:
                print(f"\n{'='*60}")
                print(f"EXR File: {os.path.basename(exr_path)}")
                print(f"Resolution: {width}x{height}")
                print(f"Available channels/layers:")
                for ch in channels:
                    print(f"  - {ch}")
                print(f"{'='*60}\n")

            # Determine which channels to read
            channels_to_read = self._get_channels_for_layer(channels, layer)

            if not channels_to_read:
                # Fallback to RGBA if layer not found
                print(f"Warning: Layer '{layer}' not found. Available channels: {channels}")
                print(f"Falling back to RGBA or RGB...")
                if "R" in channels and "G" in channels and "B" in channels:
                    if "A" in channels:
                        channels_to_read = ["R", "G", "B", "A"]
                    else:
                        channels_to_read = ["R", "G", "B"]
                else:
                    raise ValueError(f"Cannot find suitable channels. Available: {channels}")

            # Read pixels for specified channels
            # OpenImageIO returns data in scanline order (row-major)
            num_channels = len(channels_to_read)

            # Create channel indices for reading
            channel_indices = [channels.index(ch) for ch in channels_to_read]

            # Read image data
            pixels = inp.read_image(format="float")  # Returns numpy array [H, W, C]

            if pixels is None:
                raise RuntimeError(f"Failed to read image data from {exr_path}")

            # Extract only the channels we want
            selected_pixels = pixels[:, :, channel_indices]

            # Ensure RGBA (add alpha if RGB only)
            if selected_pixels.shape[2] == 3:
                # Add alpha channel (opaque)
                alpha = np.ones((height, width, 1), dtype=np.float32)
                selected_pixels = np.concatenate([selected_pixels, alpha], axis=2)

            # Convert to torch tensor [H, W, C] -> [1, H, W, C]
            # Note: Keep as float32 for HDR support
            tensor = torch.from_numpy(selected_pixels.astype(np.float32))
            tensor = tensor.unsqueeze(0)  # Add batch dimension

            return (tensor,)

        finally:
            inp.close()

    def _get_channels_for_layer(self, available_channels: list, layer_name: str) -> list:
        """
        Determine which channels to read based on layer name.

        Args:
            available_channels: List of all available channel names
            layer_name: Requested layer (e.g., "RGBA", "diffuse.RGB", "specular")

        Returns:
            List of channel names to read

        Handles both:
        - Simple names: "RGBA", "RGB", "R", "G", "B", "A"
        - Layer.channel names: "diffuse.R", "specular.G", etc.
        - Layer names: "diffuse" (expands to diffuse.R, diffuse.G, diffuse.B, diffuse.A)
        """
        # Normalize layer name
        layer_name = layer_name.strip()

        # Case 1: Simple channel request (RGBA, RGB)
        if layer_name == "RGBA":
            if all(ch in available_channels for ch in ["R", "G", "B", "A"]):
                return ["R", "G", "B", "A"]
            elif all(ch in available_channels for ch in ["R", "G", "B"]):
                return ["R", "G", "B"]

        if layer_name == "RGB":
            if all(ch in available_channels for ch in ["R", "G", "B"]):
                return ["R", "G", "B"]

        # Case 2: Single channel request
        if layer_name in available_channels:
            return [layer_name]

        # Case 3: Layer prefix (e.g., "diffuse", "specular")
        # Check if this is a layer prefix
        # OpenEXR convention: layer.channel (e.g., "diffuse.R", "specular.G")
        possible_channels = []

        # Try RGBA
        for suffix in ["R", "G", "B", "A"]:
            full_name = f"{layer_name}.{suffix}"
            if full_name in available_channels:
                possible_channels.append(full_name)

        if possible_channels:
            return possible_channels

        # Try RGB only
        possible_channels = []
        for suffix in ["R", "G", "B"]:
            full_name = f"{layer_name}.{suffix}"
            if full_name in available_channels:
                possible_channels.append(full_name)

        if possible_channels:
            return possible_channels

        # Case 4: Check if layer_name matches any channel exactly
        matching = [ch for ch in available_channels if layer_name in ch]
        if matching:
            return matching[:4]  # Return up to 4 channels

        return []
