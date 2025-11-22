"""
Tensor utility functions for ComfyUI_Detonate.

Provides common tensor operations, type conversions, and validation
for working with ComfyUI IMAGE tensors.
"""

import torch
from typing import Tuple, Optional


def validate_image_tensor(tensor: torch.Tensor, name: str = "image") -> None:
    """
    Validate that a tensor matches ComfyUI IMAGE format.

    Args:
        tensor: Input tensor to validate
        name: Name for error messages

    Raises:
        ValueError: If tensor doesn't match expected format

    Expected format:
        - Shape: [B, H, W, C]
        - Type: torch.Tensor (Float32)
        - Range: 0.0 - 1.0
        - Channels: C=3 (RGB) or C=4 (RGBA)
    """
    if not isinstance(tensor, torch.Tensor):
        raise ValueError(f"{name} must be a torch.Tensor, got {type(tensor)}")

    if tensor.dim() != 4:
        raise ValueError(
            f"{name} must be 4D tensor [B,H,W,C], got shape {tensor.shape}"
        )

    B, H, W, C = tensor.shape

    if C not in [3, 4]:
        raise ValueError(
            f"{name} must have 3 (RGB) or 4 (RGBA) channels, got {C} channels"
        )

    if H < 1 or W < 1:
        raise ValueError(f"{name} dimensions must be >= 1, got H={H}, W={W}")


def ensure_alpha_channel(tensor: torch.Tensor, alpha_value: float = 1.0) -> torch.Tensor:
    """
    Ensure tensor has alpha channel (C=4).
    If input is C=3, adds alpha channel with specified value.

    Args:
        tensor: Input tensor [B,H,W,C] where C=3 or C=4
        alpha_value: Value for alpha channel if adding (default 1.0)

    Returns:
        Tensor with shape [B,H,W,4]
    """
    validate_image_tensor(tensor)

    B, H, W, C = tensor.shape

    if C == 4:
        return tensor

    # C == 3, add alpha channel
    alpha = torch.full((B, H, W, 1), alpha_value, dtype=tensor.dtype, device=tensor.device)
    return torch.cat([tensor, alpha], dim=3)


def remove_alpha_channel(tensor: torch.Tensor) -> torch.Tensor:
    """
    Remove alpha channel from tensor, returning only RGB.

    Args:
        tensor: Input tensor [B,H,W,C] where C=3 or C=4

    Returns:
        Tensor with shape [B,H,W,3]
    """
    validate_image_tensor(tensor)

    B, H, W, C = tensor.shape

    if C == 3:
        return tensor

    # C == 4, remove alpha channel
    return tensor[:, :, :, :3]


def get_alpha_channel(tensor: torch.Tensor) -> Optional[torch.Tensor]:
    """
    Extract alpha channel from tensor.

    Args:
        tensor: Input tensor [B,H,W,C] where C=3 or C=4

    Returns:
        Alpha channel [B,H,W,1] if C=4, None if C=3
    """
    validate_image_tensor(tensor)

    B, H, W, C = tensor.shape

    if C == 3:
        return None

    return tensor[:, :, :, 3:4]


def set_alpha_channel(tensor: torch.Tensor, alpha: torch.Tensor) -> torch.Tensor:
    """
    Replace alpha channel in tensor.

    Args:
        tensor: Input tensor [B,H,W,C] where C=4
        alpha: Alpha channel [B,H,W,1]

    Returns:
        Tensor with replaced alpha channel [B,H,W,4]
    """
    validate_image_tensor(tensor)

    B, H, W, C = tensor.shape

    if C != 4:
        raise ValueError(f"Tensor must have 4 channels to set alpha, got {C}")

    if alpha.shape != (B, H, W, 1):
        raise ValueError(
            f"Alpha must have shape [{B},{H},{W},1], got {alpha.shape}"
        )

    rgb = tensor[:, :, :, :3]
    return torch.cat([rgb, alpha], dim=3)


