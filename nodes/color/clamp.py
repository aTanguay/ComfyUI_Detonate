"""
Clamp node for ComfyUI_Detonate.

Constrain pixel values to specified min/max range.
Essential for managing float images with HDR values.

Reference: Nuke/Natron Clamp node
https://learn.foundry.com/nuke/content/reference_guide/color_nodes/clamp.html
https://natron.readthedocs.io/en/v2.3.15/plugins/net.sf.openfx.Clamp.html
"""

import torch
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateClamp:
    """
    Constrain pixel values to min/max range.

    Clamps values to specified minimum and maximum, with optional
    remapping for out-of-range values.

    Common uses:
    - Fix overbright HDR pixels
    - Clamp to 0-1 before operations requiring that range
    - Create binary masks via thresholding
    - Normalize depth passes

    Nuke/Natron equivalent: Clamp
    """

    CATEGORY = "detonate/color"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "minimum": ("FLOAT", {
                    "default": 0.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "maximum": ("FLOAT", {
                    "default": 1.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "min_clamp_to_enabled": ("BOOLEAN", {
                    "default": False,
                }),
                "min_clamp_to": ("FLOAT", {
                    "default": 0.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "max_clamp_to_enabled": ("BOOLEAN", {
                    "default": False,
                }),
                "max_clamp_to": ("FLOAT", {
                    "default": 1.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "channels": (["rgba", "rgb", "alpha"], {
                    "default": "rgba",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "clamp"

    def clamp(
        self,
        image: torch.Tensor,
        minimum: float = 0.0,
        maximum: float = 1.0,
        min_clamp_to_enabled: bool = False,
        min_clamp_to: float = 0.0,
        max_clamp_to_enabled: bool = False,
        max_clamp_to: float = 1.0,
        channels: str = "rgba"
    ) -> tuple:
        """
        Clamp pixel values to specified range.

        Args:
            image: Input tensor [B,H,W,C]
            minimum: Minimum value threshold
            maximum: Maximum value threshold
            min_clamp_to_enabled: If true, remap values below minimum
            min_clamp_to: Replacement value for pixels below minimum
            max_clamp_to_enabled: If true, remap values above maximum
            max_clamp_to: Replacement value for pixels above maximum
            channels: Which channels to clamp ("rgba", "rgb", "alpha")

        Returns:
            Tuple containing clamped image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Ensure alpha channel exists
        image_rgba = ensure_alpha_channel(image, alpha_value=1.0)

        # Determine which channels to process
        if channels == "rgba":
            # Process all channels
            result = self._clamp_channels(
                image_rgba,
                minimum, maximum,
                min_clamp_to_enabled, min_clamp_to,
                max_clamp_to_enabled, max_clamp_to,
                channel_indices=[0, 1, 2, 3]
            )
        elif channels == "rgb":
            # Process RGB only
            rgb_clamped = self._clamp_channels(
                image_rgba[:, :, :, :3],
                minimum, maximum,
                min_clamp_to_enabled, min_clamp_to,
                max_clamp_to_enabled, max_clamp_to,
                channel_indices=[0, 1, 2]
            )
            result = torch.cat([rgb_clamped, image_rgba[:, :, :, 3:4]], dim=3)
        else:  # "alpha"
            # Process alpha only
            alpha_clamped = self._clamp_channels(
                image_rgba[:, :, :, 3:4],
                minimum, maximum,
                min_clamp_to_enabled, min_clamp_to,
                max_clamp_to_enabled, max_clamp_to,
                channel_indices=[0]
            )
            result = torch.cat([image_rgba[:, :, :, :3], alpha_clamped], dim=3)

        # Match output channels to input
        if C == 3:
            result = result[:, :, :, :3]

        return (result,)

    def _clamp_channels(
        self,
        tensor: torch.Tensor,
        minimum: float,
        maximum: float,
        min_clamp_to_enabled: bool,
        min_clamp_to: float,
        max_clamp_to_enabled: bool,
        max_clamp_to: float,
        channel_indices: list
    ) -> torch.Tensor:
        """
        Apply clamping to specified channels.

        Args:
            tensor: Input tensor
            minimum: Minimum threshold
            maximum: Maximum threshold
            min_clamp_to_enabled: Enable min remapping
            min_clamp_to: Min replacement value
            max_clamp_to_enabled: Enable max remapping
            max_clamp_to: Max replacement value
            channel_indices: Which channel indices to process

        Returns:
            Clamped tensor
        """
        result = tensor.clone()

        # Handle min clamping
        if min_clamp_to_enabled:
            # Remap values below minimum to min_clamp_to
            mask = result < minimum
            result = torch.where(mask, torch.tensor(min_clamp_to, dtype=result.dtype, device=result.device), result)
        else:
            # Standard clamp to minimum
            result = torch.clamp(result, min=minimum)

        # Handle max clamping
        if max_clamp_to_enabled:
            # Remap values above maximum to max_clamp_to
            mask = result > maximum
            result = torch.where(mask, torch.tensor(max_clamp_to, dtype=result.dtype, device=result.device), result)
        else:
            # Standard clamp to maximum
            result = torch.clamp(result, max=maximum)

        return result
