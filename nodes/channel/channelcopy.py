"""
ChannelCopy node for ComfyUI_Detonate.

Copy channels from one input stream to another.
Essential for multi-stream workflows and render pass compositing.

Reference: Nuke Copy node / Fusion ChannelBooleans
"""

import torch
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateChannelCopy:
    """
    Copy channels from source (B) to base (A).

    Two inputs: A (base) and B (source)
    Selected channels from B replace corresponding channels in A.

    Common uses:
    - Replace alpha with clean matte
    - Copy RGB from one stream, alpha from another
    - Combine different render passes
    - Channel swapping workflows

    Nuke/Fusion equivalent: Copy / ChannelBooleans
    """

    CATEGORY = "detonate/channel"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base": ("IMAGE",),  # A input
                "source": ("IMAGE",),  # B input
            },
            "optional": {
                "copy_red": ("BOOLEAN", {
                    "default": False,
                }),
                "copy_green": ("BOOLEAN", {
                    "default": False,
                }),
                "copy_blue": ("BOOLEAN", {
                    "default": False,
                }),
                "copy_alpha": ("BOOLEAN", {
                    "default": True,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "copy_channels"

    def copy_channels(
        self,
        base: torch.Tensor,
        source: torch.Tensor,
        copy_red: bool = False,
        copy_green: bool = False,
        copy_blue: bool = False,
        copy_alpha: bool = True
    ) -> tuple:
        """
        Copy selected channels from source to base.

        Args:
            base: Base image (A) [B,H,W,C]
            source: Source image (B) to copy channels from [B,H,W,C]
            copy_red: Copy red channel from source to base
            copy_green: Copy green channel from source to base
            copy_blue: Copy blue channel from source to base
            copy_alpha: Copy alpha channel from source to base

        Returns:
            Tuple containing result image [B,H,W,C]
        """
        validate_image_tensor(base, "base")
        validate_image_tensor(source, "source")

        B1, H1, W1, C1 = base.shape
        B2, H2, W2, C2 = source.shape

        # Ensure both have alpha channels
        base_rgba = ensure_alpha_channel(base, alpha_value=1.0)
        source_rgba = ensure_alpha_channel(source, alpha_value=1.0)

        # Resize source to match base dimensions if needed
        if H1 != H2 or W1 != W2:
            # Permute to [B,C,H,W] for interpolation
            source_rgba_nchw = source_rgba.permute(0, 3, 1, 2)
            source_rgba_nchw = torch.nn.functional.interpolate(
                source_rgba_nchw,
                size=(H1, W1),
                mode='bilinear',
                align_corners=False
            )
            source_rgba = source_rgba_nchw.permute(0, 2, 3, 1)

        # Handle batch size mismatch (broadcast if source has batch=1)
        if B1 != B2:
            if B2 == 1:
                source_rgba = source_rgba.repeat(B1, 1, 1, 1)
            elif B1 == 1:
                base_rgba = base_rgba.repeat(B2, 1, 1, 1)
                B1 = B2
            else:
                raise ValueError(f"Incompatible batch sizes: base={B1}, source={B2}")

        # Start with base
        result = base_rgba.clone()

        # Copy selected channels from source
        if copy_red:
            result[:, :, :, 0] = source_rgba[:, :, :, 0]

        if copy_green:
            result[:, :, :, 1] = source_rgba[:, :, :, 1]

        if copy_blue:
            result[:, :, :, 2] = source_rgba[:, :, :, 2]

        if copy_alpha:
            result[:, :, :, 3] = source_rgba[:, :, :, 3]

        # Match output channels to base input
        if C1 == 3:
            result = result[:, :, :, :3]

        return (result,)
