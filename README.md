# ComfyUI_Detonate

Professional compositing nodes for ComfyUI - bringing Nuke and DaVinci Fusion workflows to AI-powered image generation.

## Overview

ComfyUI_Detonate provides industry-standard compositing tools familiar to VFX professionals, enabling traditional compositing workflows alongside AI image generation. All nodes support 32-bit float images with full precision, just like professional compositing software.

## Features

- **Professional-grade algorithms** based on Nuke and Fusion
- **Full float image support** (0-∞ range, not limited to 0-1)
- **Multi-channel EXR support** for CG render passes
- **Cryptomatte ID mattes** for object/material extraction
- **Depth-based compositing** (ZDefocus, ZMerge) for CG workflows 🔥 **NEW!**
- **Visual effects** (Glow, Defocus, Sharpen) for professional finishing 🔥 **NEW!**
- **Professional color grading** with Bezier curves 🔥 **NEW!**
- **Procedural generators** (Ramp, Noise) for masks and textures 🔥 **NEW!**
- **Premultiplied alpha workflow** for accurate compositing
- **GPU-accelerated** operations using PyTorch
- **Batch processing** support for efficient workflows
- **Industry-standard** blend modes and color operations

## 🎉 Version 0.6.0 - Tier 4: Production Finishing!

**8 new professional nodes** for final polish and creative effects:

1. **Crop** - Aspect ratio presets (16:9, 2.39:1, etc.) + soft edges (linear/smooth/gaussian falloff)
2. **Exposure** - Photographic f-stops + per-channel exposure + highlight rolloff + response curves (linear/log/filmic)
3. **Vignette** - Multiple shapes (circular/oval/rectangular) + falloff curves + color tinting
4. **Grain** - 4 grain types (film/digital/organic/halftone) + luminance-dependent + per-channel intensity
5. **HueSatVal** - Direct HSV manipulation + selective hue ranges (reds/yellows/etc.) + preserve luminance
6. **Denoise** - 3 algorithms (bilateral/median/gaussian) + detail preservation + luma/chroma separation
7. **LUT** - 1D/3D .cube file support + trilinear interpolation + LUT caching + strength control
8. **CornerPin** - 4-point perspective transform + homography calculation (DLT/SVD) + multiple filter modes

**Total node count: 34 nodes** (9 Tier 1 + 8 Tier 2 + 1 Cryptomatte + 8 Tier 3 + 8 Tier 4)

## 🎉 Version 0.5.0 - Quality-of-Life Upgrades!

We've upgraded **5 core nodes** with professional enhancements that weren't in the original implementations:

### Merge - 16 Blend Modes (was 8)
**Added 8 Photoshop-style blends:**
Overlay, Soft Light, Hard Light, Color Dodge, Color Burn, Divide, Difference, Exclusion

Perfect for advanced compositing, glow effects, and color grading workflows.

