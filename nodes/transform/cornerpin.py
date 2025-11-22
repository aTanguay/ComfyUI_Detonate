"""
CornerPin node for ComfyUI_Detonate.

4-point perspective transform for screen replacements and warping.
Essential for tracking and match-moving workflows.

Reference: Nuke CornerPin2D, After Effects Corner Pin
https://learn.foundry.com/nuke/content/reference_guide/transform_nodes/cornerpin.html
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor


class DetonateCornerPin:
    """
    4-point perspective transform (corner pinning).

    Maps four corner points to new positions using perspective
    transformation (homography). Essential for screen replacements,
    match-moving, and perspective correction.

    Solves for homography matrix H where:
    [x']   [h11 h12 h13]   [x]
    [y'] = [h21 h22 h23] * [y]
    [1 ]   [h31 h32  1 ]   [1]

    Common uses:
    - Screen replacements (phones, monitors, billboards)
    - Perspective correction
    - Match-moving integration
    - Planar tracking application
    - De-keystone correction

    Nuke/AE equivalent: CornerPin2D / Corner Pin Effect
    """

    CATEGORY = "detonate/transform"

    # Detonate improvement: Filter modes for sampling!
    FILTER_MODES = ["bilinear", "bicubic", "nearest"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Source corners (from image corners by default)
                "from_x1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_y1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_x2": ("FLOAT", {"default": 1920.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_y2": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_x3": ("FLOAT", {"default": 1920.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_y3": ("FLOAT", {"default": 1080.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_x4": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "from_y4": ("FLOAT", {"default": 1080.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                # Destination corners
                "to_x1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_y1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_x2": ("FLOAT", {"default": 1920.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_y2": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_x3": ("FLOAT", {"default": 1920.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_y3": ("FLOAT", {"default": 1080.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_x4": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "to_y4": ("FLOAT", {"default": 1080.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                # Filter mode (Detonate improvement!)
                "filter": (cls.FILTER_MODES, {
                    "default": "bilinear",
                }),
                # Inverse transform (Detonate improvement!)
                "invert": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "corner_pin"

    def corner_pin(
        self,
        image: torch.Tensor,
        from_x1: float = 0.0, from_y1: float = 0.0,
        from_x2: float = 1920.0, from_y2: float = 0.0,
        from_x3: float = 1920.0, from_y3: float = 1080.0,
        from_x4: float = 0.0, from_y4: float = 1080.0,
        to_x1: float = 0.0, to_y1: float = 0.0,
        to_x2: float = 1920.0, to_y2: float = 0.0,
        to_x3: float = 1920.0, to_y3: float = 1080.0,
        to_x4: float = 0.0, to_y4: float = 1080.0,
        filter: str = "bilinear",
        invert: bool = False
    ) -> tuple:
        """
        Apply 4-point perspective transform.

        Detonate improvements:
        1. Multiple filter modes (bilinear, bicubic, nearest)
        2. Inverse transformation
        3. Automatic homography calculation

        Args:
            image: Input tensor [B,H,W,C]
            from_x1, from_y1: Source corner 1 (top-left)
            from_x2, from_y2: Source corner 2 (top-right)
            from_x3, from_y3: Source corner 3 (bottom-right)
            from_x4, from_y4: Source corner 4 (bottom-left)
            to_x1, to_y1: Destination corner 1
            to_x2, to_y2: Destination corner 2
            to_x3, to_y3: Destination corner 3
            to_x4, to_y4: Destination corner 4
            filter: Interpolation filter mode
            invert: Invert transformation

        Returns:
            Tuple containing warped image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Define source and destination points
        src_points = torch.tensor([
            [from_x1, from_y1],
            [from_x2, from_y2],
            [from_x3, from_y3],
            [from_x4, from_y4],
        ], dtype=torch.float32)

        dst_points = torch.tensor([
            [to_x1, to_y1],
            [to_x2, to_y2],
            [to_x3, to_y3],
            [to_x4, to_y4],
        ], dtype=torch.float32)

        # Swap if inverted
        if invert:
            src_points, dst_points = dst_points, src_points

        # Calculate homography matrix
        H = self._compute_homography(src_points, dst_points)

        if H is None:
            # Failed to compute homography, return original
            return (image,)

        H = H.to(image.device)

        # Apply perspective transform
        result = self._apply_perspective_transform(image, H, filter)

        return (result,)

    def _compute_homography(
        self,
        src: torch.Tensor,
        dst: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute homography matrix from 4 point correspondences.

        Solves the equation: dst = H @ src
        Using Direct Linear Transform (DLT) algorithm.

        Args:
            src: Source points [4, 2]
            dst: Destination points [4, 2]

        Returns:
            Homography matrix [3, 3] or None if singular
        """
        # Build matrix A for DLT
        # For each point correspondence, we get 2 equations
        A = []
        for i in range(4):
            x, y = src[i]
            u, v = dst[i]

            # First equation
            A.append([-x, -y, -1, 0, 0, 0, u*x, u*y, u])
            # Second equation
            A.append([0, 0, 0, -x, -y, -1, v*x, v*y, v])

        A = torch.tensor(A, dtype=torch.float32)  # [8, 9]

        # Solve using SVD
        try:
            U, S, Vt = torch.linalg.svd(A)

            # Solution is last column of V (last row of Vt)
            h = Vt[-1, :]

            # Reshape to 3x3 matrix
            H = h.reshape(3, 3)

            # Normalize so that H[2, 2] = 1
            H = H / H[2, 2]

            return H

        except Exception:
            return None

    def _apply_perspective_transform(
        self,
        image: torch.Tensor,
        H: torch.Tensor,
        filter_mode: str
    ) -> torch.Tensor:
        """
        Apply perspective transformation using homography matrix.

        Uses grid_sample with computed transformation grid.

        Args:
            image: Input image [B,H,W,C]
            H: Homography matrix [3,3]
            filter_mode: Interpolation mode

        Returns:
            Warped image [B,H,W,C]
        """
        B, H, W, C = image.shape

        # Convert to [B,C,H,W] for grid_sample
        img_nchw = image.permute(0, 3, 1, 2)

        # Create coordinate grid
        y_coords = torch.linspace(0, H - 1, H, device=image.device)
        x_coords = torch.linspace(0, W - 1, W, device=image.device)
        y_grid, x_grid = torch.meshgrid(y_coords, x_coords, indexing='ij')

        # Stack to [H, W, 2]
        coords = torch.stack([x_grid, y_grid], dim=2)

        # Add homogeneous coordinate
        ones = torch.ones(H, W, 1, device=image.device)
        coords_homog = torch.cat([coords, ones], dim=2)  # [H, W, 3]

        # Flatten for matrix multiplication
        coords_flat = coords_homog.reshape(-1, 3).T  # [3, H*W]

        # Apply inverse homography: H_inv @ coords
        # (We want to find where each output pixel comes from in the source)
        H_inv = torch.inverse(H)
        H_inv = H_inv.to(image.device)

        transformed = H_inv @ coords_flat  # [3, H*W]

        # Convert from homogeneous coordinates
        transformed = transformed.T  # [H*W, 3]
        transformed_x = transformed[:, 0] / (transformed[:, 2] + 1e-8)
        transformed_y = transformed[:, 1] / (transformed[:, 2] + 1e-8)

        # Reshape to [H, W]
        transformed_x = transformed_x.reshape(H, W)
        transformed_y = transformed_y.reshape(H, W)

        # Normalize to [-1, 1] range for grid_sample
        norm_x = 2.0 * transformed_x / (W - 1) - 1.0
        norm_y = 2.0 * transformed_y / (H - 1) - 1.0

        # Stack to grid [H, W, 2]
        grid = torch.stack([norm_x, norm_y], dim=2)

        # Expand for batch
        grid = grid.unsqueeze(0).repeat(B, 1, 1, 1)  # [B, H, W, 2]

        # Map filter mode to grid_sample mode
        if filter_mode == "bicubic":
            mode = "bicubic"
        elif filter_mode == "nearest":
            mode = "nearest"
        else:
            mode = "bilinear"

        # Apply grid sampling
        warped_nchw = F.grid_sample(
            img_nchw,
            grid,
            mode=mode,
            padding_mode='zeros',
            align_corners=True
        )

        # Convert back to [B,H,W,C]
        result = warped_nchw.permute(0, 2, 3, 1)

        return result
