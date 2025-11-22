"""
Defocus node for ComfyUI_Detonate.

Lens-style defocus blur with bokeh effects. Simulates realistic
out-of-focus blur mimicking actual camera lens characteristics.

Different from Gaussian blur - uses circular/shaped kernels for
more realistic lens simulation.

Improvements over Nuke:
- Multiple bokeh shapes (circular, hexagonal, octagonal)
- Aspect ratio control for anamorphic lenses
- Quality presets for speed/quality tradeoff

Reference: Nuke Defocus documentation
"""

import torch
import torch.nn.functional as F
import math
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateDefocus:
    """
    Realistic lens defocus with bokeh effects.

    Simulates out-of-focus blur using circular or shaped kernels
    that mimic camera lens apertures. More realistic than simple
    Gaussian blur for depth-of-field effects.

    Common uses:
    - Background defocus for subject isolation
    - Cinematic shallow depth of field
    - Lens simulation to match footage
    - Beauty/soft focus effects
    - Simulate specific lens characteristics

    Improvements:
    - Multiple bokeh shapes
    - Anamorphic lens simulation
    - Quality control
    """

    CATEGORY = "detonate/filter"

    BOKEH_SHAPES = ["circular", "hexagonal", "octagonal"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.5,
                }),
                "bokeh_shape": (cls.BOKEH_SHAPES, {
                    "default": "circular",
                }),
                "aspect_ratio": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                }),
                "quality": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "defocus"

    def defocus(
        self,
        image: torch.Tensor,
        size: float,
        bokeh_shape: str,
        aspect_ratio: float,
        quality: int
    ) -> tuple:
        """
        Apply lens-style defocus blur.

        Args:
            image: Input tensor [B,H,W,C]
            size: Defocus radius (0-100)
            bokeh_shape: Kernel shape (circular, hexagonal, octagonal)
            aspect_ratio: Bokeh aspect ratio (0.1-10, 1=circular)
            quality: Sampling quality (1=fast, 5=best)

        Returns:
            Tuple containing defocused image [B,H,W,C]
        """
        validate_image_tensor(image)

        if size < 0.1:
            return (image,)

        # Ensure RGBA
        image_rgba = ensure_alpha_channel(image)

        # Create bokeh kernel
        kernel = self._create_bokeh_kernel(size, bokeh_shape, aspect_ratio, quality)

        # Apply convolution
        result = self._apply_bokeh_kernel(image_rgba, kernel)

        return (result,)

    def _create_bokeh_kernel(
        self,
        size: float,
        shape: str,
        aspect_ratio: float,
        quality: int
    ) -> torch.Tensor:
        """
        Create bokeh kernel based on shape and parameters.

        Args:
            size: Kernel radius
            shape: Bokeh shape
            aspect_ratio: Width/height ratio
            quality: Sampling quality (affects kernel size)

        Returns:
            2D kernel tensor
        """
        # Kernel size based on radius and quality
        kernel_radius = int(size * quality)
        kernel_size = kernel_radius * 2 + 1

        # Create coordinate grid
        y, x = torch.meshgrid(
            torch.arange(kernel_size, dtype=torch.float32) - kernel_radius,
            torch.arange(kernel_size, dtype=torch.float32) - kernel_radius,
            indexing='ij'
        )

        # Apply aspect ratio
        x = x / aspect_ratio

        if shape == "circular":
            # Circular aperture (disk)
            dist = torch.sqrt(x ** 2 + y ** 2)
            kernel = (dist <= size).float()

        elif shape == "hexagonal":
            # Hexagonal aperture (6 sides)
            kernel = self._hexagon_kernel(x, y, size)

        elif shape == "octagonal":
            # Octagonal aperture (8 sides)
            kernel = self._octagon_kernel(x, y, size)

        else:
            # Default to circular
            dist = torch.sqrt(x ** 2 + y ** 2)
            kernel = (dist <= size).float()

        # Normalize kernel
        kernel = kernel / (kernel.sum() + 1e-7)

        return kernel

    def _hexagon_kernel(self, x: torch.Tensor, y: torch.Tensor, size: float) -> torch.Tensor:
        """
        Create hexagonal bokeh kernel (6-blade aperture).
        """
        # Hexagon can be defined as intersection of 3 pairs of parallel lines
        # rotated by 60 degrees

        # Convert to polar coordinates
        r = torch.sqrt(x ** 2 + y ** 2)
        theta = torch.atan2(y, x)

        # Hexagon distance function
        # A hexagon is 6 sides, each 60 degrees apart
        # For each angle, check if point is inside
        angle_step = math.pi / 3  # 60 degrees

        # Distance to hexagon edge at current angle
        # Hexagon formula: r ≤ size / cos(theta mod 60°)
        angle_mod = torch.abs((theta % (2 * angle_step)) - angle_step)
        max_r = size / torch.cos(angle_mod)

        kernel = (r <= max_r).float()

        return kernel

    def _octagon_kernel(self, x: torch.Tensor, y: torch.Tensor, size: float) -> torch.Tensor:
        """
        Create octagonal bokeh kernel (8-blade aperture).
        """
        # Octagon: 8 sides, 45 degrees apart
        r = torch.sqrt(x ** 2 + y ** 2)
        theta = torch.atan2(y, x)

        angle_step = math.pi / 4  # 45 degrees

        angle_mod = torch.abs((theta % (2 * angle_step)) - angle_step)
        max_r = size / torch.cos(angle_mod)

        kernel = (r <= max_r).float()

        return kernel

    def _apply_bokeh_kernel(
        self,
        image: torch.Tensor,
        kernel: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply bokeh kernel via convolution.

        Args:
            image: RGBA image [B,H,W,4]
            kernel: 2D kernel [K,K]

        Returns:
            Blurred image [B,H,W,4]
        """
        B, H, W, C = image.shape

        # Convert to NCHW
        image_nchw = image.permute(0, 3, 1, 2)

        # Expand kernel for each channel: [C, 1, K, K]
        kernel_expanded = kernel.unsqueeze(0).unsqueeze(0).repeat(C, 1, 1, 1)
        kernel_expanded = kernel_expanded.to(image.device)

        # Calculate padding
        kernel_size = kernel.shape[0]
        padding = kernel_size // 2

        # Apply convolution (grouped by channel)
        blurred = F.conv2d(
            image_nchw,
            kernel_expanded,
            padding=padding,
            groups=C
        )

        # Convert back to BHWC
        return blurred.permute(0, 2, 3, 1)
