"""
Blur node for ComfyUI_Detonate.

Applies Gaussian blur to images with separate X/Y control.
Essential for softening, glows, depth of field effects.

Reference: Nuke Blur node, Natron CImgBlur.cpp
https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/blur.html
https://github.com/NatronGitHub/openfx-misc/blob/master/CImg/Blur/CImgBlur.cpp
"""

import torch
import torch.nn.functional as F
import math
from ...utils import validate_image_tensor


class DetonateBlur:
    """
    Gaussian blur with separate X/Y size control.

    Applies a two-pass separable Gaussian blur (horizontal then vertical)
    for optimal performance. Supports float images with full precision.

    Formula: Gaussian kernel G(x) = (1/(σ*sqrt(2π))) * exp(-(x²/(2σ²)))

    Common uses:
    - Softening edges
    - Creating glows
    - Defocus effects
    - Matte softening

    Nuke/Fusion equivalent: Blur node
    """

    CATEGORY = "detonate/filter"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size_x": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.0,
                    "max": 1000.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "size_y": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.0,
                    "max": 1000.0,
                    "step": 0.1,
                    "display": "slider",
                }),
            },
            "optional": {
                "blur_alpha": ("BOOLEAN", {
                    "default": True,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "blur"

    def blur(
        self,
        image: torch.Tensor,
        size_x: float,
        size_y: float,
        blur_alpha: bool = True
    ) -> tuple:
        """
        Apply Gaussian blur to image.

        Args:
            image: Input tensor [B,H,W,C]
            size_x: Horizontal blur radius in pixels
            size_y: Vertical blur radius in pixels
            blur_alpha: Whether to blur alpha channel

        Returns:
            Tuple containing blurred image [B,H,W,C]
        """
        validate_image_tensor(image)

        # Early exit if no blur
        if size_x == 0.0 and size_y == 0.0:
            return (image,)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Convert to [B,C,H,W] for processing
        image_nchw = image.permute(0, 3, 1, 2)

        # Determine which channels to blur
        if has_alpha and not blur_alpha:
            # Blur RGB only, preserve alpha
            rgb = image_nchw[:, :3, :, :]
            alpha = image_nchw[:, 3:4, :, :]

            blurred_rgb = self._apply_gaussian_blur(rgb, size_x, size_y)
            result_nchw = torch.cat([blurred_rgb, alpha], dim=1)
        else:
            # Blur all channels
            result_nchw = self._apply_gaussian_blur(image_nchw, size_x, size_y)

        # Convert back to [B,H,W,C]
        result = result_nchw.permute(0, 2, 3, 1)

        return (result,)

    def _apply_gaussian_blur(
        self,
        image_nchw: torch.Tensor,
        size_x: float,
        size_y: float
    ) -> torch.Tensor:
        """
        Apply separable Gaussian blur to image in NCHW format.

        Args:
            image_nchw: Image tensor [B,C,H,W]
            size_x: Horizontal blur radius
            size_y: Vertical blur radius

        Returns:
            Blurred image [B,C,H,W]
        """
        result = image_nchw

        # Apply horizontal blur
        if size_x > 0.0:
            kernel_size_x = self._calculate_kernel_size(size_x)
            if kernel_size_x > 1:
                # Ensure odd kernel size
                kernel_size_x = kernel_size_x if kernel_size_x % 2 == 1 else kernel_size_x + 1
                sigma_x = size_x / 2.0  # Approximate sigma from size

                # Create 1D Gaussian kernel for horizontal
                kernel_x = self._create_gaussian_kernel_1d(kernel_size_x, sigma_x)
                kernel_x = kernel_x.to(result.device).to(result.dtype)

                # Apply horizontal blur
                result = self._convolve_1d(result, kernel_x, dim=3)  # dim=3 is width

        # Apply vertical blur
        if size_y > 0.0:
            kernel_size_y = self._calculate_kernel_size(size_y)
            if kernel_size_y > 1:
                # Ensure odd kernel size
                kernel_size_y = kernel_size_y if kernel_size_y % 2 == 1 else kernel_size_y + 1
                sigma_y = size_y / 2.0  # Approximate sigma from size

                # Create 1D Gaussian kernel for vertical
                kernel_y = self._create_gaussian_kernel_1d(kernel_size_y, sigma_y)
                kernel_y = kernel_y.to(result.device).to(result.dtype)

                # Apply vertical blur
                result = self._convolve_1d(result, kernel_y, dim=2)  # dim=2 is height

        return result

    def _calculate_kernel_size(self, size: float) -> int:
        """
        Calculate kernel size from blur size.
        Rule of thumb: kernel should be at least 6*sigma (3*sigma on each side)

        Args:
            size: Blur size (radius)

        Returns:
            Kernel size (odd integer)
        """
        sigma = size / 2.0
        kernel_size = int(math.ceil(sigma * 6))

        # Ensure minimum size of 1
        kernel_size = max(1, kernel_size)

        # Ensure odd
        if kernel_size % 2 == 0:
            kernel_size += 1

        return kernel_size

    def _create_gaussian_kernel_1d(self, kernel_size: int, sigma: float) -> torch.Tensor:
        """
        Create 1D Gaussian kernel.

        Args:
            kernel_size: Size of kernel (odd integer)
            sigma: Standard deviation

        Returns:
            Gaussian kernel [kernel_size]
        """
        # Create coordinate grid
        coords = torch.arange(kernel_size, dtype=torch.float32)
        coords = coords - (kernel_size - 1) / 2.0

        # Calculate Gaussian
        # G(x) = (1/(σ*sqrt(2π))) * exp(-(x²/(2σ²)))
        gaussian = torch.exp(-(coords ** 2) / (2 * sigma ** 2))

        # Normalize
        gaussian = gaussian / gaussian.sum()

        return gaussian

    def _convolve_1d(
        self,
        image: torch.Tensor,
        kernel: torch.Tensor,
        dim: int
    ) -> torch.Tensor:
        """
        Apply 1D convolution along specified dimension.

        Args:
            image: Input image [B,C,H,W]
            kernel: 1D kernel [K]
            dim: Dimension to convolve (2=height, 3=width)

        Returns:
            Convolved image [B,C,H,W]
        """
        B, C, H, W = image.shape
        kernel_size = kernel.shape[0]
        padding = kernel_size // 2

        # Reshape kernel for conv2d
        if dim == 3:  # Horizontal (width)
            # Kernel shape: [C, 1, 1, K]
            kernel_2d = kernel.view(1, 1, 1, kernel_size).repeat(C, 1, 1, 1)
            pad = (padding, padding, 0, 0)  # (left, right, top, bottom)
        else:  # Vertical (height)
            # Kernel shape: [C, 1, K, 1]
            kernel_2d = kernel.view(1, 1, kernel_size, 1).repeat(C, 1, 1, 1)
            pad = (0, 0, padding, padding)  # (left, right, top, bottom)

        # Pad image
        image_padded = F.pad(image, pad, mode='reflect')

        # Apply convolution (groups=C for channel-wise convolution)
        result = F.conv2d(image_padded, kernel_2d, groups=C)

        return result
