"""
Grain node for ComfyUI_Detonate.

Film grain and texture addition for matching CG to live action.
Essential for photorealistic compositing.

Reference: Nuke Grain node, DaVinci Resolve Film Grain
https://learn.foundry.com/nuke/content/reference_guide/color_nodes/grain.html
"""

import torch
from ...utils import validate_image_tensor


class DetonateGrain:
    """
    Film grain and texture addition.

    Adds procedural grain/noise to match film stocks or digital
    camera noise. Supports luminance-dependent grain distribution
    and per-channel control for realistic film emulation.

    Common uses:
    - Match CG to film grain
    - Add texture to flat renders
    - Digital camera noise emulation
    - Photographic authenticity
    - Stylistic texture

    Nuke/DaVinci equivalent: Grain / Film Grain
    """

    CATEGORY = "detonate/filter"

    # Detonate improvement: Multiple grain types!
    GRAIN_TYPES = ["film", "digital", "organic", "halftone"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Grain intensity
                "intensity": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Grain size/frequency
                "size": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                # Grain type (Detonate improvement!)
                "grain_type": (cls.GRAIN_TYPES, {
                    "default": "film",
                }),
                # Color vs monochrome grain
                "color": ("BOOLEAN", {
                    "default": False,
                }),
                # Luminance dependency (Detonate improvement!)
                "shadow_bias": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "highlight_bias": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Per-channel intensity (Detonate improvement!)
                "red_intensity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "green_intensity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "blue_intensity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Random seed for reproducibility
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "step": 1,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "add_grain"

    def add_grain(
        self,
        image: torch.Tensor,
        intensity: float = 0.1,
        size: float = 1.0,
        grain_type: str = "film",
        color: bool = False,
        shadow_bias: float = 0.0,
        highlight_bias: float = 0.0,
        red_intensity: float = 1.0,
        green_intensity: float = 1.0,
        blue_intensity: float = 1.0,
        seed: int = 0
    ) -> tuple:
        """
        Add film grain to image.

        Detonate improvements:
        1. Multiple grain types (film, digital, organic, halftone)
        2. Luminance-dependent grain (shadow/highlight bias)
        3. Per-channel grain intensity
        4. Color vs monochrome grain

        Args:
            image: Input tensor [B,H,W,C]
            intensity: Grain strength
            size: Grain size (smaller = finer grain)
            grain_type: Type of grain pattern
            color: Use color grain vs monochrome
            shadow_bias: More grain in shadows (<0) or less (>0)
            highlight_bias: More grain in highlights (>0) or less (<0)
            red_intensity: Red channel grain multiplier
            green_intensity: Green channel grain multiplier
            blue_intensity: Blue channel grain multiplier
            seed: Random seed for reproducibility

        Returns:
            Tuple containing grained image [B,H,W,C]
        """
        validate_image_tensor(image)

        if intensity <= 0.0:
            return (image,)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Work on RGB only, preserve alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Set random seed for reproducibility
        generator = torch.Generator(device=image.device).manual_seed(seed)

        # Generate grain noise
        grain = self._generate_grain(
            B, H, W, size, grain_type, color, generator
        )
        grain = grain.to(image.device)

        # Apply per-channel intensity (Detonate improvement!)
        if color:
            channel_mult = torch.tensor(
                [red_intensity, green_intensity, blue_intensity],
                dtype=rgb.dtype,
                device=rgb.device
            ).view(1, 1, 1, 3)
            grain = grain * channel_mult

        # Calculate luminance for bias
        if shadow_bias != 0.0 or highlight_bias != 0.0:
            # Rec. 709 luma coefficients
            luma = rgb[:, :, :, 0:1] * 0.2126 + \
                   rgb[:, :, :, 1:2] * 0.7152 + \
                   rgb[:, :, :, 2:3] * 0.0722

            # Create luminance mask
            # shadow_bias: negative = more grain in shadows
            # highlight_bias: positive = more grain in highlights
            luma_mask = 1.0

            if shadow_bias != 0.0:
                # More grain in shadows when bias is negative
                shadow_mask = 1.0 - luma  # Inverted luma
                luma_mask = luma_mask + shadow_mask * (-shadow_bias)

            if highlight_bias != 0.0:
                # More grain in highlights when bias is positive
                highlight_mask = luma
                luma_mask = luma_mask + highlight_mask * highlight_bias

            # Apply luminance mask to grain
            if not color:
                grain = grain * luma_mask
            else:
                grain = grain * luma_mask.repeat(1, 1, 1, 3)

        # Add grain to image
        result_rgb = rgb + grain * intensity

        # Clamp to valid range
        result_rgb = torch.clamp(result_rgb, min=0.0, max=1.0)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return (result,)

    def _generate_grain(
        self,
        B: int,
        H: int,
        W: int,
        size: float,
        grain_type: str,
        color: bool,
        generator: torch.Generator
    ) -> torch.Tensor:
        """
        Generate grain noise pattern.

        Detonate improvement: Multiple grain types!

        Args:
            B: Batch size
            H: Height
            W: Width
            size: Grain size
            grain_type: Type of grain
            color: Color vs monochrome
            generator: Random generator

        Returns:
            Grain tensor [B,H,W,C] where C=3 if color else C=1
        """
        channels = 3 if color else 1

        if grain_type == "film":
            # Film grain: Gaussian distribution, slightly correlated
            grain = torch.randn(B, H, W, channels, generator=generator)

            # Apply size by downsampling and upsampling
            if size != 1.0:
                grain = self._apply_grain_size(grain, size)

        elif grain_type == "digital":
            # Digital noise: More uniform, less correlated
            grain = torch.rand(B, H, W, channels, generator=generator) * 2.0 - 1.0

            if size != 1.0:
                grain = self._apply_grain_size(grain, size)

        elif grain_type == "organic":
            # Organic texture: Multiple scales of noise
            grain = torch.randn(B, H, W, channels, generator=generator)

            # Add multiple octaves
            grain2 = torch.randn(B, H, W, channels, generator=generator)
            grain = grain * 0.7 + grain2 * 0.3

            if size != 1.0:
                grain = self._apply_grain_size(grain, size)

        elif grain_type == "halftone":
            # Halftone pattern: Regular dot structure
            grain = self._generate_halftone(B, H, W, channels, size, generator)

        else:
            grain = torch.randn(B, H, W, channels, generator=generator)

        # Normalize to -0.5 to +0.5 range
        grain = grain * 0.5

        # If monochrome, ensure shape is [B,H,W,1]
        if not color and grain.shape[3] != 1:
            grain = grain.mean(dim=3, keepdim=True)

        return grain

    def _apply_grain_size(
        self,
        grain: torch.Tensor,
        size: float
    ) -> torch.Tensor:
        """
        Apply grain size by downsampling/upsampling.

        Larger size = coarser grain.

        Args:
            grain: Input grain [B,H,W,C]
            size: Size multiplier

        Returns:
            Resized grain [B,H,W,C]
        """
        if size == 1.0:
            return grain

        B, H, W, C = grain.shape

        # Calculate scaled dimensions
        H_scaled = max(1, int(H / size))
        W_scaled = max(1, int(W / size))

        # Convert to [B,C,H,W] for interpolation
        grain_nchw = grain.permute(0, 3, 1, 2)

        # Downsample
        grain_down = torch.nn.functional.interpolate(
            grain_nchw,
            size=(H_scaled, W_scaled),
            mode='bilinear',
            align_corners=False
        )

        # Upsample back to original size
        grain_up = torch.nn.functional.interpolate(
            grain_down,
            size=(H, W),
            mode='bilinear',
            align_corners=False
        )

        # Convert back to [B,H,W,C]
        result = grain_up.permute(0, 2, 3, 1)

        return result

    def _generate_halftone(
        self,
        B: int,
        H: int,
        W: int,
        C: int,
        size: float,
        generator: torch.Generator
    ) -> torch.Tensor:
        """
        Generate halftone dot pattern.

        Creates regular dot structure similar to print halftones.

        Args:
            B, H, W, C: Tensor dimensions
            size: Dot size
            generator: Random generator

        Returns:
            Halftone pattern [B,H,W,C]
        """
        # Create coordinate grid
        y = torch.linspace(0, H * size, H).unsqueeze(1).repeat(1, W)
        x = torch.linspace(0, W * size, W).unsqueeze(0).repeat(H, 1)

        # Create dot pattern using sine waves
        pattern = torch.sin(x * 0.5) * torch.sin(y * 0.5)

        # Add randomness
        noise = torch.randn(H, W, generator=generator) * 0.3
        pattern = pattern + noise

        # Expand to batch and channels
        pattern = pattern.unsqueeze(0).unsqueeze(3).repeat(B, 1, 1, C)

        return pattern
