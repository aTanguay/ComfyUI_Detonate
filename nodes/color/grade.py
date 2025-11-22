"""
Grade node for ComfyUI_Detonate.

Professional color grading using lift/gamma/gain controls.
Industry-standard tool for film scan color grading.

Reference: Nuke Grade node
https://learn.foundry.com/nuke/content/reference_guide/color_nodes/grade.html
Formula: https://www.chrisbturner.com/blog/nukes-grade-node-demystified
"""

import torch
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateGrade:
    """
    Professional color grading with lift/gamma/gain controls.

    Implements Nuke's Grade node formula for precise color correction:
    A = multiply * (gain-lift) / (whitepoint-blackpoint)
    B = offset + lift - A*blackpoint
    output = pow(A*input + B, 1/gamma)

    Workflow:
    1. Set blackpoint/whitepoint to establish input range
    2. Use lift to adjust shadows
    3. Use gain to adjust highlights
    4. Use gamma to adjust midtones
    5. Use offset for final tweaks

    Operates on straight (unpremultiplied) alpha images.
    Use Unpremult → Grade → Premult workflow.

    Nuke/Fusion equivalent: Grade / ColorCorrector (grade mode)
    """

    CATEGORY = "detonate/color"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Input range
                "blackpoint": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "number",
                }),
                "whitepoint": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "display": "number",
                }),
                # Master controls
                "lift": ("FLOAT", {
                    "default": 0.0,
                    "min": -0.5,
                    "max": 0.5,
                    "step": 0.01,
                    "display": "slider",
                }),
                "gamma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "gain": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "offset": ("FLOAT", {
                    "default": 0.0,
                    "min": -0.5,
                    "max": 0.5,
                    "step": 0.01,
                    "display": "slider",
                }),
                "multiply": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "grade"

    def grade(
        self,
        image: torch.Tensor,
        blackpoint: float = 0.0,
        whitepoint: float = 1.0,
        lift: float = 0.0,
        gamma: float = 1.0,
        gain: float = 1.0,
        offset: float = 0.0,
        multiply: float = 1.0
    ) -> tuple:
        """
        Apply grade color correction to image.

        Complete formula:
        A = multiply * (gain-lift) / (whitepoint-blackpoint)
        B = offset + lift - A*blackpoint
        output = pow(A*input + B, 1/gamma)

        Args:
            image: Input tensor [B,H,W,C] (should be straight/unpremultiplied alpha)
            blackpoint: Input black level (source black)
            whitepoint: Input white level (source white)
            lift: Output black level (affects shadows most)
            gamma: Midtone adjustment (pow(x, 1/gamma))
            gain: Output white level (affects highlights most)
            offset: Simple addition to all values
            multiply: Overall multiplier

        Returns:
            Tuple containing graded image [B,H,W,C]
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

        # Prevent division by zero
        if abs(whitepoint - blackpoint) < 1e-7:
            whitepoint = blackpoint + 1e-7

        # Apply Grade formula
        # A = multiply * (gain - lift) / (whitepoint - blackpoint)
        A = multiply * (gain - lift) / (whitepoint - blackpoint)

        # B = offset + lift - A * blackpoint
        B = offset + lift - A * blackpoint

        # result = pow(A * input + B, 1/gamma)
        # First apply linear transform: A*input + B
        result_rgb = A * rgb + B

        # Ensure non-negative for pow operation
        result_rgb = torch.clamp(result_rgb, min=0.0)

        # Apply gamma (clamp gamma to prevent issues)
        gamma_safe = max(0.01, gamma)
        result_rgb = torch.pow(result_rgb + 1e-7, 1.0 / gamma_safe)

        # Reconstruct with alpha
        if has_alpha:
            result = torch.cat([result_rgb, alpha], dim=3)
        else:
            result = result_rgb

        return (result,)
