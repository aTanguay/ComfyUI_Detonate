"""
TriMap Generator node for ComfyUI_Detonate.

Generate trimaps for AI inpainting workflows.
Trimaps help AI models understand what to keep, remove, and decide on.

Reference: Image matting workflows, AI inpainting best practices
"""

import torch
import numpy as np
import cv2
from typing import Tuple


class DetonateTriMapGenerator:
    """
    Generate trimaps for AI inpainting and matting workflows.

    A trimap divides an image into three regions:
    - Foreground (white, 1.0): Definitely keep this
    - Background (black, 0.0): Definitely remove this  
    - Unknown (gray, 0.5): AI should decide

    This is ESSENTIAL for high-quality AI inpainting because it tells
    the AI model exactly which areas need attention vs which are certain.

    Features:
    - Auto-generate trimap from alpha mask
    - Adjustable unknown region width
    - Threshold controls for foreground/background
    - Multiple unknown region modes
    - Handles anti-aliased edges properly

    Workflow:
    1. Input: Alpha mask from keyer, roto, or background removal
    2. Set thresholds (what's definitely fg/bg)
    3. Set unknown width (transition zone)
    4. Output: Trimap for AI inpainting

    Common uses:
    - Prepare masks for AI inpainting models
    - Image matting workflows
    - Refine background removal results
    - Guide AI models for better edge quality

    This node is UNIQUE to ComfyUI - no other equivalent exists.
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
            "optional": {
                "foreground_threshold": ("FLOAT", {
                    "default": 0.95,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Alpha above this = definite foreground (white)",
                }),
                "background_threshold": ("FLOAT", {
                    "default": 0.05,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Alpha below this = definite background (black)",
                }),
                "unknown_width": ("FLOAT", {
                    "default": 10.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.5,
                    "display": "slider",
                    "tooltip": "Width of unknown region around edges (pixels)",
                }),
                "unknown_mode": (["Edge Distance", "Threshold Only", "Full Unknown"], {
                    "default": "Edge Distance",
                    "tooltip": "How to generate unknown region",
                }),
                "output_format": (["Trimap (0/0.5/1)", "Visualization (RGB)"], {
                    "default": "Trimap (0/0.5/1)",
                    "tooltip": "Output as trimap or visual preview",
                }),
            },
        }

    RETURN_TYPES = ("MASK", "IMAGE")
    RETURN_NAMES = ("trimap", "preview")
    FUNCTION = "generate_trimap"

    def generate_trimap(
        self,
        mask: torch.Tensor,
        foreground_threshold: float = 0.95,
        background_threshold: float = 0.05,
        unknown_width: float = 10.0,
        unknown_mode: str = "Edge Distance",
        output_format: str = "Trimap (0/0.5/1)"
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generate trimap from alpha mask.

        Trimap format:
        - 1.0 (white) = Foreground (keep)
        - 0.0 (black) = Background (remove)
        - 0.5 (gray) = Unknown (AI decides)

        Args:
            mask: Input alpha mask [B, H, W]
            foreground_threshold: Alpha > this = foreground
            background_threshold: Alpha < this = background
            unknown_width: Width of unknown region (pixels)
            unknown_mode: How to generate unknown region
            output_format: Trimap or RGB visualization

        Returns:
            trimap: Trimap mask [B, H, W]
            preview: RGB visualization [B, H, W, 3]
        """
        device = mask.device
        B, H, W = mask.shape

        # Process each mask in batch
        trimaps = []
        previews = []

        for b in range(B):
            alpha = mask[b].cpu().numpy()  # [H, W]

            # Generate trimap
            if unknown_mode == "Threshold Only":
                trimap = self._threshold_trimap(
                    alpha,
                    foreground_threshold,
                    background_threshold
                )
            elif unknown_mode == "Full Unknown":
                trimap = self._full_unknown_trimap(
                    alpha,
                    foreground_threshold,
                    background_threshold
                )
            else:  # "Edge Distance"
                trimap = self._edge_distance_trimap(
                    alpha,
                    foreground_threshold,
                    background_threshold,
                    unknown_width
                )

            trimaps.append(torch.from_numpy(trimap).to(device))

            # Generate RGB preview
            preview = self._create_preview(trimap)
            previews.append(torch.from_numpy(preview).to(device))

        trimap_output = torch.stack(trimaps, dim=0)
        preview_output = torch.stack(previews, dim=0)

        return (trimap_output, preview_output)

    def _threshold_trimap(
        self,
        alpha: np.ndarray,
        fg_thresh: float,
        bg_thresh: float
    ) -> np.ndarray:
        """
        Simple threshold-based trimap.

        Args:
            alpha: Input alpha [H, W]
            fg_thresh: Foreground threshold
            bg_thresh: Background threshold

        Returns:
            Trimap [H, W] with values 0.0, 0.5, 1.0
        """
        trimap = np.full_like(alpha, 0.5, dtype=np.float32)  # Start with unknown

        # Foreground: alpha > fg_thresh
        trimap[alpha >= fg_thresh] = 1.0

        # Background: alpha < bg_thresh
        trimap[alpha <= bg_thresh] = 0.0

        return trimap

    def _full_unknown_trimap(
        self,
        alpha: np.ndarray,
        fg_thresh: float,
        bg_thresh: float
    ) -> np.ndarray:
        """
        Trimap with everything between thresholds as unknown.

        Args:
            alpha: Input alpha [H, W]
            fg_thresh: Foreground threshold
            bg_thresh: Background threshold

        Returns:
            Trimap [H, W] with values 0.0, 0.5, 1.0
        """
        trimap = np.full_like(alpha, 0.5, dtype=np.float32)

        # Foreground: alpha >= fg_thresh
        trimap[alpha >= fg_thresh] = 1.0

        # Background: alpha <= bg_thresh
        trimap[alpha <= bg_thresh] = 0.0

        # Everything else stays unknown (0.5)

        return trimap

    def _edge_distance_trimap(
        self,
        alpha: np.ndarray,
        fg_thresh: float,
        bg_thresh: float,
        unknown_width: float
    ) -> np.ndarray:
        """
        Generate trimap with unknown region based on distance from edges.

        This is the most useful mode - creates an unknown band around
        the foreground/background boundary.

        Args:
            alpha: Input alpha [H, W]
            fg_thresh: Foreground threshold
            bg_thresh: Background threshold
            unknown_width: Width of unknown region (pixels)

        Returns:
            Trimap [H, W] with values 0.0, 0.5, 1.0
        """
        # Start with threshold-based classification
        trimap = np.full_like(alpha, 0.5, dtype=np.float32)

        # Initial foreground and background
        fg_mask = (alpha >= fg_thresh).astype(np.uint8)
        bg_mask = (alpha <= bg_thresh).astype(np.uint8)

        if unknown_width < 0.1:
            # No unknown region, just use thresholds
            trimap[fg_mask == 1] = 1.0
            trimap[bg_mask == 1] = 0.0
            return trimap

        # Erode foreground to create unknown band
        kernel_size = int(unknown_width * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        kernel_size = max(3, kernel_size)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        iterations = max(1, int(unknown_width / 2))

        # Eroded foreground = definite foreground
        fg_eroded = cv2.erode(fg_mask, kernel, iterations=iterations)

        # Dilated background = definite background
        bg_dilated = cv2.dilate(bg_mask, kernel, iterations=iterations)

        # Apply to trimap
        trimap[fg_eroded == 1] = 1.0  # Definite foreground
        trimap[bg_dilated == 1] = 0.0  # Definite background
        # Everything else stays unknown (0.5)

        return trimap

    def _create_preview(self, trimap: np.ndarray) -> np.ndarray:
        """
        Create RGB visualization of trimap.

        Foreground = Green
        Background = Red
        Unknown = Blue

        Args:
            trimap: Trimap [H, W] with values 0.0, 0.5, 1.0

        Returns:
            RGB preview [H, W, 3]
        """
        H, W = trimap.shape
        preview = np.zeros((H, W, 3), dtype=np.float32)

        # Foreground = Green (0, 1, 0)
        fg_mask = trimap >= 0.9
        preview[fg_mask] = [0.0, 1.0, 0.0]

        # Background = Red (1, 0, 0)
        bg_mask = trimap <= 0.1
        preview[bg_mask] = [1.0, 0.0, 0.0]

        # Unknown = Blue (0, 0, 1)
        unknown_mask = (trimap > 0.1) & (trimap < 0.9)
        preview[unknown_mask] = [0.0, 0.0, 1.0]

        return preview
