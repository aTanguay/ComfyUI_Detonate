# ComfyUI_Detonate

Professional compositing nodes for ComfyUI - bringing Nuke and DaVinci Fusion workflows to AI-powered image generation.

## Overview

ComfyUI_Detonate provides industry-standard compositing tools familiar to VFX professionals, enabling traditional compositing workflows alongside AI image generation. All nodes support 32-bit float images with full precision, just like professional compositing software.

## Features

- **Professional-grade algorithms** based on Nuke and Fusion
- **Full float image support** (0-∞ range, not limited to 0-1)
- **Premultiplied alpha workflow** for accurate compositing
- **GPU-accelerated** operations using PyTorch
- **Batch processing** support for efficient workflows
- **Industry-standard** blend modes and color operations

## Implemented Nodes (4/8 Priority 1)

### Channel Operations
- **Premultiply** - Convert straight alpha to premultiplied alpha
- **Unpremultiply** - Convert premultiplied alpha to straight alpha (with epsilon and clamping options)
- **Shuffle** - Rearrange channels (R, G, B, A, constants, luminance)

### Compositing
- **Merge** - 8 blend modes: Over, Under, Plus, Screen, Multiply, Stencil, Mask, Atop
  - Mix parameter for blend strength
  - Optional mask input
  - Auto-resize images to match dimensions

### Filters
- **Blur** - Gaussian blur with separate X/Y control
  - Separable convolution for performance
  - Optional alpha channel blurring
  - GPU-accelerated

## Installation

1. Clone into your ComfyUI `custom_nodes` directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/aTanguay/ComfyUI_Detonate.git
```

2. Install dependencies:
```bash
cd ComfyUI_Detonate
pip install -r requirements.txt
```

3. Restart ComfyUI

## Usage

### Basic Compositing Workflow

1. **Load images** using standard ComfyUI nodes
2. **Premultiply** images before compositing (if using straight alpha)
3. **Merge** layers using blend modes (Over, Screen, Multiply, etc.)
4. **Unpremultiply** before color correction
5. **Apply color corrections** (Grade, ColorCorrect - coming soon)
6. **Premultiply** again before final merge
7. **Save** result

### Example: Green Screen Composite

```
LoadImage (foreground) → Premultiply → Merge (Over) → Output
                                         ↑
LoadImage (background) → Premultiply ───┘
```

### Example: Creating Alpha from Channel

```
LoadImage → Shuffle (red → alpha) → Premultiply → Merge
```

## Coming Soon (Priority 1)

- **Transform** - 2D transforms (translate, rotate, scale, skew)
- **ColorCorrect** - Saturation, contrast, gamma adjustments
- **Grade** - Professional lift/gamma/gain color correction
- **Erode/Dilate** - Morphological matte operations

## Technical Details

### Image Format
- **Tensor shape**: `[B, H, W, C]` (Batch, Height, Width, Channels)
- **Data type**: `torch.float32`
- **Value range**: `0.0 to ∞` (float images support HDR)
- **Channels**: 3 (RGB) or 4 (RGBA)

### Alpha Handling
ComfyUI_Detonate follows industry-standard premultiplied alpha workflow:
- **Premultiplied alpha**: RGB values are multiplied by alpha (required for accurate compositing)
- **Straight alpha**: RGB and alpha are independent (required for color correction)
- Use **Premultiply/Unpremultiply** nodes to convert between formats

## References

All implementations based on professional compositing software:
- [Natron](https://github.com/NatronGitHub/Natron) - Open-source compositor
- [Nuke](https://learn.foundry.com/nuke/) - Industry-standard compositor
- [DaVinci Fusion](https://www.blackmagicdesign.com/products/davinciresolve/fusion) - Professional compositing tools

## Development

See [PLANNING.md](PLANNING.md) for architecture and roadmap.
See [TASKS.md](TASKS.md) for detailed implementation checklist.
See [NODE_SPECIFICATIONS.md](NODE_SPECIFICATIONS.md) for precise node behaviors and formulas.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! This project aims to bring professional compositing tools to ComfyUI while maintaining accuracy to industry-standard software behavior.

---

**Status**: Active development - Priority 1 nodes in progress (4/8 complete)
**Version**: 0.1.0-alpha
