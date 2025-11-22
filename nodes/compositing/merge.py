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

    # Blend mode options (expanded from Nuke/Photoshop standard set)
    BLEND_MODES = [
        # Porter-Duff compositing
        "over",
        "under",
        "plus",
        "stencil",
        "mask",
        "atop",
        # Photoshop-style blends
        "screen",
        "multiply",
        "overlay",
        "soft_light",
        "hard_light",
        "color_dodge",
        "color_burn",
        "divide",
        "difference",
        "exclusion",
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
        # New Photoshop-style blends
        elif operation == "overlay":
            result = self._blend_overlay(fg, bg)
        elif operation == "soft_light":
            result = self._blend_soft_light(fg, bg)
        elif operation == "hard_light":
            result = self._blend_hard_light(fg, bg)
        elif operation == "color_dodge":
            result = self._blend_color_dodge(fg, bg)
        elif operation == "color_burn":
            result = self._blend_color_burn(fg, bg)
        elif operation == "divide":
            result = self._blend_divide(fg, bg)
        elif operation == "difference":
            result = self._blend_difference(fg, bg)
        elif operation == "exclusion":
            result = self._blend_exclusion(fg, bg)
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

    def _blend_overlay(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Overlay blend mode.

        Combination of multiply and screen:
        - Multiplies dark areas
        - Screens bright areas

        Formula:
        if bg < 0.5:
            result = 2 * fg * bg
        else:
            result = 1 - 2 * (1 - fg) * (1 - bg)

        Popular for adding texture and contrast.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Overlay result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Overlay formula
        mask = (bg_rgb < 0.5).float()
        multiply_part = 2 * fg_rgb * bg_rgb
        screen_part = 1.0 - 2 * (1.0 - fg_rgb) * (1.0 - bg_rgb)

        result_rgb = mask * multiply_part + (1 - mask) * screen_part

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_soft_light(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Soft light blend mode.

        Gentler version of overlay/hard light.
        Creates subtle lighting effects.

        Photoshop formula:
        if fg < 0.5:
            result = bg - (1 - 2*fg) * bg * (1 - bg)
        else:
            result = bg + (2*fg - 1) * (sqrt(bg) - bg)

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Soft light result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Soft light formula
        mask = (fg_rgb < 0.5).float()
        darken_part = bg_rgb - (1 - 2 * fg_rgb) * bg_rgb * (1 - bg_rgb)
        lighten_part = bg_rgb + (2 * fg_rgb - 1) * (torch.sqrt(bg_rgb + 1e-8) - bg_rgb)

        result_rgb = mask * darken_part + (1 - mask) * lighten_part

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_hard_light(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Hard light blend mode.

        Like overlay but uses fg as condition instead of bg.
        Creates strong lighting effects.

        Formula:
        if fg < 0.5:
            result = 2 * fg * bg
        else:
            result = 1 - 2 * (1 - fg) * (1 - bg)

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Hard light result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Hard light formula
        mask = (fg_rgb < 0.5).float()
        multiply_part = 2 * fg_rgb * bg_rgb
        screen_part = 1.0 - 2 * (1.0 - fg_rgb) * (1.0 - bg_rgb)

        result_rgb = mask * multiply_part + (1 - mask) * screen_part

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_color_dodge(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Color dodge blend mode.

        Brightens background based on foreground.
        Formula: result = bg / (1 - fg)

        Creates intense highlights. Popular for glow effects.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Color dodge result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Color dodge: bg / (1 - fg)
        # Clamp to prevent division by zero
        result_rgb = bg_rgb / (1.0 - fg_rgb + 1e-7)

        # Clamp to reasonable range (can exceed 1.0 for HDR)
        result_rgb = torch.clamp(result_rgb, 0.0, 10.0)

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_color_burn(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Color burn blend mode.

        Darkens background based on foreground.
        Formula: result = 1 - (1 - bg) / fg

        Creates intense shadows.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Color burn result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Color burn: 1 - (1 - bg) / fg
        # Clamp to prevent division by zero
        result_rgb = 1.0 - (1.0 - bg_rgb) / (fg_rgb + 1e-7)

        # Clamp to 0-1 range
        result_rgb = torch.clamp(result_rgb, 0.0, 1.0)

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_divide(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Divide blend mode.

        Divides background by foreground.
        Formula: result = bg / fg

        Useful for removing color casts and normalization.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Divide result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Divide: bg / fg
        result_rgb = bg_rgb / (fg_rgb + 1e-7)

        # Clamp to reasonable range
        result_rgb = torch.clamp(result_rgb, 0.0, 10.0)

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_difference(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Difference blend mode.

        Absolute difference between layers.
        Formula: result = abs(fg - bg)

        Great for image comparison and inversion effects.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Difference result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Difference: abs(fg - bg)
        result_rgb = torch.abs(fg_rgb - bg_rgb)

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)

    def _blend_exclusion(
        self,
        fg: torch.Tensor,
        bg: torch.Tensor
    ) -> torch.Tensor:
        """
        Exclusion blend mode.

        Similar to difference but lower contrast.
        Formula: result = fg + bg - 2 * fg * bg

        Creates softer inversion effects than difference.

        Args:
            fg: Foreground [B,H,W,4]
            bg: Background [B,H,W,4]

        Returns:
            Exclusion result [B,H,W,4]
        """
        fg_rgb = fg[:, :, :, :3]
        bg_rgb = bg[:, :, :, :3]
        fg_alpha = fg[:, :, :, 3:4]
        bg_alpha = bg[:, :, :, 3:4]

        # Exclusion: fg + bg - 2 * fg * bg
        result_rgb = fg_rgb + bg_rgb - 2 * fg_rgb * bg_rgb

        # Alpha: over composite
        result_alpha = fg_alpha + bg_alpha * (1.0 - fg_alpha)

        return torch.cat([result_rgb, result_alpha], dim=3)
