# ComfyUI_Detonate

Professional compositing nodes for ComfyUI - bringing Nuke and DaVinci Fusion workflows to AI-powered image generation.

## Overview

ComfyUI_Detonate provides industry-standard compositing tools familiar to VFX professionals, enabling traditional compositing workflows alongside AI image generation. All nodes support 32-bit float images with full precision, just like professional compositing software.

## Features

- **Professional-grade algorithms** based on Nuke and Fusion
- **Full float image support** (0-∞ range, not limited to 0-1)
- **Multi-channel EXR support** for CG render passes (NEW!)
- **Premultiplied alpha workflow** for accurate compositing
- **GPU-accelerated** operations using PyTorch
- **Batch processing** support for efficient workflows
- **Industry-standard** blend modes and color operations

## Implemented Nodes

### ✅ Tier 1: The Basics (9 nodes) - COMPLETE!
Core compositing tools used in virtually every session.

#### Channel Operations
- **Premultiply** - Convert straight alpha to premultiplied alpha
- **Unpremultiply** - Convert premultiplied alpha to straight alpha (with epsilon and clamping options)
- **Shuffle** - Rearrange channels (R, G, B, A, constants, luminance)

#### Compositing
- **Merge** - 8 blend modes: Over, Under, Plus, Screen, Multiply, Stencil, Mask, Atop
  - Mix parameter for blend strength
  - Optional mask input
  - Auto-resize images to match dimensions

#### Filters
- **Blur** - Gaussian blur with separate X/Y control
  - Separable convolution for performance
  - Optional alpha channel blurring
  - GPU-accelerated

#### Color Operations
- **ColorCorrect** - Quick color adjustments
  - Saturation, contrast, gamma, gain, offset
  - Perfect for matching composite layers
- **Grade** - Professional lift/gamma/gain color correction
  - Complete Nuke Grade formula
  - Blackpoint/whitepoint, lift, gamma, gain, offset, multiply
  - Industry-standard film scan grading

#### Transform
- **Transform** - 2D geometric transformations
  - Translate, rotate, scale, skew
  - Adjustable center point
  - Filter quality options (nearest, bilinear, bicubic)
  - Edge modes (black, clamp, repeat)

#### Matte Operations
- **Erode** - Contract mattes (morphological erosion)
  - Remove noise and fringe pixels
  - Selectable channels (RGBA, RGB, Alpha)
- **Dilate** - Expand mattes (morphological dilation)
  - Fill holes and expand coverage
  - Selectable channels (RGBA, RGB, Alpha)

---

### ✅ Tier 2: Essential Utilities (8 nodes) - COMPLETE!
The "unsexy but essential" tools for daily compositing work + CG workflow support.

#### Color Utilities
- **Clamp** - Constrain pixel values to min/max range
  - Fix HDR overbright pixels
  - Create binary masks via thresholding
  - Optional remapping for out-of-range values
- **Invert** - Invert selected channels (R, G, B, A independently)
  - Flip mattes
  - Create negative images
  - Optional clamping to 0-1
- **Saturation** - Direct saturation control
  - Simple HSV-based saturation adjustment
  - 0.0 = grayscale, 1.0 = original, >1.0 = boosted

#### Image Generation
- **Constant** - Solid color generator
  - Configurable dimensions
  - Supports HDR colors (values > 1.0)
  - Perfect for backgrounds and test patterns

#### Channel Operations
- **ChannelCopy** - Copy channels between two streams
  - Replace alpha from clean matte
  - Combine different render passes
  - Selective channel replacement

#### Matte Refinement
- **MatteControl** - All-in-one matte tool
  - Contract/expand (size parameter)
  - Blur (edge softening)
  - Gamma (density adjustment)
  - Replaces Erode→Blur→Grade workflow

#### Filters
- **EdgeDetect** - Sobel edge detection
  - Create edge mattes for effects
  - Optional pre-blur for noise reduction
  - Optional post-erode for thinning
  - Multiple output modes

#### File I/O
- **Load EXR** - Multi-channel EXR loader 🎬 **NEW!**
  - Load CG render passes (beauty, diffuse, specular, etc.)
  - Select specific AOV layers from multi-layer EXR
  - Full HDR float support
  - Industry-standard OpenImageIO backend

---

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

## Coming Soon

### 🎬 Tier 3: Keying Tools (Planned)
Professional greenscreen and matte extraction.

- **ChromaKeyer** - Green/blue screen keying with spill suppression
- **LumaKeyer** - Luminance-based key generation
- **DifferenceKeyer** - Clean plate differencing
- **Despill** - Remove greenscreen spill from edges

### ⚡ Tier 4: Advanced Tools (Planned)
Power user tools for complex workflows.

- **CornerPin** - 4-point perspective transforms
- **Defocus** - Lens-style bokeh depth of field
- **DirectionalBlur** - Motion blur effects
- **HueCorrect** - Hue-based color curves
- **GridWarp** - Manual image warping

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

**Status**: Tier 1 & 2 COMPLETE ✅ (17 nodes total) - Ready for production use!
**Version**: 0.2.0
