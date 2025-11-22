"""
HueSatVal node for ComfyUI_Detonate.

Direct HSV color space manipulation.
Essential for precise color adjustments and creative color grading.

Reference: Photoshop Hue/Saturation, DaVinci Resolve HSL
"""

import torch
from ...utils import validate_image_tensor


class DetonateHueSatVal:
    """
    Direct HSV (Hue/Saturation/Value) manipulation.

    Provides precise control over color properties in HSV space.
    Complements ColorCorrect (RGB-based) and Grade (lift/gamma/gain)
    by offering direct access to perceptual color attributes.

    Common uses:
    - Precise hue shifts
    - Saturation boosting/reduction
    - Brightness adjustment
    - Selective color correction
    - Creative color grading

    Photoshop/DaVinci equivalent: Hue/Saturation / HSL
    """

    CATEGORY = "detonate/color"

    # Detonate improvement: Selective hue ranges!
    HUE_RANGES = ["all", "reds", "yellows", "greens", "cyans", "blues", "magentas"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Master controls
                "hue": ("FLOAT", {
                    "default": 0.0,
                    "min": -180.0,
                    "max": 180.0,
                    "step": 1.0,
                    "display": "slider",
                }),
                "saturation": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "value": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Selective color range (Detonate improvement!)
                "hue_range": (cls.HUE_RANGES, {
                    "default": "all",
                }),
                "range_softness": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Preserve luminance (Detonate improvement!)
                "preserve_luminance": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "adjust_hsv"

    def adjust_hsv(
        self,
        image: torch.Tensor,
        hue: float = 0.0,
        saturation: float = 0.0,
        value: float = 0.0,
        hue_range: str = "all",
        range_softness: float = 0.3,
        preserve_luminance: bool = False
    ) -> tuple:
        """
        Adjust image in HSV color space.

        Detonate improvements:
        1. Selective hue range targeting (reds, yellows, etc.)
        2. Preserve luminance mode for color adjustments
        3. Soft hue range selection with feathering

        Args:
            image: Input tensor [B,H,W,C]
            hue: Hue shift in degrees (-180 to +180)
            saturation: Saturation adjustment (-1 to +1)
                        -1 = fully desaturate, 0 = no change, +1 = double saturation
            value: Value/brightness adjustment (-1 to +1)
                   -1 = black, 0 = no change, +1 = double brightness
            hue_range: Which hue range to affect
            range_softness: Feathering for selective hue ranges
            preserve_luminance: Maintain original luminance after adjustment

        Returns:
            Tuple containing HSV-adjusted image [B,H,W,C]
        """
        validate_image_tensor(image)

        if hue == 0.0 and saturation == 0.0 and value == 0.0:
            return (image,)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Work on RGB only, preserve alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Store original luminance if needed
        if preserve_luminance:
            # Rec. 709 luma coefficients
            orig_luma = rgb[:, :, :, 0:1] * 0.2126 + \
                       rgb[:, :, :, 1:2] * 0.7152 + \
                       rgb[:, :, :, 2:3] * 0.0722

        # Convert RGB to HSV
        hsv = self._rgb_to_hsv(rgb)

        # Create selection mask if using selective hue range
        if hue_range != "all":
            mask = self._create_hue_range_mask(
                hsv[:, :, :, 0:1], hue_range, range_softness
            )
        else:
            mask = torch.ones(B, H, W, 1, dtype=rgb.dtype, device=rgb.device)

        # Apply adjustments
        if hue != 0.0:
            # Hue shift (rotation)
            hue_shift_normalized = hue / 360.0
            hsv[:, :, :, 0:1] = (hsv[:, :, :, 0:1] + hue_shift_normalized * mask) % 1.0

        if saturation != 0.0:
            # Saturation adjustment (additive in -1 to +1 range)
            sat_adj = 1.0 + saturation
            hsv[:, :, :, 1:2] = hsv[:, :, :, 1:2] * (1.0 + mask * (sat_adj - 1.0))
            hsv[:, :, :, 1:2] = torch.clamp(hsv[:, :, :, 1:2], 0.0, 1.0)

        if value != 0.0:
            # Value adjustment (additive in -1 to +1 range)
            val_adj = 1.0 + value
            hsv[:, :, :, 2:3] = hsv[:, :, :, 2:3] * (1.0 + mask * (val_adj - 1.0))
            hsv[:, :, :, 2:3] = torch.clamp(hsv[:, :, :, 2:3], 0.0, 1.0)

        # Convert HSV back to RGB
        result_rgb = self._hsv_to_rgb(hsv)

        # Restore original luminance if requested (Detonate improvement!)
        if preserve_luminance and (saturation != 0.0 or hue != 0.0):
            new_luma = result_rgb[:, :, :, 0:1] * 0.2126 + \
                      result_rgb[:, :, :, 1:2] * 0.7152 + \
                      result_rgb[:, :, :, 2:3] * 0.0722

            # Scale RGB to match original luminance
            luma_ratio = orig_luma / (new_luma + 1e-7)
            result_rgb = result_rgb * luma_ratio
            result_rgb = torch.clamp(result_rgb, 0.0, 1.0)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return (result,)

    def _rgb_to_hsv(self, rgb: torch.Tensor) -> torch.Tensor:
        """
        Convert RGB to HSV color space.

        Args:
            rgb: RGB tensor [B,H,W,3]

        Returns:
            HSV tensor [B,H,W,3] (H, S, V in 0-1 range)
        """
        max_rgb, max_idx = torch.max(rgb, dim=3, keepdim=True)
        min_rgb = torch.min(rgb, dim=3, keepdim=True)[0]
        delta = max_rgb - min_rgb

        # Hue calculation
        hue = torch.zeros_like(max_rgb)

        # Red is max
        mask_r = (max_idx == 0) & (delta > 1e-7)
        hue[mask_r] = ((rgb[:, :, :, 1:2][mask_r] - rgb[:, :, :, 2:3][mask_r]) / delta[mask_r]) % 6.0

        # Green is max
        mask_g = (max_idx == 1) & (delta > 1e-7)
        hue[mask_g] = ((rgb[:, :, :, 2:3][mask_g] - rgb[:, :, :, 0:1][mask_g]) / delta[mask_g]) + 2.0

        # Blue is max
        mask_b = (max_idx == 2) & (delta > 1e-7)
        hue[mask_b] = ((rgb[:, :, :, 0:1][mask_b] - rgb[:, :, :, 1:2][mask_b]) / delta[mask_b]) + 4.0

        hue = hue / 6.0  # Normalize to 0-1

        # Saturation
        saturation = torch.where(max_rgb > 1e-7, delta / max_rgb, torch.zeros_like(max_rgb))

        # Value
        value = max_rgb

        hsv = torch.cat([hue, saturation, value], dim=3)
        return hsv

    def _hsv_to_rgb(self, hsv: torch.Tensor) -> torch.Tensor:
        """
        Convert HSV to RGB color space.

        Args:
            hsv: HSV tensor [B,H,W,3]

        Returns:
            RGB tensor [B,H,W,3]
        """
        h = hsv[:, :, :, 0:1] * 6.0  # Scale to 0-6
        s = hsv[:, :, :, 1:2]
        v = hsv[:, :, :, 2:3]

        i = torch.floor(h).long()
        f = h - i.float()

        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))

        # Initialize result
        rgb = torch.zeros_like(hsv)

        # i % 6 determines which formula to use
        i = i % 6

        # Case 0: (v, t, p)
        mask_0 = (i == 0)
        rgb[mask_0.squeeze(3), 0] = v[mask_0].squeeze()
        rgb[mask_0.squeeze(3), 1] = t[mask_0].squeeze()
        rgb[mask_0.squeeze(3), 2] = p[mask_0].squeeze()

        # Case 1: (q, v, p)
        mask_1 = (i == 1)
        rgb[mask_1.squeeze(3), 0] = q[mask_1].squeeze()
        rgb[mask_1.squeeze(3), 1] = v[mask_1].squeeze()
        rgb[mask_1.squeeze(3), 2] = p[mask_1].squeeze()

        # Case 2: (p, v, t)
        mask_2 = (i == 2)
        rgb[mask_2.squeeze(3), 0] = p[mask_2].squeeze()
        rgb[mask_2.squeeze(3), 1] = v[mask_2].squeeze()
        rgb[mask_2.squeeze(3), 2] = t[mask_2].squeeze()

        # Case 3: (p, q, v)
        mask_3 = (i == 3)
        rgb[mask_3.squeeze(3), 0] = p[mask_3].squeeze()
        rgb[mask_3.squeeze(3), 1] = q[mask_3].squeeze()
        rgb[mask_3.squeeze(3), 2] = v[mask_3].squeeze()

        # Case 4: (t, p, v)
        mask_4 = (i == 4)
        rgb[mask_4.squeeze(3), 0] = t[mask_4].squeeze()
        rgb[mask_4.squeeze(3), 1] = p[mask_4].squeeze()
        rgb[mask_4.squeeze(3), 2] = v[mask_4].squeeze()

        # Case 5: (v, p, q)
        mask_5 = (i == 5)
        rgb[mask_5.squeeze(3), 0] = v[mask_5].squeeze()
        rgb[mask_5.squeeze(3), 1] = p[mask_5].squeeze()
        rgb[mask_5.squeeze(3), 2] = q[mask_5].squeeze()

        return rgb

    def _create_hue_range_mask(
        self,
        hue: torch.Tensor,
        hue_range: str,
        softness: float
    ) -> torch.Tensor:
        """
        Create mask for selective hue range.

        Detonate improvement: Selective color adjustment!

        Args:
            hue: Hue channel [B,H,W,1] (0-1)
            hue_range: Which hue range to select
            softness: Feathering amount (0-1)

        Returns:
            Mask [B,H,W,1] (0-1)
        """
        # Define hue range centers (in 0-1 space)
        hue_centers = {
            "reds": 0.0,      # 0°
            "yellows": 1/6,   # 60°
            "greens": 2/6,    # 120°
            "cyans": 3/6,     # 180°
            "blues": 4/6,     # 240°
            "magentas": 5/6,  # 300°
        }

        if hue_range not in hue_centers:
            return torch.ones_like(hue)

        center = hue_centers[hue_range]

        # Calculate angular distance to center (handles wraparound)
        dist = torch.abs(hue - center)
        dist = torch.minimum(dist, 1.0 - dist)  # Wrap around

        # Range width (60° = 1/6 of circle)
        range_width = 1.0 / 6.0

        # Apply softness
        inner_width = range_width * (1.0 - softness)
        outer_width = range_width * (1.0 + softness)

        # Create smooth falloff
        mask = 1.0 - torch.clamp((dist - inner_width) / (outer_width - inner_width + 1e-7), 0.0, 1.0)

        return mask
