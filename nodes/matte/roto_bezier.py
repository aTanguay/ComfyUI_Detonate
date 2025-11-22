"""
RotoBezier node for ComfyUI_Detonate.

Interactive Bezier spline drawing for rotoscoping and masking.
Professional-grade rotoscoping tool inspired by Natron's Roto node.

Reference: Natron Roto/RotoPaint, Nuke RotoPaint, Mocha tracking
https://natron.readthedocs.io/en/rb-2.3/devel/PythonReference/NatronEngine/Roto.html
"""

import torch
import numpy as np
import json
from PIL import Image, ImageDraw
import cv2
from typing import Tuple
from ...utils.bezier_utils import discretize_spline


class DetonateRotoBezier:
    """
    Interactive Bezier spline drawing for rotoscoping.

    Professional rotoscoping tool with interactive Bezier curve editing.
    Provides high-quality mask generation from vector splines with
    anti-aliasing and feathering support.

    Features:
    - Interactive Bezier spline drawing (web widget)
    - Smooth cubic Bezier curves (de Casteljau algorithm)
    - Anti-aliased edge rendering
    - Adjustable feathering
    - Multiple spline support
    - Closed and open splines

    Workflow:
    1. Use interactive widget to draw spline shapes
    2. Adjust control points and tangent handles
    3. Set feather amount for soft edges
    4. Generate high-quality anti-aliased masks

    Common uses:
    - Rotoscoping (isolating subjects)
    - Garbage mattes (removing unwanted areas)
    - Vignettes and shape masks
    - Motion graphics shapes
    - Object isolation for compositing

    Natron/Nuke equivalent: Roto / RotoPaint
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1920,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                }),
                "height": ("INT", {
                    "default": 1080,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                }),
                "spline_data": ("STRING", {
                    "default": '{"splines":[]}',
                    "multiline": False,
                }),
            },
            "optional": {
                # Feather amount (Detonate improvement!)
                "feather": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                # Anti-aliasing quality (Detonate improvement!)
                "antialias_samples": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                    "tooltip": "Supersampling factor for anti-aliasing (1=off, 4=high quality)",
                }),
                # Invert mask (Detonate improvement!)
                "invert": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "rasterize_splines"

    def rasterize_splines(
        self,
        width: int,
        height: int,
        spline_data: str,
        feather: float = 2.0,
        antialias_samples: int = 4,
        invert: bool = False
    ) -> Tuple[torch.Tensor]:
        """
        Rasterize Bezier splines to mask.

        Detonate improvements:
        1. High-quality anti-aliasing via supersampling
        2. Adjustable feathering with distance field
        3. Multiple spline support
        4. Invert option

        Args:
            width: Mask width in pixels
            height: Mask height in pixels
            spline_data: JSON string with spline data from widget
            feather: Feather amount in pixels (soft edge)
            antialias_samples: Supersampling factor (1=off, 4=high, 16=max)
            invert: Invert mask (inside becomes outside)

        Returns:
            Tuple containing mask tensor [1, H, W]
        """
        # Parse spline data
        try:
            data = json.loads(spline_data)
            splines = data.get('splines', [])
        except json.JSONDecodeError:
            # Invalid JSON, return empty mask
            return (torch.zeros(1, height, width, dtype=torch.float32),)

        if len(splines) == 0:
            # No splines, return empty mask
            return (torch.zeros(1, height, width, dtype=torch.float32),)

        # Create mask with supersampling for anti-aliasing
        aa_factor = max(1, antialias_samples)
        aa_width = width * aa_factor
        aa_height = height * aa_factor

        # Create high-res mask
        mask_np = np.zeros((aa_height, aa_width), dtype=np.uint8)

        # Rasterize each spline
        for spline_data in splines:
            points = spline_data.get('points', [])
            closed = spline_data.get('closed', False)

            if len(points) < 2:
                continue

            # Discretize Bezier spline to point array
            spline_points = discretize_spline(
                points,
                closed=closed,
                samples_per_segment=20  # Good balance of quality/performance
            )

            if len(spline_points) == 0:
                continue

            # Scale points to supersampled resolution
            spline_points_scaled = spline_points * aa_factor

            # Convert to integer coordinates for PIL
            polygon_points = [(int(p[0]), int(p[1])) for p in spline_points_scaled]

            # Draw filled polygon
            img = Image.fromarray(mask_np)
            draw = ImageDraw.Draw(img)

            if closed and len(polygon_points) >= 3:
                # Draw filled polygon
                draw.polygon(polygon_points, fill=255, outline=255)
            else:
                # Draw line for open splines
                if len(polygon_points) >= 2:
                    draw.line(polygon_points, fill=255, width=aa_factor)

            mask_np = np.array(img)

        # Downsample for anti-aliasing
        if aa_factor > 1:
            mask_np = cv2.resize(
                mask_np,
                (width, height),
                interpolation=cv2.INTER_AREA  # Best for downsampling
            )

        # Convert to float [0, 1]
        mask_float = mask_np.astype(np.float32) / 255.0

        # Apply feathering if requested
        if feather > 0.0:
            mask_float = self._apply_feather(mask_float, feather)

        # Invert if requested
        if invert:
            mask_float = 1.0 - mask_float

        # Convert to torch tensor [1, H, W]
        mask_tensor = torch.from_numpy(mask_float).unsqueeze(0)

        return (mask_tensor,)

    def _apply_feather(
        self,
        mask: np.ndarray,
        feather_radius: float
    ) -> np.ndarray:
        """
        Apply feathering (soft edge) to mask using distance transform.

        Detonate improvement: Distance field-based feathering for
        high-quality soft edges.

        Args:
            mask: Input mask [H, W] in range [0, 1]
            feather_radius: Feather radius in pixels

        Returns:
            Feathered mask [H, W]
        """
        if feather_radius < 0.1:
            return mask

        # Convert to binary for distance transform
        binary_mask = (mask > 0.5).astype(np.uint8)

        # Compute distance transforms (inside and outside)
        dist_inside = cv2.distanceTransform(
            binary_mask,
            cv2.DIST_L2,
            cv2.DIST_MASK_PRECISE
        )
        dist_outside = cv2.distanceTransform(
            1 - binary_mask,
            cv2.DIST_L2,
            cv2.DIST_MASK_PRECISE
        )

        # Signed distance field
        sdf = dist_inside - dist_outside

        # Apply smoothstep falloff
        # Map distance to [0, 1] over feather range
        t = np.clip((sdf + feather_radius) / (2 * feather_radius), 0.0, 1.0)

        # Smoothstep for smooth falloff
        feathered = t * t * (3.0 - 2.0 * t)

        return feathered.astype(np.float32)


class DetonateRotoBezierFromImage:
    """
    RotoBezier with image input (apply splines to existing image dimensions).

    Convenience node that takes an image input and generates a mask
    at the same resolution. Useful for rotoscoping over footage.
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "spline_data": ("STRING", {
                    "default": '{"splines":[]}',
                    "multiline": False,
                }),
            },
            "optional": {
                "feather": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "antialias_samples": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                }),
                "invert": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "rasterize_from_image"

    def rasterize_from_image(
        self,
        image: torch.Tensor,
        spline_data: str,
        feather: float = 2.0,
        antialias_samples: int = 4,
        invert: bool = False
    ) -> Tuple[torch.Tensor]:
        """
        Generate mask from splines at image resolution.

        Args:
            image: Input image (used for dimensions only) [B, H, W, C]
            spline_data: JSON spline data
            feather: Feather amount
            antialias_samples: Anti-aliasing quality
            invert: Invert mask

        Returns:
            Mask tensor [1, H, W]
        """
        B, H, W, C = image.shape

        # Use main RotoBezier node
        roto = DetonateRotoBezier()
        mask = roto.rasterize_splines(
            width=W,
            height=H,
            spline_data=spline_data,
            feather=feather,
            antialias_samples=antialias_samples,
            invert=invert
        )

        return mask
