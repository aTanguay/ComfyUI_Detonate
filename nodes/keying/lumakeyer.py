"""
LumaKeyer node for ComfyUI_Detonate.

Brightness-based keying for sky replacement, highlights, shadows.
Luma keying based on pixel brightness values.

Reference: Nuke Keyer (Luminance mode), After Effects Luma Key
"""

import torch
import numpy as np
from typing import Tuple


class DetonateLumaKeyer:
    """
    Luminance-based keyer for brightness keying.

    Keys based on pixel brightness (luminance) rather than color.
    Essential for sky replacement, highlight/shadow isolation, and
    brightness-based selections.

    Features:
    - Multiple luminance modes (Rec.709, Average, Max, Min)
    - Range controls (min, max brightness)
    - Soft edge control
    - Invert option for dark/light keying
    - Multiple output modes

    Workflow:
    1. Select luminance mode (Rec.709 recommended)
    2. Set min/max brightness range to key
    3. Add softness for smooth edges
    4. Optionally invert for opposite key

    Common uses:
    - Sky replacement (key bright sky)
    - Highlight isolation
    - Shadow isolation (with invert)
    - Brightness-based masking
    - Day-for-night effects

    Nuke equivalent: Keyer (Luminance mode)
    Fusion equivalent: Luma Keyer
    """

    CATEGORY = "detonate/keying"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "luma_mode": (["Rec.709", "Average", "Max", "Min"], {
                    "default": "Rec.709",
                    "tooltip": "Luminance calculation: Rec.709 (standard), Average, Max/Min channel",
                }),
                "min_luma": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Minimum brightness to key (0=black, 1=white)",
                }),
                "max_luma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Maximum brightness to key",
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
                "invert": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert key (dark areas instead of bright)",
                }),
                "output_mode": (["Alpha", "Foreground"], {
                    "default": "Foreground",
                    "tooltip": "Output: Alpha (matte only) or Foreground (keyed image)",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output",)
    FUNCTION = "luma_key"

    def luma_key(
        self,
        image: torch.Tensor,
        luma_mode: str,
        min_luma: float,
        max_luma: float,
        softness: float,
        invert: bool = False,
        output_mode: str = "Foreground"
    ) -> Tuple[torch.Tensor]:
        """
        Perform luminance-based keying on image.

        Args:
            image: Input image [B, H, W, C]
            luma_mode: Luminance calculation mode
            min_luma: Minimum brightness to key (0-1)
            max_luma: Maximum brightness to key (0-1)
            softness: Edge softness (0-1)
            invert: Invert key (dark vs bright)
            output_mode: Output type (Alpha/Foreground)

        Returns:
            Output image [B, H, W, C]
        """
        device = image.device
        B, H, W, C = image.shape

        # Extract RGB channels
        if C == 4:
            rgb = image[..., :3]
            original_alpha = image[..., 3:4]
        else:
            rgb = image
            original_alpha = torch.ones(B, H, W, 1, device=device)

        # Calculate luminance based on mode
        if luma_mode == "Rec.709":
            # Standard Rec.709 luminance weights
            # Y = 0.2126*R + 0.7152*G + 0.0722*B
            weights = torch.tensor([0.2126, 0.7152, 0.0722], device=device)
            luma = torch.sum(rgb * weights.view(1, 1, 1, 3), dim=-1, keepdim=True)
        elif luma_mode == "Average":
            # Simple average of RGB
            luma = torch.mean(rgb, dim=-1, keepdim=True)
        elif luma_mode == "Max":
            # Maximum channel
            luma, _ = torch.max(rgb, dim=-1, keepdim=True)
        elif luma_mode == "Min":
            # Minimum channel
            luma, _ = torch.min(rgb, dim=-1, keepdim=True)
        else:
            # Default to Rec.709
            weights = torch.tensor([0.2126, 0.7152, 0.0722], device=device)
            luma = torch.sum(rgb * weights.view(1, 1, 1, 3), dim=-1, keepdim=True)

        # Generate alpha matte based on luminance range
        # Create smooth transition using softness

        # Ensure min_luma <= max_luma
        if min_luma > max_luma:
            min_luma, max_luma = max_luma, min_luma

        # Calculate key range with softness
        soft_min = min_luma - softness
        soft_max = max_luma + softness

        # Create alpha: 1.0 inside range, 0.0 outside, smooth transition
        # Lower edge (fade in from soft_min to min_luma)
        lower_alpha = torch.clamp((luma - soft_min) / (min_luma - soft_min + 1e-7), 0.0, 1.0)

        # Upper edge (fade out from max_luma to soft_max)
        upper_alpha = torch.clamp((soft_max - luma) / (soft_max - max_luma + 1e-7), 0.0, 1.0)

        # Combine: inside range = min(lower, upper)
        alpha = torch.minimum(lower_alpha, upper_alpha)

        # Apply smoothstep for smooth falloff
        alpha = alpha * alpha * (3.0 - 2.0 * alpha)

        # Invert if requested
        if invert:
            alpha = 1.0 - alpha

        # Generate output based on mode
        if output_mode == "Alpha":
            # Output alpha matte as grayscale
            output = alpha.repeat(1, 1, 1, 3)
            output = torch.cat([output, torch.ones_like(alpha)], dim=-1)
        else:  # Foreground
            # Output keyed foreground with alpha
            output = torch.cat([rgb, alpha], dim=-1)

        return (output,)


class DetonateLumaKeyerSimple:
    """
    Simplified luma keyer with single threshold.

    Quick brightness keying with single threshold and tolerance.
    Useful for simple sky replacement or highlight/shadow isolation.
    """

    CATEGORY = "detonate/keying"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Brightness threshold (0=black, 1=white)",
                }),
                "tolerance": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Key tolerance - expands key range",
                }),
                "mode": (["Brighter", "Darker"], {
                    "default": "Brighter",
                    "tooltip": "Key brighter or darker than threshold",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output",)
    FUNCTION = "luma_key_simple"

    def luma_key_simple(
        self,
        image: torch.Tensor,
        threshold: float,
        tolerance: float,
        mode: str
    ) -> Tuple[torch.Tensor]:
        """
        Simple luminance keying with single threshold.

        Args:
            image: Input image [B, H, W, C]
            threshold: Brightness threshold (0-1)
            tolerance: Key tolerance (0-1)
            mode: Brighter or Darker

        Returns:
            Output image [B, H, W, C]
        """
        device = image.device
        B, H, W, C = image.shape

        # Extract RGB
        if C == 4:
            rgb = image[..., :3]
        else:
            rgb = image

        # Calculate Rec.709 luminance
        weights = torch.tensor([0.2126, 0.7152, 0.0722], device=device)
        luma = torch.sum(rgb * weights.view(1, 1, 1, 3), dim=-1, keepdim=True)

        # Generate alpha based on mode
        if mode == "Brighter":
            # Key pixels brighter than threshold
            alpha = torch.clamp((luma - (threshold - tolerance)) / (2 * tolerance + 1e-7), 0.0, 1.0)
        else:  # Darker
            # Key pixels darker than threshold
            alpha = torch.clamp(((threshold + tolerance) - luma) / (2 * tolerance + 1e-7), 0.0, 1.0)

        # Smoothstep
        alpha = alpha * alpha * (3.0 - 2.0 * alpha)

        # Output foreground with alpha
        output = torch.cat([rgb, alpha], dim=-1)

        return (output,)
