"""
Exposure node for ComfyUI_Detonate.

Photographic stops-based exposure adjustment.
More intuitive than gain for photographers and cinematographers.

Reference: Nuke EXPTool, DaVinci Resolve Exposure
https://learn.foundry.com/nuke/content/reference_guide/color_nodes/exptool.html
"""

import torch
from ...utils import validate_image_tensor


class DetonateExposure:
    """
    Photographic stops-based exposure control.

    Uses stops (f-stops) for exposure adjustment, where each stop
    doubles or halves the exposure. More intuitive than multiply/gain
    for photographers and cinematographers.

    Formula: output = (input - pivot) * 2^stops + pivot

    Common uses:
    - Match exposure between plates
    - Brighten/darken without clipping
    - Photographic-style adjustments
    - HDR tone mapping preparation

    Nuke equivalent: EXPTool
    DaVinci Resolve equivalent: Exposure control
    """

    CATEGORY = "detonate/color"

    # Detonate improvement: Response curves!
    RESPONSE_CURVES = ["linear", "logarithmic", "filmic"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Master exposure (stops)
                "stops": ("FLOAT", {
                    "default": 0.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                # Offset (black point shift)
                "offset": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Pivot (what value stays unchanged)
                "pivot": ("FLOAT", {
                    "default": 0.18,  # 18% gray (middle gray in photography)
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "number",
                }),
                # Per-channel stops (Detonate improvement!)
                "stops_r": ("FLOAT", {
                    "default": 0.0,
                    "min": -5.0,
                    "max": 5.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "stops_g": ("FLOAT", {
                    "default": 0.0,
                    "min": -5.0,
                    "max": 5.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "stops_b": ("FLOAT", {
                    "default": 0.0,
                    "min": -5.0,
                    "max": 5.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                # Highlight protection (Detonate improvement!)
                "highlight_rolloff": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                # Response curve (Detonate improvement!)
                "response_curve": (cls.RESPONSE_CURVES, {
                    "default": "linear",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "adjust_exposure"

    def adjust_exposure(
        self,
        image: torch.Tensor,
        stops: float = 0.0,
        offset: float = 0.0,
        pivot: float = 0.18,
        stops_r: float = 0.0,
        stops_g: float = 0.0,
        stops_b: float = 0.0,
        highlight_rolloff: float = 0.0,
        response_curve: str = "linear"
    ) -> tuple:
        """
        Adjust exposure using photographic stops.

        Detonate improvements:
        1. Per-channel stops for creative color grading
        2. Highlight rolloff to prevent clipping
        3. Response curves (linear, logarithmic, filmic)

        Args:
            image: Input tensor [B,H,W,C]
            stops: Master exposure adjustment in f-stops
                   +1 = double exposure, -1 = half exposure
            offset: Black point shift (added after exposure)
            pivot: Value that remains unchanged (default 18% gray)
            stops_r, stops_g, stops_b: Per-channel stop adjustments
            highlight_rolloff: Soft clipping for highlights (0-1)
            response_curve: Exposure response curve shape

        Returns:
            Tuple containing exposure-adjusted image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape
        has_alpha = C == 4

        # Work on RGB only, preserve alpha
        if has_alpha:
            rgb = image[:, :, :, :3]
            alpha = image[:, :, :, 3:4]
        else:
            rgb = image

        # Combine master + per-channel stops
        stops_combined = torch.tensor(
            [stops + stops_r, stops + stops_g, stops + stops_b],
            dtype=rgb.dtype,
            device=rgb.device
        ).view(1, 1, 1, 3)

        # Apply response curve preprocessing
        if response_curve == "logarithmic":
            # Log space: more natural for high dynamic range
            rgb = torch.log2(rgb + 1e-7)
            pivot_adj = torch.log2(torch.tensor(pivot + 1e-7))
        elif response_curve == "filmic":
            # Filmic curve: compressed highlights/shadows
            rgb = self._apply_filmic_curve(rgb, forward=True)
            pivot_adj = self._apply_filmic_curve(torch.tensor(pivot), forward=True)
        else:  # linear
            pivot_adj = pivot

        # Apply exposure formula: output = (input - pivot) * 2^stops + pivot
        # This can be rewritten as: output = input * 2^stops + pivot * (1 - 2^stops)
        exposure_mult = torch.pow(2.0, stops_combined)
        result_rgb = (rgb - pivot_adj) * exposure_mult + pivot_adj

        # Apply offset (black point shift)
        if offset != 0.0:
            result_rgb = result_rgb + offset

        # Apply response curve postprocessing
        if response_curve == "logarithmic":
            result_rgb = torch.pow(2.0, result_rgb) - 1e-7
        elif response_curve == "filmic":
            result_rgb = self._apply_filmic_curve(result_rgb, forward=False)

        # Apply highlight rolloff if requested (Detonate improvement!)
        if highlight_rolloff > 0.0:
            result_rgb = self._apply_highlight_rolloff(result_rgb, highlight_rolloff)

        # Clamp to valid range
        result_rgb = torch.clamp(result_rgb, min=0.0)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return (result,)

    def _apply_filmic_curve(
        self,
        x: torch.Tensor,
        forward: bool = True
    ) -> torch.Tensor:
        """
        Apply filmic S-curve response.

        Compresses highlights and shadows for more pleasing tonality.
        Uses a simplified ACES-like curve.

        Args:
            x: Input tensor
            forward: True for encoding, False for decoding

        Returns:
            Transformed tensor
        """
        if forward:
            # Simplified ACES filmic curve
            # y = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
            a = 2.51
            b = 0.03
            c = 2.43
            d = 0.59
            e = 0.14

            x_safe = torch.clamp(x, min=0.0)
            numerator = x_safe * (a * x_safe + b)
            denominator = x_safe * (c * x_safe + d) + e
            result = numerator / (denominator + 1e-7)
        else:
            # Inverse curve (approximation)
            # For simplicity, use a power curve approximation
            result = torch.pow(torch.clamp(x, min=0.0), 1.0 / 2.2)

        return result

    def _apply_highlight_rolloff(
        self,
        rgb: torch.Tensor,
        rolloff: float
    ) -> torch.Tensor:
        """
        Apply soft clipping to highlights.

        Prevents harsh clipping by smoothly rolling off highlights.
        Uses a shoulder function to compress values above threshold.

        Detonate improvement: Prevents blown-out highlights!

        Args:
            rgb: Input RGB tensor [B,H,W,3]
            rolloff: Rolloff strength (0-1)

        Returns:
            RGB with soft highlight clipping [B,H,W,3]
        """
        if rolloff <= 0.0:
            return rgb

        # Threshold where rolloff begins (higher rolloff = lower threshold)
        threshold = 1.0 - (rolloff * 0.5)

        # For values above threshold, apply soft compression
        # Use a shoulder function: y = threshold + (x - threshold) / (1 + (x - threshold))
        mask = rgb > threshold
        compressed = threshold + (rgb - threshold) / (1.0 + (rgb - threshold))

        result = torch.where(mask, compressed, rgb)

        return result
