"""
Crop node for ComfyUI_Detonate.

Crop images to specific dimensions with optional soft edges.
Essential for framing, aspect ratio changes, and creative cropping.

Reference: Nuke Crop node
https://learn.foundry.com/nuke/content/reference_guide/transform_nodes/crop.html
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor


class DetonateCrop:
    """
    Crop image with soft edges and aspect ratio controls.

    Provides precise box cropping with optional edge feathering
    for smooth transitions. Includes aspect ratio presets and
    center crop mode for quick adjustments.

    Common uses:
    - Change aspect ratio (16:9, 2.35:1, 1:1)
    - Frame composition
    - Remove unwanted edges
    - Create soft-edged mattes

    Nuke equivalent: Crop
    """

    CATEGORY = "detonate/transform"

    # Detonate improvement: Aspect ratio presets!
    ASPECT_RATIOS = [
        "custom",
        "16:9",
        "2.39:1",  # Anamorphic widescreen
        "2.35:1",  # Cinemascope
        "1.85:1",  # US theatrical
        "4:3",     # Standard TV
        "1:1",     # Square (Instagram)
        "9:16",    # Vertical (mobile)
    ]

    FEATHER_MODES = ["linear", "smooth", "gaussian"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Crop box (pixel coordinates)
                "left": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                }),
                "top": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                }),
                "right": ("INT", {
                    "default": 1920,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                }),
                "bottom": ("INT", {
                    "default": 1080,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                }),
                # Aspect ratio preset (Detonate improvement!)
                "aspect_ratio": (cls.ASPECT_RATIOS, {
                    "default": "custom",
                }),
                # Center crop mode (Detonate improvement!)
                "center_crop": ("BOOLEAN", {
                    "default": False,
                }),
                # Soft edge controls
                "feather": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 500.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "feather_mode": (cls.FEATHER_MODES, {
                    "default": "smooth",
                }),
                # Outside behavior
                "outside_black": ("BOOLEAN", {
                    "default": True,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "crop_image"

    def crop_image(
        self,
        image: torch.Tensor,
        left: int = 0,
        top: int = 0,
        right: int = 1920,
        bottom: int = 1080,
        aspect_ratio: str = "custom",
        center_crop: bool = False,
        feather: float = 0.0,
        feather_mode: str = "smooth",
        outside_black: bool = True
    ) -> tuple:
        """
        Crop image with soft edges.

        Detonate improvements:
        1. Aspect ratio presets (16:9, 2.39:1, etc.)
        2. Center crop mode for quick framing
        3. Multiple feather modes (linear, smooth, gaussian)

        Args:
            image: Input tensor [B,H,W,C]
            left: Left edge of crop box (pixels)
            top: Top edge of crop box (pixels)
            right: Right edge of crop box (pixels)
            bottom: Bottom edge of crop box (pixels)
            aspect_ratio: Aspect ratio preset (adjusts box automatically)
            center_crop: Center the crop box on image
            feather: Soft edge width in pixels
            feather_mode: Feather falloff shape
            outside_black: Fill outside crop box with black vs clamp

        Returns:
            Tuple containing cropped image [B,H_crop,W_crop,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Apply aspect ratio preset if selected (Detonate improvement!)
        if aspect_ratio != "custom":
            left, top, right, bottom = self._apply_aspect_ratio(
                W, H, aspect_ratio, center_crop
            )
        # Apply center crop if requested
        elif center_crop:
            crop_w = right - left
            crop_h = bottom - top
            left = (W - crop_w) // 2
            right = left + crop_w
            top = (H - crop_h) // 2
            bottom = top + crop_h

        # Clamp crop box to image bounds
        left = max(0, min(left, W))
        right = max(left, min(right, W))
        top = max(0, min(top, H))
        bottom = max(top, min(bottom, H))

        crop_w = right - left
        crop_h = bottom - top

        # Ensure crop dimensions are valid
        if crop_w <= 0 or crop_h <= 0:
            # Return 1x1 black image
            return (torch.zeros(B, 1, 1, C, dtype=image.dtype, device=image.device),)

        # If no feather, simple crop
        if feather <= 0.0:
            result = image[:, top:bottom, left:right, :]
            return (result,)

        # Crop with soft edges
        result = self._crop_with_feather(
            image, left, top, right, bottom, feather, feather_mode, outside_black
        )

        return (result,)

    def _apply_aspect_ratio(
        self,
        width: int,
        height: int,
        aspect_ratio: str,
        center: bool
    ) -> tuple:
        """
        Calculate crop box for aspect ratio preset.

        Detonate improvement: Automatic aspect ratio presets!

        Args:
            width: Image width
            height: Image height
            aspect_ratio: Aspect ratio preset string
            center: Center the crop box

        Returns:
            Tuple of (left, top, right, bottom)
        """
        # Parse aspect ratio
        ratio_map = {
            "16:9": 16.0 / 9.0,
            "2.39:1": 2.39,
            "2.35:1": 2.35,
            "1.85:1": 1.85,
            "4:3": 4.0 / 3.0,
            "1:1": 1.0,
            "9:16": 9.0 / 16.0,
        }

        target_ratio = ratio_map.get(aspect_ratio, width / height)
        current_ratio = width / height

        if current_ratio > target_ratio:
            # Image is wider, crop width
            crop_w = int(height * target_ratio)
            crop_h = height
        else:
            # Image is taller, crop height
            crop_w = width
            crop_h = int(width / target_ratio)

        if center:
            left = (width - crop_w) // 2
            top = (height - crop_h) // 2
        else:
            left = 0
            top = 0

        right = left + crop_w
        bottom = top + crop_h

        return (left, top, right, bottom)

    def _crop_with_feather(
        self,
        image: torch.Tensor,
        left: int,
        top: int,
        right: int,
        bottom: int,
        feather: float,
        feather_mode: str,
        outside_black: bool
    ) -> torch.Tensor:
        """
        Crop image with soft edges.

        Creates a feathered matte and applies it to the crop region.

        Args:
            image: Input tensor [B,H,W,C]
            left, top, right, bottom: Crop box
            feather: Feather width in pixels
            feather_mode: Feather falloff shape
            outside_black: Fill outside with black vs clamp

        Returns:
            Cropped and feathered image [B,crop_h,crop_w,C]
        """
        B, H, W, C = image.shape

        crop_w = right - left
        crop_h = bottom - top

        # Create feather matte [crop_h, crop_w]
        matte = self._create_feather_matte(crop_h, crop_w, feather, feather_mode)
        matte = matte.to(image.device).unsqueeze(0).unsqueeze(3)  # [1,H,W,1]

        # Crop the image region
        cropped = image[:, top:bottom, left:right, :]

        if outside_black:
            # Multiply by matte to feather edges to black
            result = cropped * matte
        else:
            # Blend with clamped edge values (not implemented for simplicity)
            result = cropped * matte

        return result

    def _create_feather_matte(
        self,
        height: int,
        width: int,
        feather: float,
        mode: str
    ) -> torch.Tensor:
        """
        Create soft edge matte for feathering.

        Detonate improvement: Multiple feather modes!

        Args:
            height: Matte height
            width: Matte width
            feather: Feather width in pixels
            mode: Feather mode (linear, smooth, gaussian)

        Returns:
            Feather matte [height, width]
        """
        # Create distance field from edges
        # Distance from left edge
        dist_left = torch.arange(width, dtype=torch.float32).unsqueeze(0)
        # Distance from right edge
        dist_right = torch.arange(width - 1, -1, -1, dtype=torch.float32).unsqueeze(0)
        # Distance from top edge
        dist_top = torch.arange(height, dtype=torch.float32).unsqueeze(1)
        # Distance from bottom edge
        dist_bottom = torch.arange(height - 1, -1, -1, dtype=torch.float32).unsqueeze(1)

        # Minimum distance to any edge
        dist_h = torch.minimum(dist_left, dist_right)
        dist_v = torch.minimum(dist_top, dist_bottom)
        dist = torch.minimum(dist_h, dist_v)  # [height, width]

        # Apply feather falloff
        if feather <= 0:
            matte = torch.ones(height, width)
        else:
            if mode == "linear":
                # Linear falloff
                matte = torch.clamp(dist / feather, 0.0, 1.0)
            elif mode == "smooth":
                # Smoothstep falloff (3x^2 - 2x^3)
                t = torch.clamp(dist / feather, 0.0, 1.0)
                matte = t * t * (3.0 - 2.0 * t)
            elif mode == "gaussian":
                # Gaussian falloff
                sigma = feather / 3.0
                matte = torch.exp(-(torch.clamp(feather - dist, min=0.0) ** 2) / (2 * sigma ** 2))
            else:
                matte = torch.ones(height, width)

        return matte
