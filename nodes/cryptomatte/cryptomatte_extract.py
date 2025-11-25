"""
Cryptomatte Extract node for ComfyUI_Detonate.

Extract object/material ID mattes from Cryptomatte EXR files.
Industry-standard tool for CG compositing workflows.

Based on Psyop's Cryptomatte specification:
https://github.com/Psyop/Cryptomatte

Reference: Nuke Cryptomatte documentation
https://learn.foundry.com/nuke/content/comp_environment/cryptomatte/
"""

import torch
import numpy as np
import os
import sys
import struct
import json
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.path_utils import get_exr_files, resolve_input_path

try:
    import OpenImageIO as oiio
    OIIO_AVAILABLE = True
except ImportError:
    OIIO_AVAILABLE = False

try:
    import mmh3
    MMH3_AVAILABLE = True
except ImportError:
    MMH3_AVAILABLE = False


class DetonateCryptomatteExtract:
    """
    Extract ID mattes from Cryptomatte EXR files.

    Cryptomatte is an industry-standard system for generating ID mattes
    from CG renders. It encodes object/material IDs with support for
    motion blur, transparency, and depth of field.

    Common uses:
    - Extract specific objects from CG renders as mattes
    - Isolate materials for selective color correction
    - Create holdout mattes for compositing
    - Multi-object selection with proper anti-aliasing

    Requires: OpenImageIO, mmh3 (MurmurHash3)

    Usage:
    - Option 1: Select EXR file from dropdown (files in ComfyUI input directory)
    - Option 2: Connect IMAGE output from Load EXR node (uses stored path)
    """

    CATEGORY = "detonate/cryptomatte"

    @classmethod
    def INPUT_TYPES(cls):
        exr_files = get_exr_files(__file__)

        return {
            "required": {
                "exr_file": (exr_files, {
                    "default": exr_files[0] if exr_files else "",
                    "tooltip": "Select Cryptomatte EXR file from ComfyUI input directory"
                }),
                "cryptomatte_layer": (["CryptoObject", "CryptoMaterial", "CryptoAsset"], {
                    "default": "CryptoObject",
                    "tooltip": "Which Cryptomatte layer to extract from"
                }),
                "matte_list": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Comma-separated object/material names to extract (e.g., 'sphere_001, cube_002')"
                }),
            },
            "optional": {
                "list_objects": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print available objects to console"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("matte",)
    FUNCTION = "extract_matte"

    def extract_matte(
        self,
        exr_file: str,
        cryptomatte_layer: str = "CryptoObject",
        matte_list: str = "",
        list_objects: bool = False
    ) -> tuple:
        """
        Extract Cryptomatte ID matte from EXR file.

        Args:
            exr_file: Relative path to Cryptomatte EXR file (from ComfyUI input directory)
            cryptomatte_layer: Which Cryptomatte layer to use (CryptoObject, CryptoMaterial, CryptoAsset)
            matte_list: Comma-separated list of object/material names to extract
                       (e.g., "sphere_001, cube_002, ground_plane")
            list_objects: If true, print available objects to console

        Returns:
            Tuple containing matte image [B,H,W,C] with coverage in RGB, alpha=1

        Cryptomatte Layer Types:
        - CryptoObject - Object names (most common)
        - CryptoMaterial - Material/shader names
        - CryptoAsset - Asset/collection names

        The matte output contains coverage values (0-1) representing how much
        of each pixel belongs to the selected objects, with proper anti-aliasing.
        """
        if not OIIO_AVAILABLE:
            raise RuntimeError("OpenImageIO is required. Install with: pip install OpenImageIO")

        if not MMH3_AVAILABLE:
            raise RuntimeError("mmh3 is required for Cryptomatte. Install with: pip install mmh3")

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

            # Parse manifest from metadata
            manifest = self._parse_manifest(spec, cryptomatte_layer)

            if list_objects and manifest:
                print(f"\n{'='*60}")
                print(f"Cryptomatte Layer: {cryptomatte_layer}")
                print(f"Available objects ({len(manifest)} total):")
                for name in sorted(manifest.keys()):
                    print(f"  - {name}")
                print(f"{'='*60}\n")

            if not manifest:
                raise ValueError(f"No Cryptomatte manifest found for layer '{cryptomatte_layer}'")

            # Find Cryptomatte channels
            crypto_channels = self._find_crypto_channels(spec.channelnames, cryptomatte_layer)

            if not crypto_channels:
                raise ValueError(f"No Cryptomatte channels found for layer '{cryptomatte_layer}'")

            # Parse matte list (comma-separated object names)
            if not matte_list or not matte_list.strip():
                print("Warning: No objects specified in matte_list. Returning empty matte.")
                # Return black matte
                matte = torch.zeros((1, height, width, 4), dtype=torch.float32)
                matte[:, :, :, 3] = 1.0  # Alpha = 1
                return (matte,)

            object_names = [name.strip() for name in matte_list.split(",") if name.strip()]

            # Convert object names to ID floats
            id_floats = set()
            for name in object_names:
                if name in manifest:
                    id_floats.add(manifest[name])
                else:
                    print(f"Warning: Object '{name}' not found in manifest. Skipping.")

            if not id_floats:
                print("Warning: None of the specified objects were found in manifest.")
                # Return black matte
                matte = torch.zeros((1, height, width, 4), dtype=torch.float32)
                matte[:, :, :, 3] = 1.0
                return (matte,)

            # Read all Cryptomatte layers
            # Cryptomatte stores ID/coverage pairs in R,G (ID1, coverage1) and B,A (ID2, coverage2)
            all_pixels = inp.read_image(format="float")  # [H, W, C]

            if all_pixels is None:
                raise RuntimeError(f"Failed to read image data from {exr_path}")

            # Extract coverage for selected IDs
            matte_data = self._extract_coverage(
                all_pixels,
                spec.channelnames,
                crypto_channels,
                id_floats,
                width,
                height
            )

            # Convert to torch tensor [1, H, W, 4]
            # Put coverage in RGB (for visualization), alpha=1
            matte_rgba = np.zeros((height, width, 4), dtype=np.float32)
            matte_rgba[:, :, 0] = matte_data  # R
            matte_rgba[:, :, 1] = matte_data  # G
            matte_rgba[:, :, 2] = matte_data  # B
            matte_rgba[:, :, 3] = 1.0         # A

            tensor = torch.from_numpy(matte_rgba).unsqueeze(0)

            return (tensor,)

        finally:
            inp.close()

    def _parse_manifest(self, spec, layer_name: str):
        """
        Parse Cryptomatte manifest from EXR metadata.

        The manifest is stored as JSON in the metadata with key:
        "cryptomatte/{hash}/manifest"

        Returns:
            Dictionary mapping object names to ID floats
        """
        # Find manifest in metadata
        manifest_key = None
        for attr in spec.extra_attribs:
            if attr.name.startswith(f"cryptomatte/") and attr.name.endswith("/manifest"):
                # Check if this manifest is for our layer
                if layer_name.lower() in attr.name.lower():
                    manifest_key = attr.name
                    break

        if not manifest_key:
            # Try generic search
            for attr in spec.extra_attribs:
                if "/manifest" in attr.name:
                    manifest_key = attr.name
                    break

        if not manifest_key:
            return {}

        # Get manifest data
        manifest_json = None
        for attr in spec.extra_attribs:
            if attr.name == manifest_key:
                manifest_json = attr.value
                break

        if not manifest_json:
            return {}

        # Parse JSON manifest
        try:
            manifest_dict = json.loads(manifest_json)
        except json.JSONDecodeError:
            print(f"Warning: Failed to parse manifest JSON")
            return {}

        # Convert hex IDs to floats
        # Manifest format: {"object_name": "hex_id", ...}
        name_to_float = {}
        unpacker = struct.Struct('=f')
        packer = struct.Struct("=I")

        for name, hex_id in manifest_dict.items():
            try:
                # Convert hex string to int, then to float
                packed = packer.pack(int(hex_id, 16))
                id_float = unpacker.unpack(packed)[0]
                name_to_float[name] = id_float
            except (ValueError, struct.error) as e:
                print(f"Warning: Failed to convert ID for '{name}': {e}")
                continue

        return name_to_float

    def _find_crypto_channels(self, all_channels: list, layer_name: str) -> list:
        """
        Find all Cryptomatte channels for the specified layer.

        Cryptomatte channels are named like:
        - CryptoObject00.R, CryptoObject00.G, CryptoObject00.B, CryptoObject00.A
        - CryptoObject01.R, CryptoObject01.G, CryptoObject01.B, CryptoObject01.A
        - etc.

        Returns:
            List of layer prefixes (e.g., ["CryptoObject00", "CryptoObject01"])
        """
        # Find all matching layer numbers
        pattern = re.compile(rf"^{re.escape(layer_name)}(\d{{2}})\.")
        layer_numbers = set()

        for ch in all_channels:
            match = pattern.match(ch)
            if match:
                layer_numbers.add(match.group(1))

        # Return sorted list of layer names
        return sorted([f"{layer_name}{num}" for num in layer_numbers])

    def _extract_coverage(
        self,
        pixels: np.ndarray,
        channel_names: list,
        crypto_layers: list,
        target_ids: set,
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Extract coverage matte from Cryptomatte layers.

        Cryptomatte encodes ID/coverage pairs:
        - R,G = ID1, coverage1
        - B,A = ID2, coverage2

        Each layer can contain 2 ID samples per pixel.
        Multiple layers handle more samples (for motion blur, transparency, etc.)

        Returns:
            Coverage array [H, W] with values 0-1
        """
        # Initialize coverage accumulator
        coverage = np.zeros((height, width), dtype=np.float32)

        # Create channel index lookup
        ch_idx = {name: idx for idx, name in enumerate(channel_names)}

        # Process each Cryptomatte layer
        for layer_prefix in crypto_layers:
            # Get channel indices for this layer
            r_ch = f"{layer_prefix}.R"
            g_ch = f"{layer_prefix}.G"
            b_ch = f"{layer_prefix}.B"
            a_ch = f"{layer_prefix}.A"

            if not all(ch in ch_idx for ch in [r_ch, g_ch, b_ch, a_ch]):
                print(f"Warning: Incomplete channels for layer {layer_prefix}")
                continue

            # Extract ID and coverage pairs
            id1 = pixels[:, :, ch_idx[r_ch]]
            cov1 = pixels[:, :, ch_idx[g_ch]]
            id2 = pixels[:, :, ch_idx[b_ch]]
            cov2 = pixels[:, :, ch_idx[a_ch]]

            # Check if IDs match our target set
            # (with small tolerance for floating point comparison)
            for target_id in target_ids:
                # Match ID1
                mask1 = np.abs(id1 - target_id) < 1e-6
                coverage += np.where(mask1, cov1, 0.0)

                # Match ID2
                mask2 = np.abs(id2 - target_id) < 1e-6
                coverage += np.where(mask2, cov2, 0.0)

        # Clamp to 0-1 range
        coverage = np.clip(coverage, 0.0, 1.0)

        return coverage
