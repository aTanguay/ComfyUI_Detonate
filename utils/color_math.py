"""
Color mathematics utilities for ComfyUI_Detonate.

Provides color space conversions, color correction operations,
and mathematical functions for color manipulation.
"""

import torch
from typing import Tuple
from .tensor_utils import validate_image_tensor


def rgb_to_hsv(rgb: torch.Tensor) -> torch.Tensor:
    """
    Convert RGB to HSV color space.

    Args:
        rgb: Input tensor [B,H,W,3] or [B,H,W,4] (alpha ignored)

    Returns:
        HSV tensor [B,H,W,3] where H=[0,1], S=[0,1], V=[0,1]
        If input has alpha (C=4), returns [B,H,W,4] with alpha preserved
    """
    validate_image_tensor(rgb)

    has_alpha = rgb.shape[3] == 4

    if has_alpha:
        alpha = rgb[:, :, :, 3:4]
        rgb = rgb[:, :, :, :3]

    r = rgb[:, :, :, 0]
    g = rgb[:, :, :, 1]
    b = rgb[:, :, :, 2]

    max_val, max_idx = torch.max(rgb, dim=3)
    min_val, _ = torch.min(rgb, dim=3)
    diff = max_val - min_val

    # Hue calculation
    hue = torch.zeros_like(max_val)

    # Where diff != 0
    mask = diff != 0

    # Red is max
    r_mask = mask & (max_idx == 0)
    hue = torch.where(
        r_mask,
        ((g - b) / (diff + 1e-10)) % 6,
        hue
    )

    # Green is max
    g_mask = mask & (max_idx == 1)
    hue = torch.where(
        g_mask,
        ((b - r) / (diff + 1e-10)) + 2,
        hue
    )

    # Blue is max
    b_mask = mask & (max_idx == 2)
    hue = torch.where(
        b_mask,
        ((r - g) / (diff + 1e-10)) + 4,
        hue
    )

    hue = hue / 6.0  # Normalize to [0, 1]

    # Saturation calculation
    saturation = torch.where(
        max_val != 0,
        diff / (max_val + 1e-10),
        torch.zeros_like(max_val)
    )

    # Value is just max
    value = max_val

    # Stack HSV
    hsv = torch.stack([hue, saturation, value], dim=3)

    if has_alpha:
        hsv = torch.cat([hsv, alpha], dim=3)

    return hsv


def hsv_to_rgb(hsv: torch.Tensor) -> torch.Tensor:
    """
    Convert HSV to RGB color space.

    Args:
        hsv: Input tensor [B,H,W,3] or [B,H,W,4] (alpha preserved)
             H=[0,1], S=[0,1], V=[0,1]

    Returns:
        RGB tensor [B,H,W,3] or [B,H,W,4] if input had alpha
    """
    validate_image_tensor(hsv)

    has_alpha = hsv.shape[3] == 4

    if has_alpha:
        alpha = hsv[:, :, :, 3:4]
        hsv = hsv[:, :, :, :3]

    h = hsv[:, :, :, 0] * 6.0  # Scale hue to [0, 6]
    s = hsv[:, :, :, 1]
    v = hsv[:, :, :, 2]

    c = v * s
    x = c * (1 - torch.abs((h % 2) - 1))
    m = v - c

    # Initialize RGB
    rgb = torch.zeros_like(hsv)

    # Determine RGB based on hue sector
    mask0 = (h >= 0) & (h < 1)
    mask1 = (h >= 1) & (h < 2)
    mask2 = (h >= 2) & (h < 3)
    mask3 = (h >= 3) & (h < 4)
    mask4 = (h >= 4) & (h < 5)
    mask5 = (h >= 5) & (h < 6)

    # Sector 0: [c, x, 0]
    rgb[:, :, :, 0] = torch.where(mask0, c, rgb[:, :, :, 0])
    rgb[:, :, :, 1] = torch.where(mask0, x, rgb[:, :, :, 1])

    # Sector 1: [x, c, 0]
    rgb[:, :, :, 0] = torch.where(mask1, x, rgb[:, :, :, 0])
    rgb[:, :, :, 1] = torch.where(mask1, c, rgb[:, :, :, 1])

    # Sector 2: [0, c, x]
    rgb[:, :, :, 1] = torch.where(mask2, c, rgb[:, :, :, 1])
    rgb[:, :, :, 2] = torch.where(mask2, x, rgb[:, :, :, 2])

    # Sector 3: [0, x, c]
    rgb[:, :, :, 1] = torch.where(mask3, x, rgb[:, :, :, 1])
    rgb[:, :, :, 2] = torch.where(mask3, c, rgb[:, :, :, 2])

    # Sector 4: [x, 0, c]
    rgb[:, :, :, 0] = torch.where(mask4, x, rgb[:, :, :, 0])
    rgb[:, :, :, 2] = torch.where(mask4, c, rgb[:, :, :, 2])

    # Sector 5: [c, 0, x]
    rgb[:, :, :, 0] = torch.where(mask5, c, rgb[:, :, :, 0])
    rgb[:, :, :, 2] = torch.where(mask5, x, rgb[:, :, :, 2])

    # Add m to all channels
    rgb = rgb + m.unsqueeze(3)

    if has_alpha:
        rgb = torch.cat([rgb, alpha], dim=3)

    return rgb


