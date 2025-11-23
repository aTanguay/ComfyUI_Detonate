"""
GridWarp node for ComfyUI_Detonate.

Mesh-based image warping with control grid.
Professional tool for perspective correction and creative warping.

Reference: Nuke GridWarp, After Effects Mesh Warp, Fusion GridWarp
"""

import torch
import numpy as np
import cv2
from typing import Tuple, List
import json


class DetonateGridWarp:
    """
    Mesh-based image warping with control grid.

    Warps images using a deformable control grid (mesh).
    Essential for perspective correction, lens distortion,
    creative warping, and manual image manipulation.

    Features:
    - Grid-based mesh warping
    - Adjustable grid resolution (4x4 to 32x32)
    - Smooth interpolation (bilinear)
    - JSON grid data for persistence
    - Multiple edge modes

    Workflow:
    1. Define grid resolution (e.g., 8x8)
    2. Set grid point offsets (JSON data)
    3. Choose interpolation quality
    4. Apply warp to image

    Common uses:
    - Perspective correction
    - Lens distortion correction
    - Creative image warping
    - Building/object straightening
    - Puppet warp effects

    Nuke equivalent: GridWarp
    Fusion equivalent: GridWarp
    """

    CATEGORY = "detonate/transform"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "grid_resolution_x": ("INT", {
                    "default": 8,
                    "min": 2,
                    "max": 32,
                    "step": 1,
                    "tooltip": "Horizontal grid resolution (control points)",
                }),
                "grid_resolution_y": ("INT", {
                    "default": 8,
                    "min": 2,
                    "max": 32,
                    "step": 1,
                    "tooltip": "Vertical grid resolution (control points)",
                }),
                "grid_data": ("STRING", {
                    "default": '{"offsets":[]}',
                    "multiline": False,
                    "tooltip": "JSON grid point offsets [{'x': col, 'y': row, 'dx': offset_x, 'dy': offset_y}, ...]",
                }),
            },
            "optional": {
                "edge_mode": (["Clamp", "Black"], {
                    "default": "Clamp",
                    "tooltip": "Edge behavior: Clamp (stretch edges) or Black",
                }),
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Warp strength multiplier",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output",)
    FUNCTION = "grid_warp"

    def grid_warp(
        self,
        image: torch.Tensor,
        grid_resolution_x: int,
        grid_resolution_y: int,
        grid_data: str,
        edge_mode: str = "Clamp",
        strength: float = 1.0
    ) -> Tuple[torch.Tensor]:
        """
        Apply mesh-based grid warping to image.

        Args:
            image: Input image [B, H, W, C]
            grid_resolution_x: Grid columns (control points)
            grid_resolution_y: Grid rows (control points)
            grid_data: JSON string with grid point offsets
            edge_mode: Edge handling (Clamp/Black)
            strength: Warp strength multiplier

        Returns:
            Warped image [B, H, W, C]
        """
        device = image.device
        B, H, W, C = image.shape

        # Parse grid data
        try:
            data = json.loads(grid_data)
            offsets = data.get('offsets', [])
        except json.JSONDecodeError:
            # Invalid JSON, return unchanged
            return (image,)

        if len(offsets) == 0:
            # No grid deformation, return unchanged
            return (image,)

        # Create initial grid (uniform)
        grid_x = np.linspace(0, W - 1, grid_resolution_x, dtype=np.float32)
        grid_y = np.linspace(0, H - 1, grid_resolution_y, dtype=np.float32)

        # Create mesh grid [rows, cols]
        src_points = np.zeros((grid_resolution_y, grid_resolution_x, 2), dtype=np.float32)
        dst_points = np.zeros((grid_resolution_y, grid_resolution_x, 2), dtype=np.float32)

        for row in range(grid_resolution_y):
            for col in range(grid_resolution_x):
                x = grid_x[col]
                y = grid_y[row]

                src_points[row, col] = [x, y]
                dst_points[row, col] = [x, y]  # Start with identity

        # Apply offsets from grid data
        for offset_data in offsets:
            col = offset_data.get('x', -1)
            row = offset_data.get('y', -1)
            dx = offset_data.get('dx', 0.0) * strength
            dy = offset_data.get('dy', 0.0) * strength

            if 0 <= row < grid_resolution_y and 0 <= col < grid_resolution_x:
                dst_points[row, col, 0] += dx
                dst_points[row, col, 1] += dy

        # Process each image in batch
        result = []
        for b in range(B):
            img_np = image[b].cpu().numpy()

            # Create warp map using piecewise affine transformation
            warped = self._apply_grid_warp(
                img_np,
                src_points,
                dst_points,
                grid_resolution_x,
                grid_resolution_y,
                edge_mode
            )

            result.append(torch.from_numpy(warped).to(device))

        output = torch.stack(result, dim=0)

        return (output,)

    def _apply_grid_warp(
        self,
        image: np.ndarray,
        src_points: np.ndarray,
        dst_points: np.ndarray,
        grid_cols: int,
        grid_rows: int,
        edge_mode: str
    ) -> np.ndarray:
        """
        Apply piecewise affine warp using grid control points.

        Uses OpenCV's remap with piecewise affine approximation.

        Args:
            image: Input image [H, W, C]
            src_points: Source grid points [rows, cols, 2]
            dst_points: Destination grid points [rows, cols, 2]
            grid_cols: Grid columns
            grid_rows: Grid rows
            edge_mode: Edge handling

        Returns:
            Warped image [H, W, C]
        """
        H, W = image.shape[:2]

        # Create dense displacement map from sparse grid
        # For each pixel, find which grid cell it's in and interpolate

        # Create pixel coordinate grid
        y_coords, x_coords = np.meshgrid(
            np.arange(H, dtype=np.float32),
            np.arange(W, dtype=np.float32),
            indexing='ij'
        )

        # Initialize displacement maps
        map_x = np.zeros((H, W), dtype=np.float32)
        map_y = np.zeros((H, W), dtype=np.float32)

        # For each grid cell, compute piecewise affine transform
        for row in range(grid_rows - 1):
            for col in range(grid_cols - 1):
                # Get quad corners (source and destination)
                src_quad = np.array([
                    src_points[row, col],
                    src_points[row, col + 1],
                    src_points[row + 1, col + 1],
                    src_points[row + 1, col]
                ], dtype=np.float32)

                dst_quad = np.array([
                    dst_points[row, col],
                    dst_points[row, col + 1],
                    dst_points[row + 1, col + 1],
                    dst_points[row + 1, col]
                ], dtype=np.float32)

                # Get bounding box of source quad
                x_min = int(np.floor(src_quad[:, 0].min()))
                x_max = int(np.ceil(src_quad[:, 0].max()))
                y_min = int(np.floor(src_quad[:, 1].min()))
                y_max = int(np.ceil(src_quad[:, 1].max()))

                # Clamp to image bounds
                x_min = max(0, x_min)
                x_max = min(W, x_max)
                y_min = max(0, y_min)
                y_max = min(H, y_max)

                if x_max <= x_min or y_max <= y_min:
                    continue

                # Compute perspective transform for this quad
                # Use first 3 points for affine (faster than full perspective)
                M = cv2.getAffineTransform(src_quad[:3], dst_quad[:3])

                # Apply transform to pixels in this cell
                for y in range(y_min, y_max):
                    for x in range(x_min, x_max):
                        # Check if point is inside quad (simple bbox check for speed)
                        # For production, could use proper point-in-polygon
                        if (src_quad[0, 0] <= x <= src_quad[1, 0] and
                            src_quad[0, 1] <= y <= src_quad[2, 1]):

                            # Apply affine transform
                            src_pt = np.array([x, y, 1], dtype=np.float32)
                            dst_pt = M @ src_pt

                            map_x[y, x] = dst_pt[0]
                            map_y[y, x] = dst_pt[1]

        # Fill any unmapped pixels with identity (edge cases)
        unmapped = (map_x == 0) & (map_y == 0)
        map_x[unmapped] = x_coords[unmapped]
        map_y[unmapped] = y_coords[unmapped]

        # Apply warp using remap
        if edge_mode == "Black":
            border_mode = cv2.BORDER_CONSTANT
        else:  # Clamp
            border_mode = cv2.BORDER_REPLICATE

        warped = cv2.remap(
            image,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=border_mode,
            borderValue=0.0
        )

        return warped
