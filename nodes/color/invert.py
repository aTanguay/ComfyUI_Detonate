"""
Invert node for ComfyUI_Detonate.

Invert selected channels using 1-x formula.
Essential for flipping mattes and creating negative images.

Reference: Nuke/Natron Invert node
https://natron.readthedocs.io/en/v2.3.15/plugins/net.sf.openfx.Invert.html
"""

import torch
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateInvert:
    """
    Invert selected channels.

    Inverts channels using `1 - value` formula.
    Can invert RGB and Alpha independently.

    Common uses:
    - Flip mattes (invert alpha)
    - Create negative images
    - Invert masks for opposite selection
    - Channel manipulation workflows

    Nuke/Natron equivalent: Invert
    """

    CATEGORY = "detonate/color"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "invert_red": ("BOOLEAN", {
                    "default": True,
                }),
                "invert_green": ("BOOLEAN", {
                    "default": True,
                }),
                "invert_blue": ("BOOLEAN", {
                    "default": True,
                }),
                "invert_alpha": ("BOOLEAN", {
                    "default": False,
                }),
                "clamp": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "invert"

    def invert(
        self,
        image: torch.Tensor,
        invert_red: bool = True,
        invert_green: bool = True,
        invert_blue: bool = True,
        invert_alpha: bool = False,
        clamp: bool = False
    ) -> tuple:
        """
        Invert selected channels.

        Formula: output = 1.0 - input

        Args:
            image: Input tensor [B,H,W,C]
            invert_red: Invert red channel
            invert_green: Invert green channel
            invert_blue: Invert blue channel
            invert_alpha: Invert alpha channel
            clamp: If true, clamp result to 0-1 (prevents negatives from HDR)

        Returns:
            Tuple containing inverted image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Ensure alpha channel exists
        image_rgba = ensure_alpha_channel(image, alpha_value=1.0)

        # Clone for result
        result = image_rgba.clone()

        # Invert selected channels
        if invert_red:
            result[:, :, :, 0] = 1.0 - result[:, :, :, 0]

        if invert_green:
            result[:, :, :, 1] = 1.0 - result[:, :, :, 1]

        if invert_blue:
            result[:, :, :, 2] = 1.0 - result[:, :, :, 2]

        if invert_alpha:
            result[:, :, :, 3] = 1.0 - result[:, :, :, 3]

        # Optional clamping to 0-1 range
        if clamp:
            result = torch.clamp(result, 0.0, 1.0)

        # Match output channels to input
        if C == 3:
            result = result[:, :, :, :3]

        return (result,)
