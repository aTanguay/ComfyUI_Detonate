"""
MatteControl node for ComfyUI_Detonate.

All-in-one matte refinement combining contract/expand, blur, and gamma.
Replaces Erode → Blur → Grade workflows with single node.

Reference: Fusion Matte Control / Nuke FilterErode (blur mode)
https://jayaretv.com/fusion/matte-control-node/
https://www.keheka.com/alpha-density-matte-control-tool-for-nuke/
"""

import torch
import torch.nn.functional as F
from ...utils import validate_image_tensor, ensure_alpha_channel


class DetonateMatteControl:
    """
    All-in-one matte refinement tool.

    Combines three operations in proper order:
    1. Contract/Expand (erode/dilate)
    2. Blur (soften edges)
    3. Gamma (adjust density)

    Single node replaces complex matte cleanup workflows.

    Common uses:
    - Choke and soften mattes
    - Spread and blur edges
    - Thicken thin mattes
    - Clean noisy mattes

    Fusion equivalent: Matte Control
    """

    CATEGORY = "detonate/matte"

    # Detonate improvement: Multiple kernel shapes!
    KERNEL_SHAPES = ["square", "circular", "cross", "diamond"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "size": ("INT", {
                    "default": 0,
                    "min": -100,
                    "max": 100,
                    "step": 1,
                    "display": "slider",
                }),
                "kernel_shape": (cls.KERNEL_SHAPES, {
                    "default": "square",
                }),
                "blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider",
                }),
                "gamma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 4.0,
                    "step": 0.01,
                    "display": "slider",
                }),
                "channels": (["alpha", "rgb", "rgba"], {
                    "default": "alpha",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "refine_matte"

    def refine_matte(
        self,
        image: torch.Tensor,
        size: int = 0,
        kernel_shape: str = "square",
        blur: float = 0.0,
        gamma: float = 1.0,
        channels: str = "alpha"
    ) -> tuple:
        """
        Refine matte with contract/expand, blur, and gamma.

        Process order (important!):
        1. Contract/Expand (size parameter with Detonate improvement: 4 kernel shapes!)
           - Square: Traditional morphological operations
           - Circular: More natural, organic edges
           - Cross: Directional (horizontal + vertical only)
           - Diamond: 45-degree diagonal emphasis
        2. Blur (edge softening)
        3. Gamma (density adjustment)

        Args:
            image: Input tensor [B,H,W,C]
            size: Contract/expand amount
                  < 0: Contract (erode, choke)
                  > 0: Expand (dilate, spread)
                  = 0: No change
            kernel_shape: Shape of morphological kernel
            blur: Gaussian blur size in pixels
            gamma: Gamma adjustment for matte density
                   < 1.0: Darken/thin matte
                   > 1.0: Lighten/thicken matte
            channels: Which channels to process

        Returns:
            Tuple containing refined matte [B,H,W,C]
        """
        validate_image_tensor(image)

        B, H, W, C = image.shape

        # Ensure alpha channel exists
        image_rgba = ensure_alpha_channel(image, alpha_value=1.0)

        # Determine which channels to process
        if channels == "alpha":
            # Process alpha only
            rgb = image_rgba[:, :, :, :3]
            alpha = image_rgba[:, :, :, 3:4]

            alpha_processed = self._process_channels(alpha, size, kernel_shape, blur, gamma)

            result = torch.cat([rgb, alpha_processed], dim=3)

        elif channels == "rgb":
            # Process RGB only
            rgb = image_rgba[:, :, :, :3]
            alpha = image_rgba[:, :, :, 3:4]

            rgb_processed = self._process_channels(rgb, size, kernel_shape, blur, gamma)

            result = torch.cat([rgb_processed, alpha], dim=3)

        else:  # "rgba"
            # Process all channels
            result = self._process_channels(image_rgba, size, kernel_shape, blur, gamma)

        # Match output channels to input
        if C == 3:
            result = result[:, :, :, :3]

        return (result,)

    def _process_channels(
        self,
        tensor: torch.Tensor,
        size: int,
        kernel_shape: str,
        blur: float,
        gamma: float
    ) -> torch.Tensor:
        """
        Apply matte refinement pipeline to tensor.

        Args:
            tensor: Input tensor [B,H,W,C]
            size: Contract/expand size
            kernel_shape: Morphological kernel shape
            blur: Blur size
            gamma: Gamma value

        Returns:
            Processed tensor [B,H,W,C]
        """
        result = tensor

        # Step 1: Contract/Expand (morphological operation)
        if size != 0:
            result = self._morphology_operation(result, abs(size), "erode" if size < 0 else "dilate", kernel_shape)

        # Step 2: Blur
        if blur > 0.0:
            result = self._apply_blur(result, blur)

        # Step 3: Gamma
        if gamma != 1.0:
            result = self._apply_gamma(result, gamma)

        return result

    def _morphology_operation(
        self,
        tensor: torch.Tensor,
        size: int,
        operation: str,
        kernel_shape: str
    ) -> torch.Tensor:
        """
        Apply morphological operation (erode or dilate) with various kernel shapes.

        Detonate improvement: Support for circular, cross, and diamond kernels!

        Args:
            tensor: Input tensor [B,H,W,C]
            size: Operation size
            operation: "erode" or "dilate"
            kernel_shape: Shape of kernel ("square", "circular", "cross", "diamond")

        Returns:
            Processed tensor [B,H,W,C]
        """
        B, H, W, C = tensor.shape

        # Convert to [B,C,H,W] for processing
        tensor_nchw = tensor.permute(0, 3, 1, 2)

        # Create kernel based on shape
        kernel = self._create_kernel(size, kernel_shape)
        kernel = kernel.to(tensor.device)

        # Pad tensor
        padding = size
        tensor_padded = F.pad(tensor_nchw, (padding, padding, padding, padding), mode='replicate')

        # Apply morphological operation using unfold + kernel masking
        # Unfold creates sliding windows
        B_p, C_p, H_p, W_p = tensor_padded.shape
        kernel_size = 2 * size + 1

        # Unfold to get all neighborhoods
        unfolded = F.unfold(tensor_padded, kernel_size=(kernel_size, kernel_size), stride=1)
        # Shape: [B, C*kernel_size*kernel_size, H*W]

        # Reshape to [B, C, kernel_size*kernel_size, H*W]
        unfolded = unfolded.view(B, C, kernel_size * kernel_size, H * W)

        # Apply kernel mask
        kernel_flat = kernel.view(-1, 1)  # [kernel_size*kernel_size, 1]

        # Only consider pixels where kernel is 1
        kernel_mask = kernel_flat > 0.5  # Boolean mask

        if operation == "erode":
            # Erosion: minimum among masked pixels
            # Set non-masked pixels to inf so they don't affect min
            masked_values = unfolded.clone()
            masked_values[:, :, ~kernel_mask.squeeze(), :] = float('inf')
            result_flat, _ = torch.min(masked_values, dim=2)
        else:  # "dilate"
            # Dilation: maximum among masked pixels
            # Set non-masked pixels to -inf so they don't affect max
            masked_values = unfolded.clone()
            masked_values[:, :, ~kernel_mask.squeeze(), :] = float('-inf')
            result_flat, _ = torch.max(masked_values, dim=2)

        # Reshape back
        result_nchw = result_flat.view(B, C, H, W)

        # Convert back to [B,H,W,C]
        result = result_nchw.permute(0, 2, 3, 1)

        return result

    def _create_kernel(
        self,
        size: int,
        shape: str
    ) -> torch.Tensor:
        """
        Create morphological kernel with specified shape.

        Args:
            size: Kernel radius
            shape: Kernel shape

        Returns:
            Binary kernel tensor [kernel_size, kernel_size]
        """
        kernel_size = 2 * size + 1
        kernel = torch.zeros(kernel_size, kernel_size)

        center = size

        if shape == "square":
            # All ones (traditional morphological kernel)
            kernel.fill_(1.0)

        elif shape == "circular":
            # Circular kernel (Euclidean distance)
            for i in range(kernel_size):
                for j in range(kernel_size):
                    dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
                    if dist <= size:
                        kernel[i, j] = 1.0

        elif shape == "cross":
            # Cross shape (horizontal + vertical only)
            kernel[center, :] = 1.0  # Horizontal line
            kernel[:, center] = 1.0  # Vertical line

        elif shape == "diamond":
            # Diamond shape (Manhattan distance)
            for i in range(kernel_size):
                for j in range(kernel_size):
                    dist = abs(i - center) + abs(j - center)
                    if dist <= size:
                        kernel[i, j] = 1.0

        return kernel

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

        # Convert to [B,C,H,W] for convolution
        tensor_nchw = tensor.permute(0, 3, 1, 2)

        # Calculate sigma from blur size
        # Standard relationship: sigma ≈ size / 2
        sigma = blur_size / 2.0
        if sigma < 0.1:
            return tensor

        # Calculate kernel size (odd number, 3-6 sigma coverage)
        kernel_size = int(2 * round(3 * sigma) + 1)
        kernel_size = max(3, kernel_size)

        # Create 1D Gaussian kernel
        kernel_radius = kernel_size // 2
        coords = torch.arange(kernel_size, dtype=torch.float32, device=tensor.device) - kernel_radius
        gaussian = torch.exp(-(coords ** 2) / (2 * sigma ** 2))
        gaussian = gaussian / gaussian.sum()

        # Apply separable convolution (horizontal then vertical)
        # Horizontal blur
        kernel_h = gaussian.view(1, 1, 1, kernel_size).repeat(C, 1, 1, 1)
        result = F.conv2d(
            tensor_nchw,
            kernel_h,
            padding=(0, kernel_radius),
            groups=C
        )

        # Vertical blur
        kernel_v = gaussian.view(1, 1, kernel_size, 1).repeat(C, 1, 1, 1)
        result = F.conv2d(
            result,
            kernel_v,
            padding=(kernel_radius, 0),
            groups=C
        )

        # Convert back to [B,H,W,C]
        result = result.permute(0, 2, 3, 1)

        return result

    def _apply_gamma(
        self,
        tensor: torch.Tensor,
        gamma: float
    ) -> torch.Tensor:
        """
        Apply gamma correction.

        Args:
            tensor: Input tensor [B,H,W,C]
            gamma: Gamma value

        Returns:
            Gamma-corrected tensor [B,H,W,C]
        """
        # Ensure non-negative for pow operation
        tensor_safe = torch.clamp(tensor, min=0.0)

        # Apply gamma: output = input^(1/gamma)
        result = torch.pow(tensor_safe + 1e-7, 1.0 / gamma)

        return result
