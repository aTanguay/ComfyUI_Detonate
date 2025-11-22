"""
EdgeDetect node for ComfyUI_Detonate.

Detect edges using Sobel operator.
Creates edge mattes for effects, selections, and stylistic looks.

Reference: Nuke EdgeDetect node
https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/edgedetect.html
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor
from ...utils.image_processing import calculate_luminance


class DetonateEdgeDetect:
    """
    Detect edges using Sobel operator.

    Applies Sobel edge detection to create edge mattes.
    Optional pre-blur for noise reduction and post-erode for thinning.

    Common uses:
    - Create edge mattes for effects
    - Line art / sketch effects
    - Edge-based selections
    - Sharpening guidance

    Nuke equivalent: EdgeDetect
    """

    CATEGORY = "detonate/filter"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "channels": (["luminance", "rgb", "red", "green", "blue", "alpha"], {
                    "default": "luminance",
                }),
                "pre_blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 20.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "erode": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "display": "slider",
                }),
                "output_mode": (["replace_alpha", "replace_rgb", "multiply_alpha"], {
                    "default": "replace_alpha",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "detect_edges"

    def detect_edges(
        self,
        image: torch.Tensor,
        channels: str = "luminance",
        pre_blur: float = 0.0,
        erode: int = 0,
        output_mode: str = "replace_alpha"
    ) -> tuple:
        """
        Detect edges using Sobel operator.

        Process:
        1. Optional pre-blur (noise reduction)
        2. Sobel edge detection
        3. Optional post-erode (thin edges)
        4. Output based on mode

        Args:
            image: Input tensor [B,H,W,C]
            channels: Which channel(s) to detect edges from
            pre_blur: Blur applied before edge detection (reduces noise)
            erode: Erode applied after detection (thins edges)
            output_mode: How to output edge matte
                         - replace_alpha: Edges → alpha channel
                         - replace_rgb: Edges → RGB (grayscale)
                         - multiply_alpha: Edges × alpha channel

        Returns:
            Tuple containing edge-detected image [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Step 1: Select channel(s) to process
        if channels == "luminance":
            # Calculate luminance from RGB
            if C >= 3:
                input_channel = calculate_luminance(image[:, :, :, :3])
            else:
                input_channel = image.mean(dim=3, keepdim=True)
        elif channels == "rgb":
            # Average of RGB channels
            input_channel = image[:, :, :, :3].mean(dim=3, keepdim=True)
        elif channels == "red":
            input_channel = image[:, :, :, 0:1]
        elif channels == "green":
            input_channel = image[:, :, :, 1:2]
        elif channels == "blue":
            input_channel = image[:, :, :, 2:3]
        elif channels == "alpha":
            if C == 4:
                input_channel = image[:, :, :, 3:4]
            else:
                input_channel = torch.ones((B, H, W, 1), dtype=image.dtype, device=image.device)
        else:
            input_channel = image[:, :, :, 0:1]

        # Step 2: Pre-blur (optional)
        if pre_blur > 0.0:
            input_channel = self._apply_blur(input_channel, pre_blur)

        # Step 3: Sobel edge detection
        edges = self._sobel_edge_detection(input_channel)

        # Step 4: Post-erode (optional)
        if erode > 0:
            edges = self._apply_erode(edges, erode)

        # Step 5: Output based on mode
        result = self._format_output(image, edges, output_mode)

        return (result,)

    def _sobel_edge_detection(
        self,
        tensor: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply Sobel operator for edge detection.

        Uses standard Sobel kernels for horizontal and vertical edges.

        Args:
            tensor: Input tensor [B,H,W,1]

        Returns:
            Edge magnitude tensor [B,H,W,1]
        """
        # Convert to [B,C,H,W] for convolution
        tensor_nchw = tensor.permute(0, 3, 1, 2)

        # Sobel kernels
        # Horizontal (Gx)
        sobel_x = torch.tensor([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ], dtype=torch.float32, device=tensor.device).view(1, 1, 3, 3)

        # Vertical (Gy)
        sobel_y = torch.tensor([
            [-1, -2, -1],
            [ 0,  0,  0],
            [ 1,  2,  1]
        ], dtype=torch.float32, device=tensor.device).view(1, 1, 3, 3)

        # Apply Sobel kernels
        Gx = F.conv2d(tensor_nchw, sobel_x, padding=1)
        Gy = F.conv2d(tensor_nchw, sobel_y, padding=1)

        # Edge magnitude: sqrt(Gx^2 + Gy^2)
        magnitude = torch.sqrt(Gx ** 2 + Gy ** 2 + 1e-8)

        # Normalize to 0-1 range
        max_val = magnitude.max()
        if max_val > 0:
            magnitude = magnitude / max_val

        # Convert back to [B,H,W,C]
        edges = magnitude.permute(0, 2, 3, 1)

        return edges

    def _apply_blur(
        self,
        tensor: torch.Tensor,
        blur_size: float
    ) -> torch.Tensor:
        """
        Apply Gaussian blur.

        Args:
            tensor: Input tensor [B,H,W,C]
            blur_size: Blur size in pixels

        Returns:
            Blurred tensor [B,H,W,C]
        """
        B, H, W, C = tensor.shape

        # Convert to [B,C,H,W]
        tensor_nchw = tensor.permute(0, 3, 1, 2)

        # Calculate sigma
        sigma = blur_size / 2.0
        if sigma < 0.1:
            return tensor

        # Calculate kernel size
        kernel_size = int(2 * round(3 * sigma) + 1)
        kernel_size = max(3, kernel_size)

        # Create 1D Gaussian kernel
        kernel_radius = kernel_size // 2
        coords = torch.arange(kernel_size, dtype=torch.float32, device=tensor.device) - kernel_radius
        gaussian = torch.exp(-(coords ** 2) / (2 * sigma ** 2))
        gaussian = gaussian / gaussian.sum()

        # Horizontal blur
        kernel_h = gaussian.view(1, 1, 1, kernel_size).repeat(C, 1, 1, 1)
        result = F.conv2d(tensor_nchw, kernel_h, padding=(0, kernel_radius), groups=C)

        # Vertical blur
        kernel_v = gaussian.view(1, 1, kernel_size, 1).repeat(C, 1, 1, 1)
        result = F.conv2d(result, kernel_v, padding=(kernel_radius, 0), groups=C)

        # Convert back to [B,H,W,C]
        result = result.permute(0, 2, 3, 1)

        return result

    def _apply_erode(
        self,
        tensor: torch.Tensor,
        size: int
    ) -> torch.Tensor:
        """
        Apply morphological erosion.

        Args:
            tensor: Input tensor [B,H,W,C]
            size: Erosion size

        Returns:
            Eroded tensor [B,H,W,C]
        """
        B, H, W, C = tensor.shape

        # Convert to [B,C,H,W]
        tensor_nchw = tensor.permute(0, 3, 1, 2)

        # Kernel size
        kernel_size = 2 * size + 1
        padding = size

        # Erosion: -max_pool(-x) = min_pool(x)
        result_nchw = -F.max_pool2d(
            -tensor_nchw,
            kernel_size=kernel_size,
            stride=1,
            padding=padding
        )

        # Convert back to [B,H,W,C]
        result = result_nchw.permute(0, 2, 3, 1)

        return result

    def _format_output(
        self,
        image: torch.Tensor,
        edges: torch.Tensor,
        output_mode: str
    ) -> torch.Tensor:
        """
        Format edge detection output based on mode.

        Args:
            image: Original image [B,H,W,C]
            edges: Edge matte [B,H,W,1]
            output_mode: Output mode

        Returns:
            Formatted output [B,H,W,C]
        """
        B, H, W, C = image.shape

        if output_mode == "replace_alpha":
            # Edges → alpha channel
            if C >= 3:
                result = torch.cat([image[:, :, :, :3], edges], dim=3)
            else:
                # If input is grayscale, convert to RGB first
                rgb = image[:, :, :, :1].repeat(1, 1, 1, 3)
                result = torch.cat([rgb, edges], dim=3)

        elif output_mode == "replace_rgb":
            # Edges → RGB (grayscale)
            edges_rgb = edges.repeat(1, 1, 1, 3)
            if C == 4:
                result = torch.cat([edges_rgb, image[:, :, :, 3:4]], dim=3)
            else:
                result = edges_rgb

        elif output_mode == "multiply_alpha":
            # Edges × alpha channel
            if C == 4:
                alpha_mult = image[:, :, :, 3:4] * edges
                result = torch.cat([image[:, :, :, :3], alpha_mult], dim=3)
            else:
                # No alpha to multiply, treat as replace_alpha
                if C >= 3:
                    result = torch.cat([image[:, :, :, :3], edges], dim=3)
                else:
                    rgb = image[:, :, :, :1].repeat(1, 1, 1, 3)
                    result = torch.cat([rgb, edges], dim=3)

        else:
            result = image

        return result
