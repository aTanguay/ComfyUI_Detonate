# Node Documentation

**Welcome to the ComfyUI_Detonate Node Reference!**

This guide explains every node in beginner-friendly terms. Whether you're new to compositing or coming from Photoshop, we'll help you understand what each tool does and when to use it.

---

## 📖 How to Use This Guide

Each node page includes:
- **Plain language explanation** - No confusing jargon!
- **When to use it** - Real-world examples
- **Parameter guide** - What each setting does
- **Tips & tricks** - Beginner and professional techniques
- **Example workflows** - Step-by-step tutorials
- **Related nodes** - What works well together

**Complexity Ratings:**
- ⭐ **Beginner** - Easy to understand, hard to mess up
- ⭐⭐ **Intermediate** - Needs some practice
- ⭐⭐⭐ **Advanced** - Professional tool, take your time to learn

---

## 🚀 Quick Start Paths

**New to Compositing?** Start here:
1. [Merge](compositing/merge.md) - Combine images (like Photoshop layers)
2. [Transform](transforms/transform.md) - Move, rotate, scale images
3. [Blur](filters/blur.md) - Soften images
4. [Grade](color/grade.md) - Professional color correction
5. [Noise](generators/noise.md) - Generate textures and grain

**Coming from Photoshop?**
- Photoshop "Layers" → [Merge](compositing/merge.md)
- Photoshop "Levels/Curves" → [Grade](color/grade.md)
- Photoshop "Gaussian Blur" → [Blur](filters/blur.md)
- Photoshop "Add Noise" → [Noise](generators/noise.md)
- Photoshop "Select by Color" → [ChromaKeyer](keying/chromakeyer.md)

**Want to Remove Greenscreens?**
1. [ChromaKeyer](keying/chromakeyer.md) - Remove green/blue backgrounds
2. [MatteControl](matte/mattecontrol.md) - Refine edges
3. [Despill](keying/despill.md) - Remove green fringe
4. [Merge](compositing/merge.md) - Composite onto new background

---

## 📚 Nodes by Category

### 🎨 **Compositing** - Combining Images

These nodes let you layer images on top of each other, like Photoshop layers but with more control.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **[Merge](compositing/merge.md)** | ⭐⭐ | ✅ | Combine two images with blend modes (Over, Screen, Multiply, etc.) |
| **Copy** | ⭐ | 📝 | Copy channels from one image to another |
| **Switch** | ⭐ | 📝 | Switch between multiple inputs based on index |

**When to use Compositing nodes:** Putting people on new backgrounds, adding effects layers, building up complex images from pieces.

---

### 🌈 **Color** - Color Correction & Grading

These nodes adjust colors, brightness, contrast, and overall image tone. Essential for making different shots match or creating a specific mood.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **[Grade](color/grade.md)** | ⭐⭐⭐ | ✅ | Professional color grading (Lift/Gamma/Gain) |
| **ColorCorrect** | ⭐⭐ | 📝 | Quick color adjustments (saturation, contrast, gamma) |
| **Clamp** | ⭐ | 📝 | Limit pixel values to a range (prevent out-of-range values) |
| **Invert** | ⭐ | 📝 | Invert colors (negative image) |
| **HSVAdjust** | ⭐⭐ | 📝 | Adjust Hue, Saturation, Value separately |
| **Saturation** | ⭐ | 📝 | Change color intensity (grayscale to vivid) |
| **Exposure** | ⭐ | 📝 | Photographic exposure control (stops) |

**When to use Color nodes:** Matching shots, fixing bad lighting, creating mood, color grading for film look.

---

### 🔑 **Keying** - Background Removal

These nodes remove solid-color backgrounds (greenscreen/bluescreen) and create transparency. Core VFX workflow!

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **[ChromaKeyer](keying/chromakeyer.md)** | ⭐⭐⭐ | ✅ | Remove greenscreen/bluescreen backgrounds |
| **LumaKeyer** | ⭐⭐ | 📝 | Remove based on brightness (black or white backgrounds) |
| **Despill** | ⭐⭐ | 📝 | Remove green/blue color spill from edges |

**When to use Keying nodes:** Greenscreen removal, virtual backgrounds, product photography, VFX compositing.

