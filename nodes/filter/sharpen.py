"""
Sharpen node for ComfyUI_Detonate.

Enhance edge detail using unsharp mask technique. Industry-standard
sharpening for recovering detail from soft renders and matching sharp footage.

Based on classic unsharp mask algorithm with improvements:
- Luminance-only sharpening mode
- Threshold for noise suppression
- Clamp option for clean output

Reference: Unsharp masking - https://en.wikipedia.org/wiki/Unsharp_masking
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor, ensure_alpha_channel, calculate_luminance


class DetonateSharpen:
    """
    Enhance edge detail using unsharp mask technique.

    Classic formula: sharpened = original + (original - blurred) × amount

    Extracts high-frequency detail by subtracting a blurred version,
    then adds it back with a multiplier to enhance edges.

    Common uses:
    - Recover soft renders from CG
    - Enhance texture detail in materials
    - Pre-sharpen before upscaling
    - Match sharp camera plates
    - Bring back detail after blur operations

    Improvements over Nuke:
    - Luminance-only mode (avoid color fringing)
    - Threshold control (suppress noise)
    - Channel selection
    """

    CATEGORY = "detonate/filter"

    CHANNEL_OPTIONS = ["rgb", "rgba", "luminance", "alpha"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 5.0,
                    "step": 0.1,
                }),
                "amount": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 5.0,
                    "step": 0.1,
                }),
                "threshold": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 0.5,
                    "step": 0.01,
                }),
                "channels": (cls.CHANNEL_OPTIONS, {
                    "default": "luminance",
                }),
                "clamp": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "sharpen"

    def sharpen(
        self,
        image: torch.Tensor,
        size: float,
        amount: float,
        threshold: float,
        channels: str,
        clamp: bool
    ) -> tuple:
        """
        Apply unsharp mask sharpening.

        Args:
            image: Input tensor [B,H,W,C]
            size: Blur radius for detection (0.5-5)
            amount: Sharpening intensity (0-5)
            threshold: Noise suppression threshold (0-0.5)
            channels: Which channels to sharpen
            clamp: Clamp output to 0-1 range

        Returns:
            Tuple containing sharpened image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Ensure RGBA
        image_rgba = ensure_alpha_channel(image)

        # If amount is zero, return original
        if amount < 0.01:
            return (image_rgba,)

        # Apply sharpening based on channel mode
        if channels == "luminance":
            result = self._sharpen_luminance(image_rgba, size, amount, threshold)
        elif channels == "alpha":
            result = self._sharpen_alpha(image_rgba, size, amount, threshold)
        elif channels == "rgb":
            result = self._sharpen_rgb(image_rgba, size, amount, threshold)
        else:  # rgba
            result = self._sharpen_rgba(image_rgba, size, amount, threshold)

        # Optional clamping
        if clamp:
            result = torch.clamp(result, 0.0, 1.0)

        return (result,)

    def _sharpen_luminance(
        self,
        image: torch.Tensor,
        size: float,
        amount: float,
        threshold: float
    ) -> torch.Tensor:
        """
        Sharpen luminance only (avoid color artifacts).

        This is often the best mode - sharpens detail without
        creating color fringing.
        """
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        # Calculate luminance
        luma = calculate_luminance(image)

        # Blur luminance
        blurred_luma = self._gaussian_blur(luma, size)

        # Extract detail
        detail = luma - blurred_luma

        # Apply threshold (suppress noise)
        if threshold > 0:
            detail_mask = (torch.abs(detail) > threshold).float()
            detail = detail * detail_mask

        # Add detail back to luminance
        sharpened_luma = luma + detail * amount

        # Apply luminance change to RGB
        luma_ratio = sharpened_luma / (luma + 1e-7)
        sharpened_rgb = rgb * luma_ratio

        return torch.cat([sharpened_rgb, alpha], dim=3)

    def _sharpen_rgb(
        self,
        image: torch.Tensor,
        size: float,
        amount: float,
        threshold: float
    ) -> torch.Tensor:
        """
        Sharpen RGB channels independently.
        """
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        # Blur RGB
        blurred = self._gaussian_blur(rgb, size)

        # Extract detail
        detail = rgb - blurred

        # Apply threshold
        if threshold > 0:
            detail_mask = (torch.abs(detail) > threshold).float()
            detail = detail * detail_mask

        # Add detail back
        sharpened = rgb + detail * amount

        return torch.cat([sharpened, alpha], dim=3)

    def _sharpen_alpha(
        self,
        image: torch.Tensor,
        size: float,
        amount: float,
        threshold: float
    ) -> torch.Tensor:
        """
        Sharpen alpha channel only.
        """
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        # Blur alpha
        blurred = self._gaussian_blur(alpha, size)

        # Extract detail
        detail = alpha - blurred

        # Apply threshold
        if threshold > 0:
            detail_mask = (torch.abs(detail) > threshold).float()
            detail = detail * detail_mask

        # Add detail back
        sharpened_alpha = alpha + detail * amount

        return torch.cat([rgb, sharpened_alpha], dim=3)

    def _sharpen_rgba(
        self,
        image: torch.Tensor,
        size: float,
        amount: float,
        threshold: float
    ) -> torch.Tensor:
        """
        Sharpen all channels including alpha.
        """
        # Blur entire image
        blurred = self._gaussian_blur(image, size)

        # Extract detail
        detail = image - blurred

        # Apply threshold
        if threshold > 0:
            detail_mask = (torch.abs(detail) > threshold).float()
            detail = detail * detail_mask

        # Add detail back
        sharpened = image + detail * amount

        return sharpened

    def _gaussian_blur(self, image: torch.Tensor, size: float) -> torch.Tensor:
        """
        Apply Gaussian blur using separable convolution.

        Args:
            image: Tensor [B,H,W,C]
            size: Blur radius

        Returns:
            Blurred image
        """
        B, H, W, C = image.shape

        # Convert to NCHW
        image_nchw = image.permute(0, 3, 1, 2)

        # Create Gaussian kernel
        kernel_size = int(size * 4) + 1
        if kernel_size % 2 == 0:
            kernel_size += 1

        kernel_size = max(3, kernel_size)
        sigma = size / 2.0

        # 1D Gaussian
        x = torch.arange(kernel_size, dtype=torch.float32, device=image.device) - (kernel_size - 1) / 2
        gaussian_1d = torch.exp(-x ** 2 / (2 * sigma ** 2))
        gaussian_1d = gaussian_1d / gaussian_1d.sum()

        # Create kernels for each channel
        kernel_h = gaussian_1d.view(1, 1, -1).repeat(C, 1, 1)
        kernel_v = gaussian_1d.view(1, 1, -1).repeat(C, 1, 1)

        padding = kernel_size // 2

        # Horizontal blur
        blurred_h = F.conv2d(
            image_nchw,
            kernel_h.unsqueeze(2),
            padding=(0, padding),
            groups=C
        )

        # Vertical blur
        blurred = F.conv2d(
            blurred_h,
            kernel_v.unsqueeze(3),
            padding=(padding, 0),
            groups=C
        )

        # Convert back to BHWC
        return blurred.permute(0, 2, 3, 1)
