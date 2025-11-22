"""
Merge node for ComfyUI_Detonate.

Core compositing node with industry-standard blend modes.
Combines foreground and background images using various algorithms.

Reference: Natron Merge node, Porter-Duff compositing
https://natron.readthedocs.io/en/rb-2.5/plugins/net.sf.openfx.MergePlugin.html
https://github.com/devernay/openfx-supportext/blob/master/ofxsMerging.h
"""

import torch
from ...utils import (
    validate_image_tensor,
    ensure_alpha_channel,
    resize_tensors_to_match,
)


class DetonateMerge:
    """
    Merge/composite two images using various blend modes.

    Implements industry-standard Porter-Duff compositing operations
    and blend modes. Expects premultiplied alpha inputs for accurate
    compositing (use Premultiply node if needed).

    Common operations:
    - Over: Standard compositing (A over B)
    - Under: A under B
    - Plus: Additive blending
    - Screen: Lighten blend
    - Multiply: Darken blend

    Nuke/Fusion equivalent: Merge node
    """

    CATEGORY = "detonate/compositing"

    # Blend mode options (Priority 1 - most common)
    BLEND_MODES = [
        "over",
        "under",
        "plus",
        "screen",
        "multiply",
        "stencil",
        "mask",
        "atop",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "foreground": ("IMAGE",),
                "background": ("IMAGE",),
                "operation": (cls.BLEND_MODES, {
                    "default": "over",
                }),
            },
            "optional": {
                "mix": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "mask": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "merge"

    def merge(
        self,
        foreground: torch.Tensor,
        background: torch.Tensor,
        operation: str,
        mix: float = 1.0,
        mask: torch.Tensor = None
    ) -> tuple:
        """
        Merge two images using specified blend mode.

        Args:
            foreground: Foreground (A) image [B,H,W,C]
            background: Background (B) image [B,H,W,C]
            operation: Blend mode to use
            mix: Blend factor 0.0-1.0
            mask: Optional mask image [B,H,W,C] or [B,H,W,1]

        Returns:
            Tuple containing merged image [B,H,W,4]
        """
        validate_image_tensor(foreground, "foreground")
        validate_image_tensor(background, "background")

        # Ensure both images have alpha
        fg = ensure_alpha_channel(foreground, alpha_value=1.0)
        bg = ensure_alpha_channel(background, alpha_value=1.0)

        # Resize to match if needed
        fg, bg = resize_tensors_to_match(fg, bg)

        # Apply blend mode
        if operation == "over":
            result = self._blend_over(fg, bg)
        elif operation == "under":
            result = self._blend_under(fg, bg)
        elif operation == "plus":
            result = self._blend_plus(fg, bg)
        elif operation == "screen":
            result = self._blend_screen(fg, bg)
        elif operation == "multiply":
            result = self._blend_multiply(fg, bg)
        elif operation == "stencil":
            result = self._blend_stencil(fg, bg)
        elif operation == "mask":
            result = self._blend_mask(fg, bg)
        elif operation == "atop":
            result = self._blend_atop(fg, bg)
        else:
            raise ValueError(f"Unknown blend mode: {operation}")

        # Apply mix if not 1.0
        if mix < 1.0:
            result = bg * (1.0 - mix) + result * mix

        # Apply mask if provided
        if mask is not None:
            validate_image_tensor(mask, "mask")
            mask = ensure_alpha_channel(mask, alpha_value=1.0)

            # Resize mask if needed
            if mask.shape[:3] != result.shape[:3]:
                from ...utils import resize_tensor
                B, H, W, _ = result.shape
                mask = resize_tensor(mask, H, W)

            # Use mask's first channel (or average all channels)
            # as the mask value
            if mask.shape[3] == 4:
                mask_value = mask[:, :, :, :1]  # Use first channel
            else:
                mask_value = mask

            # Blend: result where mask is white, bg where mask is black
            result = bg * (1.0 - mask_value) + result * mask_value

        return (result,)

    def _blend_over(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Over blend mode (A over B).

        Formula: result = A + B * (1 - A.alpha)

        This is the standard compositing operation.
        Assumes premultiplied alpha.

        Args:
            fg: Foreground [B,H,W,4] (premultiplied)
            bg: Background [B,H,W,4] (premultiplied)

        Returns:
            Composited result [B,H,W,4]
        """
        fg_alpha = fg[:, :, :, 3:4]

        # result = fg + bg * (1 - fg_alpha)
        result_rgb = fg[:, :, :, :3] + bg[:, :, :, :3] * (1.0 - fg_alpha)
        result_alpha = fg_alpha + bg[:, :, :, 3:4] * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_under(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Under blend mode (A under B).

        Formula: result = B + A * (1 - B.alpha)

        Places A under B (swap fg and bg in over operation).

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Composited result [B,H,W,4]
        """
        # Under is just Over with fg/bg swapped
        return self._blend_over(bg, fg)

    def _blend_plus(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Plus blend mode (additive).

        Formula: result = A + B

        Adds pixel values. Great for lights, glows, and effects.
        Can produce values > 1.0 (float images support this).

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Additive result [B,H,W,4]
        """
        return fg + bg

    def _blend_screen(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Screen blend mode.

        Formula: result = 1 - (1 - A) * (1 - B)

        Lightens image. Popular for highlights and glows.
        Always produces lighter or equal result.

        Note: For premultiplied images, we need to unpremultiply,
        screen, then repremultiply. For now, applying to RGB directly
        as a simplified approach.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Screen result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Screen blend: 1 - (1-A)*(1-B)
        result_rgb = 1.0 - (1.0 - fg_rgb) * (1.0 - bg_rgb)

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_multiply(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Multiply blend mode.

        Formula: result = A * B

        Darkens image. Ideal for shadows and darkening.
        Always produces darker or equal result.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Multiply result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Multiply blend
        result_rgb = fg_rgb * bg_rgb

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_stencil(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Stencil blend mode.

        Uses A's alpha to cut a hole in B.
        Where A.alpha is 1, result is transparent.
        Where A.alpha is 0, result is B.

        Formula: result = B * (1 - A.alpha)

        Args:
            fg: Foreground [B,H,W,4] (used for alpha only)
            bg: Background [B,H,W,4]

        Returns:
            Stencil result [B,H,W,4]
        """
        fg_alpha = fg[:, :, :, 3:4]

        # Cut hole in bg using fg's alpha
        result_rgb = bg[:, :, :, :3] * (1.0 - fg_alpha)
        result_alpha = bg[:, :, :, 3:4] * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_mask(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Mask blend mode.

        Intersect A and B's alphas.
        Shows A only where both A and B have alpha.

        Formula: result.rgb = A.rgb, result.alpha = A.alpha * B.alpha

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Masked result [B,H,W,4]
        """
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        result_rgb = fg[:, :, :, :3]
        result_alpha = fg_alpha * bg_alpha

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_atop(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Atop blend mode.

        Composite A over B only where B has alpha.
        Outside B's alpha, shows B.

        Formula: result = A * B.alpha + B * (1 - A.alpha)

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Atop result [B,H,W,4]
        """
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        result_rgb = fg[:, :, :, :3] * bg_alpha + bg[:, :, :, :3] * (1.0 - fg_alpha)
        result_alpha = bg_alpha

        return torch.cat([result_rgb, result_alpha], dim=3)
