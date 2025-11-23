"""
MatteControl node for ComfyUI_Detonate.

All-in-one professional matte refinement tool.
Essential compositor workflow: clean up mattes in a single node.

Reference: Nuke FilterErode + Blur combo, Fusion MatteControl
"""

import torch
import numpy as np
import cv2
from typing import Tuple


class DetonateMatteControl:
    """
    Professional all-in-one matte refinement tool.

    Combines the most common matte operations in proper order:
    1. Contract/Expand (erode/dilate)
    2. Blur edges
    3. Gamma correction
    4. Black/White point clipping

    This is the #1 requested matte tool by compositors - replaces
    chains of 4-5 nodes with a single professional control.

    Features:
    - Erode/Dilate with adjustable size
    - Edge blur (Gaussian)
    - Gamma correction for matte density
    - Black point / White point clipping
    - Proper operation ordering
    - Preview modes for each stage

    Workflow:
    1. Contract/expand to fix edge contamination
    2. Blur to soften edges
    3. Gamma to adjust overall density
    4. Black/white points to clean up values

    Common uses:
    - Clean up keyer output
    - Refine rotoscoped mattes
    - Fix AI-generated masks
    - Prepare mattes for compositing

    Nuke equivalent: FilterErode + Blur + Grade combo
    Fusion equivalent: MatteControl
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
            "optional": {
                "erode_dilate": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Negative = contract (erode), Positive = expand (dilate)",
                }),
                "blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Blur amount for softening edges",
                }),
                "gamma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Gamma correction (< 1 = lighter, > 1 = darker)",
                }),
                "black_point": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "display": "slider",
                    "tooltip": "Values below this become black (0.0)",
                }),
                "white_point": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "display": "slider",
                    "tooltip": "Values above this become white (1.0)",
                }),
                "preview_mode": (["Final", "After Erode/Dilate", "After Blur", "After Gamma"], {
                    "default": "Final",
                    "tooltip": "Preview intermediate stages of processing",
                }),
            },
        }

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "refine_matte"

    def refine_matte(
        self,
        mask: torch.Tensor,
        erode_dilate: float = 0.0,
        blur: float = 0.0,
        gamma: float = 1.0,
        black_point: float = 0.0,
        white_point: float = 1.0,
        preview_mode: str = "Final"
    ) -> Tuple[torch.Tensor]:
        """
        Refine matte using professional matte control operations.

        Processing order:
        1. Erode/Dilate (contract/expand edges)
        2. Blur (soften edges)
        3. Gamma (adjust overall density)
        4. Black/White point (clip values)

        Args:
            mask: Input mask [B, H, W]
            erode_dilate: Erode (negative) or dilate (positive) amount
            blur: Gaussian blur radius
            gamma: Gamma correction
            black_point: Values below this become 0.0
            white_point: Values above this become 1.0
            preview_mode: Show intermediate stage or final result

        Returns:
            Refined mask [B, H, W]
        """
        device = mask.device
        B, H, W = mask.shape

        # Process each mask in batch
        result = []
        for b in range(B):
            matte = mask[b].cpu().numpy()  # [H, W]

            # Stage 1: Erode/Dilate
            if abs(erode_dilate) > 0.01:
                matte = self._erode_dilate(matte, erode_dilate)

            if preview_mode == "After Erode/Dilate":
                result.append(torch.from_numpy(matte).to(device))
                continue

            # Stage 2: Blur
            if blur > 0.01:
                matte = self._blur(matte, blur)

            if preview_mode == "After Blur":
                result.append(torch.from_numpy(matte).to(device))
                continue

            # Stage 3: Gamma
            if abs(gamma - 1.0) > 0.001:
                matte = self._gamma_correct(matte, gamma)

            if preview_mode == "After Gamma":
                result.append(torch.from_numpy(matte).to(device))
                continue

            # Stage 4: Black/White point clipping
            if abs(black_point) > 0.001 or abs(white_point - 1.0) > 0.001:
                matte = self._clip_levels(matte, black_point, white_point)

            # Final result
            result.append(torch.from_numpy(matte).to(device))

        output = torch.stack(result, dim=0)

        return (output,)

    def _erode_dilate(self, matte: np.ndarray, amount: float) -> np.ndarray:
        """
        Erode (shrink) or dilate (expand) the matte.

        Args:
            matte: Input matte [H, W]
            amount: Negative = erode, Positive = dilate

        Returns:
            Processed matte [H, W]
        """
        if abs(amount) < 0.01:
            return matte

        # Convert to uint8 for OpenCV morphological operations
        matte_uint8 = (np.clip(matte, 0, 1) * 255).astype(np.uint8)

        # Create kernel
        kernel_size = int(abs(amount) * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1  # Must be odd
        kernel_size = max(3, kernel_size)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))

        # Apply erosion or dilation
        if amount < 0:
            # Erode (contract)
            iterations = max(1, int(abs(amount) / 2))
            processed = cv2.erode(matte_uint8, kernel, iterations=iterations)
        else:
            # Dilate (expand)
            iterations = max(1, int(amount / 2))
            processed = cv2.dilate(matte_uint8, kernel, iterations=iterations)

        # Convert back to float
        return processed.astype(np.float32) / 255.0

    def _blur(self, matte: np.ndarray, blur_radius: float) -> np.ndarray:
        """
        Apply Gaussian blur to soften matte edges.

        Args:
            matte: Input matte [H, W]
            blur_radius: Blur radius in pixels

        Returns:
            Blurred matte [H, W]
        """
        if blur_radius < 0.01:
            return matte

        # Calculate kernel size (must be odd)
        kernel_size = int(blur_radius * 2) * 2 + 1
        kernel_size = max(3, kernel_size)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(
            matte,
            (kernel_size, kernel_size),
            sigmaX=blur_radius,
            sigmaY=blur_radius
        )

        return blurred

    def _gamma_correct(self, matte: np.ndarray, gamma: float) -> np.ndarray:
        """
        Apply gamma correction to adjust matte density.

        Args:
            matte: Input matte [H, W]
            gamma: Gamma value (< 1 = lighter, > 1 = darker)

        Returns:
            Gamma-corrected matte [H, W]
        """
        if abs(gamma - 1.0) < 0.001:
            return matte

        # Clamp to valid range before gamma
        matte = np.clip(matte, 0.0, 1.0)

        # Apply gamma correction
        corrected = np.power(matte, gamma)

        return corrected

    def _clip_levels(
        self,
        matte: np.ndarray,
        black_point: float,
        white_point: float
    ) -> np.ndarray:
        """
        Clip black and white points to clean up matte values.

        Args:
            matte: Input matte [H, W]
            black_point: Values below this become 0.0
            white_point: Values above this become 1.0

        Returns:
            Clipped matte [H, W]
        """
        # Ensure black_point < white_point
        if black_point >= white_point:
            white_point = black_point + 0.001

        # Remap values
        # Values below black_point → 0.0
        # Values above white_point → 1.0
        # Values between → linear remap to 0-1
        clipped = np.clip((matte - black_point) / (white_point - black_point + 1e-7), 0.0, 1.0)

        return clipped
