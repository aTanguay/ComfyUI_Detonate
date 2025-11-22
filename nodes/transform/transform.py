"""
Transform node for ComfyUI_Detonate.

2D geometric transformations with translate, rotate, scale, and skew.
Professional-grade transforms with multiple filter quality options.

Reference: Nuke Transform node
https://learn.foundry.com/nuke/content/reference_guide/transform_nodes/transform.html
"""

import torch
import torch.nn.functional as F
import math
from ...utils import validate_image_tensor


class DetonateTransform:
    """
    2D geometric transformations (translate, rotate, scale, skew).

    Implements professional-grade 2D transforms using affine transformations.
    Transform order: Translate → Rotate → Scale → Skew (from center point)

    Common uses:
    - Position adjustment
    - Rotation and scaling
    - Perspective correction (with skew)
    - Image alignment

    Nuke/Fusion equivalent: Transform
    """

    CATEGORY = "detonate/transform"

    FILTER_MODES = ["nearest", "bilinear", "bicubic"]
    EDGE_MODES = ["black", "clamp", "repeat"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Translation
                "translate_x": ("FLOAT", {
                    "default": 0.0,
                    "min": -4096.0,
                    "max": 4096.0,
                    "step": 0.1,
                    "display": "number",
                }),
                "translate_y": ("FLOAT", {
                    "default": 0.0,
                    "min": -4096.0,
                    "max": 4096.0,
                    "step": 0.1,
                    "display": "number",
                }),
                # Rotation
                "rotate": ("FLOAT", {
                    "default": 0.0,
                    "min": -360.0,
                    "max": 360.0,
                    "step": 0.1,
                    "display": "number",
                }),
                # Scale
                "scale_x": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "scale_y": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "number",
                }),
                # Skew
                "skew_x": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "skew_y": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "number",
                }),
                # Center point (normalized to image dimensions)
                "center_x": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "center_y": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Quality and edge handling
                "filter": (cls.FILTER_MODES, {
                    "default": "bilinear",
                }),
                "edge_mode": (cls.EDGE_MODES, {
                    "default": "black",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "transform"

    def transform(
        self,
        image: torch.Tensor,
        translate_x: float = 0.0,
        translate_y: float = 0.0,
        rotate: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        skew_x: float = 0.0,
        skew_y: float = 0.0,
        center_x: float = 0.5,
        center_y: float = 0.5,
        filter: str = "bilinear",
        edge_mode: str = "black"
    ) -> tuple:
        """
        Apply 2D geometric transformation to image.

        Args:
            image: Input tensor [B,H,W,C]
            translate_x: Horizontal translation in pixels
            translate_y: Vertical translation in pixels
            rotate: Rotation in degrees (clockwise)
            scale_x: Horizontal scale factor
            scale_y: Vertical scale factor
            skew_x: Horizontal skew
            skew_y: Vertical skew
            center_x: Transform center X (0-1, normalized)
            center_y: Transform center Y (0-1, normalized)
            filter: Interpolation mode (nearest, bilinear, bicubic)
            edge_mode: Edge handling (black, clamp, repeat)

        Returns:
            Tuple containing transformed image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Early exit if no transform
        is_identity = (
            translate_x == 0.0 and translate_y == 0.0 and
            rotate == 0.0 and
            scale_x == 1.0 and scale_y == 1.0 and
            skew_x == 0.0 and skew_y == 0.0
        )
        if is_identity:
            return (image,)

        # Convert to [B,C,H,W] for processing
        image_nchw = image.permute(0, 3, 1, 2)

        # Calculate center point in pixel coordinates
        center_px = torch.tensor([center_x * W, center_y * H], dtype=torch.float32, device=image.device)

        # Build affine transformation matrix
        affine_matrix = self._build_affine_matrix(
            translate_x=translate_x,
            translate_y=translate_y,
            rotate=rotate,
            scale_x=scale_x,
            scale_y=scale_y,
            skew_x=skew_x,
            skew_y=skew_y,
            center=center_px,
            image_size=(W, H)
        )

        # Apply transformation
        result_nchw = self._apply_affine_transform(
            image_nchw,
            affine_matrix,
            filter=filter,
            edge_mode=edge_mode
        )

        # Convert back to [B,H,W,C]
        result = result_nchw.permute(0, 2, 3, 1)

        return (result,)

    def _build_affine_matrix(
        self,
        translate_x: float,
        translate_y: float,
        rotate: float,
        scale_x: float,
        scale_y: float,
        skew_x: float,
        skew_y: float,
        center: torch.Tensor,
        image_size: tuple
    ) -> torch.Tensor:
        """
        Build combined affine transformation matrix.

        Transform order: Translate → Rotate → Scale → Skew
        All operations are relative to center point.

        Args:
            translate_x, translate_y: Translation in pixels
            rotate: Rotation in degrees
            scale_x, scale_y: Scale factors
            skew_x, skew_y: Skew factors
            center: Center point [x, y] in pixels
            image_size: (width, height)

        Returns:
            Affine matrix [2, 3] for grid_sample
        """
        W, H = image_size
        cx, cy = center[0].item(), center[1].item()

        # Convert rotation to radians
        angle_rad = math.radians(rotate)
        cos_r = math.cos(angle_rad)
        sin_r = math.sin(angle_rad)

        # Build transformation matrix (homogeneous coordinates)
        # Start with identity
        matrix = torch.eye(3, dtype=torch.float32, device=center.device)

        # 1. Translate to center
        T_to_center = torch.tensor([
            [1, 0, -cx],
            [0, 1, -cy],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        # 2. Scale
        S = torch.tensor([
            [scale_x, 0, 0],
            [0, scale_y, 0],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        # 3. Rotate
        R = torch.tensor([
            [cos_r, -sin_r, 0],
            [sin_r, cos_r, 0],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        # 4. Skew
        K = torch.tensor([
            [1, skew_x, 0],
            [skew_y, 1, 0],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        # 5. Translate back from center + user translation
        T_from_center = torch.tensor([
            [1, 0, cx + translate_x],
            [0, 1, cy + translate_y],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        # Combine transformations (right to left)
        matrix = T_from_center @ K @ R @ S @ T_to_center

        # Convert to normalized coordinates for grid_sample
        # grid_sample expects coordinates in [-1, 1]
        normalize = torch.tensor([
            [2.0/W, 0, -1],
            [0, 2.0/H, -1],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        denormalize = torch.tensor([
            [W/2.0, 0, W/2.0],
            [0, H/2.0, H/2.0],
            [0, 0, 1]
        ], dtype=torch.float32, device=center.device)

        # Final matrix in normalized space
        matrix_normalized = normalize @ torch.inverse(matrix) @ denormalize

        # Extract [2, 3] affine matrix (drop last row)
        affine_matrix = matrix_normalized[:2, :]

        return affine_matrix

    def _apply_affine_transform(
        self,
        image: torch.Tensor,
        affine_matrix: torch.Tensor,
        filter: str,
        edge_mode: str
    ) -> torch.Tensor:
        """
        Apply affine transformation using grid_sample.

        Args:
            image: Input [B,C,H,W]
            affine_matrix: Affine transformation [2, 3]
            filter: Interpolation mode
            edge_mode: Padding mode

        Returns:
            Transformed image [B,C,H,W]
        """
        B, C, H, W = image.shape

        # Create affine grid
        # affine_grid expects [B, 2, 3] matrix
        affine_matrix_batch = affine_matrix.unsqueeze(0).repeat(B, 1, 1)

        grid = F.affine_grid(
            affine_matrix_batch,
            size=(B, C, H, W),
            align_corners=False
        )

        # Map filter mode
        if filter == "nearest":
            mode = "nearest"
        elif filter == "bilinear":
            mode = "bilinear"
        elif filter == "bicubic":
            mode = "bicubic"
        else:
            mode = "bilinear"

        # Map edge mode
        if edge_mode == "black":
            padding_mode = "zeros"
        elif edge_mode == "clamp":
            padding_mode = "border"
        elif edge_mode == "repeat":
            padding_mode = "reflection"  # Closest to repeat
        else:
            padding_mode = "zeros"

        # Apply transformation
        result = F.grid_sample(
            image,
            grid,
            mode=mode,
            padding_mode=padding_mode,
            align_corners=False
        )

        return result
