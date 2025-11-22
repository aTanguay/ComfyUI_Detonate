"""
Vignette node for ComfyUI_Detonate.

Lens vignetting effect - darken or lighten image edges.
Essential for photographic looks and focus control.

Reference: Common in many compositing packages
DaVinci Resolve Vignette, Photoshop Lens Correction
"""

import torch
import math
from ...utils import validate_image_tensor


class DetonateVignette:
    """
    Lens vignetting effect with shape and color controls.

    Creates natural lens vignetting (darkened edges) or inverse
    vignetting (lightened edges). Supports multiple shapes and
    falloff curves for creative control.

    Common uses:
    - Photographic vignette effect
    - Draw attention to center
    - Frame composition
    - Stylistic darkening/lightening
    - Color tinting at edges

    DaVinci/Photoshop equivalent: Vignette
    """

    CATEGORY = "detonate/filter"

    # Detonate improvement: Multiple vignette shapes!
    SHAPES = ["circular", "oval", "rectangular"]

    # Detonate improvement: Multiple falloff curves!
    FALLOFFS = ["linear", "quadratic", "cubic", "smooth"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Intensity
                "amount": ("FLOAT", {
                    "default": 0.5,
                    "min": -2.0,  # Negative = lighten edges
                    "max": 2.0,   # Positive = darken edges
                    "step": 0.01,
                    "display": "slider",
                }),
                # Size and position
                "size": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "feather": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "center_x": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "center_y": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Shape controls (Detonate improvement!)
                "shape": (cls.SHAPES, {
                    "default": "circular",
                }),
                "aspect_ratio": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number",
                }),
                # Falloff curve (Detonate improvement!)
                "falloff": (cls.FALLOFFS, {
                    "default": "quadratic",
                }),
                # Color tint (Detonate improvement!)
                "tint_r": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "tint_g": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "tint_b": ("FLOAT", {
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
    FUNCTION = "apply_vignette"

    def apply_vignette(
        self,
        image: torch.Tensor,
        amount: float = 0.5,
        size: float = 0.5,
        feather: float = 0.5,
        center_x: float = 0.5,
        center_y: float = 0.5,
        shape: str = "circular",
        aspect_ratio: float = 1.0,
        falloff: str = "quadratic",
        tint_r: float = 0.0,
        tint_g: float = 0.0,
        tint_b: float = 0.0
    ) -> tuple:
        """
        Apply vignette effect to image.

        Detonate improvements:
        1. Multiple shapes (circular, oval, rectangular)
        2. Multiple falloff curves (linear, quadratic, cubic, smooth)
        3. Color tinting for stylistic effects
        4. Inverse vignette (negative amount)

        Args:
            image: Input tensor [B,H,W,C]
            amount: Vignette intensity (>0 darken, <0 lighten)
            size: Vignette size (smaller = more vignetting)
            feather: Edge softness
            center_x: Horizontal center (0-1)
            center_y: Vertical center (0-1)
            shape: Vignette shape
            aspect_ratio: Shape aspect ratio (for oval/rectangular)
            falloff: Falloff curve type
            tint_r, tint_g, tint_b: Color tint at edges

        Returns:
            Tuple containing vignetted image [B,H,W,C]
        """
        validate_image_tensor(image)

        if amount == 0.0 and tint_r == 0.0 and tint_g == 0.0 and tint_b == 0.0:
            return (image,)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Work on RGB only, preserve alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Create vignette matte
        matte = self._create_vignette_matte(
            H, W, size, feather, center_x, center_y,
            shape, aspect_ratio, falloff
        )
        matte = matte.to(image.device).unsqueeze(0).unsqueeze(3)  # [1,H,W,1]

        # Apply vignette darkening/lightening
        if amount != 0.0:
            # Vignette multiplier: 1.0 at center, (1 - amount) at edges
            vignette_mult = 1.0 - matte * amount
            rgb = rgb * vignette_mult

        # Apply color tint (Detonate improvement!)
        if tint_r != 0.0 or tint_g != 0.0 or tint_b != 0.0:
            tint = torch.tensor(
                [tint_r, tint_g, tint_b],
                dtype=rgb.dtype,
                device=rgb.device
            ).view(1, 1, 1, 3)
            rgb = rgb + matte * tint

        # Clamp to valid range
        rgb = torch.clamp(rgb, min=0.0, max=1.0)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([rgb, alpha], dim=3)
        else:
            result = rgb

        return (result,)

    def _create_vignette_matte(
        self,
        height: int,
        width: int,
        size: float,
        feather: float,
        center_x: float,
        center_y: float,
        shape: str,
        aspect_ratio: float,
        falloff: str
    ) -> torch.Tensor:
        """
        Create vignette matte.

        Detonate improvement: Multiple shapes and falloff curves!

        Args:
            height, width: Image dimensions
            size: Vignette size
            feather: Edge softness
            center_x, center_y: Center position (0-1)
            shape: Vignette shape
            aspect_ratio: Shape aspect ratio
            falloff: Falloff curve type

        Returns:
            Vignette matte [height, width] (0=center, 1=edge)
        """
        # Create normalized coordinate grid
        y_coords = torch.linspace(0, 1, height).unsqueeze(1).repeat(1, width)
        x_coords = torch.linspace(0, 1, width).unsqueeze(0).repeat(height, 1)

        # Center coordinates
        y_centered = y_coords - center_y
        x_centered = x_coords - center_x

        # Apply aspect ratio
        x_scaled = x_centered * aspect_ratio

        # Calculate distance based on shape
        if shape == "circular":
            # Euclidean distance
            dist = torch.sqrt(x_scaled ** 2 + y_centered ** 2)
        elif shape == "oval":
            # Elliptical distance (same as circular with aspect ratio)
            dist = torch.sqrt(x_scaled ** 2 + y_centered ** 2)
        elif shape == "rectangular":
            # Chebyshev distance (max of x, y)
            dist = torch.maximum(torch.abs(x_scaled), torch.abs(y_centered))
        else:
            dist = torch.sqrt(x_scaled ** 2 + y_centered ** 2)

        # Normalize distance by image diagonal
        max_dist = math.sqrt((0.5 * aspect_ratio) ** 2 + 0.5 ** 2)
        dist = dist / max_dist

        # Apply size and feather
        # Size determines where vignette starts
        # Feather determines transition width
        if size <= 0:
            size = 0.01

        # Feather range: [size * (1 - feather), size * (1 + feather)]
        inner_radius = size * (1.0 - feather)
        outer_radius = size * (1.0 + feather)

        # Normalize distance to 0-1 range within feather region
        if outer_radius > inner_radius:
            t = (dist - inner_radius) / (outer_radius - inner_radius)
            t = torch.clamp(t, 0.0, 1.0)
        else:
            t = (dist > size).float()

        # Apply falloff curve (Detonate improvement!)
        if falloff == "linear":
            matte = t
        elif falloff == "quadratic":
            matte = t * t
        elif falloff == "cubic":
            matte = t * t * t
        elif falloff == "smooth":
            # Smoothstep
            matte = t * t * (3.0 - 2.0 * t)
        else:
            matte = t

        return matte
