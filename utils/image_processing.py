"""
Image processing utilities for ComfyUI_Detonate.

Provides common image operations like premultiplication, alpha handling,
and basic image manipulations.
"""

import torch
from typing import Tuple
from .tensor_utils import (
    validate_image_tensor,
    ensure_alpha_channel,
    get_alpha_channel,
    set_alpha_channel,
    clamp_tensor
)


def premultiply_alpha(
    image: torch.Tensor,
    epsilon: float = 1e-7
) -> torch.Tensor:
    """
    Premultiply RGB channels by alpha channel.
    Converts from straight alpha to premultiplied alpha.

    Formula: result.rgb = input.rgb * input.alpha

    Args:
        image: Input tensor [B,H,W,C] where C=4 (RGBA)
        epsilon: Not used for premultiply (kept for API consistency)

    Returns:
        Premultiplied image [B,H,W,4]

    Raises:
        ValueError: If input doesn't have alpha channel (C!=4)
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    if C != 4:
        raise ValueError(
            f"Premultiply requires RGBA image (C=4), got C={C}. "
            "Use ensure_alpha_channel() first if needed."
        )

    rgb = image[:, :, :, :3]
    alpha = image[:, :, :, 3:4]

    # Multiply RGB by alpha
    premult_rgb = rgb * alpha

    # Concatenate with alpha (unchanged)
    return torch.cat([premult_rgb, alpha], dim=3)


def unpremultiply_alpha(
    image: torch.Tensor,
    epsilon: float = 1e-7,
    clamp_output: bool = False,
    max_value: float = 10.0
) -> torch.Tensor:
    """
    Unpremultiply RGB channels by alpha channel.
    Converts from premultiplied alpha to straight alpha.

    Formula: result.rgb = input.rgb / (input.alpha + epsilon)

    Args:
        image: Input tensor [B,H,W,C] where C=4 (RGBA)
        epsilon: Small value to prevent division by zero (default 1e-7)
        clamp_output: Whether to clamp RGB to max_value (default False)
        max_value: Maximum RGB value if clamping (default 10.0)

    Returns:
        Unpremultiplied image [B,H,W,4]

    Raises:
        ValueError: If input doesn't have alpha channel (C!=4)
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    if C != 4:
        raise ValueError(
            f"Unpremultiply requires RGBA image (C=4), got C={C}. "
            "Use ensure_alpha_channel() first if needed."
        )

    rgb = image[:, :, :, :3]
    alpha = image[:, :, :, 3:4]

    # Divide RGB by alpha (with epsilon to prevent division by zero)
    unpremult_rgb = rgb / (alpha + epsilon)

    # Optional: clamp to prevent extreme values
    if clamp_output:
        unpremult_rgb = torch.clamp(unpremult_rgb, 0.0, max_value)

    # Concatenate with alpha (unchanged)
    return torch.cat([unpremult_rgb, alpha], dim=3)


def calculate_luminance(
    image: torch.Tensor,
    coefficients: Tuple[float, float, float] = (0.2126, 0.7152, 0.0722)
) -> torch.Tensor:
    """
    Calculate luminance from RGB image using specified coefficients.

    Default uses Rec. 709 coefficients:
    L = R * 0.2126 + G * 0.7152 + B * 0.0722

    Args:
        image: Input tensor [B,H,W,C] where C>=3
        coefficients: (R, G, B) coefficients (default: Rec. 709)

    Returns:
        Luminance tensor [B,H,W,1]
    """
    validate_image_tensor(image)

    r_coef, g_coef, b_coef = coefficients

    rgb = image[:, :, :, :3]
    r = rgb[:, :, :, 0:1]
    g = rgb[:, :, :, 1:2]
    b = rgb[:, :, :, 2:3]

    luminance = r * r_coef + g * g_coef + b * b_coef

    return luminance


def normalize_range(
    image: torch.Tensor,
    in_min: float = 0.0,
    in_max: float = 1.0,
    out_min: float = 0.0,
    out_max: float = 1.0
) -> torch.Tensor:
    """
    Normalize image from input range to output range.

    Formula: result = (image - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

    Args:
        image: Input tensor [B,H,W,C]
        in_min: Input range minimum (default 0.0)
        in_max: Input range maximum (default 1.0)
        out_min: Output range minimum (default 0.0)
        out_max: Output range maximum (default 1.0)

    Returns:
        Normalized image
    """
    validate_image_tensor(image)

    if in_max == in_min:
        raise ValueError("in_max must not equal in_min")

    # Normalize to 0-1
    normalized = (image - in_min) / (in_max - in_min)

    # Scale to output range
    result = normalized * (out_max - out_min) + out_min

    return result