---

### 🔄 **Transform** - Movement & Distortion

These nodes move, rotate, scale, and warp images. Essential for positioning elements and creative effects.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **Transform** | ⭐⭐ | 📝 | Move, rotate, scale, skew images |
| **CornerPin** | ⭐⭐⭐ | 📝 | 4-point perspective warp (screen replacement) |
| **[DisplacementMap](transforms/displacementmap.md)** | ⭐⭐⭐ | 📝 | Distort with displacement maps (heat waves, ripples) |
| **[GridWarp](transforms/gridwarp.md)** | ⭐⭐⭐ | 📝 | Mesh-based warping (manual control grid) |

**When to use Transform nodes:** Positioning elements, perspective correction, lens distortion, creative warping.

---

### 🌫️ **Filter** - Blur, Sharpen, & Effects

These nodes modify image clarity, add glows, detect edges, and create various filter effects.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **Blur** | ⭐ | 📝 | Gaussian blur (soften images) |
| **Sharpen** | ⭐ | 📝 | Increase image sharpness/detail |
| **EdgeDetect** | ⭐⭐ | 📝 | Find edges in images (Sobel, Canny) |
| **Median** | ⭐⭐ | 📝 | Remove noise while preserving edges |
| **Bilateral** | ⭐⭐ | 📝 | Smart blur (preserves edges) |
| **Glow** | ⭐⭐ | 📝 | Add light bloom/glow to bright areas |
| **EdgeBlur** | ⭐⭐ | 📝 | Blur only at edges (for keying) |

**When to use Filter nodes:** Softening backgrounds, adding glows, removing noise, creating depth of field.

---

### 🎲 **Generator** - Create from Nothing

These nodes generate images from mathematical algorithms - no input image required!

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **Constant** | ⭐ | 📝 | Solid color image (flat color field) |
| **[Noise](generators/noise.md)** | ⭐⭐ | ✅ | Procedural noise (Perlin, Simplex, Worley, etc.) |
| **Gradient** | ⭐ | 📝 | Color gradients (linear, radial) |
| **Checkerboard** | ⭐ | 📝 | Checkerboard patterns (testing, mattes) |

**When to use Generator nodes:** Creating textures, film grain, backgrounds, displacement maps, test patterns.

---

### 🎭 **Matte** - Alpha Channel Operations

These nodes manipulate alpha channels (transparency) and refine mattes from keying.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **Premultiply** | ⭐⭐ | 📝 | Multiply RGB by alpha (prepare for compositing) |
| **Unpremultiply** | ⭐⭐ | 📝 | Divide RGB by alpha (prepare for color correction) |
| **[MatteControl](matte/mattecontrol.md)** | ⭐⭐⭐ | 📝 | All-in-one matte refinement (erode, blur, gamma, levels) |
| **Erode** | ⭐⭐ | 📝 | Shrink/expand mattes (edge control) |

**When to use Matte nodes:** Refining keying results, fixing edge fringing, preparing for compositing.

---

### 🔀 **Channel** - Channel Manipulation

These nodes work with individual color channels (Red, Green, Blue, Alpha) and rearrange them.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **Shuffle** | ⭐⭐ | 📝 | Rearrange channels (copy Red to Alpha, etc.) |
| **ChannelCopy** | ⭐ | 📝 | Copy specific channel to another |
| **SetAlpha** | ⭐ | 📝 | Replace alpha channel with new mask |
| **RemoveAlpha** | ⭐ | 📝 | Remove alpha channel (RGBA → RGB) |

**When to use Channel nodes:** Custom matte creation, channel math, advanced compositing tricks.

---

### 🏔️ **Depth** - 3D Compositing

These nodes work with depth information for realistic compositing of 3D renders.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **ZDefocus** | ⭐⭐⭐ | 📝 | Depth-based blur (realistic depth of field) |
| **DepthMerge** | ⭐⭐⭐ | 📝 | Composite using depth (automatic layering) |
| **DepthToPosition** | ⭐⭐⭐ | 📝 | Convert depth map to 3D positions |
| **PositionToNormal** | ⭐⭐⭐ | 📝 | Calculate surface normals from positions |

