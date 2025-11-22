"""
Constant node for ComfyUI_Detonate.

Generates solid color images with specified dimensions and RGBA values.
Essential for backgrounds, test patterns, and color references.

Reference: Nuke Constant node
https://learn.foundry.com/nuke/content/reference_guide/image_nodes/constant.html
"""

import torch


class DetonateConstant:
    """
    Generate solid color image with specified dimensions.

    Creates an image where every pixel is the same RGBA color.
    Supports HDR colors (values > 1.0) for bloom/glow effects.

    Common uses:
    - Solid backgrounds
    - Test patterns
    - Color references
    - Full white mattes

    Nuke/Fusion equivalent: Constant / Background
    """

    CATEGORY = "detonate/generator"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1920,
                    "min": 1,
                    "max": 16384,
                    "step": 1,
                    "display": "number",
                }),
                "height": ("INT", {
                    "default": 1080,
                    "min": 1,
                    "max": 16384,
                    "step": 1,
                    "display": "number",
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4096,
                    "step": 1,
                    "display": "number",
                }),
            },
            "optional": {
                "red": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "green": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "blue": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "alpha": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        width: int,
        height: int,
        batch_size: int = 1,
        red: float = 0.0,
        green: float = 0.0,
        blue: float = 0.0,
        alpha: float = 1.0
    ) -> tuple:
        """
        Generate solid color image.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            batch_size: Number of images in batch
            red: Red channel value (0.0 to ∞, supports HDR)
            green: Green channel value (0.0 to ∞, supports HDR)
            blue: Blue channel value (0.0 to ∞, supports HDR)
            alpha: Alpha channel value (0.0 to 1.0)

        Returns:
            Tuple containing solid color image [B,H,W,C]
        """
        # Create tensor with specified color
        # Shape: [B, H, W, C]
        color_values = [red, green, blue, alpha]

        image = torch.full(
            (batch_size, height, width, 4),
            fill_value=0.0,
            dtype=torch.float32
        )

        # Set color values for each channel
        for c in range(4):
            image[:, :, :, c] = color_values[c]

        return (image,)
