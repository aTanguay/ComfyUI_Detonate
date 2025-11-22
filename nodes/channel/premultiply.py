"""
Premultiply and Unpremultiply nodes for ComfyUI_Detonate.

Converts between straight alpha and premultiplied alpha representations.
Essential for proper compositing and color correction workflows.

Reference: Natron Premult.cpp
https://github.com/NatronGitHub/openfx-misc/blob/master/Premult/Premult.cpp
"""

import torch
from ...utils import (
    validate_image_tensor,
    ensure_alpha_channel,
    premultiply_alpha,
    unpremultiply_alpha,
)


class DetonatePremultiply:
    """
    Premultiply RGB channels by alpha channel.

    Converts from straight alpha to premultiplied alpha by multiplying
    RGB values by their corresponding alpha value.

    Formula: result.rgb = input.rgb * input.alpha

    Use before: Merge operations, filtering, transforms
    Nuke/Fusion equivalent: Premult node
    """

    CATEGORY = "detonate/channel"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "premultiply"

    def premultiply(self, image: torch.Tensor) -> tuple:
        """
        Premultiply RGB by alpha.

        Args:
            image: Input tensor [B,H,W,C] where C=3 or C=4

        Returns:
            Tuple containing premultiplied image [B,H,W,4]
        """
        validate_image_tensor(image)

        # Ensure alpha channel exists (add alpha=1.0 if RGB only)
        image_with_alpha = ensure_alpha_channel(image, alpha_value=1.0)

        # Apply premultiply
        result = premultiply_alpha(image_with_alpha)

        return (result,)


class DetonateUnpremultiply:
    """
    Unpremultiply RGB channels by alpha channel.

    Converts from premultiplied alpha to straight alpha by dividing
    RGB values by their corresponding alpha value.

    Formula: result.rgb = input.rgb / (input.alpha + epsilon)

    Use before: Color correction, grading, painting in transparent areas
    Use after: Loading premultiplied images, compositing operations
    Nuke/Fusion equivalent: Unpremult node
    """

    CATEGORY = "detonate/channel"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "epsilon": ("FLOAT", {
                    "default": 1e-7,
                    "min": 1e-10,
                    "max": 1e-5,
                    "step": 1e-8,
                    "display": "number",
                }),
                "clamp_output": ("BOOLEAN", {
                    "default": False,
                }),
                "max_value": ("FLOAT", {
                    "default": 10.0,
                    "min": 1.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "number",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "unpremultiply"

    def unpremultiply(
        self,
        image: torch.Tensor,
        epsilon: float = 1e-7,
        clamp_output: bool = False,
        max_value: float = 10.0
    ) -> tuple:
        """
        Unpremultiply RGB by alpha.

        Args:
            image: Input tensor [B,H,W,C] where C=3 or C=4
            epsilon: Small value to prevent division by zero
            clamp_output: Whether to clamp RGB to max_value
            max_value: Maximum RGB value if clamping

        Returns:
            Tuple containing unpremultiplied image [B,H,W,4]
        """
        validate_image_tensor(image)

        # Ensure alpha channel exists (add alpha=1.0 if RGB only)
        image_with_alpha = ensure_alpha_channel(image, alpha_value=1.0)

        # Apply unpremultiply
        result = unpremultiply_alpha(
            image_with_alpha,
            epsilon=epsilon,
            clamp_output=clamp_output,
            max_value=max_value
        )

        return (result,)
