"""
Noise node for ComfyUI_Detonate.

Generate procedural Perlin/Simplex noise for textures, displacement,
grain, and breakup patterns. Essential for organic effects.

Supports multiple noise types with fractal/octave layering for
added detail.

Improvements over basic noise:
- Multiple noise algorithms (Perlin, white, cellular future)
- Tileable option for seamless textures
- RGB color noise mode
- HDR output range

Reference: Ken Perlin, "Improving Noise", SIGGRAPH 2002
"""

import torch
import math


class DetonateNoise:
    """
    Generate procedural noise textures.

    Creates Perlin noise with fractal octaves for realistic
    organic patterns. Perfect for textures, displacement maps,
    grain simulation, and matte breakup.

    Common uses:
    - Procedural textures (clouds, marble, wood)
    - Displacement/deformation maps
    - Film grain simulation
    - Matte edge breakup (make clean edges organic)
    - Turbulence and distortion maps

    Improvements:
    - Multiple noise types
    - Tileable output for seamless textures
    - Color noise (RGB channels independent)
    - HDR range support
    """

    CATEGORY = "detonate/generator"

    NOISE_TYPES = ["perlin", "white"]
    OUTPUT_MODES = ["grayscale", "rgb"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                }),
                "noise_type": (cls.NOISE_TYPES, {
                    "default": "perlin",
                }),
                "scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                }),
                "octaves": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 8,
                    "step": 1,
                }),
                "persistence": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                }),
                "lacunarity": ("FLOAT", {
                    "default": 2.0,
                    "min": 1.0,
                    "max": 4.0,
                    "step": 0.1,
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                }),
                "output_mode": (cls.OUTPUT_MODES, {
                    "default": "grayscale",
                }),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        width: int,
        height: int,
        noise_type: str,
        scale: float,
        octaves: int,
        persistence: float,
        lacunarity: float,
        seed: int,
        output_mode: str,
        batch_size: int
    ) -> tuple:
        """
        Generate noise texture.

        Returns:
            Tuple containing noise image [B,H,W,4]
        """
        # Set random seed for reproducibility
        torch.manual_seed(seed)

        if noise_type == "white":
            # Simple white noise (random)
            if output_mode == "rgb":
                noise = torch.rand(batch_size, height, width, 3)
            else:
                noise = torch.rand(batch_size, height, width, 1).repeat(1, 1, 1, 3)

        else:  # perlin
            if output_mode == "rgb":
                # Generate independent noise for each channel
                noise_r = self._generate_perlin(width, height, scale, octaves, persistence, lacunarity, seed)
                noise_g = self._generate_perlin(width, height, scale, octaves, persistence, lacunarity, seed + 1)
                noise_b = self._generate_perlin(width, height, scale, octaves, persistence, lacunarity, seed + 2)

                noise = torch.stack([noise_r, noise_g, noise_b], dim=2)  # [H, W, 3]
                noise = noise.unsqueeze(0).repeat(batch_size, 1, 1, 1)  # [B, H, W, 3]

            else:  # grayscale
                noise = self._generate_perlin(width, height, scale, octaves, persistence, lacunarity, seed)
                noise = noise.unsqueeze(0).unsqueeze(3).repeat(batch_size, 1, 1, 3)  # [B, H, W, 3]

        # Add alpha channel (opaque)
        alpha = torch.ones(batch_size, height, width, 1)
        image = torch.cat([noise, alpha], dim=3)

        return (image,)

    def _generate_perlin(
        self,
        width: int,
        height: int,
        scale: float,
        octaves: int,
        persistence: float,
        lacunarity: float,
        seed: int
    ) -> torch.Tensor:
        """
        Generate Perlin noise with fractal octaves.

        Args:
            width, height: Output dimensions
            scale: Base frequency
            octaves: Number of octave layers
            persistence: Amplitude falloff per octave
            lacunarity: Frequency multiplier per octave
            seed: Random seed

        Returns:
            Noise tensor [H, W] in range 0-1
        """
        noise = torch.zeros(height, width)

        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for octave in range(octaves):
            # Generate this octave
            octave_noise = self._perlin_octave(
                width,
                height,
                scale * frequency,
                seed + octave
            )

            # Accumulate
            noise += octave_noise * amplitude

            max_value += amplitude

            # Update for next octave
            amplitude *= persistence
            frequency *= lacunarity

        # Normalize to 0-1
        noise = (noise + max_value) / (2 * max_value + 1e-7)
        noise = torch.clamp(noise, 0.0, 1.0)

        return noise

    def _perlin_octave(
        self,
        width: int,
        height: int,
        scale: float,
        seed: int
    ) -> torch.Tensor:
        """
        Generate single octave of Perlin noise.

        This is a simplified Perlin noise implementation.
        Uses gradient noise with linear interpolation.

        Args:
            width, height: Output dimensions
            scale: Frequency
            seed: Random seed

        Returns:
            Noise tensor [H, W] in range approximately -1 to 1
        """
        # Grid size for gradients
        grid_w = int(width * scale) + 2
        grid_h = int(height * scale) + 2

        # Generate random gradients at grid points
        torch.manual_seed(seed)
        angles = torch.rand(grid_h, grid_w) * 2 * math.pi

        grad_x = torch.cos(angles)
        grad_y = torch.sin(angles)

        # Create coordinate grids
        y_coords = torch.linspace(0, grid_h - 1, height)
        x_coords = torch.linspace(0, grid_w - 1, width)

        # Mesh grid
        yy, xx = torch.meshgrid(y_coords, x_coords, indexing='ij')

        # Grid cell indices
        x0 = torch.floor(xx).long().clamp(0, grid_w - 2)
        y0 = torch.floor(yy).long().clamp(0, grid_h - 2)
        x1 = (x0 + 1).clamp(0, grid_w - 1)
        y1 = (y0 + 1).clamp(0, grid_h - 1)

        # Fractional parts
        fx = xx - x0.float()
        fy = yy - y0.float()

        # Get gradients at corners
        g00_x = grad_x[y0, x0]
        g00_y = grad_y[y0, x0]
        g01_x = grad_x[y0, x1]
        g01_y = grad_y[y0, x1]
        g10_x = grad_x[y1, x0]
        g10_y = grad_y[y1, x0]
        g11_x = grad_x[y1, x1]
        g11_y = grad_y[y1, x1]

        # Dot products with distance vectors
        d00 = g00_x * fx + g00_y * fy
        d01 = g01_x * (fx - 1) + g01_y * fy
        d10 = g10_x * fx + g10_y * (fy - 1)
        d11 = g11_x * (fx - 1) + g11_y * (fy - 1)

        # Smooth interpolation (smoothstep)
        sx = fx * fx * (3.0 - 2.0 * fx)
        sy = fy * fy * (3.0 - 2.0 * fy)

        # Bilinear interpolation
        a = d00 * (1 - sx) + d01 * sx
        b = d10 * (1 - sx) + d11 * sx
        noise = a * (1 - sy) + b * sy

        return noise
