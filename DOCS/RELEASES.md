# ComfyUI_Detonate Releases

This document explains the tiered release structure for ComfyUI_Detonate, allowing users to install node packages based on their needs.

---

## Release Tiers

ComfyUI_Detonate is organized into three tiers, each building on the previous one:

### 🎯 Tier 1: The Basics (v0.1.0) - **AVAILABLE NOW** ✅

**Essential compositing tools used in virtually every session.**

Perfect for:
- Basic compositing workflows
- Layer blending and color correction
- Matte creation and cleanup
- Fundamental image operations

**Included nodes (9 total):**
- Premultiply / Unpremultiply
- Shuffle
- Merge (8 blend modes)
- Blur
- ColorCorrect
- Grade
- Transform
- Erode / Dilate

**Installation:**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/aTanguay/ComfyUI_Detonate.git
cd ComfyUI_Detonate
pip install -r requirements.txt
```

**Use cases:**
- ✅ Composite foreground over background with proper alpha
- ✅ Color grade and match composite layers
- ✅ Clean up and refine mattes
- ✅ Position, rotate, and scale elements
- ✅ Blur and soften edges
- ✅ Create mattes from channels

---

### 🚀 Tier 2: Intermediate Tools (v0.2.0) - **COMING SOON**

**Professional keying and advanced matte operations.**

Perfect for:
- Green screen / blue screen work
- Advanced keying workflows
- Professional matte refinement
- Color and channel manipulation

**Planned nodes (~15 total):**
- ChromaKeyer (green/blue screen)
- LumaKeyer (luminance-based keying)
- MatteControl (all-in-one matte tool)
- Clamp (value constraints)
- Saturation (direct saturation control)
- Invert (color/channel inversion)
- ChannelCopy (multi-stream operations)
- DifferenceKeyer (clean plate differencing)
- Constant/Background (solid colors)
- EdgeDetect (edge extraction)

**Estimated release:** Q2 2025

**Use cases:**
- ✅ Professional green screen keying
- ✅ Advanced matte cleanup and refinement
- ✅ Luma-based matte generation
- ✅ Selective color adjustments
- ✅ Complex channel operations

---

### ⚡ Tier 3: Advanced Tools (v0.3.0) - **PLANNED**

**Specialized tools for advanced VFX workflows.**

Perfect for:
- Complex transformations
- Advanced filtering
- Specialized effects
- Professional VFX workflows

**Planned nodes (~20 total):**
- CornerPin (4-point perspective)
- Defocus (lens-style bokeh)
- DirectionalBlur (motion blur)
- Sharpen (unsharp mask)
- HueCorrect (hue-based curves)
- Glow (highlight blooming)
- GridWarp (manual warping)
- LensDistortion (distort/undistort)
- IDistort/Displace (displacement mapping)
- Median (noise reduction)
- VectorBlur (motion vector-based)
- FrameHold / TimeOffset (time operations)
- Ramp/Gradient generators
- And more...

**Estimated release:** Q3-Q4 2025

**Use cases:**
- ✅ Screen replacements (CornerPin)
- ✅ Realistic depth of field (Defocus)
- ✅ Advanced blur effects
- ✅ Selective color grading
- ✅ Complex geometric transforms
- ✅ Temporal effects

---

## Installation Options

### Option 1: Latest Stable Release (Recommended)
Install the latest stable release with proven, tested nodes:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/aTanguay/ComfyUI_Detonate.git
cd ComfyUI_Detonate
pip install -r requirements.txt
```

The repository contains the latest stable v0.2.0 release (Tier 1 + Tier 2: 16 nodes).

Future tiers will be released as development continues.

---

## Requirements

### Minimum System Requirements
- **Python:** 3.8 or higher
- **PyTorch:** 2.0.0 or higher
- **ComfyUI:** Latest stable version
- **VRAM:** 4GB+ (8GB+ recommended for 4K images)

### Core Dependencies
```
torch>=2.0.0
numpy>=1.20.0
pillow>=9.0.0
```

### Optional Dependencies (Advanced Features)
```
opencv-python>=4.5.0  # For advanced keying (Tier 2+)
scikit-image>=0.19.0  # For specialized filters (Tier 3)
scipy>=1.7.0          # For advanced algorithms (Tier 3)
```

---

## Upgrade Path

When new tiers are released, you can upgrade by pulling the latest changes:

```bash
cd ComfyUI/custom_nodes/ComfyUI_Detonate
git pull
pip install -r requirements.txt --upgrade
```

Then restart ComfyUI to load the new nodes.

---

## Version Compatibility

Each tier is **backwards compatible** - upgrading to a higher tier keeps all nodes from previous tiers:

- **Tier 2** includes all Tier 1 nodes + new intermediate nodes
- **Tier 3** includes all Tier 1 & 2 nodes + new advanced nodes

Your existing workflows will continue to work when upgrading!

---

## Release Schedule

- **v0.1.0** (Tier 1: The Basics) - ✅ **Released: January 22, 2025**
- **v0.2.0** (Tier 2: Intermediate) - 🚧 **Target: Q2 2025**
- **v0.3.0** (Tier 3: Advanced) - 📋 **Target: Q3-Q4 2025**

---

## Getting Help

- **Documentation:** See [NODE_SPECIFICATIONS.md](NODE_SPECIFICATIONS.md) for detailed node behavior
- **Planning:** See [PLANNING.md](PLANNING.md) for architecture and roadmap
- **Tasks:** See [TASKS.md](TASKS.md) for development progress
- **Issues:** Report bugs at https://github.com/aTanguay/ComfyUI_Detonate/issues

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

**Current Release:** v0.2.0 (Tier 1 + Tier 2) ✅
**Status:** Production Ready - 16 professional nodes available!

### Tier 2: Essential Utilities (v0.2.0) - **AVAILABLE NOW** ✅

**The "unsexy but essential" daily compositing tools.**

Perfect for:
- HDR value management
- Matte manipulation
- Quick color adjustments
- Channel operations
- Image generation

**Included nodes (7 total):**
- Clamp (constrain values, create masks)
- Invert (flip channels independently)
- Constant (solid color generator)
- Saturation (direct HSV saturation)
- ChannelCopy (copy channels between streams)
- MatteControl (all-in-one matte refinement)
- EdgeDetect (Sobel edge detection)

**Installation:**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/aTanguay/ComfyUI_Detonate.git
cd ComfyUI_Detonate
pip install -r requirements.txt
```

**Use cases:**
- ✅ Fix overbright HDR pixels with Clamp
- ✅ Flip mattes with Invert
- ✅ Generate test patterns with Constant
- ✅ Boost/reduce saturation quickly
- ✅ Replace alpha from clean matte (ChannelCopy)
- ✅ One-node matte cleanup (MatteControl)
- ✅ Create edge mattes for effects

---


