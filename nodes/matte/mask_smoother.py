"""
MaskSmoother node for ComfyUI_Detonate.

Applies professional bezier-style smoothing and edge refinement to masks.
Takes masks from ComfyUI's native drawing tools and refines them with
professional-grade edge quality, feathering, and smoothing.

This is the practical alternative to interactive rotoscoping - use ComfyUI's
existing mask drawing tools, then refine the edges here.

Nuke/Fusion equivalent: FilterErode + Blur (but with better edge quality)
"""

import torch
import numpy as np
import cv2
from typing import Tuple


class DetonateMaskSmoother:
    """
    Professional mask edge smoothing and refinement.

    Takes masks from ComfyUI's native tools and applies professional-grade
    edge smoothing, anti-aliasing, and feathering. Perfect for refining
    hand-drawn masks or AI-generated masks.

    Features:
    - Bezier-style edge smoothing (reduces jagged edges)
    - High-quality anti-aliasing
    - Professional feathering with multiple falloff curves
    - Edge contract/expand operations
    - Maintains fine detail while smoothing

    Workflow:
    1. Draw mask using ComfyUI's native mask tools
    2. Connect mask to this node
    3. Adjust smoothing and feathering
    4. Get professional-quality refined mask

    Common uses:
    - Refining hand-drawn masks
    - Smoothing AI-generated masks (SAM, etc.)
    - Creating soft edges for compositing
    - Converting rough masks to production quality
    - Fixing aliasing in masks
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
            "optional": {
                # Edge smoothing (reduces jaggies)
                "smooth_iterations": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Number of smoothing passes (0=off, 2=good balance, 5+=very smooth)"
                }),

                # Edge contract/expand
                "edge_adjust": ("FLOAT", {
                    "default": 0.0,
                    "min": -50.0,
                    "max": 50.0,
                    "step": 0.5,
                    "tooltip": "Contract (-) or expand (+) mask edge in pixels"
                }),

                # Feather amount
                "feather": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.5,
                    "tooltip": "Feather/soften edge in pixels"
                }),

                # Feather falloff type
                "feather_type": (["Smooth", "Linear", "Gaussian"], {
                    "default": "Smooth",
                    "tooltip": "Edge falloff curve: Smooth (natural), Linear (even), Gaussian (soft)"
                }),

                # Anti-aliasing quality
                "antialias_quality": (["Off", "Low", "Medium", "High"], {
                    "default": "Medium",
                    "tooltip": "Anti-aliasing quality (Off=1x, Low=2x, Medium=4x, High=8x)"
                }),

                # Invert
                "invert": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert mask after processing"
                }),
            }
        }

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "smooth_mask"

    def smooth_mask(
        self,
        mask: torch.Tensor,
        smooth_iterations: int = 2,
        edge_adjust: float = 0.0,
        feather: float = 0.0,
        feather_type: str = "Smooth",
        antialias_quality: str = "Medium",
        invert: bool = False
    ) -> Tuple[torch.Tensor]:
        """
        Apply professional edge smoothing and refinement to mask.

        Args:
            mask: Input mask tensor [B, H, W] or [H, W]
            smooth_iterations: Number of smoothing passes (0-10)
            edge_adjust: Contract (-) or expand (+) edge in pixels
            feather: Feather amount in pixels
            feather_type: Falloff curve (Smooth/Linear/Gaussian)
            antialias_quality: Anti-aliasing level (Off/Low/Medium/High)
            invert: Invert final mask

        Returns:
            Refined mask tensor [B, H, W]
        """
        # Handle batch dimension
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)  # [H, W] -> [1, H, W]

        B, H, W = mask.shape

        # Determine AA factor
        aa_factor_map = {
            "Off": 1,
            "Low": 2,
            "Medium": 4,
            "High": 8
        }
        aa_factor = aa_factor_map.get(antialias_quality, 4)

        # Process each mask in batch
        result_masks = []

        for i in range(B):
            mask_np = mask[i].cpu().numpy()

            # Upsample for anti-aliasing if enabled
            if aa_factor > 1:
                aa_h = H * aa_factor
                aa_w = W * aa_factor
                mask_np = cv2.resize(
                    mask_np,
                    (aa_w, aa_h),
                    interpolation=cv2.INTER_LINEAR
                )

            # Edge smoothing (bilateral-style filter preserves edges while smoothing)
            if smooth_iterations > 0:
                for _ in range(smooth_iterations):
                    # Use morphological closing + opening to smooth jagged edges
                    # while preserving overall shape
                    kernel_size = max(3, int(3 * aa_factor))
                    kernel = cv2.getStructuringElement(
                        cv2.MORPH_ELLIPSE,
                        (kernel_size, kernel_size)
                    )

                    # Close (fill small holes, smooth convex edges)
                    mask_np = cv2.morphologyEx(
                        mask_np,
                        cv2.MORPH_CLOSE,
                        kernel,
                        iterations=1
                    )

                    # Open (remove small protrusions, smooth concave edges)
                    mask_np = cv2.morphologyEx(
                        mask_np,
                        cv2.MORPH_OPEN,
                        kernel,
                        iterations=1
                    )

                    # Gentle Gaussian blur to further smooth
                    blur_size = max(3, int(3 * aa_factor))
                    if blur_size % 2 == 0:
                        blur_size += 1
                    mask_np = cv2.GaussianBlur(
                        mask_np,
                        (blur_size, blur_size),
                        sigmaX=0.5 * aa_factor
                    )

            # Edge adjust (contract/expand)
            if abs(edge_adjust) > 0.1:
                scaled_adjust = edge_adjust * aa_factor

                # Convert to binary for morphology
                binary_mask = (mask_np > 0.5).astype(np.uint8)

                if scaled_adjust > 0:
                    # Dilate (expand)
                    kernel_size = max(3, int(abs(scaled_adjust) * 2 + 1))
                    if kernel_size % 2 == 0:
                        kernel_size += 1
                    kernel = cv2.getStructuringElement(
                        cv2.MORPH_ELLIPSE,
                        (kernel_size, kernel_size)
                    )
                    binary_mask = cv2.dilate(
                        binary_mask,
                        kernel,
                        iterations=1
                    )
                else:
                    # Erode (contract)
                    kernel_size = max(3, int(abs(scaled_adjust) * 2 + 1))
                    if kernel_size % 2 == 0:
                        kernel_size += 1
                    kernel = cv2.getStructuringElement(
                        cv2.MORPH_ELLIPSE,
                        (kernel_size, kernel_size)
                    )
                    binary_mask = cv2.erode(
                        binary_mask,
                        kernel,
                        iterations=1
                    )

                mask_np = binary_mask.astype(np.float32)

            # Feathering using distance transform
            if feather > 0.1:
                mask_np = self._apply_feather(
                    mask_np,
                    feather * aa_factor,
                    feather_type
                )

            # Downsample if anti-aliasing was used
            if aa_factor > 1:
                mask_np = cv2.resize(
                    mask_np,
                    (W, H),
                    interpolation=cv2.INTER_AREA  # Best for downsampling
                )

            # Invert if requested
            if invert:
                mask_np = 1.0 - mask_np

            # Ensure range [0, 1]
            mask_np = np.clip(mask_np, 0.0, 1.0)

            result_masks.append(torch.from_numpy(mask_np))

        # Stack batch
        result = torch.stack(result_masks, dim=0)

        return (result,)

    def _apply_feather(
        self,
        mask: np.ndarray,
        feather_radius: float,
        feather_type: str = "Smooth"
    ) -> np.ndarray:
        """
        Apply feathering using distance transform.

        Args:
            mask: Input mask [H, W] in range [0, 1]
            feather_radius: Feather radius in pixels
            feather_type: Falloff curve type

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

        # Map distance to [0, 1] over feather range
        t = np.clip((sdf + feather_radius) / (2 * feather_radius), 0.0, 1.0)

        # Apply selected falloff curve
        if feather_type == "Linear":
            feathered = t
        elif feather_type == "Smooth":
            # Smoothstep for natural falloff
            feathered = t * t * (3.0 - 2.0 * t)
        elif feather_type == "Gaussian":
            # Gaussian falloff
            sigma = 1.0
            x = (t - 0.5) * 6.0
            feathered = np.exp(-0.5 * (x / sigma) ** 2)
            feathered = np.clip(feathered, 0.0, 1.0)
        else:
            feathered = t * t * (3.0 - 2.0 * t)

        return feathered.astype(np.float32)


