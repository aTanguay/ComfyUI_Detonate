"""
Glow node for ComfyUI_Detonate.

Add luminous glow effect to bright areas. Multi-scale bloom with
threshold control for professional light effects.

Based on Nuke Glow and Natron Bloom implementations, with improvements:
- Adaptive threshold
- Saturation boost in glow
- Better blur falloff
- Optional masking

Reference: Masaki Kawase, "Practical Implementation of High Dynamic Range Rendering", GDC 2004
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor, ensure_alpha_channel, calculate_luminance


class DetonateGlow:
    """
    Add luminous glow effect to bright areas of an image.

    Uses multi-scale Gaussian blur with geometric progression to create
    realistic bloom/glow effects. Essential for light rays, magic effects,
    UI elements, and highlight enhancement.

    Common uses:
    - Light rays and sun glows
    - Magic spells and energy effects
    - Glowing UI elements and holograms
    - Headlight bloom and lens flares
    - Sci-fi laser beams

    Improvements over Nuke/Natron:
    - Saturation boost for more vibrant glow
    - Better threshold falloff
    - Optional mask input
    """

    CATEGORY = "detonate/filter"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("FLOAT", {
                    "default": 10.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                }),
                "threshold": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "intensity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 5.0,
                    "step": 0.1,
                }),
                "iterations": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                }),
                "ratio": ("FLOAT", {
                    "default": 2.0,
                    "min": 1.0,
                    "max": 3.0,
                    "step": 0.1,
                }),
                "saturation_boost": ("FLOAT", {
                    "default": 1.1,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05,
                }),
            },
            "optional": {
                "mask": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_glow"

    def apply_glow(
        self,
        image: torch.Tensor,
        size: float,
        threshold: float,
        intensity: float,
        iterations: int,
        ratio: float,
        saturation_boost: float,
        mask: torch.Tensor = None
    ) -> tuple:
        """
        Apply glow effect to image.

        Args:
            image: Input tensor [B,H,W,C]
            size: Glow radius (0-100)
            threshold: Brightness threshold (0-1)
            intensity: Glow strength multiplier (0-5)
            iterations: Number of blur passes (1-10)
            ratio: Blur size progression (1-3)
            saturation_boost: Boost glow saturation (0-2)
            mask: Optional mask to limit glow regions

        Returns:
            Tuple containing glowing image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Ensure RGBA
        image_rgba = ensure_alpha_channel(image)

        # Extract RGB
        rgb = image_rgba[:, :, :, :3]
        alpha = image_rgba[:, :, :, 3:4]

        # If size is too small, return original
        if size < 0.1:
            return (image_rgba,)

        # Calculate luminance for thresholding
        luminance = calculate_luminance(image_rgba)

        # Create threshold mask (smooth falloff)
        if threshold >= 1.0:
            # Nothing bright enough, return original
            return (image_rgba,)

        # Smooth threshold with falloff
        threshold_mask = torch.clamp((luminance - threshold) / (1.0 - threshold + 1e-7), 0.0, 1.0)

        # Extract bright pixels
        bright_pixels = rgb * threshold_mask

        # Boost saturation in glow if requested
        if saturation_boost != 1.0:
            bright_pixels = self._adjust_saturation(bright_pixels, saturation_boost)

        # Multi-scale blur accumulation (geometric progression)
        glow_accumulator = torch.zeros_like(rgb)

        for i in range(iterations):
            # Calculate blur size for this iteration
            current_size = size * (ratio ** i)

            # Apply Gaussian blur
            blurred = self._gaussian_blur(bright_pixels, current_size)

            # Accumulate with equal weight
            glow_accumulator += blurred / iterations

        # Apply intensity
        glow = glow_accumulator * intensity

        # Apply optional mask
        if mask is not None:
            validate_image_tensor(mask)
            # Resize mask to match image if needed
            if mask.shape[1:3] != (H, W):
                mask = F.interpolate(
                    mask.permute(0, 3, 1, 2),
                    size=(H, W),
                    mode='bilinear',
                    align_corners=False
                ).permute(0, 2, 3, 1)

            # Use mask luminance as strength
            mask_strength = calculate_luminance(ensure_alpha_channel(mask))
            glow = glow * mask_strength

        # Composite glow over original (additive)
        result_rgb = rgb + glow

        # Combine with original alpha
        result = torch.cat([result_rgb, alpha], dim=3)

        return (result,)

    def _gaussian_blur(self, image: torch.Tensor, size: float) -> torch.Tensor:
        """
        Apply Gaussian blur using separable convolution.

        Args:
            image: RGB tensor [B,H,W,3]
            size: Blur radius

        Returns:
            Blurred image
        """
        if size < 0.1:
            return image

        # Convert to NCHW for PyTorch conv
        image_nchw = image.permute(0, 3, 1, 2)  # [B,3,H,W]

        # Create Gaussian kernel
        kernel_size = int(size * 4) + 1  # Ensure odd size
        if kernel_size % 2 == 0:
            kernel_size += 1

        kernel_size = max(3, kernel_size)  # Minimum size 3
        sigma = size / 2.0

        # 1D Gaussian kernel
        x = torch.arange(kernel_size, dtype=torch.float32, device=image.device) - (kernel_size - 1) / 2
        gaussian_1d = torch.exp(-x ** 2 / (2 * sigma ** 2))
        gaussian_1d = gaussian_1d / gaussian_1d.sum()

        # Reshape for conv1d: [out_channels, in_channels/groups, kernel_size]
        kernel_h = gaussian_1d.view(1, 1, -1).repeat(3, 1, 1)  # [3,1,K]
        kernel_v = gaussian_1d.view(1, 1, -1).repeat(3, 1, 1)  # [3,1,K]

        padding = kernel_size // 2

        # Horizontal blur
        blurred_h = F.conv2d(
            image_nchw,
            kernel_h.unsqueeze(2),  # [3,1,1,K]
            padding=(0, padding),
            groups=3
        )

        # Vertical blur
        blurred = F.conv2d(
            blurred_h,
            kernel_v.unsqueeze(3),  # [3,1,K,1]
            padding=(padding, 0),
            groups=3
        )

        # Convert back to BHWC
        return blurred.permute(0, 2, 3, 1)

    def _adjust_saturation(self, rgb: torch.Tensor, saturation: float) -> torch.Tensor:
        """
        Adjust saturation of RGB image.

        Args:
            rgb: RGB tensor [B,H,W,3]
            saturation: Saturation multiplier (0-2)

        Returns:
            Saturation-adjusted RGB
        """
        # Calculate luminance
        luma = rgb[:, :, :, 0:1] * 0.299 + rgb[:, :, :, 1:2] * 0.587 + rgb[:, :, :, 2:3] * 0.114

        # Interpolate between grayscale and original
        # saturation=0 -> grayscale, saturation=1 -> original, saturation>1 -> boosted
        result = luma + (rgb - luma) * saturation

        return result
