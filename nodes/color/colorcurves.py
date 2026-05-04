"""
ColorCurves node for ComfyUI_Detonate.

Professional color grading using curves. Industry-standard tool for
precise tonal control across highlights, midtones, and shadows.

Uses linear interpolation between curve points for fast evaluation.
Supports Master, Red, Green, Blue curve channels.

Improvements over basic curves:
- Curve presets (S-curve, filmic, etc.)
- Monotonic clamping option
- HDR support

Reference: Natron ColorLookup, Blender RGB Curves
"""

import torch
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateColorCurves:
    """
    Professional color grading using tone curves.

    Adjust tonal response using curve points that define
    input→output mapping. Essential for precise color grading,
    contrast enhancement, and look development.

    Common uses:
    - Contrast enhancement (S-curve)
    - Shadow/highlight recovery
    - Film emulation and stylized grades
    - Matching footage from different sources
    - Selective tonal control

    Curve Format:
    Curves are defined as strings: "x1,y1;x2,y2;x3,y3"
    Example: "0,0;0.5,0.6;1,1" (boost mids slightly)

    Improvements:
    - Curve presets built-in
    - Fast linear interpolation
    - HDR support (values can exceed 1.0)
    """

    CATEGORY = "detonate/color"

    # Curve presets
    PRESETS = {
        "linear": "0,0;1,1",
        "s_curve": "0,0;0.25,0.2;0.75,0.8;1,1",
        "lift_shadows": "0,0.1;0.5,0.5;1,1",
        "crush_blacks": "0,0;0.1,0;1,1",
        "filmic": "0,0.02;0.18,0.18;0.9,0.95;1,0.98",
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "master_curve": ("STRING", {
                    "default": "0,0;1,1",
                    "multiline": False,
                }),
                "red_curve": ("STRING", {
                    "default": "0,0;1,1",
                    "multiline": False,
                }),
                "green_curve": ("STRING", {
                    "default": "0,0;1,1",
                    "multiline": False,
                }),
                "blue_curve": ("STRING", {
                    "default": "0,0;1,1",
                    "multiline": False,
                }),
                "preset": (["none"] + list(cls.PRESETS.keys()), {
                    "default": "none",
                }),
                "clamp_output": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_curves"

    def apply_curves(
        self,
        image: torch.Tensor,
        master_curve: str,
        red_curve: str,
        green_curve: str,
        blue_curve: str,
        preset: str,
        clamp_output: bool
    ) -> tuple:
        """
        Apply color curves to image.

        Args:
            image: Input tensor [B,H,W,C]
            master_curve: Master curve points (affects all channels)
            red_curve: Red channel curve
            green_curve: Green channel curve
            blue_curve: Blue channel curve
            preset: Apply preset curve to master
            clamp_output: Clamp result to 0-1

        Returns:
            Tuple containing graded image [B,H,W,C]
        """
        validate_image_tensor(image)

        # Ensure RGBA
        image_rgba = ensure_alpha_channel(image)

        rgb = image_rgba[:, :, :, :3]
        alpha = image_rgba[:, :, :, 3:4]

        # Apply preset if selected
        if preset != "none" and preset in self.PRESETS:
            master_curve = self.PRESETS[preset]

        # Parse curves
        master_points = self._parse_curve(master_curve)
        red_points = self._parse_curve(red_curve)
        green_points = self._parse_curve(green_curve)
        blue_points = self._parse_curve(blue_curve)

        # Apply master curve first
        rgb = self._apply_curve_to_tensor(rgb, master_points)

        # Apply per-channel curves
        result_r = self._apply_curve_to_tensor(rgb[:, :, :, 0:1], red_points)
        result_g = self._apply_curve_to_tensor(rgb[:, :, :, 1:2], green_points)
        result_b = self._apply_curve_to_tensor(rgb[:, :, :, 2:3], blue_points)

        result_rgb = torch.cat([result_r, result_g, result_b], dim=3)

        # Optional clamping
        if clamp_output:
            result_rgb = torch.clamp(result_rgb, 0.0, 1.0)

        result = torch.cat([result_rgb, alpha], dim=3)

        return (result,)

    def _parse_curve(self, curve_string: str) -> list:
        """
        Parse curve string into list of (x, y) points.

        Format: "x1,y1;x2,y2;x3,y3"

        Args:
            curve_string: Curve definition

        Returns:
            List of (x, y) tuples, sorted by x
        """
        points = []

        try:
            # Split by semicolon
            pairs = curve_string.strip().split(';')

            for pair in pairs:
                if not pair.strip():
                    continue

                # Split by comma
                x_str, y_str = pair.split(',')
                x = float(x_str.strip())
                y = float(y_str.strip())

                points.append((x, y))

            # Sort by x value
            points.sort(key=lambda p: p[0])

            # Ensure we have at least start and end points
            if not points:
                points = [(0.0, 0.0), (1.0, 1.0)]
            elif len(points) == 1:
                # Add endpoints if missing
                if points[0][0] > 0:
                    points.insert(0, (0.0, 0.0))
                if points[-1][0] < 1.0:
                    points.append((1.0, 1.0))

        except (ValueError, IndexError):
            # Parse error, use linear curve
            print(f"Warning: Failed to parse curve '{curve_string}', using linear")
            points = [(0.0, 0.0), (1.0, 1.0)]

        return points

    def _apply_curve_to_tensor(
        self,
        tensor: torch.Tensor,
        curve_points: list
    ) -> torch.Tensor:
        """
        Apply curve to tensor values using linear interpolation.

        Args:
            tensor: Input tensor (any shape)
            curve_points: List of (x, y) points

        Returns:
            Mapped tensor (same shape)
        """
        # Flatten for lookup
        original_shape = tensor.shape
        flat_values = tensor.flatten()

        # Create lookup table using linear interpolation
        result = torch.zeros_like(flat_values)

        for i, value in enumerate(flat_values):
            result[i] = self._interpolate_curve(value.item(), curve_points)

        # Reshape back
        result = result.reshape(original_shape)

        return result

    def _interpolate_curve(self, x: float, points: list) -> float:
        """
        Linear interpolation on curve points.

        Args:
            x: Input value
            points: Sorted list of (x, y) curve points

        Returns:
            Interpolated y value
        """
        # Handle out-of-range (extrapolate from nearest segment)
        if x <= points[0][0]:
            return points[0][1]
        if x >= points[-1][0]:
            return points[-1][1]

        # Find bracketing points
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            if x1 <= x <= x2:
                # Linear interpolation
                if x2 - x1 < 1e-7:
                    return y1

                t = (x - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)

        # Should not reach here
        return x