class DetonateMaskFromColor:
    """
    Create mask from color selection (like Photoshop's color range).

    Select a color and tolerance to create a mask. Useful for quick
    selections and color-based masking.
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "color": ("STRING", {
                    "default": "#00FF00",
                    "tooltip": "Color to select (hex format)"
                }),
                "tolerance": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Color matching tolerance (0=exact, 1=loose)"
                }),
            },
            "optional": {
                "feather": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 50.0,
                    "step": 0.5
                }),
                "invert": ("BOOLEAN", {
                    "default": False
                }),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "create_mask"

    def create_mask(
        self,
        image: torch.Tensor,
        color: str,
        tolerance: float,
        feather: float = 2.0,
        invert: bool = False
    ) -> Tuple[torch.Tensor]:
        """
        Create mask by selecting a color range.

        Args:
            image: Input image [B, H, W, C]
            color: Target color (hex string like "#00FF00")
            tolerance: Color matching tolerance (0-1)
            feather: Edge feathering
            invert: Invert selection

        Returns:
            Mask tensor [B, H, W]
        """
        # Parse hex color
        color = color.lstrip('#')
        r = int(color[0:2], 16) / 255.0
        g = int(color[2:4], 16) / 255.0
        b = int(color[4:6], 16) / 255.0
        target_color = torch.tensor([r, g, b], device=image.device)

        B, H, W, C = image.shape

        # Compute color distance
        # Use Euclidean distance in RGB space
        diff = image[..., :3] - target_color.view(1, 1, 1, 3)
        distance = torch.sqrt(torch.sum(diff ** 2, dim=-1))

        # Normalize distance to [0, 1]
        # sqrt(3) is max possible distance in RGB cube
        distance = distance / 1.732

        # Convert to mask based on tolerance
        # tolerance=0 means exact match, tolerance=1 means everything
        mask = 1.0 - torch.clamp(distance / (tolerance + 0.001), 0.0, 1.0)

        # Apply feathering if requested
        if feather > 0.1:
            smoother = DetonateMaskSmoother()
            mask = smoother.smooth_mask(
                mask,
                smooth_iterations=0,
                edge_adjust=0.0,
                feather=feather,
                feather_type="Smooth",
                antialias_quality="Medium",
                invert=False
            )[0]

        # Invert if requested
        if invert:
            mask = 1.0 - mask

        return (mask,)
