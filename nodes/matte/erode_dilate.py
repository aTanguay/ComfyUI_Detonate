"""
Erode and Dilate nodes for ComfyUI_Detonate.

Morphological operations for matte expansion and contraction.
Essential for matte cleanup and refinement.

Reference: Nuke Erode/Dilate nodes
https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/erode_filter.html
https://www.keheka.com/erode-dilate-technique/
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateErode:
    """
    Erode (contract) mattes and alpha channels.

    Shrinks bright regions by taking the minimum value in a neighborhood.
    Useful for:
    - Removing bright speckles and noise
    - Cleaning up matte edges
    - Removing fringe pixels
    - Matte deflation

    Nuke/Fusion equivalent: Erode / FilterErode
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "slider",
                }),
            },
            "optional": {
                "channels": (["rgba", "rgb", "alpha"], {
                    "default": "alpha",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "erode"

    def erode(
        self,
        image: torch.Tensor,
        size: int,
        channels: str = "alpha"
    ) -> tuple:
        """
        Erode (contract) image using morphological erosion.

        Positive size: Contract bright areas (erode)
        Size 0: No operation

        Args:
            image: Input tensor [B,H,W,C]
            size: Erosion size in pixels (>0)
            channels: Which channels to process

        Returns:
            Tuple containing eroded image [B,H,W,C]
        """
        validate_image_tensor(image)

        if size == 0:
            return (image,)

        return self._apply_morphology(image, size, "erode", channels)

    def _apply_morphology(
        self,
        image: torch.Tensor,
        size: int,
        operation: str,
        channels: str
    ) -> tuple:
        """
        Apply morphological operation to image.

        Args:
            image: Input tensor [B,H,W,C]
            size: Operation size
            operation: "erode" or "dilate"
            channels: Which channels to process

        Returns:
            Tuple containing processed image
        """
        B, H, W, C = image.shape

        # Ensure alpha channel exists
        image_rgba = ensure_alpha_channel(image, alpha_value=1.0)

        # Determine which channels to process
        if channels == "alpha":
            # Process alpha only
            rgb = image_rgba[:, :, :, :3]
            alpha = image_rgba[:, :, :, 3:4]

            alpha_processed = self._morphology_operation(alpha, size, operation)

            result = torch.cat([rgb, alpha_processed], dim=3)

        elif channels == "rgb":
            # Process RGB only
            rgb = image_rgba[:, :, :, :3]
            alpha = image_rgba[:, :, :, 3:4]

            rgb_processed = self._morphology_operation(rgb, size, operation)

            result = torch.cat([rgb_processed, alpha], dim=3)

        else:  # "rgba"
            # Process all channels
            result = self._morphology_operation(image_rgba, size, operation)

        # Match output channels to input
        if C == 3:
            result = result[:, :, :, :3]

        return (result,)

    def _morphology_operation(
        self,
        tensor: torch.Tensor,
        size: int,
        operation: str
    ) -> torch.Tensor:
        """
        Apply morphological operation using pooling.

        Erosion: Use -max_pool(-x) to get minimum in neighborhood
        Dilation: Use max_pool(x) to get maximum in neighborhood

        Args:
            tensor: Input tensor [B,H,W,C]
            size: Kernel size
            operation: "erode" or "dilate"

        Returns:
            Processed tensor [B,H,W,C]
        """
        B, H, W, C = tensor.shape

        # Convert to [B,C,H,W] for pooling
        tensor_nchw = tensor.permute(0, 3, 1, 2)

        # Kernel size (must be odd)
        kernel_size = 2 * size + 1

        # Padding to maintain size
        padding = size

        if operation == "erode":
            # Erosion: minimum in neighborhood
            # Trick: -max_pool(-x) = min_pool(x)
            result_nchw = -F.max_pool2d(
                -tensor_nchw,
                kernel_size=kernel_size,
                stride=1,
                padding=padding
            )
        else:  # "dilate"
            # Dilation: maximum in neighborhood
            result_nchw = F.max_pool2d(
                tensor_nchw,
                kernel_size=kernel_size,
                stride=1,
                padding=padding
            )

        # Convert back to [B,H,W,C]
        result = result_nchw.permute(0, 2, 3, 1)

        return result


class DetonateDilate:
    """
    Dilate (expand) mattes and alpha channels.

    Grows bright regions by taking the maximum value in a neighborhood.
    Useful for:
    - Filling holes in mattes
    - Expanding matte edges
    - Matte inflation
    - Covering more area

    Nuke/Fusion equivalent: Dilate / ErodeDilate (negative size)
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "slider",
                }),
            },
            "optional": {
                "channels": (["rgba", "rgb", "alpha"], {
                    "default": "alpha",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "dilate"

    def dilate(
        self,
        image: torch.Tensor,
        size: int,
        channels: str = "alpha"
    ) -> tuple:
        """
        Dilate (expand) image using morphological dilation.

        Positive size: Expand bright areas (dilate)
        Size 0: No operation

        Args:
            image: Input tensor [B,H,W,C]
            size: Dilation size in pixels (>0)
            channels: Which channels to process

        Returns:
            Tuple containing dilated image [B,H,W,C]
        """
        validate_image_tensor(image)

        if size == 0:
            return (image,)

        # Reuse erode's morphology function
        erode_node = DetonateErode()
        return erode_node._apply_morphology(image, size, "dilate", channels)