def clamp_tensor(
    tensor: torch.Tensor,
    min_val: float = 0.0,
    max_val: float = 1.0
) -> torch.Tensor:
    """
    Clamp tensor values to specified range.

    Args:
        tensor: Input tensor
        min_val: Minimum value (default 0.0)
        max_val: Maximum value (default 1.0)

    Returns:
        Clamped tensor
    """
    return torch.clamp(tensor, min_val, max_val)


def resize_tensors_to_match(
    tensor_a: torch.Tensor,
    tensor_b: torch.Tensor,
    mode: str = "bilinear"
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Resize tensors to match dimensions.
    Resizes smaller tensor to match larger tensor's dimensions.

    Args:
        tensor_a: First tensor [B,H,W,C]
        tensor_b: Second tensor [B,H,W,C]
        mode: Interpolation mode ('nearest', 'bilinear', 'bicubic')

    Returns:
        Tuple of (tensor_a_resized, tensor_b_resized)
    """
    validate_image_tensor(tensor_a, "tensor_a")
    validate_image_tensor(tensor_b, "tensor_b")

    _, h_a, w_a, _ = tensor_a.shape
    _, h_b, w_b, _ = tensor_b.shape

    if (h_a, w_a) == (h_b, w_b):
        return tensor_a, tensor_b

    # Determine target size (use larger dimensions)
    target_h = max(h_a, h_b)
    target_w = max(w_a, w_b)

    # Resize if needed
    if (h_a, w_a) != (target_h, target_w):
        tensor_a = resize_tensor(tensor_a, target_h, target_w, mode)

    if (h_b, w_b) != (target_h, target_w):
        tensor_b = resize_tensor(tensor_b, target_h, target_w, mode)

    return tensor_a, tensor_b


def resize_tensor(
    tensor: torch.Tensor,
    height: int,
    width: int,
    mode: str = "bilinear"
) -> torch.Tensor:
    """
    Resize tensor to specified dimensions.

    Args:
        tensor: Input tensor [B,H,W,C]
        height: Target height
        width: Target width
        mode: Interpolation mode ('nearest', 'bilinear', 'bicubic')

    Returns:
        Resized tensor [B,height,width,C]
    """
    validate_image_tensor(tensor)

    B, H, W, C = tensor.shape

    if (H, W) == (height, width):
        return tensor

    # Convert to [B,C,H,W] for interpolation
    tensor_nchw = tensor.permute(0, 3, 1, 2)

    # Resize
    resized = torch.nn.functional.interpolate(
        tensor_nchw,
        size=(height, width),
        mode=mode,
        align_corners=False if mode != "nearest" else None
    )

    # Convert back to [B,H,W,C]
    return resized.permute(0, 2, 3, 1)


def batch_size(tensor: torch.Tensor) -> int:
    """
    Get batch size from tensor.

    Args:
        tensor: Input tensor [B,H,W,C]

    Returns:
        Batch size (B)
    """
    validate_image_tensor(tensor)
    return tensor.shape[0]


def image_dimensions(tensor: torch.Tensor) -> Tuple[int, int]:
    """
    Get image dimensions (height, width) from tensor.

    Args:
        tensor: Input tensor [B,H,W,C]

    Returns:
        Tuple of (height, width)
    """
    validate_image_tensor(tensor)
    return tensor.shape[1], tensor.shape[2]


def channel_count(tensor: torch.Tensor) -> int:
    """
    Get number of channels from tensor.

    Args:
        tensor: Input tensor [B,H,W,C]

    Returns:
        Number of channels (3 or 4)
    """
    validate_image_tensor(tensor)
    return tensor.shape[3]


def copy_to_device(tensor: torch.Tensor, device: torch.device) -> torch.Tensor:
    """
    Copy tensor to specified device if not already there.

    Args:
        tensor: Input tensor
        device: Target device

    Returns:
        Tensor on target device
    """
    if tensor.device == device:
        return tensor
    return tensor.to(device)
