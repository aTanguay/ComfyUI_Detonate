"""
Ramp node for ComfyUI_Detonate.

Generate procedural gradients for masks, lighting effects, and backgrounds.
Essential utility for creating smooth transitions and falloffs.

Supports multiple gradient types:
- Linear: Directional gradient
- Radial: Circular falloff from center
- Angle: Angular/conical gradient
- Box: Rectangular falloff

Improvements over Nuke:
- Falloff curves for more control
- Full RGBA color support (not just grayscale)
- HDR support (colors can exceed 1.0)

Reference: Nuke Ramp node
"""

import torch
import math
from ...utils import validate_image_tensor


class DetonateRamp:
    """
    Generate procedural gradients.

    Create smooth gradients for masks, lighting ramps, vignettes,
    and backgrounds. Supports linear, radial, angle, and box types
    with customizable falloff curves.

    Common uses:
    - Vignettes (radial gradient for edge darkening)
    - Lighting ramps (simulate directional light falloff)
    - Mask generation (soft falloff masks)
    - Simple gradient backgrounds
    - Drive displacement and other effects

    Improvements:
    - Falloff curves (linear, smooth, exponential, logarithmic)
    - Full RGBA color gradients
    - HDR color support
    """

    CATEGORY = "detonate/generator"

    GRADIENT_TYPES = ["linear", "radial", "angle", "box"]
    FALLOFF_TYPES = ["linear", "smooth", "exponential", "logarithmic"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                }),
                "gradient_type": (cls.GRADIENT_TYPES, {
                    "default": "linear",
                }),
                "falloff": (cls.FALLOFF_TYPES, {
                    "default": "linear",
                }),
                # Colors
                "color_start_r": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "color_start_g": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "color_start_b": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "color_start_a": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "color_end_r": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "color_end_g": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "color_end_b": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "color_end_a": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                # Position controls
                "start_x": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "start_y": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "end_x": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "end_y": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        width: int,
        height: int,
        gradient_type: str,
        falloff: str,
        color_start_r: float,
        color_start_g: float,
        color_start_b: float,
        color_start_a: float,
        color_end_r: float,
        color_end_g: float,
        color_end_b: float,
        color_end_a: float,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        center_x: float,
        center_y: float,
        batch_size: int
    ) -> tuple:
        """
        Generate gradient image.

        Returns:
            Tuple containing gradient image [B,H,W,4]
        """
        # Create gradient values [H, W] (0 to 1)
        if gradient_type == "linear":
            gradient = self._linear_gradient(width, height, start_x, start_y, end_x, end_y)
        elif gradient_type == "radial":
            gradient = self._radial_gradient(width, height, center_x, center_y)
        elif gradient_type == "angle":
            gradient = self._angle_gradient(width, height, center_x, center_y)
        else:  # box
            gradient = self._box_gradient(width, height, center_x, center_y)

        # Apply falloff curve
        gradient = self._apply_falloff(gradient, falloff)

        # Expand to batch
        gradient = gradient.unsqueeze(0).repeat(batch_size, 1, 1)  # [B, H, W]

        # Create color gradient [B, H, W, 4]
        color_start = torch.tensor([color_start_r, color_start_g, color_start_b, color_start_a])
        color_end = torch.tensor([color_end_r, color_end_g, color_end_b, color_end_a])

        # Interpolate colors
        gradient_4d = gradient.unsqueeze(3)  # [B, H, W, 1]
        image = color_start + (color_end - color_start) * gradient_4d

        return (image,)

    def _linear_gradient(
        self,
        width: int,
        height: int,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float
    ) -> torch.Tensor:
        """
        Create linear gradient from start to end point.
        """
        # Create coordinate grid (0 to 1)
        y_coords = torch.linspace(0, 1, height).unsqueeze(1).repeat(1, width)
        x_coords = torch.linspace(0, 1, width).unsqueeze(0).repeat(height, 1)

        # Direction vector
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx ** 2 + dy ** 2) + 1e-7

        # Normalize direction
        dx /= length
        dy /= length

        # Project each point onto gradient direction
        px = x_coords - start_x
        py = y_coords - start_y

        # Dot product with direction
        gradient = (px * dx + py * dy) / length

        # Clamp to 0-1
        gradient = torch.clamp(gradient, 0.0, 1.0)

        return gradient

    def _radial_gradient(
        self,
        width: int,
        height: int,
        center_x: float,
        center_y: float
    ) -> torch.Tensor:
        """
        Create radial gradient from center.
        """
        # Create coordinate grid
        y_coords = torch.linspace(0, 1, height).unsqueeze(1).repeat(1, width)
        x_coords = torch.linspace(0, 1, width).unsqueeze(0).repeat(height, 1)

        # Distance from center
        dx = x_coords - center_x
        dy = y_coords - center_y

        # Euclidean distance
        max_radius = math.sqrt(0.5 ** 2 + 0.5 ** 2)  # Max distance from corner
        distance = torch.sqrt(dx ** 2 + dy ** 2)

        # Normalize to 0-1
        gradient = distance / max_radius

        # Clamp to 0-1
        gradient = torch.clamp(gradient, 0.0, 1.0)

        return gradient

    def _angle_gradient(
        self,
        width: int,
        height: int,
        center_x: float,
        center_y: float
    ) -> torch.Tensor:
        """
        Create angular/conical gradient around center.
        """
        # Create coordinate grid
        y_coords = torch.linspace(0, 1, height).unsqueeze(1).repeat(1, width)
        x_coords = torch.linspace(0, 1, width).unsqueeze(0).repeat(height, 1)

        # Offset from center
        dx = x_coords - center_x
        dy = y_coords - center_y

        # Calculate angle (atan2)
        angle = torch.atan2(dy, dx)

        # Normalize from [-π, π] to [0, 1]
        gradient = (angle + math.pi) / (2 * math.pi)

        return gradient

    def _box_gradient(
        self,
        width: int,
        height: int,
        center_x: float,
        center_y: float
    ) -> torch.Tensor:
        """
        Create box gradient (rectangular falloff from center).
        """
        # Create coordinate grid
        y_coords = torch.linspace(0, 1, height).unsqueeze(1).repeat(1, width)
        x_coords = torch.linspace(0, 1, width).unsqueeze(0).repeat(height, 1)

        # Distance from center (Chebyshev distance / L-infinity)
        dx = torch.abs(x_coords - center_x)
        dy = torch.abs(y_coords - center_y)

        # Max of x and y distances
        distance = torch.maximum(dx, dy)

        # Normalize (max distance is 0.5 from center to edge)
        gradient = distance / 0.5

        # Clamp to 0-1
        gradient = torch.clamp(gradient, 0.0, 1.0)

        return gradient

    def _apply_falloff(self, gradient: torch.Tensor, falloff: str) -> torch.Tensor:
        """
        Apply falloff curve to gradient.

        Args:
            gradient: Input gradient [H, W] in range 0-1
            falloff: Falloff type

        Returns:
            Modified gradient
        """
        if falloff == "linear":
            return gradient

        elif falloff == "smooth":
            # Smoothstep (ease in/out)
            return gradient * gradient * (3.0 - 2.0 * gradient)

        elif falloff == "exponential":
            # Exponential falloff (sharp near edges)
            return gradient ** 2

        elif falloff == "logarithmic":
            # Logarithmic (sharp in center)
            return torch.sqrt(gradient)

        else:
            return gradient