**When to use Depth nodes:** 3D render compositing, realistic depth of field, relighting from depth/normals.

---

### 📼 **IO** - Time Operations

These nodes manipulate time - hold frames, offset timing, retime sequences.

| Node | Complexity | Status | Description |
|------|-----------|--------|-------------|
| **FrameHold** | ⭐ | 📝 | Freeze on specific frame |
| **TimeOffset** | ⭐ | 📝 | Shift sequence forward/backward in time |

**When to use Time nodes:** Timing adjustments, freeze frames, temporal effects.

---

## 🎓 Learning Paths

### **Path 1: Basic Compositing** (Beginner)
Learn to combine images and adjust colors:
1. [Noise](generators/noise.md) - Generate test patterns
2. [Merge](compositing/merge.md) - Combine images
3. Transform - Position elements
4. [Grade](color/grade.md) - Match colors
5. Blur - Add depth

### **Path 2: Greenscreen Workflow** (Intermediate)
Complete keying pipeline:
1. [ChromaKeyer](keying/chromakeyer.md) - Remove greenscreen
2. [MatteControl](matte/mattecontrol.md) - Refine edges
3. Despill - Remove color spill
4. Unpremultiply → [Grade](color/grade.md) → Premultiply - Color match
5. [Merge](compositing/merge.md) - Final composite

### **Path 3: Advanced Effects** (Advanced)
Professional techniques:
1. [Noise](generators/noise.md) + [DisplacementMap](transforms/displacementmap.md) - Heat waves
2. Glow + [Merge](compositing/merge.md) (Screen) - Light effects
3. [GridWarp](transforms/gridwarp.md) - Perspective correction
4. ZDefocus - Realistic depth of field
5. [Grade](color/grade.md) + HSVAdjust - Film look color grading

---

## 🔍 Search by Use Case

**"I want to..."**

**...combine images:** [Merge](compositing/merge.md), Copy, Switch
**...remove greenscreen:** [ChromaKeyer](keying/chromakeyer.md), [MatteControl](matte/mattecontrol.md), Despill
**...color correct:** [Grade](color/grade.md), ColorCorrect, HSVAdjust, Saturation, Exposure
**...add effects:** Glow, [Noise](generators/noise.md), Blur, EdgeDetect
**...distort/warp:** Transform, [DisplacementMap](transforms/displacementmap.md), [GridWarp](transforms/gridwarp.md), CornerPin
**...work with transparency:** Premultiply, Unpremultiply, SetAlpha, [MatteControl](matte/mattecontrol.md)
**...generate textures:** [Noise](generators/noise.md), Gradient, Constant, Checkerboard
**...refine edges:** [MatteControl](matte/mattecontrol.md), Erode, EdgeBlur, Bilateral
**...create depth effects:** ZDefocus, DepthMerge, Blur

---

## 📝 Documentation Status

**Legend:**
- ✅ **Complete** - Full beginner-friendly guide available
- 📝 **Coming Soon** - Documentation in progress
- ⚠️ **Experimental** - Node is experimental, docs may change

**Current Status:** 4 of 45 nodes documented (9%)

**Completed:**
- [Merge](compositing/merge.md) (Compositing)
- [Grade](color/grade.md) (Color)
- [ChromaKeyer](keying/chromakeyer.md) (Keying)
- [Noise](generators/noise.md) (Generator)

**Next Priority:**
- Transform (Transform)
- Blur (Filter)
- MatteControl (Matte)
- Premultiply/Unpremultiply (Matte)

---

## 💡 Tips for Learning

1. **Start simple** - Don't try to learn everything at once
2. **Follow the learning paths** - Structured approach beats random exploration
3. **Build example workflows** - Hands-on practice is best
4. **Read the "Common Mistakes"** section in each guide
5. **Experiment!** - Can't break anything, try different settings

---

## 🤝 Need Help?

- Check individual node documentation pages
- Look at "Works Great With" sections for workflow ideas
- Try the example workflows to learn by doing
- Refer to DEVLOG.md for version history and features

**Remember:** Professional compositors use these same tools - you're learning industry-standard techniques! Take your time and have fun. 🎨
