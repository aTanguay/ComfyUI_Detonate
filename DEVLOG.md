# ComfyUI_Detonate - Development Log

This document tracks the development history and version releases of ComfyUI_Detonate.

For current status and features, see [README.md](README.md).  
For project planning, see [PLANNING.md](PLANNING.md).

---

## 🎉 Version 0.10.0 - Bridge Tools Round 2: AI Inpainting Perfection! 🎨

**Release Date:** 2025-01-23

**Essential tools for AI inpainting and tiled generation workflows!**

### New Bridge Tools (2 Critical Nodes)

**1. TriMap Generator** ⭐⭐⭐ - Perfect AI inpainting setup
   - **Auto-generate trimaps** - White (keep), Black (remove), Gray (AI decides)
   - **Adjustable unknown width** - Control transition zone size
   - **Multiple modes** - Edge Distance, Threshold Only, Full Unknown
   - **RGB preview** - See trimap regions (Green=FG, Red=BG, Blue=Unknown)
   - **Threshold controls** - Define foreground/background certainty
   - Essential for high-quality AI inpainting - tells AI exactly what needs work
   - **UNIQUE:** No proper trimap generator exists in ComfyUI ecosystem

**2. Seam Blender** ⭐⭐⭐ - Remove AI tiling seams
   - **Multiple blend methods** - Feather (fast), Gradient (good), Poisson (best)
   - **Auto-detect seams** - Find tile boundaries automatically
   - **Manual seam placement** - JSON array for precise control
   - **Adjustable blend width** - Control transition smoothness
   - **Horizontal & vertical** - Handle any tiling pattern
   - Fixes visible seams from AI tiled generation, panorama stitching
   - **UNIQUE:** Solves specific AI tiling problem, doesn't exist elsewhere

**MatteControl Highlight** ⭐⭐⭐ - Professional matte refinement (Tier 2 node)
   - **All-in-one workflow** - Erode/Dilate + Blur + Gamma + Levels in one node
   - **Preview modes** - See each processing stage
   - **Proper operation order** - Industry-standard matte cleanup pipeline
   - Replaces 4-5 node chains with a single professional control
   - Essential daily tool for every compositor

**Total node count: 44 nodes**

---

## 🎉 Version 0.9.0 - Bridge Tools: GenAI ↔ Compositing! 🌉

**Release Date:** 2025-01-23

**Unique tools bridging traditional compositing and generative AI workflows!**

### What Makes These Special?

These nodes fill critical gaps in the ComfyUI ecosystem - they either don't exist elsewhere or lack professional-grade implementations. Built specifically to help compositors work with AI-generated images.

### Bridge Tools (3 Unique Nodes)

**1. Edge Defringe (AlphaPremultFix)** ⭐⭐⭐ - Fix AI image edge artifacts
   - **Erode Matte technique** - Shrink alpha, dilate color to fill edge
   - **Color suppression** - Remove greenscreen spill and color contamination
   - **Premult fix** - Remove dark/bright halos from premult errors
   - **Problem color selection** - Green, Blue, Red, Custom, or Auto-detect
   - **Multiple modes** - Erode Matte, Color Suppress, Premult Fix, or All
   - Essential for cleaning up AI inpainting, background removal, and greenscreen artifacts
   - **UNIQUE:** Nothing else in ComfyUI handles edge defringing this comprehensively

**2. Displacement Map** ⭐⭐⭐ - Professional IDistort-style warping
   - **UV displacement** - R=X, G=Y vector field warping
   - **Adjustable scale** - Independent X/Y displacement strength
   - **Edge modes** - Clamp, Wrap, or Black
   - **Bilinear interpolation** - Smooth, high-quality results
   - **Center-neutral option** - 0.5 = no displacement (standard)
   - **Alpha as Y option** - Use alpha channel for Y displacement
   - Perfect for heat distortion, refraction, lens correction, creative warping
   - **UNIQUE:** No professional displacement mapping exists in ComfyUI

**3. GridWarp** ⭐⭐ - Mesh-based image warping
   - **Control grid** - 2×2 to 32×32 mesh resolution
   - **Piecewise affine** - Smooth quad-based warping
   - **JSON grid data** - Persistent grid point offsets
   - **Strength control** - Warp intensity multiplier
   - **Edge modes** - Clamp or Black
   - Ideal for perspective correction, lens distortion, creative warping, building straightening
   - **UNIQUE:** Mesh-based warping doesn't exist in ComfyUI

**Total node count: 42 nodes**

---

## 🎉 Version 0.8.0 - Tier 6: Professional Keying! 🎬

**Release Date:** 2025-01-22

**Essential greenscreen and brightness keying tools!**

### Keying Toolkit (3 Professional Nodes)