def adjust_saturation(
    image: torch.Tensor,
    saturation: float = 1.0
) -> torch.Tensor:
    """
    Adjust image saturation.

    Args:
        image: Input tensor [B,H,W,C]
        saturation: Saturation multiplier
                   0.0 = grayscale
                   1.0 = no change
                   >1.0 = increased saturation

    Returns:
        Saturation-adjusted image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape
    has_alpha = C == 4

    # Convert to HSV
    hsv = rgb_to_hsv(image)

    # Adjust saturation
    if has_alpha:
        hsv[:, :, :, 1] = hsv[:, :, :, 1] * saturation
        hsv[:, :, :, 1] = torch.clamp(hsv[:, :, :, 1], 0.0, 1.0)
    else:
        hsv[:, :, :, 1] = hsv[:, :, :, 1] * saturation
        hsv[:, :, :, 1] = torch.clamp(hsv[:, :, :, 1], 0.0, 1.0)

    # Convert back to RGB
    return hsv_to_rgb(hsv)


def adjust_contrast(
    image: torch.Tensor,
    contrast: float = 1.0,
    pivot: float = 0.5
) -> torch.Tensor:
    """
    Adjust image contrast around a pivot point.

    Formula: result = (input - pivot) * contrast + pivot

    Args:
        image: Input tensor [B,H,W,C]
        contrast: Contrast multiplier
                 <1.0 = reduced contrast
                 1.0 = no change
                 >1.0 = increased contrast
        pivot: Pivot point (default 0.5 = middle gray)

    Returns:
        Contrast-adjusted image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    # Preserve alpha
    if C == 4:
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        adjusted_rgb = (rgb - pivot) * contrast + pivot

        return torch.cat([adjusted_rgb, alpha], dim=3)
    else:
        return (image - pivot) * contrast + pivot


def apply_gamma(
    image: torch.Tensor,
    gamma: float = 1.0,
    epsilon: float = 1e-10
) -> torch.Tensor:
    """
    Apply gamma correction to image.

    Formula: result = pow(input, 1/gamma)

    Args:
        image: Input tensor [B,H,W,C]
        gamma: Gamma value
              <1.0 = darken
              1.0 = no change
              >1.0 = brighten
        epsilon: Small value to prevent negative inputs to pow

    Returns:
        Gamma-corrected image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    if gamma <= 0:
        gamma = max(epsilon, gamma)  # Prevent invalid gamma

    # Preserve alpha
    if C == 4:
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        # Ensure non-negative values for pow
        rgb = torch.clamp(rgb, min=0.0)

        # Apply gamma
        corrected_rgb = torch.pow(rgb + epsilon, 1.0 / gamma)

        return torch.cat([corrected_rgb, alpha], dim=3)
    else:
        # Ensure non-negative values for pow
        image = torch.clamp(image, min=0.0)
        return torch.pow(image + epsilon, 1.0 / gamma)


def apply_gain(
    image: torch.Tensor,
    gain: float = 1.0
) -> torch.Tensor:
    """
    Apply gain (multiply) to image.

    Formula: result = input * gain

    Args:
        image: Input tensor [B,H,W,C]
        gain: Gain multiplier

    Returns:
        Gain-adjusted image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    # Preserve alpha
    if C == 4:
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        adjusted_rgb = rgb * gain

        return torch.cat([adjusted_rgb, alpha], dim=3)
    else:
        return image * gain


def apply_offset(
    image: torch.Tensor,
    offset: float = 0.0
) -> torch.Tensor:
    """
    Apply offset (add) to image.

    Formula: result = input + offset

    Args:
        image: Input tensor [B,H,W,C]
        offset: Offset value

    Returns:
        Offset-adjusted image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    # Preserve alpha
    if C == 4:
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        adjusted_rgb = rgb + offset

        return torch.cat([adjusted_rgb, alpha], dim=3)
    else:
        return image + offset


def apply_lift(
    image: torch.Tensor,
    lift: float = 0.0
) -> torch.Tensor:
    """
    Apply lift to image (affects shadows most).

    Fusion formula: Lift scales color values around white.
    A lift of 0.5 makes black (0) -> 0.5, while white (1) remains 1.

    Approximation: result = input + lift * (1 - input)

    Args:
        image: Input tensor [B,H,W,C]
        lift: Lift value (typically 0.0 to 1.0)

    Returns:
        Lift-adjusted image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    # Preserve alpha
    if C == 4:
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        # Lift affects shadows more than highlights
        adjusted_rgb = rgb + lift * (1.0 - rgb)

        return torch.cat([adjusted_rgb, alpha], dim=3)
    else:
        return image + lift * (1.0 - image)


def lerp(
    a: torch.Tensor,
    b: torch.Tensor,
    t: float
) -> torch.Tensor:
    """
    Linear interpolation between two tensors.

    Formula: result = a * (1 - t) + b * t

    Args:
        a: First tensor
        b: Second tensor
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated tensor
    """
    return a * (1.0 - t) + b * t


def clamp_color(
    image: torch.Tensor,
    min_val: float = 0.0,
    max_val: float = 1.0,
    clamp_alpha: bool = True
) -> torch.Tensor:
    """
    Clamp color values to specified range.

    Args:
        image: Input tensor [B,H,W,C]
        min_val: Minimum value
        max_val: Maximum value
        clamp_alpha: Whether to clamp alpha channel (default True)

    Returns:
        Clamped image
    """
    validate_image_tensor(image)

    B, H, W, C = image.shape

    if C == 4 and not clamp_alpha:
        rgb = image[:, :, :, :3]
        alpha = image[:, :, :, 3:4]

        clamped_rgb = torch.clamp(rgb, min_val, max_val)

        return torch.cat([clamped_rgb, alpha], dim=3)
    else:
        return torch.clamp(image, min_val, max_val)
