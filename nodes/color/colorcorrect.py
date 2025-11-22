"""
ColorCorrect node for ComfyUI_Detonate.

Quick color adjustments for matching composite layers with saturation,
contrast, gamma, gain, and offset controls.

Reference: Nuke ColorCorrect node, Fusion ColorCorrector
https://learn.foundry.com/nuke/content/reference_guide/color_nodes/colorcorrect.html
"""

import torch
from ...utils import (
    validate_image_tensor,
    ensure_alpha_channel,
    adjust_saturation,
    adjust_contrast,
    apply_gamma,
    apply_gain,
    apply_offset,
)


class DetonateColorCorrect:
    """
    Quick color correction for matching composite layers.

    Provides saturation, contrast, gamma, gain, and offset controls
    for quick color adjustments. Simpler than Grade node but very
    useful for matching layers in composites.

    Key differences from Grade:
    - Grade: Film scan color grading (lift/gamma/gain workflow)
    - ColorCorrect: Layer matching (saturation/contrast controls)

    Operates on straight (unpremultiplied) alpha images.
    Use Unpremult → ColorCorrect → Premult workflow.

    Nuke/Fusion equivalent: ColorCorrect / ColorCorrector
    """

    CATEGORY = "detonate/color"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Saturation
                "saturation": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Hue shift (Detonate improvement!)
                "hue_shift": ("FLOAT", {
                    "default": 0.0,
                    "min": -180.0,
                    "max": 180.0,
                    "step": 1.0,
                    "display": "slider",
                }),
                # Contrast
                "contrast": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Gamma
                "gamma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Gain (Multiply)
                "gain": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Offset (Add)
                "offset": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "color_correct"

    def color_correct(
        self,
        image: torch.Tensor,
        saturation: float = 1.0,
        hue_shift: float = 0.0,
        contrast: float = 1.0,
        gamma: float = 1.0,
        gain: float = 1.0,
        offset: float = 0.0
    ) -> tuple:
        """
        Apply color correction to image.

        Operation order:
        1. Contrast
        2. Saturation
        3. Hue shift (Detonate improvement!)
        4. Gamma
        5. Gain (multiply)
        6. Offset (add)

        Args:
            image: Input tensor [B,H,W,C] (should be straight/unpremultiplied alpha)
            saturation: Saturation multiplier (0=gray, 1=no change, >1=oversaturated)
            hue_shift: Hue rotation in degrees (-180 to +180)
            contrast: Contrast multiplier (<1=less, 1=no change, >1=more)
            gamma: Gamma correction (pow(x, 1/gamma)) (<1=darken, 1=no change, >1=brighten)
            gain: Gain multiplier (multiply)
            offset: Offset value (add)

        Returns:
            Tuple containing color-corrected image [B,H,W,C]
        """
        validate_image_tensor(image)

        result = image

        # Apply contrast (around 0.5 pivot)
        if contrast != 1.0:
            result = adjust_contrast(result, contrast, pivot=0.5)

        # Apply saturation
        if saturation != 1.0:
            result = adjust_saturation(result, saturation)

        # Apply hue shift (Detonate improvement!)
        if hue_shift != 0.0:
            result = self._apply_hue_shift(result, hue_shift)

        # Apply gamma
        if gamma != 1.0:
            result = apply_gamma(result, gamma)

        # Apply gain (multiply)
        if gain != 1.0:
            result = apply_gain(result, gain)

        # Apply offset (add)
        if offset != 0.0:
            result = apply_offset(result, offset)

        return (result,)

    def _apply_hue_shift(
        self,
        image: torch.Tensor,
        hue_shift_degrees: float
    ) -> torch.Tensor:
        """
        Apply hue shift to image.

        Converts RGB → HSV, shifts hue, converts back to RGB.

        Args:
            image: Input tensor [B,H,W,C]
            hue_shift_degrees: Hue rotation in degrees

        Returns:
            Hue-shifted image [B,H,W,C]
        """
        B, H, W, C = image.shape
        has_alpha = C == 4

        # Extract RGB and alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Convert RGB to HSV
        # Formula from RGB to HSV:
        # V = max(R,G,B)
        # S = (V - min(R,G,B)) / V  if V != 0
        # H calculation based on which channel is max

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

        # Apply hue shift (normalized: 360 degrees = 1.0)
        hue_shift_normalized = hue_shift_degrees / 360.0
        hue = (hue + hue_shift_normalized) % 1.0

        # Convert HSV back to RGB
        h = hue * 6.0  # Scale to 0-6
        i = torch.floor(h).long()
        f = h - i.float()

        p = value * (1.0 - saturation)
        q = value * (1.0 - saturation * f)
        t = value * (1.0 - saturation * (1.0 - f))

        # Initialize result
        result_rgb = torch.zeros_like(rgb)

        # i % 6 determines which formula to use
        i = i % 6

        # Case 0: (v, t, p)
        mask_0 = (i == 0)
        result_rgb[mask_0.squeeze(3), 0] = value[mask_0].squeeze()
        result_rgb[mask_0.squeeze(3), 1] = t[mask_0].squeeze()
        result_rgb[mask_0.squeeze(3), 2] = p[mask_0].squeeze()

        # Case 1: (q, v, p)
        mask_1 = (i == 1)
        result_rgb[mask_1.squeeze(3), 0] = q[mask_1].squeeze()
        result_rgb[mask_1.squeeze(3), 1] = value[mask_1].squeeze()
        result_rgb[mask_1.squeeze(3), 2] = p[mask_1].squeeze()

        # Case 2: (p, v, t)
        mask_2 = (i == 2)
        result_rgb[mask_2.squeeze(3), 0] = p[mask_2].squeeze()
        result_rgb[mask_2.squeeze(3), 1] = value[mask_2].squeeze()
        result_rgb[mask_2.squeeze(3), 2] = t[mask_2].squeeze()

        # Case 3: (p, q, v)
        mask_3 = (i == 3)
        result_rgb[mask_3.squeeze(3), 0] = p[mask_3].squeeze()
        result_rgb[mask_3.squeeze(3), 1] = q[mask_3].squeeze()
        result_rgb[mask_3.squeeze(3), 2] = value[mask_3].squeeze()

        # Case 4: (t, p, v)
        mask_4 = (i == 4)
        result_rgb[mask_4.squeeze(3), 0] = t[mask_4].squeeze()
        result_rgb[mask_4.squeeze(3), 1] = p[mask_4].squeeze()
        result_rgb[mask_4.squeeze(3), 2] = value[mask_4].squeeze()

        # Case 5: (v, p, q)
        mask_5 = (i == 5)
        result_rgb[mask_5.squeeze(3), 0] = value[mask_5].squeeze()
        result_rgb[mask_5.squeeze(3), 1] = p[mask_5].squeeze()
        result_rgb[mask_5.squeeze(3), 2] = q[mask_5].squeeze()

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return result
