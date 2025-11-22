"""
Saturation node for ComfyUI_Detonate.

Direct saturation control without affecting luminance.
Simpler than ColorCorrect when only saturation adjustment is needed.

Reference: Nuke Saturation / HSV Tools
https://learn.foundry.com/nuke/content/comp_environment/color_correction/making_hsv_corrections.html
"""

import torch
from ...utils import validate_image_tensor, ensure_alpha_channel
from ...utils.color_math import rgb_to_hsv, hsv_to_rgb


class DetonateSaturation:
    """
    Adjust color saturation without affecting luminance.

    Converts RGB to HSV, adjusts S channel, converts back.
    Simpler alternative to ColorCorrect for saturation-only adjustments.

    Common uses:
    - Desaturation (reduce to grayscale)
    - Enhance color vibrancy
    - Stylistic color treatments
    - Partial desaturation for mood

    Nuke/Fusion equivalent: Saturation / ColorCorrector (saturation)
    """

    CATEGORY = "detonate/color"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "saturation": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "adjust_saturation"

    def adjust_saturation(
        self,
        image: torch.Tensor,
        saturation: float = 1.0
    ) -> tuple:
        """
        Adjust color saturation.

        Saturation values:
        - 0.0: Complete desaturation (grayscale)
        - 1.0: No change (original colors)
        - 2.0: Double saturation (very vivid)

        Works on straight (unpremultiplied) alpha images.

        Args:
            image: Input tensor [B,H,W,C]
            saturation: Saturation multiplier (0.0 = grayscale, 1.0 = original, >1.0 = boosted)

        Returns:
            Tuple containing adjusted image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Work on RGB only, preserve alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Early exit if saturation is 1.0 (no change)
        if saturation == 1.0:
            return (image,)

        # Convert RGB to HSV
        hsv = rgb_to_hsv(rgb)

        # Adjust saturation channel
        hsv[:, :, :, 1] = hsv[:, :, :, 1] * saturation

        # Clamp saturation to valid range [0, 1]
        hsv[:, :, :, 1] = torch.clamp(hsv[:, :, :, 1], 0.0, 1.0)

        # Convert back to RGB
        result_rgb = hsv_to_rgb(hsv)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return (result,)
