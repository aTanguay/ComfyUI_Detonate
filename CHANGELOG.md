# Changelog

All notable changes to ComfyUI_Detonate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-22

### Added - Priority 1: The Basics (Essential Compositing Tools) ✅

This release includes all 8 Priority 1 nodes - the essential toolkit for professional compositing workflows.

#### Channel Operations
- **Premultiply** - Convert straight alpha to premultiplied alpha
  - Essential for proper compositing workflow
  - Handles missing alpha channels gracefully
- **Unpremultiply** - Convert premultiplied alpha to straight alpha
  - Epsilon parameter to prevent division by zero
  - Optional clamping to prevent extreme values
  - Required before color correction operations
- **Shuffle** - Rearrange and manipulate image channels
  - 7 source options: R, G, B, A, 0 (black), 1 (white), luminance
  - Perfect for creating mattes from channels
  - Rec. 709 luminance calculation

#### Compositing
- **Merge** - Industry-standard compositing with 8 blend modes
  - Over, Under, Plus (additive)
  - Screen (lighten), Multiply (darken)
  - Stencil, Mask, Atop
  - Mix parameter for blend strength (0-1)
  - Optional mask input
  - Auto-resize images to match dimensions
  - Proper premultiplied alpha handling

#### Filters
- **Blur** - Gaussian blur with professional quality
  - Separate X/Y size control for directional blur
  - Separable convolution (2-pass) for performance
  - Optional alpha channel blurring
  - GPU-accelerated using PyTorch
  - Automatic kernel size calculation (6σ rule)

#### Color Operations
- **ColorCorrect** - Quick color adjustments for layer matching
  - Saturation (0-4, 0=grayscale, 1=no change)
  - Contrast (around 0.5 pivot point)
  - Gamma (pow(x, 1/gamma) midtone adjustment)
  - Gain (multiply) and Offset (add)
  - Simpler alternative to Grade for quick tweaks
- **Grade** - Professional lift/gamma/gain color correction
  - Complete Nuke Grade formula implementation
  - Blackpoint/whitepoint for input range remapping
  - Lift (affects shadows most)
  - Gamma (affects midtones)
  - Gain (affects highlights most)
  - Offset and Multiply controls
  - Industry-standard film scan grading tool

#### Transform
- **Transform** - 2D geometric transformations
  - Translate (X/Y position in pixels)
  - Rotate (degrees, clockwise)
  - Scale (separate X/Y or uniform)
  - Skew (X/Y shear)
  - Adjustable center point (normalized 0-1)
  - Filter quality: Nearest, Bilinear, Bicubic
  - Edge modes: Black, Clamp (border), Repeat (reflection)
  - Uses PyTorch affine transformations for GPU acceleration

#### Matte Operations
- **Erode** - Contract mattes using morphological erosion
  - Size parameter (0-100 pixels)
  - Remove noise, fringe pixels, bright speckles
  - Selectable channels: RGBA, RGB, or Alpha only
  - GPU-accelerated using max pooling
- **Dilate** - Expand mattes using morphological dilation
  - Size parameter (0-100 pixels)
  - Fill holes, expand coverage
  - Selectable channels: RGBA, RGB, or Alpha only
  - GPU-accelerated using max pooling

### Technical Features

- **Full 32-bit float support** - HDR images with values 0 to infinity
- **GPU acceleration** - All nodes use PyTorch CUDA operations
- **Batch processing** - Efficient multi-image operations throughout
- **Premultiplied alpha workflow** - Industry-standard compositing
- **Professional accuracy** - Based on Nuke, Fusion, and Natron algorithms
- **Comprehensive documentation** - NODE_SPECIFICATIONS.md with exact formulas

### Infrastructure

- Complete utility library (tensor_utils, image_processing, color_math)
- Proper ComfyUI node registration system
- Professional project structure with organized categories
- Detailed planning and task documentation

### References

All implementations based on:
- Nuke official documentation (Foundry)
- Fusion documentation (Blackmagic Design)
- Natron open-source compositor (openfx-misc)
- Porter-Duff compositing algorithms
- Professional color science standards

---

## Roadmap

### [0.2.0] - Priority 2: Intermediate Tools (Planned)

- **ChromaKeyer** - Green/blue screen keying with spill suppression
- **LumaKeyer** - Luminance-based key generation
- **MatteControl** - All-in-one matte refinement
- **Clamp** - Constrain values to min/max range
- **Saturation** - Direct saturation control
- **Invert** - Invert color/channel values
- **ChannelCopy** - Copy channels between streams

### [0.3.0] - Priority 3: Advanced Tools (Planned)

- **CornerPin** - 4-point perspective transforms
- **Defocus** - Lens-style bokeh defocus
- **DirectionalBlur** - Motion-style directional blur
- **Sharpen** - Unsharp mask sharpening
- **HueCorrect** - Hue-based color adjustments
- **Glow** - Highlight blooming effects
- **Additional blend modes** - And more advanced operations

---

## Version History

- **0.1.0** (2025-01-22) - Priority 1: The Basics - 8 essential nodes ✅
- **0.0.1** (2025-01-21) - Initial project setup and planning