### Grade - Per-Channel RGB Controls
**Added separate R/G/B lift/gamma/gain controls** (like Nuke's full Grade node)

Now supports precise per-channel color correction for matching problematic footage. Master controls + per-channel adjustments work together.

### ColorCorrect - Hue Shift
**Added hue rotation control** (-180° to +180°)

Essential for color matching between different camera sources or lighting conditions. Uses proper RGB→HSV→RGB conversion.

### EdgeDetect - 4 Algorithms (was 1)
**Added Laplacian, Prewitt, and Scharr** (in addition to Sobel)

Different algorithms for different needs:
- **Sobel**: Standard, balanced
- **Laplacian**: Fine edges, more noise-sensitive
- **Prewitt**: Simpler, faster
- **Scharr**: Best rotation invariance

### MatteControl - 4 Kernel Shapes (was 1)
**Added Circular, Cross, and Diamond** (in addition to Square)

Professional matte refinement with shape control:
- **Square**: Traditional morphology
- **Circular**: Natural, organic edges
- **Cross**: Directional (H+V only)
- **Diamond**: 45° diagonal emphasis

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
- **Load EXR** - Multi-channel EXR loader 🎬
  - Load CG render passes (beauty, diffuse, specular, etc.)
  - Select specific AOV layers from multi-layer EXR
  - Full HDR float support
  - Industry-standard OpenImageIO backend

---

### 🎯 Cryptomatte: Object/Material ID Mattes (1 node) - NEW!
Industry-standard ID matte extraction for CG compositing workflows.

- **Cryptomatte Extract** - Extract object/material ID mattes 🔥 **NEW!**
  - Load Cryptomatte-encoded EXR files from any renderer
  - Select objects/materials by name for automatic matte extraction
  - Perfect anti-aliasing with motion blur and transparency support
  - CryptoObject, CryptoMaterial, CryptoAsset support
  - Works with renders from Blender, Maya, Houdini, Cinema 4D, etc.
  - Based on Psyop's open-source Cryptomatte specification

**Example workflow:**
```
Render EXR with Cryptomatte → CryptomatteExtract("car, wheels") → Matte
                                                                    ↓
LoadEXR (beauty pass) ──────────────────────────────→ ColorCorrect (masked) → Output
```

---

### ✅ Tier 3: Effects & Color (8 nodes) - COMPLETE! 🎉
Production-essential tools for professional finishing and CG workflows.

#### Visual Effects
- **Glow** ⭐ - Multi-scale bloom with threshold control
  - Luminous glow for bright areas
  - Geometric blur progression (5-10 iterations)
  - Saturation boost for vibrant glows
  - Perfect for light rays, magic effects, UI elements

- **Defocus** - Lens-style bokeh blur
  - Circular, hexagonal, and octagonal bokeh shapes
  - Anamorphic lens simulation (aspect ratio control)
  - More realistic than Gaussian blur
  - Quality presets for speed/quality tradeoff

- **Sharpen** - Unsharp mask sharpening
  - Luminance-only mode (avoid color fringing)
  - Threshold control for noise suppression
  - Recover detail from soft renders

#### Depth-Based Tools (CG Pipeline)
- **ZDefocus** ⭐⭐ - Depth-based depth-of-field
  - Uses Z-depth channel from CG renders
  - Layer-based processing for realistic DOF
  - Auto-detect depth channels
  - Animate focus distance for rack focus effects

- **ZMerge** ⭐⭐ - Depth compositing
  - Composite layers using Z-depth (closer pixels win)
  - Essential for CG layer compositing
  - Edge antialiasing (improvement over Nuke!)
  - Auto-detect depth channels

#### Professional Color Grading
- **ColorCurves** ⭐ - Bezier curve color grading
  - Master, Red, Green, Blue curves
  - Built-in presets: S-curve, filmic, lift shadows, crush blacks
  - Industry-standard tonal control
  - HDR support

#### Procedural Generators
- **Ramp** - Gradient generator
  - 4 types: Linear, Radial, Angle, Box
  - Falloff curves: Linear, Smooth, Exponential, Logarithmic
  - Full RGBA color support with HDR
  - Perfect for vignettes, lighting ramps, masks

- **Noise** - Procedural Perlin noise
  - Fractal noise with octaves
  - Grayscale or RGB color noise
  - Reproducible (seed control)
  - Perfect for textures, grain, matte breakup

---

### ✅ Tier 4: Production Finishing (8 nodes) - COMPLETE! 🎉
Final polish and creative finishing tools for professional output.

#### Framing & Composition
- **Crop** - Aspect ratio presets + soft edges
  - **7 aspect ratio presets**: 16:9, 2.39:1, 2.35:1, 1.85:1, 4:3, 1:1, 9:16
  - **3 feather modes**: Linear, Smooth (smoothstep), Gaussian
  - **Center crop mode** for quick framing
  - Perfect for format changes and creative framing

#### Photographic Controls
- **Exposure** ⭐ - Photographic f-stops exposure
  - **Per-channel stops** (R/G/B) for creative color grading
  - **Highlight rolloff** - Prevent blown highlights
  - **3 response curves**: Linear, Logarithmic (HDR), Filmic (ACES-like)
  - More intuitive than multiply/gain for photographers

- **Vignette** - Lens vignetting effect
  - **3 shapes**: Circular, Oval, Rectangular
  - **4 falloff curves**: Linear, Quadratic, Cubic, Smooth
  - **Color tinting** for stylistic edges
  - **Inverse mode** - Lighten edges instead of darken

#### Texture & Film Emulation
- **Grain** ⭐ - Film grain and texture
  - **4 grain types**: Film (Gaussian), Digital (uniform), Organic (multi-scale), Halftone (dot pattern)
  - **Luminance-dependent** - Shadow/highlight bias controls
  - **Per-channel intensity** (R/G/B)
  - **Color vs monochrome** grain
  - Essential for matching CG to live action

#### Advanced Color Control
- **HueSatVal** - Direct HSV manipulation
  - **Selective hue ranges** - Target specific colors (reds, yellows, greens, cyans, blues, magentas)
  - **Range softness** - Feathered transitions
  - **Preserve luminance** mode
  - Perfect for precise color adjustments

- **LUT** ⭐⭐ - 1D/3D color lookup tables
  - **Industry-standard .cube file support**
  - **Trilinear interpolation** for 3D LUTs
  - **LUT caching** for performance
  - **Strength control** - Mix with original
  - Apply film emulation and creative grades

#### Noise Reduction & Warping
- **Denoise** - Edge-preserving noise reduction
  - **3 algorithms**: Bilateral (edge-preserving), Median (salt-and-pepper), Gaussian (simple)
  - **Detail preservation** control
  - **Luma/chroma separation** - Denoise brightness and color independently
  - Perfect for cleaning noisy footage

- **CornerPin** ⭐⭐ - 4-point perspective transform
  - **Homography calculation** (DLT/SVD algorithm)
  - **3 filter modes**: Bilinear, Bicubic, Nearest
  - **Inverse transformation**
  - Essential for screen replacements and match-moving

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

### 🎬 Future Tiers: Keying & Advanced Tools (Planned)
Professional keying tools and advanced transforms for complex workflows.

**Keying:**
- **ChromaKeyer** - Green/blue screen keying with spill suppression
- **LumaKeyer** - Luminance-based key generation
- **DifferenceKeyer** - Clean plate differencing
- **Despill** - Remove greenscreen spill from edges

**Advanced Transforms:**
- **GridWarp** - Manual image warping with grid control
- **DirectionalBlur** - Motion blur effects with angle control
- **LensDistort** - Lens distortion correction and simulation

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

**Status**: Tier 1, 2, 3 & 4 COMPLETE + Cryptomatte ✅ (34 nodes total) - Production-ready VFX toolkit!
**Version**: 0.6.0
