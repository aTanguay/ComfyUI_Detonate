"""
ComfyUI_Detonate Utilities Package

Provides common utilities for tensor operations, image processing,
and color mathematics used by all nodes.
"""

from .tensor_utils import (
    validate_image_tensor,
    ensure_alpha_channel,
    remove_alpha_channel,
    get_alpha_channel,
    set_alpha_channel,
    clamp_tensor,
    resize_tensors_to_match,
    resize_tensor,
    batch_size,
    image_dimensions,
    channel_count,
    copy_to_device,
)

from .image_processing import (
    premultiply_alpha,
    unpremultiply_alpha,
    calculate_luminance,
    normalize_range,
    invert_image,
    blend_images,
    apply_mask,
    extract_channel,
    create_constant_image,
)

from .color_math import (
    rgb_to_hsv,
    hsv_to_rgb,
    adjust_saturation,
    adjust_contrast,
    apply_gamma,
    apply_gain,
    apply_offset,
    apply_lift,
    lerp,
    clamp_color,
)

__all__ = [
    # tensor_utils
    "validate_image_tensor",
    "ensure_alpha_channel",
    "remove_alpha_channel",
    "get_alpha_channel",
    "set_alpha_channel",
    "clamp_tensor",
    "resize_tensors_to_match",
    "resize_tensor",
    "batch_size",
    "image_dimensions",
    "channel_count",
    "copy_to_device",
    # image_processing
    "premultiply_alpha",
    "unpremultiply_alpha",
    "calculate_luminance",
    "normalize_range",
    "invert_image",
    "blend_images",
    "apply_mask",
    "extract_channel",
    "create_constant_image",
    # color_math
    "rgb_to_hsv",
    "hsv_to_rgb",
    "adjust_saturation",
    "adjust_contrast",
    "apply_gamma",
    "apply_gain",
    "apply_offset",
    "apply_lift",
    "lerp",
    "clamp_color",
]
