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
        3. Gamma
        4. Gain (multiply)
        5. Offset (add)

        Args:
            image: Input tensor [B,H,W,C] (should be straight/unpremultiplied alpha)
            saturation: Saturation multiplier (0=gray, 1=no change, >1=oversaturated)
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
