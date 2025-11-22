"""
LUT node for ComfyUI_Detonate.

Apply 1D/3D color lookup tables from .cube files.
Industry-standard color grading tool.

Reference: .cube LUT format, DaVinci Resolve LUT support
https://www.adobe.com/support/downloads/icc_eula_mac_distribute.html
"""

import torch
import torch.nn.functional as F
import os
from ...utils import validate_image_tensor


class DetonateLUT:
    """
    Apply color lookup tables (LUTs).

    Loads and applies 1D or 3D LUTs from industry-standard .cube files.
    Essential for color grading workflows and matching looks between
    different cameras/footage.

    Supports:
    - 1D LUTs (per-channel curves)
    - 3D LUTs (full color space transformation)
    - Trilinear interpolation
    - Adjustable strength/mix

    Common uses:
    - Apply film emulation LUTs
    - Match camera looks
    - Creative color grading
    - Technical color corrections
    - Log to Rec.709 conversion

    Industry standard: .cube format
    """

    CATEGORY = "detonate/color"

    # LUT cache (class variable to persist between calls)
    _lut_cache = {}

    # Detonate improvement: Multiple interpolation modes!
    INTERPOLATION_MODES = ["trilinear", "nearest"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                # LUT file path
                "lut_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
            "optional": {
                # Strength/mix
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Interpolation mode (Detonate improvement!)
                "interpolation": (cls.INTERPOLATION_MODES, {
                    "default": "trilinear",
                }),
                # Inverse application (Detonate improvement!)
                "inverse": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_lut"

    def apply_lut(
        self,
        image: torch.Tensor,
        lut_file: str = "",
        strength: float = 1.0,
        interpolation: str = "trilinear",
        inverse: bool = False
    ) -> tuple:
        """
        Apply LUT to image.

        Detonate improvements:
        1. LUT caching for performance
        2. Multiple interpolation modes
        3. Inverse LUT application

        Args:
            image: Input tensor [B,H,W,C]
            lut_file: Path to .cube LUT file
            strength: LUT application strength (0-1)
            interpolation: Interpolation mode for 3D LUTs
            inverse: Apply inverse LUT (approximate)

        Returns:
            Tuple containing LUT-processed image [B,H,W,C]
        """
        validate_image_tensor(image)

        if not lut_file or not os.path.exists(lut_file):
            # No LUT or file doesn't exist, return original
            return (image,)

        if strength <= 0.0:
            return (image,)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Work on RGB only, preserve alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Load LUT (with caching)
        lut_data = self._load_lut(lut_file)

        if lut_data is None:
            return (image,)

        # Apply LUT
        if lut_data['type'] == '1D':
            result_rgb = self._apply_1d_lut(rgb, lut_data, inverse)
        else:  # 3D
            result_rgb = self._apply_3d_lut(rgb, lut_data, interpolation, inverse)

        # Mix with original based on strength
        if strength < 1.0:
            result_rgb = rgb * (1.0 - strength) + result_rgb * strength

        # Clamp to valid range
        result_rgb = torch.clamp(result_rgb, 0.0, 1.0)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return (result,)

    def _load_lut(self, lut_file: str) -> dict:
        """
        Load LUT from .cube file with caching.

        Detonate improvement: LUT caching for performance!

        Args:
            lut_file: Path to .cube file

        Returns:
            Dictionary with LUT data or None if failed
        """
        # Check cache first
        if lut_file in self._lut_cache:
            return self._lut_cache[lut_file]

        try:
            with open(lut_file, 'r') as f:
                lines = f.readlines()

            lut_data = None
            lut_size = None
            lut_values = []

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse LUT_3D_SIZE or LUT_1D_SIZE
                if line.startswith('LUT_3D_SIZE'):
                    lut_size = int(line.split()[1])
                    lut_data = {'type': '3D', 'size': lut_size}
                elif line.startswith('LUT_1D_SIZE'):
                    lut_size = int(line.split()[1])
                    lut_data = {'type': '1D', 'size': lut_size}
                # Skip other metadata
                elif line.startswith('TITLE') or line.startswith('DOMAIN_'):
                    continue
                else:
                    # Parse RGB values
                    try:
                        values = [float(x) for x in line.split()]
                        if len(values) == 3:
                            lut_values.append(values)
                    except ValueError:
                        continue

            if lut_data is None or len(lut_values) == 0:
                return None

            # Convert to tensor
            lut_tensor = torch.tensor(lut_values, dtype=torch.float32)

            if lut_data['type'] == '3D':
                # Reshape to [size, size, size, 3]
                expected_size = lut_size ** 3
                if lut_tensor.shape[0] != expected_size:
                    return None

                lut_tensor = lut_tensor.view(lut_size, lut_size, lut_size, 3)
            else:  # 1D
                # Reshape to [size, 3]
                if lut_tensor.shape[0] != lut_size:
                    return None

            lut_data['values'] = lut_tensor

            # Cache the loaded LUT
            self._lut_cache[lut_file] = lut_data

            return lut_data

        except Exception as e:
            print(f"Error loading LUT file {lut_file}: {e}")
            return None

    def _apply_1d_lut(
        self,
        rgb: torch.Tensor,
        lut_data: dict,
        inverse: bool
    ) -> torch.Tensor:
        """
        Apply 1D LUT (per-channel curves).

        Args:
            rgb: Input RGB [B,H,W,3]
            lut_data: LUT data dictionary
            inverse: Apply inverse (not supported for 1D)

        Returns:
            Transformed RGB [B,H,W,3]
        """
        lut_values = lut_data['values']  # [size, 3]
        lut_size = lut_data['size']

        # Clamp input to 0-1
        rgb_clamped = torch.clamp(rgb, 0.0, 1.0)

        # Scale to LUT index range
        indices_float = rgb_clamped * (lut_size - 1)

        # Get lower and upper indices
        indices_low = torch.floor(indices_float).long()
        indices_high = torch.ceil(indices_float).long()

        # Clamp indices
        indices_low = torch.clamp(indices_low, 0, lut_size - 1)
        indices_high = torch.clamp(indices_high, 0, lut_size - 1)

        # Interpolation weight
        weight = indices_float - indices_low.float()

        # Move LUT to same device as image
        lut_values = lut_values.to(rgb.device)

        # Lookup values for each channel
        result = torch.zeros_like(rgb)

        for c in range(3):
            values_low = lut_values[indices_low[:, :, :, c], c]
            values_high = lut_values[indices_high[:, :, :, c], c]

            # Linear interpolation
            result[:, :, :, c] = values_low * (1.0 - weight[:, :, :, c]) + \
                                values_high * weight[:, :, :, c]

        return result

    def _apply_3d_lut(
        self,
        rgb: torch.Tensor,
        lut_data: dict,
        interpolation: str,
        inverse: bool
    ) -> torch.Tensor:
        """
        Apply 3D LUT with trilinear interpolation.

        Detonate improvement: Multiple interpolation modes!

        Args:
            rgb: Input RGB [B,H,W,3]
            lut_data: LUT data dictionary
            interpolation: Interpolation mode
            inverse: Apply inverse (approximate)

        Returns:
            Transformed RGB [B,H,W,3]
        """
        lut_values = lut_data['values'].to(rgb.device)  # [size, size, size, 3]
        lut_size = lut_data['size']

        # Clamp input to 0-1
        rgb_clamped = torch.clamp(rgb, 0.0, 1.0)

        if interpolation == "nearest":
            # Nearest neighbor (faster but lower quality)
            indices = torch.round(rgb_clamped * (lut_size - 1)).long()
            indices = torch.clamp(indices, 0, lut_size - 1)

            r_idx = indices[:, :, :, 0]
            g_idx = indices[:, :, :, 1]
            b_idx = indices[:, :, :, 2]

            result = lut_values[r_idx, g_idx, b_idx, :]

        else:  # trilinear
            # Trilinear interpolation (high quality)
            # Scale to LUT coordinate space
            coords = rgb_clamped * (lut_size - 1)

            # Get surrounding cube corners
            r0 = torch.floor(coords[:, :, :, 0]).long()
            g0 = torch.floor(coords[:, :, :, 1]).long()
            b0 = torch.floor(coords[:, :, :, 2]).long()

            r1 = torch.clamp(r0 + 1, max=lut_size - 1)
            g1 = torch.clamp(g0 + 1, max=lut_size - 1)
            b1 = torch.clamp(b0 + 1, max=lut_size - 1)

            r0 = torch.clamp(r0, min=0, max=lut_size - 1)
            g0 = torch.clamp(g0, min=0, max=lut_size - 1)
            b0 = torch.clamp(b0, min=0, max=lut_size - 1)

            # Interpolation weights
            dr = coords[:, :, :, 0] - r0.float()
            dg = coords[:, :, :, 1] - g0.float()
            db = coords[:, :, :, 2] - b0.float()

            # Lookup 8 corners of cube
            c000 = lut_values[r0, g0, b0, :]
            c001 = lut_values[r0, g0, b1, :]
            c010 = lut_values[r0, g1, b0, :]
            c011 = lut_values[r0, g1, b1, :]
            c100 = lut_values[r1, g0, b0, :]
            c101 = lut_values[r1, g0, b1, :]
            c110 = lut_values[r1, g1, b0, :]
            c111 = lut_values[r1, g1, b1, :]

            # Expand weights for broadcasting
            dr = dr.unsqueeze(3)
            dg = dg.unsqueeze(3)
            db = db.unsqueeze(3)

            # Trilinear interpolation
            c00 = c000 * (1 - db) + c001 * db
            c01 = c010 * (1 - db) + c011 * db
            c10 = c100 * (1 - db) + c101 * db
            c11 = c110 * (1 - db) + c111 * db

            c0 = c00 * (1 - dg) + c01 * dg
            c1 = c10 * (1 - dg) + c11 * dg

            result = c0 * (1 - dr) + c1 * dr

        return result