**1. ChromaKeyer** ⭐⭐⭐ - Professional greenscreen/bluescreen keying
   - **Screen color presets** - Green, Blue, Custom RGB
   - **Color difference algorithm** - Industry-standard keying
   - **Threshold & tolerance controls** - Precise key tuning
   - **Softness control** - Smooth edge transitions
   - **Spill suppression** - Remove green/blue color cast from edges
   - **Multiple output modes** - Alpha, Foreground, Raw Key, Despilled
   - Essential for greenscreen removal and virtual production

**2. LumaKeyer** ⭐⭐ - Advanced brightness-based keying
   - **Multiple luma modes** - Rec.709, Average, Max, Min
   - **Range controls** - Min/Max brightness selection
   - **Soft edges** - Smooth key transitions
   - **Invert option** - Key dark or bright areas
   - **Output modes** - Alpha or Foreground
   - Perfect for sky replacement, highlight/shadow isolation

**3. LumaKeyer Simple** ⭐ - Quick single-threshold luma keyer
   - **Single threshold** - Fast brightness keying
   - **Tolerance control** - Adjust key range
   - **Brighter/Darker modes** - Quick selection
   - Ideal for simple sky replacement or quick selections

**Total node count: 39 nodes**

---

## 🎉 Version 0.7.0 - Tier 5: Interactive Masking! 🔥

**Release Date:** 2025-01-22

**MAJOR FEATURE: Professional Rotoscoping Tools + Phase 1.5 Enhancements!**

### RotoBezier - Interactive Spline Drawing

The #1 requested feature by compositors is here! Draw precise masks directly in ComfyUI with professional Bezier spline tools.

**2 nodes with Phase 1.5 professional enhancements:**

**1. RotoBezier** - Interactive Bezier spline drawing for mask creation
   - **Web-based interactive drawing widget** - Click to draw points, drag handles for smooth curves
   - **de Casteljau's algorithm** from Natron for numerically stable Bezier evaluation
   - **Supersampling anti-aliasing** (1-16×) for film-quality smooth edges
   - **Distance field feathering** with smoothstep falloff (better than gaussian blur!)
   - **🔥 Phase 1.5: Shape operations** - Add/Subtract/Intersect per spline for complex boolean masking
   - **🔥 Phase 1.5: Falloff curves** - Linear/Smooth/Gaussian feather types for artistic control
   - **🔥 Phase 1.5: Per-spline invert** - Individual control over each shape's contribution
   - **🔥 Phase 1.5: Preset shapes** - Circle, Rectangle, Star generators for quick work
   - **Multiple splines** - Draw multiple shapes with boolean operations
   - **Keyboard shortcuts** - Enter to close, Delete to remove, Escape to cancel
   - **JSON-based data exchange** between web widget and Python backend

**2. RotoBezier From Image** - Automatically matches input image dimensions
   - Same features as RotoBezier
   - Convenience node for rotoscoping over footage

**Why this is a game-changer:**
- **Replaces Natron/Nuke RotoPaint** for basic rotoscoping workflows
- **Best-in-class implementation** with modern web UI and high-quality rendering
- **Essential for garbage mattes** - quickly isolate subjects for compositing
- **Professional soft edges** - distance field feathering beats traditional blur approaches
- **🔥 Shape operations** - Add/Subtract/Intersect for complex boolean masking like Photoshop
- **🔥 Artistic feathering** - Choose between Linear, Smooth (smoothstep), or Gaussian falloff curves

**Total node count: 36 nodes**

---

## 🎉 Version 0.6.0 - Tier 4: Production Finishing!

**Release Date:** 2025-01-22

**8 new professional nodes** for final polish and creative effects:

1. **Crop** - Aspect ratio presets (16:9, 2.39:1, etc.) + soft edges (linear/smooth/gaussian falloff)
2. **Exposure** - Photographic f-stops + per-channel exposure + highlight rolloff + response curves (linear/log/filmic)
3. **Vignette** - Multiple shapes (circular/oval/rectangular) + falloff curves + color tinting
4. **Grain** - 4 grain types (film/digital/organic/halftone) + luminance-dependent + per-channel intensity
5. **HueSatVal** - Direct HSV manipulation + selective hue ranges (reds/yellows/etc.) + preserve luminance
6. **Denoise** - 3 algorithms (bilateral/median/gaussian) + detail preservation + luma/chroma separation
7. **LUT** - 1D/3D .cube file support + trilinear interpolation + LUT caching + strength control
8. **CornerPin** - 4-point perspective transform + homography calculation (DLT/SVD) + multiple filter modes

**Total node count: 34 nodes**

---

## 🎉 Version 0.5.0 - Quality-of-Life Upgrades!

**Release Date:** 2025-01-22

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

**Total node count: 26 nodes**

---

## Earlier Versions

See [CHANGELOG.md](DOCS/CHANGELOG.md) for detailed commit history.

For complete development history, see the git commit log.
