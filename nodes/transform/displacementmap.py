"""
DisplacementMap node for ComfyUI_Detonate.

Professional UV displacement (IDistort equivalent) for image warping.
Uses displacement maps to distort images with vector fields.

Reference: Nuke IDistort, After Effects Displacement Map, Fusion Displace
"""

import torch
import numpy as np
import cv2
from typing import Tuple


class DetonateDisplacementMap:
    """
    Professional displacement mapping (IDistort-style warping).

    Warps images using displacement maps (UV vector fields).
    Essential for heat distortion, refraction, lens distortion,
    and creative image warping effects.

    Features:
    - UV channel displacement (RG = XY vectors)
    - Adjustable displacement scale
    - Multiple edge modes (Clamp, Wrap, Black)
    - Bilinear interpolation for smooth results
    - Support for both IMAGE and MASK displacement

    Workflow:
    1. Create displacement map (red = X, green = Y)
    2. Set displacement scale (how strong)
    3. Choose edge behavior
    4. Apply to image for warping

    Common uses:
    - Heat distortion effects
    - Glass/water refraction
    - Lens distortion correction
    - Creative image warping
    - Turbulence displacement

    Nuke equivalent: IDistort
    Fusion equivalent: Displace
    """

    CATEGORY = "detonate/transform"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "displacement_map": ("IMAGE",),
                "scale_x": ("FLOAT", {
                    "default": 10.0,
                    "min": -1000.0,
                    "max": 1000.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Horizontal displacement scale (pixels)",
                }),
                "scale_y": ("FLOAT", {
                    "default": 10.0,
                    "min": -1000.0,
                    "max": 1000.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Vertical displacement scale (pixels)",
                }),
            },
            "optional": {
                "edge_mode": (["Clamp", "Wrap", "Black"], {
                    "default": "Clamp",
                    "tooltip": "Edge behavior: Clamp (stretch edge pixels), Wrap (tile), Black",
                }),
                "center_neutral": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Treat 0.5 as neutral (no displacement), otherwise 0.0 is neutral",
                }),
                "use_alpha_as_y": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Use displacement map alpha as Y displacement (RG = XY, A = Y override)",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output",)
    FUNCTION = "displace"

    def displace(
        self,
        image: torch.Tensor,
        displacement_map: torch.Tensor,
        scale_x: float,
        scale_y: float,
        edge_mode: str = "Clamp",
        center_neutral: bool = True,
        use_alpha_as_y: bool = False
    ) -> Tuple[torch.Tensor]:
        """
        Apply displacement mapping to image.

        Args:
            image: Input image to displace [B, H, W, C]
            displacement_map: UV displacement map [B, H, W, C] (R=X, G=Y)
            scale_x: X displacement scale (pixels)
            scale_y: Y displacement scale (pixels)
            edge_mode: Edge handling (Clamp/Wrap/Black)
            center_neutral: Treat 0.5 as neutral (standard for displacement maps)
            use_alpha_as_y: Use alpha channel for Y displacement

        Returns:
            Displaced image [B, H, W, C]
        """
        device = image.device
        B, H, W, C = image.shape

        # Ensure displacement map matches image resolution
        disp_B, disp_H, disp_W, disp_C = displacement_map.shape

        if disp_H != H or disp_W != W:
            # Resize displacement map to match image
            displacement_map = torch.nn.functional.interpolate(
                displacement_map.permute(0, 3, 1, 2),  # [B, C, H, W]
                size=(H, W),
                mode='bilinear',
                align_corners=False
            ).permute(0, 2, 3, 1)  # Back to [B, H, W, C]

        # Process each image in batch
        result = []
        for b in range(B):
            img = image[b]  # [H, W, C]
            disp = displacement_map[b % disp_B]  # [H, W, C] - cycle if batch sizes differ

            # Extract displacement vectors
            if use_alpha_as_y and disp.shape[-1] >= 4:
                # R = X, A = Y
                disp_x = disp[..., 0]  # Red channel
                disp_y = disp[..., 3]  # Alpha channel
            else:
                # R = X, G = Y (standard)
                disp_x = disp[..., 0]  # Red channel
                disp_y = disp[..., 1] if disp.shape[-1] >= 2 else torch.zeros_like(disp[..., 0])  # Green channel

            # Apply neutral centering (0.5 = no displacement)
            if center_neutral:
                disp_x = disp_x - 0.5
                disp_y = disp_y - 0.5

            # Scale displacement
            disp_x = disp_x * scale_x
            disp_y = disp_y * scale_y

            # Create sampling grid
            # Generate pixel coordinates
            y_coords = torch.arange(H, dtype=torch.float32, device=device).view(H, 1).repeat(1, W)
            x_coords = torch.arange(W, dtype=torch.float32, device=device).view(1, W).repeat(H, 1)

            # Apply displacement to coordinates
            sample_x = x_coords + disp_x
            sample_y = y_coords + disp_y

            # Handle edge modes
            if edge_mode == "Clamp":
                sample_x = torch.clamp(sample_x, 0, W - 1)
                sample_y = torch.clamp(sample_y, 0, H - 1)
            elif edge_mode == "Wrap":
                sample_x = sample_x % W
                sample_y = sample_y % H
            # Black mode: out-of-bounds will return 0 in sampling

            # Convert to numpy for cv2.remap (more efficient than custom bilinear)
            img_np = img.cpu().numpy()
            map_x = sample_x.cpu().numpy().astype(np.float32)
            map_y = sample_y.cpu().numpy().astype(np.float32)

            # Apply displacement using cv2.remap (bilinear interpolation)
            if edge_mode == "Black":
                border_mode = cv2.BORDER_CONSTANT
                border_value = 0.0
            elif edge_mode == "Wrap":
                border_mode = cv2.BORDER_WRAP
                border_value = 0.0
            else:  # Clamp
                border_mode = cv2.BORDER_REPLICATE
                border_value = 0.0

            displaced = cv2.remap(
                img_np,
                map_x,
                map_y,
                interpolation=cv2.INTER_LINEAR,
                borderMode=border_mode,
                borderValue=border_value
            )

            result.append(torch.from_numpy(displaced).to(device))

        output = torch.stack(result, dim=0)

        return (output,)
