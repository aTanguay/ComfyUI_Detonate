"""
ChromaKeyer node for ComfyUI_Detonate.

Professional greenscreen/bluescreen chroma keying.
Industry-standard color difference keying algorithm.

Reference: Nuke IBKColour, Keylight, DaVinci Fusion Chroma Keyer
"""

import torch
import numpy as np
from typing import Tuple


class DetonateChromaKeyer:
    """
    Professional chroma keyer for greenscreen/bluescreen removal.

    Uses color difference keying algorithm to extract alpha mattes from
    solid color backgrounds. Essential for VFX compositing workflows.

    Features:
    - Screen color selection (Green, Blue, Custom RGB)
    - Threshold and tolerance controls
    - Soft edge control (feathering)
    - Spill suppression (remove color cast from edges)
    - Multiple output modes

    Workflow:
    1. Select screen color (green/blue/custom)
    2. Adjust threshold to set initial key range
    3. Use tolerance to expand key range
    4. Add softness for smooth edges
    5. Enable despill to remove color fringing

    Common uses:
    - Greenscreen/bluescreen removal
    - Product photography background removal
    - Virtual production keying
    - Interview/talking head compositing

    Nuke equivalent: IBKColour, Keylight
    Fusion equivalent: Delta Keyer, Primatte
    """

    CATEGORY = "detonate/keying"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "screen_color": (["Green", "Blue", "Custom"], {
                    "default": "Green",
                }),
                "threshold": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Key threshold - lower = more aggressive keying",
                }),
                "tolerance": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Key tolerance - expands key range",
                }),
                "softness": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Edge softness - smooth key edges",
                }),
            },
            "optional": {
                "custom_color_r": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "custom_color_g": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "custom_color_b": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "despill": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Spill suppression - remove color cast from edges",
                }),
                "output_mode": (["Alpha", "Foreground", "Raw Key", "Despilled"], {
                    "default": "Foreground",
                    "tooltip": "Output: Alpha (matte only), Foreground (keyed image), Raw Key, Despilled (color corrected)",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output",)
    FUNCTION = "chroma_key"

    def chroma_key(
        self,
        image: torch.Tensor,
        screen_color: str,
        threshold: float,
        tolerance: float,
        softness: float,
        custom_color_r: float = 0.0,
        custom_color_g: float = 1.0,
        custom_color_b: float = 0.0,
        despill: float = 0.5,
        output_mode: str = "Foreground"
    ) -> Tuple[torch.Tensor]:
        """
        Perform chroma keying on image.

        Args:
            image: Input image [B, H, W, C]
            screen_color: Screen color preset (Green/Blue/Custom)
            threshold: Key threshold (0-1)
            tolerance: Key tolerance (0-1)
            softness: Edge softness (0-1)
            custom_color_r/g/b: Custom screen color RGB
            despill: Spill suppression amount (0-1)
            output_mode: Output type (Alpha/Foreground/Raw Key/Despilled)

        Returns:
            Output image [B, H, W, C]
        """
        device = image.device
        B, H, W, C = image.shape

        # Determine screen color
        if screen_color == "Green":
            key_color = torch.tensor([0.0, 1.0, 0.0], device=device)
        elif screen_color == "Blue":
            key_color = torch.tensor([0.0, 0.0, 1.0], device=device)
        else:  # Custom
            key_color = torch.tensor([custom_color_r, custom_color_g, custom_color_b], device=device)

        # Extract RGB channels
        if C == 4:
            rgb = image[..., :3]
            original_alpha = image[..., 3:4]
        else:
            rgb = image
            original_alpha = torch.ones(B, H, W, 1, device=device)

        # Calculate color difference from key color
        # Using Euclidean distance in RGB space
        color_diff = torch.sqrt(torch.sum((rgb - key_color.view(1, 1, 1, 3)) ** 2, dim=-1, keepdim=True))

        # Normalize to [0, 1] range
        # Maximum possible distance in RGB space is sqrt(3) ≈ 1.732
        color_diff = color_diff / 1.732

        # Generate alpha matte based on color difference
        # threshold: center of key range
        # tolerance: width of key range
        # softness: feather edges

        # Calculate key range
        key_min = threshold - tolerance
        key_max = threshold + tolerance + softness

        # Create alpha using smoothstep
        alpha = torch.clamp((color_diff - key_min) / (key_max - key_min + 1e-7), 0.0, 1.0)

        # Apply smoothstep for smooth falloff
        alpha = alpha * alpha * (3.0 - 2.0 * alpha)

        # Apply spill suppression if requested
        if despill > 0.0:
            rgb_despilled = self._despill(rgb, key_color, despill)
        else:
            rgb_despilled = rgb

        # Generate output based on mode
        if output_mode == "Alpha":
            # Output alpha matte as grayscale
            output = alpha.repeat(1, 1, 1, 3)
        elif output_mode == "Foreground":
            # Output keyed foreground with alpha
            output = torch.cat([rgb_despilled, alpha], dim=-1)
        elif output_mode == "Raw Key":
            # Output raw key (before softness) as grayscale
            raw_key = torch.clamp((color_diff - threshold) / (tolerance + 1e-7), 0.0, 1.0)
            output = raw_key.repeat(1, 1, 1, 3)
        elif output_mode == "Despilled":
            # Output despilled RGB without alpha
            output = torch.cat([rgb_despilled, torch.ones_like(alpha)], dim=-1)
        else:
            # Default: Foreground
            output = torch.cat([rgb_despilled, alpha], dim=-1)

        # Ensure output has 4 channels (RGBA)
        if output.shape[-1] == 3:
            output = torch.cat([output, torch.ones(B, H, W, 1, device=device)], dim=-1)

        return (output,)

    def _despill(
        self,
        rgb: torch.Tensor,
        key_color: torch.Tensor,
        amount: float
    ) -> torch.Tensor:
        """
        Remove color spill (green/blue cast) from keyed edges.

        Uses the industry-standard despill algorithm:
        For each pixel, reduce the key color channel by the amount
        it exceeds the average of the other two channels.

        Args:
            rgb: Input RGB [B, H, W, 3]
            key_color: Screen color [3]
            amount: Despill strength (0-1)

        Returns:
            Despilled RGB [B, H, W, 3]
        """
        device = rgb.device

        # Find dominant channel in key color
        key_channel = torch.argmax(key_color)

        # Create channel indices
        if key_channel == 0:  # Red
            primary = rgb[..., 0:1]
            secondary = (rgb[..., 1:2] + rgb[..., 2:3]) / 2.0
        elif key_channel == 1:  # Green (most common)
            primary = rgb[..., 1:2]
            secondary = (rgb[..., 0:1] + rgb[..., 2:3]) / 2.0
        else:  # Blue
            primary = rgb[..., 2:3]
            secondary = (rgb[..., 0:1] + rgb[..., 1:2]) / 2.0

        # Calculate spill amount (how much primary exceeds secondary)
        spill = torch.clamp(primary - secondary, 0.0, 1.0)

        # Remove spill from primary channel
        primary_despilled = primary - (spill * amount)

        # Reconstruct RGB
        rgb_despilled = rgb.clone()
        if key_channel == 0:
            rgb_despilled[..., 0:1] = primary_despilled
        elif key_channel == 1:
            rgb_despilled[..., 1:2] = primary_despilled
        else:
            rgb_despilled[..., 2:3] = primary_despilled

        return torch.clamp(rgb_despilled, 0.0, 1.0)