def invert_image(
    image: torch.Tensor,
    invert_alpha: bool = False
) -> torch.Tensor:
    """
    Invert image colors (1.0 - value).

    Args:
        image: Input tensor [B,H,W,C]
        invert_alpha: Whether to invert alpha channel (default False)

    Returns:
        Inverted image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    if C == 3:
        # RGB only
        return 1.0 - image
    else:
        # RGBA
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        inverted_rgb = 1.0 - rgb
        inverted_alpha = (1.0 - alpha) if invert_alpha else alpha

        return torch.cat([inverted_rgb, inverted_alpha], dim=3)


def blend_images(
    fg: torch.Tensor,
    bg: torch.Tensor,
    mix: float = 1.0
) -> torch.Tensor:
    """
    Blend two images using linear interpolation.

    Formula: result = fg * mix + bg * (1 - mix)

    Args:
        fg: Foreground tensor [B,H,W,C]
        bg: Background tensor [B,H,W,C]
        mix: Blend factor 0.0-1.0 (default 1.0)

    Returns:
        Blended image

    Note:
        Images must have same dimensions. Use resize_tensors_to_match() if needed.
    """
    validate_image_tensor(fg, "foreground")
    validate_image_tensor(bg, "background")

    if fg.shape != bg.shape:
        raise ValueError(
            f"Foreground and background must have same shape. "
            f"Got fg={fg.shape}, bg={bg.shape}"
        )

    mix = max(0.0, min(1.0, mix))  # Clamp to 0-1

    return fg * mix + bg * (1.0 - mix)


def apply_mask(
    image: torch.Tensor,
    mask: torch.Tensor,
    invert_mask: bool = False
) -> torch.Tensor:
    """
    Apply mask to image (multiply).

    Args:
        image: Input tensor [B,H,W,C]
        mask: Mask tensor [B,H,W,1] or [B,H,W,C]
        invert_mask: Whether to invert mask (default False)

    Returns:
        Masked image

    Note:
        If mask is [B,H,W,1], it's broadcast to all channels.
        If mask is [B,H,W,C], channel-wise masking is applied.
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    # Validate mask shape
    if mask.dim() != 4:
        raise ValueError(f"Mask must be 4D tensor, got shape {mask.shape}")

    if mask.shape[:3] != (B, H, W):
        raise ValueError(
            f"Mask dimensions [B,H,W] must match image. "
            f"Got mask={mask.shape[:3]}, image={image.shape[:3]}"
        )

    mask_channels = mask.shape[3]
    if mask_channels != 1 and mask_channels != C:
        raise ValueError(
            f"Mask must have 1 or {C} channels, got {mask_channels}"
        )

    # Invert mask if requested
    if invert_mask:
        mask = 1.0 - mask

    # Apply mask
    return image * mask


def extract_channel(
    image: torch.Tensor,
    channel_index: int
) -> torch.Tensor:
    """
    Extract single channel from image as grayscale.

    Args:
        image: Input tensor [B,H,W,C]
        channel_index: Channel to extract (0=R, 1=G, 2=B, 3=A)

    Returns:
        Grayscale image [B,H,W,1]
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    if channel_index < 0 or channel_index >= C:
        raise ValueError(
            f"Channel index {channel_index} out of range for {C} channels"
        )

    return image[:, :, :, channel_index:channel_index+1]


def create_constant_image(
    batch_size: int,
    height: int,
    width: int,
    color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
    device: torch.device = torch.device("cpu"),
    dtype: torch.dtype = torch.float32
) -> torch.Tensor:
    """
    Create constant color image.

    Args:
        batch_size: Batch size
        height: Image height
        width: Image width
        color: RGBA color tuple (default black with alpha=1)
        device: Target device (default CPU)
        dtype: Data type (default float32)

    Returns:
        Constant color image [B,H,W,4]
    """
    r, g, b, a = color

    image = torch.zeros(
        (batch_size, height, width, 4),
        device=device,
        dtype=dtype
    )

    image[:, :, :, 0] = r
    image[:, :, :, 1] = g
    image[:, :, :, 2] = b
    image[:, :, :, 3] = a

    return image
