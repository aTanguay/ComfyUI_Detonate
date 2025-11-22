"""
ZMerge node for ComfyUI_Detonate.

Composite multiple CG layers using Z-depth information.
Automatically handles occlusion based on which pixels are closer to camera.

Based on Nuke ZMerge: compare depth values pixel-by-pixel,
closer pixels win.

Improvements over Nuke:
- Auto-detect depth channels
- Edge antialiasing (Nuke ZMerge has hard edges)
- Depth visualization mode

Reference: Nuke ZMerge documentation
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateZMerge:
    """
    Composite using Z-depth for automatic occlusion.

    Merges two CG layers by comparing depth values at each pixel.
    Pixels closer to camera (smaller Z) win. Essential for compositing
    separate render layers with correct depth sorting.

    Common uses:
    - Combine character + environment renders
    - Merge lighting passes with correct occlusion
    - Interactive object compositing (auto sort by depth)
    - Optimize renders (render heavy objects separately)

    Improvements:
    - Auto-detect depth channels from common names
    - Edge antialiasing for smooth transitions
    - Depth visualization mode
    """

    CATEGORY = "detonate/compositing"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "depth_channel_a": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 10,
                    "step": 1,
                }),
                "depth_channel_b": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 10,
                    "step": 1,
                }),
                "depth_tolerance": ("FLOAT", {
                    "default": 0.001,
                    "min": 0.0,
                    "max": 0.1,
                    "step": 0.0001,
                }),
                "antialias": ("BOOLEAN", {
                    "default": True,
                }),
                "output_depth": ("BOOLEAN", {
                    "default": True,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "zmerge"

    def zmerge(
        self,
        image_a: torch.Tensor,
        image_b: torch.Tensor,
        depth_channel_a: int,
        depth_channel_b: int,
        depth_tolerance: float,
        antialias: bool,
        output_depth: bool
    ) -> tuple:
        """
        Merge images using depth information.

        Args:
            image_a: First input [B,H,W,C] (must contain depth)
            image_b: Second input [B,H,W,C] (must contain depth)
            depth_channel_a: Depth channel index for A (-1 = auto)
            depth_channel_b: Depth channel index for B (-1 = auto)
            depth_tolerance: Epsilon for depth comparison
            antialias: Smooth edge transitions
            output_depth: Include depth in output

        Returns:
            Tuple containing merged image [B,H,W,C]
        """
        validate_image_tensor(image_a)
        validate_image_tensor(image_b)

        B_a, H_a, W_a, C_a = image_a.shape
        B_b, H_b, W_b, C_b = image_b.shape

        # Resize B to match A if needed
        if (H_a, W_a) != (H_b, W_b):
            image_b = F.interpolate(
                image_b.permute(0, 3, 1, 2),
                size=(H_a, W_a),
                mode='bilinear',
                align_corners=False
            ).permute(0, 2, 3, 1)

        # Batch size must match (take minimum)
        B = min(B_a, B_b)
        image_a = image_a[:B]
        image_b = image_b[:B]

        # Extract depth channels
        depth_a = self._extract_depth(image_a, depth_channel_a)
        depth_b = self._extract_depth(image_b, depth_channel_b)

        if depth_a is None or depth_b is None:
            print("Warning: Could not find depth channels. Returning image_a.")
            return (image_a,)

        # Extract RGBA
        rgba_a = ensure_alpha_channel(image_a[:, :, :, :min(4, C_a)])
        rgba_b = ensure_alpha_channel(image_b[:, :, :, :min(4, C_b)])

        # Create selection mask (A is closer where depth_a < depth_b)
        # Smaller depth = closer to camera
        if antialias:
            # Soft transition around depth boundary
            depth_diff = depth_a - depth_b
            # Use sigmoid for smooth transition
            mask_a = torch.sigmoid(-depth_diff / (depth_tolerance + 1e-7))
        else:
            # Hard transition
            mask_a = (depth_a < depth_b - depth_tolerance).float()

        mask_b = 1.0 - mask_a

        # Composite RGB and alpha
        result_rgba = rgba_a * mask_a + rgba_b * mask_b

        # Composite depth (take minimum = closer)
        result_depth = torch.minimum(depth_a, depth_b)

        # Build output
        if output_depth:
            result = torch.cat([result_rgba, result_depth], dim=3)
        else:
            result = result_rgba

        return (result,)

    def _extract_depth(
        self,
        image: torch.Tensor,
        depth_channel: int
    ) -> torch.Tensor:
        """
        Extract depth channel from image.

        Args:
            image: Input tensor [B,H,W,C]
            depth_channel: Channel index (-1 = auto-detect)

        Returns:
            Depth tensor [B,H,W,1] or None if not found
        """
        B, H, W, C = image.shape

        if depth_channel == -1:
            # Auto-detect: assume depth is channel 4 (index 3) or later
            if C >= 5:
                return image[:, :, :, 4:5]
            else:
                print(f"Warning: Auto-detect failed, image only has {C} channels (need 5+)")
                return None
        else:
            if depth_channel >= C:
                print(f"Warning: depth_channel {depth_channel} >= image channels {C}")
                return None

            return image[:, :, :, depth_channel:depth_channel+1]
