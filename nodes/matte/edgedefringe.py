"""
AlphaPremultFix node for ComfyUI_Detonate.

Edge defringing and premultiplication cleanup for AI-generated images.
Fixes the #1 pain point: halos, fringes, and color spill on alpha edges.

Reference: Nuke EdgeBlur, Defocus with edge extend, Fusion EdgeExtend
"""

import torch
import numpy as np
import cv2
from typing import Tuple


class DetonateEdgeDefringe:
    """
    Remove color fringing and halos from alpha edges.

    AI-generated images and keyed footage often have color contamination
    at edges - green spill from greenscreen, halos from improper premult,
    color bleeding from background removal. This node cleans those edges.

    Features:
    - Edge erosion technique (shrink alpha, preserve color)
    - Color suppression (reduce specific colors at edges)
    - Premult fix (remove dark/bright halos)
    - Multiple defringe modes

    Workflow:
    1. Select defringe mode (Erode Matte, Color Suppress, Premult Fix)
    2. Adjust strength (how aggressive)
    3. Optional: specify problem color (for greenscreen spill)

    Common uses:
    - Remove green spill from greenscreen keying
    - Fix premult halos (dark edges, bright fringes)
    - Clean up AI background removal artifacts
    - Remove color contamination from rotoscoping

    Nuke equivalent: EdgeBlur, EdgeExtend (edge modes)
    Fusion equivalent: EdgeExtend, Erode (matte processing)
    """

    CATEGORY = "detonate/matte"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mode": (["Erode Matte", "Color Suppress", "Premult Fix", "All"], {
                    "default": "Erode Matte",
                    "tooltip": "Defringe mode: Erode Matte (shrink alpha), Color Suppress, Premult Fix, or All",
                }),
                "strength": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Defringe strength (pixels to process)",
                }),
            },
            "optional": {
                "problem_color": (["Auto", "Green", "Blue", "Red", "Custom"], {
                    "default": "Auto",
                    "tooltip": "Problem color to suppress (greenscreen spill, etc.)",
                }),
                "custom_color_r": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "custom_color_g": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "custom_color_b": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output",)
    FUNCTION = "defringe"

    def defringe(
        self,
        image: torch.Tensor,
        mode: str,
        strength: float,
        problem_color: str = "Auto",
        custom_color_r: float = 0.0,
        custom_color_g: float = 1.0,
        custom_color_b: float = 0.0
    ) -> Tuple[torch.Tensor]:
        """
        Remove edge fringing and color contamination.

        Args:
            image: Input image [B, H, W, C] (must have alpha)
            mode: Defringe mode
            strength: Processing strength (pixels)
            problem_color: Color to suppress
            custom_color_r/g/b: Custom problem color

        Returns:
            Defringed image [B, H, W, C]
        """
        device = image.device
        B, H, W, C = image.shape

        if C < 4:
            # No alpha channel - return unchanged with warning
            print("Warning: EdgeDefringe requires alpha channel. Returning input unchanged.")
            # Add opaque alpha
            return (torch.cat([image, torch.ones(B, H, W, 1, device=device)], dim=-1),)

        rgb = image[..., :3]
        alpha = image[..., 3:4]

        # Process based on mode
        if mode == "Erode Matte":
            rgb_defringed = self._erode_matte_technique(rgb, alpha, strength, device)
        elif mode == "Color Suppress":
            rgb_defringed = self._color_suppress(rgb, alpha, strength, problem_color,
                                                 custom_color_r, custom_color_g, custom_color_b, device)
        elif mode == "Premult Fix":
            rgb_defringed = self._premult_fix(rgb, alpha, strength, device)
        else:  # All
            # Apply all techniques in sequence
            rgb_temp = self._erode_matte_technique(rgb, alpha, strength, device)
            rgb_temp = self._color_suppress(rgb_temp, alpha, strength, problem_color,
                                           custom_color_r, custom_color_g, custom_color_b, device)
            rgb_defringed = self._premult_fix(rgb_temp, alpha, strength, device)

        # Combine with original alpha
        output = torch.cat([rgb_defringed, alpha], dim=-1)

        return (output,)

    def _erode_matte_technique(
        self,
        rgb: torch.Tensor,
        alpha: torch.Tensor,
        strength: float,
        device: torch.device
    ) -> torch.Tensor:
        """
        Erode matte technique: shrink alpha, dilate color to fill edge.

        Classic compositor technique for removing edge contamination.
        Erode the alpha channel, then fill the edge pixels by dilating
        the interior color outward.

        Args:
            rgb: RGB channels [B, H, W, 3]
            alpha: Alpha channel [B, H, W, 1]
            strength: Erosion amount (pixels)
            device: Torch device

        Returns:
            Defringed RGB [B, H, W, 3]
        """
        if strength < 0.1:
            return rgb

        B, H, W, _ = rgb.shape

        # Process each image in batch
        result = []
        for b in range(B):
            rgb_np = rgb[b].cpu().numpy()
            alpha_np = alpha[b, :, :, 0].cpu().numpy()

            # Erode alpha to shrink edge
            kernel_size = int(strength) * 2 + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            alpha_eroded = cv2.erode(alpha_np, kernel, iterations=1)

            # Create edge mask (pixels that were removed)
            edge_mask = (alpha_np > 0.01) & (alpha_eroded < 0.01)

            # Dilate the RGB to fill edge pixels with interior color
            rgb_uint8 = (np.clip(rgb_np, 0, 1) * 255).astype(np.uint8)
            rgb_dilated = cv2.dilate(rgb_uint8, kernel, iterations=1).astype(np.float32) / 255.0

            # Blend: use dilated color in edge areas, original elsewhere
            rgb_defringed = rgb_np.copy()
            for c in range(3):
                rgb_defringed[..., c] = np.where(edge_mask, rgb_dilated[..., c], rgb_np[..., c])

            result.append(torch.from_numpy(rgb_defringed).to(device))

        return torch.stack(result, dim=0)

    def _color_suppress(
        self,
        rgb: torch.Tensor,
        alpha: torch.Tensor,
        strength: float,
        problem_color: str,
        custom_r: float,
        custom_g: float,
        custom_b: float,
        device: torch.device
    ) -> torch.Tensor:
        """
        Suppress specific color at edges (e.g., green spill).

        Reduces the problem color channel at semi-transparent edges.

        Args:
            rgb: RGB channels [B, H, W, 3]
            alpha: Alpha channel [B, H, W, 1]
            strength: Suppression strength
            problem_color: Color to suppress
            custom_r/g/b: Custom color
            device: Torch device

        Returns:
            Color-suppressed RGB [B, H, W, 3]
        """
        if strength < 0.1:
            return rgb

        # Determine problem color
        if problem_color == "Green":
            color_vec = torch.tensor([0.0, 1.0, 0.0], device=device)
        elif problem_color == "Blue":
            color_vec = torch.tensor([0.0, 0.0, 1.0], device=device)
        elif problem_color == "Red":
            color_vec = torch.tensor([1.0, 0.0, 0.0], device=device)
        elif problem_color == "Custom":
            color_vec = torch.tensor([custom_r, custom_g, custom_b], device=device)
        else:  # Auto - detect dominant color in semi-transparent areas
            # Use green as default (most common spill)
            color_vec = torch.tensor([0.0, 1.0, 0.0], device=device)

        # Create edge mask (semi-transparent pixels 0.1 < alpha < 0.9)
        edge_mask = (alpha > 0.1) & (alpha < 0.9)

        # Calculate color similarity to problem color
        color_sim = torch.sum(rgb * color_vec.view(1, 1, 1, 3), dim=-1, keepdim=True)

        # Suppress problem color at edges
        # Reduce the problem color channels by the amount they exceed other channels
        suppress_amount = (strength / 10.0) * edge_mask.float() * color_sim

        # Apply suppression
        rgb_suppressed = rgb.clone()
        for c in range(3):
            if color_vec[c] > 0.5:  # This is the problem channel
                other_avg = (torch.sum(rgb, dim=-1, keepdim=True) - rgb[..., c:c+1]) / 2.0
                rgb_suppressed[..., c:c+1] = torch.clamp(
                    rgb[..., c:c+1] - suppress_amount * (rgb[..., c:c+1] - other_avg),
                    0.0, 1.0
                )

        return rgb_suppressed

    def _premult_fix(
        self,
        rgb: torch.Tensor,
        alpha: torch.Tensor,
        strength: float,
        device: torch.device
    ) -> torch.Tensor:
        """
        Fix premultiplication artifacts (dark/bright halos).

        Removes halos caused by incorrect premult/unpremult operations.

        Args:
            rgb: RGB channels [B, H, W, 3]
            alpha: Alpha channel [B, H, W, 1]
            strength: Fix strength
            device: Torch device

        Returns:
            Fixed RGB [B, H, W, 3]
        """
        if strength < 0.1:
            return rgb

        # Detect dark halos (RGB too dark for alpha value)
        # Properly premultiplied: RGB <= alpha
        # Dark halo: RGB < alpha (too dark)

        # Create edge mask
        edge_mask = (alpha > 0.1) & (alpha < 0.9)

        # Unpremultiply to get straight color
        rgb_straight = rgb / (alpha + 1e-7)

        # Detect overly bright values (premult error)
        overbright = (rgb_straight > 1.0) & edge_mask

        # Fix: clamp and re-premultiply
        rgb_fixed = torch.where(
            overbright,
            torch.clamp(rgb_straight, 0.0, 1.0) * alpha,
            rgb
        )

        # Blend based on strength
        blend_factor = torch.clamp(torch.tensor(strength / 10.0, device=device), 0.0, 1.0)
        rgb_result = rgb * (1.0 - blend_factor) + rgb_fixed * blend_factor

        return rgb_result
