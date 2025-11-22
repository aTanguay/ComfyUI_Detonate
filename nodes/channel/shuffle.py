"""
Shuffle node for ComfyUI_Detonate.

Rearrange, copy, and manipulate channels within an image.
Essential for channel management and matte creation.

Reference: Nuke Shuffle documentation
https://learn.foundry.com/nuke/content/reference_guide/channel_nodes/shuffle.html
"""

import torch
from ...utils import (
    validate_image_tensor,
    ensure_alpha_channel,
    calculate_luminance,
)


class DetonateShuffle:
    """
    Shuffle and rearrange image channels.

    Allows copying any input channel to any output channel, or
    filling channels with constants (0 or 1) or calculated values (luminance).

    Common uses:
    - Swap channels (R ↔ B)
    - Copy channel to alpha (create matte from red channel)
    - Generate luminance-based alpha
    - Create constant colors

    Nuke/Fusion equivalent: Shuffle / ChannelBooleans
    """

    CATEGORY = "detonate/channel"

    # Channel source options
    CHANNEL_OPTIONS = [
        "red",
        "green",
        "blue",
        "alpha",
        "0 (black)",
        "1 (white)",
        "luminance",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "red_output": (cls.CHANNEL_OPTIONS, {
                    "default": "red",
                }),
                "green_output": (cls.CHANNEL_OPTIONS, {
                    "default": "green",
                }),
                "blue_output": (cls.CHANNEL_OPTIONS, {
                    "default": "blue",
                }),
                "alpha_output": (cls.CHANNEL_OPTIONS, {
                    "default": "alpha",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "shuffle"

    def shuffle(
        self,
        image: torch.Tensor,
        red_output: str,
        green_output: str,
        blue_output: str,
        alpha_output: str
    ) -> tuple:
        """
        Shuffle image channels.

        Args:
            image: Input tensor [B,H,W,C] where C=3 or C=4
            red_output: Source for red channel
            green_output: Source for green channel
            blue_output: Source for blue channel
            alpha_output: Source for alpha channel

        Returns:
            Tuple containing shuffled image [B,H,W,4]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Ensure alpha channel for input
        image_rgba = ensure_alpha_channel(image, alpha_value=1.0)

        # Pre-calculate luminance if needed
        luminance = None
        if any(ch == "luminance" for ch in [red_output, green_output, blue_output, alpha_output]):
            luminance = calculate_luminance(image_rgba)

        # Create output tensor
        output = torch.zeros((B, H, W, 4), dtype=image.dtype, device=image.device)

        # Process each output channel
        output[:, :, :, 0] = self._get_channel(image_rgba, red_output, luminance)
        output[:, :, :, 1] = self._get_channel(image_rgba, green_output, luminance)
        output[:, :, :, 2] = self._get_channel(image_rgba, blue_output, luminance)
        output[:, :, :, 3] = self._get_channel(image_rgba, alpha_output, luminance)

        return (output,)

    def _get_channel(
        self,
        image: torch.Tensor,
        source: str,
        luminance: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Get channel data from source specification.

        Args:
            image: RGBA image tensor [B,H,W,4]
            source: Channel source name
            luminance: Pre-calculated luminance [B,H,W,1] (optional)

        Returns:
            Channel data [B,H,W]
        """
        if source == "red":
            return image[:, :, :, 0]
        elif source == "green":
            return image[:, :, :, 1]
        elif source == "blue":
            return image[:, :, :, 2]
        elif source == "alpha":
            return image[:, :, :, 3]
        elif source == "0 (black)":
            return torch.zeros_like(image[:, :, :, 0])
        elif source == "1 (white)":
            return torch.ones_like(image[:, :, :, 0])
        elif source == "luminance":
            if luminance is None:
                raise ValueError("Luminance not calculated")
            return luminance[:, :, :, 0]
        else:
            raise ValueError(f"Unknown channel source: {source}")
