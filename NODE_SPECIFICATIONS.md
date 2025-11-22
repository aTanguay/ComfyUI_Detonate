# ComfyUI_Detonate - Node Specifications

This document provides precise technical specifications for each node, documenting exact behavior from Nuke and Fusion to ensure our implementations match professional compositor expectations.

**Purpose:** Reference document for implementation - captures exact formulas, parameters, edge cases, and expected behaviors.

---

## Priority Tier 1: Essential Daily Tools

### 1. Merge Node (Compositing)

**Nuke:** Merge | **Fusion:** Merge
**Category:** `detonate/compositing`

#### Purpose
Layer multiple images together using various compositing algorithms to combine pixel values from foreground (A) and background (B) inputs.

#### Core Behavior
- Default operation: "Over" (A over B)
- **Critical:** Nuke expects premultiplied input images for most merge operations (except "matte" operation which requires unpremultiplied)
- Fusion: Additive merging (default) assumes premultiplied alpha; Subtractive mode available via slider

#### Blend Modes / Operations

**Over (A over B):**
- Formula: `result = A + B * (1 - A.alpha)`
- A is composited over B according to A's alpha channel
- Most common compositing operation
- Requires premultiplied inputs

**Under (A under B):**
- Places A under B
- Useful when background should cover foreground
- Formula: `result = B + A * (1 - B.alpha)`

**Plus (Additive):**
- Formula: `result = A + B`
- Adds pixel values from both inputs
- Great for light glows, fire, lighting passes
- Can produce values > 1.0

**Screen:**
- Formula: `result = 1 - (1 - A) * (1 - B)`
- Lightens the result
- Popular for highlights, energy glows, visual effects
- Always produces lighter or equal result

**Multiply:**
- Formula: `result = A * B`
- Darkens based on both A and B values
- Ideal for shadows, texture blending
- Always produces darker or equal result

**Stencil:**
- Equivalent to "Merge Held Out with Invert inputs swapped" (Nuke)
- Uses A's alpha to cut a hole in B

**Mask:**
- Optional mask input limits merge to non-black areas of mask
- Mask is separate from A and B inputs

**Atop:**
- Composite A over B only where B has alpha
- Formula: `result = A * B.alpha + B * (1 - A.alpha)`

#### Parameters
- **operation/apply_mode:** Blend mode selection (dropdown)
- **mix/opacity:** Blend factor 0.0-1.0 (default 1.0)
- **mask:** Optional mask input (IMAGE)
- **channels:** Which channels to process (rgba, rgb, alpha, etc.)

#### Alpha Handling
- Input images should be premultiplied (for most operations)
- Output is premultiplied
- Alpha channel is composited along with RGB

#### Edge Cases
- Division by zero: N/A for most modes
- Out-of-range values: Can occur with Plus mode (values > 1.0)
- Missing alpha: Treat as alpha=1.0 (fully opaque)

#### ComfyUI Implementation Notes
- Input A: Foreground (IMAGE tensor [B,H,W,C])
- Input B: Background (IMAGE tensor [B,H,W,C])
- Mask: Optional (MASK or IMAGE)
- Must handle both C=3 (RGB) and C=4 (RGBA)
- If C=3, treat as alpha=1.0

---

### 2. Transform Node

**Nuke:** Transform | **Fusion:** Transform
**Category:** `detonate/transform`

#### Purpose
Translate, rotate, scale, and skew 2D images with motion blur support and various filtering options.

#### Core Parameters

**Translate:**
- X/Y position offset in pixels
- Range: -∞ to +∞
- Default: 0, 0

**Rotate:**
- Rotation in degrees
- Range: -∞ to +∞ (wraps at 360°)
- Default: 0
- Positive values: clockwise rotation

**Scale:**
- Uniform scale or separate X/Y
- Range: 0.0 to +∞
- Default: 1.0 (100%)
- Values < 1.0 shrink, > 1.0 enlarge

**Center Point:**
- Transform pivot point
- Default: Image center
- X/Y coordinates in pixel space

**Skew:**
- X/Y skew values
- Range: -∞ to +∞
- Default: 0, 0
- Shears the image along axes

#### Filter Quality Options

**Nearest (Impulse):**
- Fastest, lowest quality
- No interpolation
- Good for pixel art or when speed is critical

**Bilinear:**
- Medium speed and quality
- Linear interpolation
- Good balance for most cases

**Bicubic:**
- Slower, high quality
- Cubic interpolation
- Best for high-quality output

**Lanczos/Sinc:**
- Highest quality
- Sharpest results
- Slowest performance

#### Motion Blur (Optional for v1.0)

**Shutter:**
- Controls how long shutter is open
- Range: 0.0 to 1.0+
- Default: 0.5
- Higher values = more blur

**Samples:**
- Number of samples for motion blur
- Range: 1 to 32+
- Default: 16
- Higher values = smoother blur, slower performance

#### Edge Modes

**Black:**
- Areas outside image are black/transparent
- Most common for compositing

**Clamp:**
- Repeat edge pixels
- Prevents black borders

**Repeat/Tile:**
- Tile the image
- Useful for seamless patterns

#### Transform Order
Standard order: Translate → Rotate → Scale → Skew (applied from center point)

#### ComfyUI Implementation Notes
- Use PyTorch's `affine_grid` and `grid_sample` for transforms
- Filter quality maps to `grid_sample` interpolation mode
- Motion blur: Sample at multiple time steps and average (optional for v1.0)
- Handle batch dimension correctly
- Preserve alpha channel

#### Edge Cases
- Scale = 0: Collapse to single line/point
- Extreme rotations: Use modulo 360 for display
- Very large images: May hit memory limits with motion blur

---

### 3. Blur Node

**Nuke:** Blur | **Fusion:** Blur
**Category:** `detonate/filter`

#### Purpose
Apply Gaussian blur to images or mattes with separate X/Y control for directional softening.

#### Core Algorithm
- Gaussian filter (default, smoothest)
- Two-pass separable convolution (horizontal then vertical)
- For large blur sizes: uses downsampling optimization

#### Parameters

**Size (X/Y):**
- Blur radius in pixels
- Range: 0.0 to 1000+ pixels
- Default: 1.0
- Separate X and Y controls for directional blur
- Size 0 = no blur

**Filter Type:**
- Gaussian (default): Smoothest, slowest
- Box: Faster, blockier
- Triangle: Medium quality and speed
- Quadratic: Alternative falloff

**Quality:**
- Controls filter kernel size or iterations
- Higher quality = more accurate Gaussian approximation
- Trade-off with performance

**Channels:**
- Which channels to blur (rgba, rgb, alpha only, etc.)
- Default: all channels

#### Mathematical Formula

Gaussian kernel: `G(x) = (1 / (σ * sqrt(2π))) * exp(-(x² / (2σ²)))`

Where:
- σ (sigma) = size / 2 (approximately)
- x = distance from center pixel

#### Technical Implementation
- Separable filter: blur X, then blur Y (much faster than 2D)
- Kernel size: typically 6σ (3σ on each side)
- For size > 20 pixels: consider downsampling then upsampling

#### Alpha Handling
- Blur applies to alpha channel if C=4
- Premultiplication status preserved (blur doesn't change it)
- Can blur alpha independently via channel selection

#### Edge Cases
- Size = 0: Return input unchanged
- Size < 0: Treat as 0 (no negative blur)
- Very large sizes (>100): May be slow, consider optimization

#### ComfyUI Implementation Notes
- Use PyTorch's Gaussian blur or implement separable convolution
- `torch.nn.functional.gaussian_blur` available in PyTorch 1.9+
- For older versions: Manual convolution with Gaussian kernel
- Batch processing: Apply blur to entire batch
- GPU acceleration strongly recommended

#### Performance Targets
- 1080p, size=5: <50ms
- 4K, size=5: <200ms
- Larger sizes: Scale linearly with kernel size

---

### 4. Grade Node

**Nuke:** Grade | **Fusion:** ColorCorrector (grade mode)
**Category:** `detonate/color`

#### Purpose
Professional color grading using lift/gamma/gain controls for shadows, midtones, and highlights with separate RGB channel control.

#### Core Formula (Nuke)

Complete equation:
```
A = multiply * (gain - lift) / (whitepoint - blackpoint)
B = offset + lift - A * blackpoint
output = pow(A * input + B, 1/gamma)
```

#### Parameters

**Blackpoint:**
- Input black level
- Range: -∞ to 1.0
- Default: 0.0
- Sets source black point
- Remaps input range lower bound

**Whitepoint:**
- Input white level
- Range: 0.0 to +∞
- Default: 1.0
- Sets source white point
- Remaps input range upper bound

**Lift:**
- Output black level (shadows)
- Range: -∞ to +∞
- Default: 0.0
- Master + separate RGB controls
- Affects shadows most, highlights least
- Fusion: Scales color values around white
  - Example: Lift 0.5 makes RGB(0,0,0) → RGB(0.5,0.5,0.5)

**Gamma:**
- Midtone adjustment
- Range: 0.01 to +∞
- Default: 1.0
- Master + separate RGB controls
- Formula: `pow(value, 1/gamma)`
- Values > 1.0 brighten midtones
- Values < 1.0 darken midtones
- Pure black and white unaffected

**Gain:**
- Output white level (highlights)
- Range: -∞ to +∞
- Default: 1.0
- Master + separate RGB controls
- Affects highlights most, shadows least
- Fusion: Multiplier of pixel value
  - Example: Gain 1.2 makes RGB(0.5,0.5,0.4) → RGB(0.6,0.6,0.48)

**Offset:**
- Simple addition to all values
- Range: -∞ to +∞
- Default: 0.0
- Master + separate RGB controls
- Raises/lowers all values equally
- Applied after lift/gain scaling

**Multiply:**
- Overall multiplier
- Range: 0.0 to +∞
- Default: 1.0
- Master + separate RGB controls
- Applied before other operations

#### Control Structure
Each parameter (except blackpoint/whitepoint) has:
- **Master:** Affects all RGB channels equally
- **Red:** Red channel only
- **Green:** Green channel only
- **Blue:** Blue channel only

#### Workflow Best Practices
1. Set Blackpoint/Whitepoint to establish input range
2. Use Lift to set shadows to match background
3. Use Gain to set highlights to match background
4. Use Gamma to adjust midtone contrast
5. Use Offset for final tweaks

#### Alpha Handling
- Typically operates on RGB only, alpha unchanged
- If applied to premultiplied image: should unpremult first
- Option to grade alpha channel separately

#### Edge Cases
- Gamma = 0: Clamp to minimum value (e.g., 0.01)
- Whitepoint = Blackpoint: Avoid division by zero, clamp
- Negative gamma: Not allowed, clamp to positive
- Out-of-range output: Can produce values < 0 or > 1

#### ComfyUI Implementation Notes
- Process each pixel through the formula
- Vectorize using PyTorch operations (no loops)
- Handle master + RGB channels: `result = master_factor * rgb_factor`
- Expect straight alpha input (unpremultiplied)
- Preserve alpha channel

---

### 5. Premultiply / Unpremultiply Nodes

**Nuke:** Premult / Unpremult | **Fusion:** (built into Merge)
**Category:** `detonate/channel`

#### Purpose
Convert between straight alpha and premultiplied alpha representations for proper compositing and color correction.

#### Background: Alpha Types

**Straight Alpha (Unpremultiplied):**
- RGB and alpha stored independently
- RGB values represent actual color regardless of transparency
- Black in alpha = transparent, but RGB still has color data
- Required for color correction operations

**Premultiplied Alpha:**
- RGB values multiplied by alpha channel
- Transparent areas (alpha=0) have RGB=0
- Required for most merge/compositing operations
- More accurate for filtering and scaling

#### Premultiply Node

**Operation:**
```python
result.rgb = input.rgb * input.alpha
result.alpha = input.alpha  # unchanged
```

**When to Use:**
- After loading unpremultiplied images
- Before Merge operations
- After color correction (unpremult → correct → premult)

**Parameters:**
- **channels:** Which color channels to premultiply (default: rgb)
- **alpha_channel:** Which channel to use as alpha (default: alpha)

#### Unpremultiply Node

**Operation:**
```python
result.rgb = input.rgb / (input.alpha + epsilon)
result.alpha = input.alpha  # unchanged
```

**Division by Zero Handling:**
- Add small epsilon (1e-7) to alpha before division
- Prevents division by zero when alpha=0
- Alternative: clamp alpha to minimum value

**When to Use:**
- Before color correction operations
- To inspect/modify color in transparent areas
- Before certain filters that expect straight alpha

**Parameters:**
- **channels:** Which color channels to unpremultiply (default: rgb)
- **alpha_channel:** Which channel to use as alpha (default: alpha)
- **epsilon:** Small value to prevent division by zero (default: 1e-7)

#### Workflow Pattern (Critical)

**Color Correction on Premultiplied Images:**
```
Input (premult) → Unpremult → Grade/ColorCorrect → Premult → Output
```

This ensures:
1. Color correction affects all color pixels (not just opaque ones)
2. Proper feathered edge from alpha is restored
3. Output is ready for compositing

#### Edge Cases

**Premultiply:**
- Alpha > 1.0: Clips RGB or allows values > 1.0 (configurable)
- RGB values already > alpha: Results in brighter values

**Unpremultiply:**
- Alpha = 0: Use epsilon to avoid infinity
- Alpha very small: Can produce extremely large RGB values
  - Option to clamp output to reasonable range (e.g., 0-10)
- Negative alpha: Clamp to 0 or absolute value

#### ComfyUI Implementation Notes
- Simple element-wise operations, very fast
- Handle batch dimension correctly
- C=3 (RGB): No alpha channel, skip operation or error
- C=4 (RGBA): Process normally
- Option to specify custom alpha channel index

---

### 6. Shuffle Node

**Nuke:** Shuffle / Shuffle2 | **Fusion:** ChannelBooleans
**Category:** `detonate/channel`

#### Purpose
Rearrange, copy, and manipulate channels between layers and within a single image.

#### Core Capabilities

**Channel Reordering:**
- Swap channel positions (e.g., R→G, G→B, B→R)
- Copy channel to multiple outputs
- Replace channel with constant (0 or 1)

**Examples:**
- Swap red and green: `out.r = in.g, out.g = in.r, out.b = in.b`
- Copy red to alpha: `out.a = in.r`
- Generate matte from luma: Calculate luminance, assign to output channel

#### Input Mapping
For each output channel (R, G, B, A), specify source:
- **Input channels:** red, green, blue, alpha (from input image)
- **Constants:** 0 (black), 1 (white)
- **Calculated:** Luminance (0.2126*R + 0.7152*G + 0.0722*B)

#### Parameters

**Red Output:** Source for red channel (dropdown)
- Options: red, green, blue, alpha, 0, 1, luminance

**Green Output:** Source for green channel (dropdown)
- Options: red, green, blue, alpha, 0, 1, luminance

**Blue Output:** Source for blue channel (dropdown)
- Options: red, green, blue, alpha, 0, 1, luminance

**Alpha Output:** Source for alpha channel (dropdown)
- Options: red, green, blue, alpha, 0, 1, luminance

#### Common Use Cases

1. **Create Alpha from Luminance:**
   - R=red, G=green, B=blue, A=luminance

2. **Invert RGB (keep alpha):**
   - Use Invert node instead, but could do: R=1-red, etc.

3. **Extract Channel as Grayscale:**
   - R=red, G=red, B=red, A=1 (red channel as RGB)

4. **Generate Constant Color:**
   - R=1, G=0, B=0, A=1 (solid red)

5. **Swap Channels:**
   - R=blue, G=green, B=red, A=alpha (R↔B swap)

#### Advanced: Multi-Layer Shuffling
- Nuke's Shuffle2 supports multiple input streams
- Can copy channels between separate images
- Our implementation: Start with single-input (simpler)

#### ComfyUI Implementation Notes
- Simple channel indexing and copying
- Very fast operation
- Handle C=3: Treat missing alpha as 1.0
- Output always C=4 if user requests alpha output
- Luminance calculation: Rec. 709 coefficients
  - `L = 'R * 0.2126 + G * 0.7152 + B * 0.0722`

#### Edge Cases
- Input C=3, user requests alpha input: Use 1.0
- Output alpha when input C=3: Add alpha channel to output
- All outputs set to constants: Valid (generates solid color)

---

### 7. ColorCorrect Node

**Nuke:** ColorCorrect | **Fusion:** ColorCorrector
**Category:** `detonate/color`

#### Purpose
Quick color adjustments for matching composite layers using saturation, contrast, gamma, gain, and offset controls with separate tonal range targeting.

#### Key Differences from Grade Node
- **Grade:** Designed for film scan color grading (lift/gamma/gain workflow)
- **ColorCorrect:** Designed for matching composite layers (has Saturation & Contrast)

#### Tonal Ranges
Each control can target different tonal ranges:
- **Master:** Entire dynamic range (all pixels equally)
- **Shadows:** Dark areas of image
- **Midtones:** Middle gray values
- **Highlights:** Bright areas of image

#### Parameters

**Saturation:**
- Range: 0.0 to 2.0+ (default 1.0)
- 0.0 = grayscale (no color)
- 1.0 = no change
- >1.0 = oversaturated
- Fusion: 0 = gray pixels, higher values = more chroma
- Per tonal range control

**Contrast:**
- Range: 0.0 to 2.0+ (default 1.0)
- < 1.0 = reduced contrast (moves toward midgray)
- 1.0 = no change
- > 1.0 = increased contrast (pushes toward black/white)
- Increases difference between light and dark areas
- Per tonal range control

**Gamma:**
- Range: 0.1 to 10.0 (default 1.0)
- Formula: `pow(value, 1/gamma)`
- < 1.0 = darken midtones
- 1.0 = no change
- > 1.0 = brighten midtones
- Pure black and white unaffected
- Per tonal range and per RGB channel

**Gain (Multiply):**
- Range: 0.0 to 10.0+ (default 1.0)
- Simple multiplication: `result = input * gain`
- Useful for tinting and brightness
- Per tonal range and per RGB channel
- Fusion: Affects higher values more than lower values

**Offset (Add):**
- Range: -1.0 to +1.0 (default 0.0)
- Simple addition: `result = input + offset`
- Raises/lowers all values equally
- Per tonal range and per RGB channel

#### Tonal Range Isolation
Ranges determined by luminance masks:
- **Shadows:** Luminance < ~0.33
- **Midtones:** Luminance ~0.33 to ~0.66
- **Highlights:** Luminance > ~0.66

Smooth falloff between ranges (not hard cutoffs)

#### Operation Order
Typical order (may vary by implementation):
1. Contrast
2. Saturation
3. Gamma
4. Gain (multiply)
5. Offset (add)

#### Alpha Handling
- Operates on RGB only, alpha unchanged
- Should use unpremultiplied (straight alpha) input
- For premultiplied images: Unpremult → ColorCorrect → Premult

#### ComfyUI Implementation Notes
- More complex than Grade due to tonal range masking
- Saturation: Convert RGB→HSV, adjust S, convert back
- Contrast: `result = (input - 0.5) * contrast + 0.5`
- Generate luminance masks for shadow/mid/highlight separation
- Apply controls weighted by luminance masks
- Vectorize all operations for performance

#### Edge Cases
- Saturation < 0: Clamp to 0
- Gamma = 0: Clamp to small positive value
- Contrast = 0: All pixels become midgray
- Extreme values: Can produce out-of-range pixels

---

### 8. Erode / Dilate Nodes

**Nuke:** Erode (fast), Erode (filter), Dilate | **Fusion:** ErodeDilate
**Category:** `detonate/matte`

#### Purpose
Morphological operations to expand (dilate) or contract (erode) mattes and alpha channels, essential for matte cleanup and refinement.

#### Core Operations

**Erode (Contract):**
- Positive size values: darker areas expand into lighter areas
- Shrinks bright regions
- Removes small bright details
- Useful for: Cleaning up matte noise, removing fringe

**Dilate (Expand):**
- Negative size values: brighter areas expand into darker areas
- Grows bright regions
- Fills small holes
- Useful for: Expanding mattes, filling gaps

#### Nuke Variants

**Erode (fast):**
- Fastest implementation
- Lower quality
- Good for interactive work

**Erode (filter):**
- Higher quality
- Multiple filter options:
  - **Box:** Fastest, hard edges
  - **Gaussian:** Slowest, softest edges (best quality)
  - **Triangle:** Medium quality and speed

#### Parameters

**Size:**
- Range: -100 to +100 pixels (typical)
- Negative: Dilate (expand bright areas)
- Positive: Erode (contract bright areas)
- 0: No change
- Larger absolute values = stronger effect

**Filter (filter variant only):**
- Box, Triangle, Gaussian, Quadratic
- Controls computation speed vs quality
- Gaussian: Smoothest but slowest

**Channels:**
- Which channels to process
- Typically used on alpha/matte channels
- Can apply to RGB for special effects

#### Mathematical Implementation

**Box Filter Erode:**
- For each pixel, examine neighborhood within size radius
- Erode: Take minimum value in neighborhood
- Dilate: Take maximum value in neighborhood

**Gaussian Filter:**
- Weighted average with Gaussian falloff
- Smoother results than box filter
- More computationally expensive

#### Erode/Dilate Technique (Advanced)

**Kill Bright Detail:**
1. Erode by N pixels
2. Dilate by N pixels
- Removes bright specks/noise

**Kill Dark Detail:**
1. Dilate by N pixels
2. Erode by N pixels
- Fills dark holes/gaps

This technique is very versatile for:
- Wire removal
- Cleaning blue/green screens
- Removing noise
- Filling holes in core mattes

#### Alpha Handling
- Typically operates on alpha channel only
- Can work on RGB for special effects
- Works with both straight and premultiplied alpha

#### ComfyUI Implementation Notes
- Use OpenCV's morphological operations if available
  - `cv2.erode()` and `cv2.dilate()`
  - `cv2.morphologyEx()` for combined operations
- Fallback: Manual implementation with min/max pooling
- PyTorch: `torch.nn.functional.max_pool2d` / min pooling
- Box filter: Simpler and faster (use for v1.0)
- Gaussian filter: Add in future version

#### Performance
- Box filter: Very fast, real-time even for large sizes
- Gaussian: Slower, may need optimization for large sizes
- Size impacts performance: O(size²) for naive implementation

#### Edge Cases
- Size = 0: Return input unchanged
- Very large size: May produce all-black or all-white output
- Edge behavior: Typically clamp (repeat edge pixels)

---

## Implementation Priorities

### Phase 1: Critical Nodes (Weeks 1-2)
1. **Premultiply / Unpremultiply** - Simplest, foundational for alpha workflow
2. **Shuffle** - Simple channel operations
3. **Blur** - Basic filter, well-documented in PyTorch

### Phase 2: Core Compositing (Weeks 3-4)
4. **Merge** - Core compositing, moderate complexity
5. **Transform** - Geometric operations, use PyTorch built-ins

### Phase 3: Color Tools (Weeks 5-6)
6. **ColorCorrect** - Simpler than Grade, immediate utility
7. **Grade** - Complex but essential, complete formula documented

### Phase 4: Matte Tools (Week 7)
8. **Erode / Dilate** - Matte operations, can use OpenCV or PyTorch

---

## Testing Requirements

For each node, test with:

1. **Basic Operation:**
   - Default parameters produce expected output
   - All parameters work within valid ranges

2. **Alpha Handling:**
   - C=3 (RGB) input handled correctly
   - C=4 (RGBA) input processed properly
   - Premultiplied vs straight alpha behavior documented

3. **Edge Cases:**
   - Extreme parameter values (min/max)
   - Division by zero scenarios
   - Empty/invalid inputs

4. **Batch Processing:**
   - Batches (B>1) processed correctly
   - Memory usage scales linearly

5. **Performance:**
   - 1080p: <100ms per operation
   - 4K: <500ms per operation

6. **Visual Validation:**
   - Compare output to Nuke/Fusion with same parameters
   - Create example workflows demonstrating each mode/feature

---

## Sources & References

### Nuke Documentation
- [Merge Node](https://learn.foundry.com/nuke/content/reference_guide/merge_nodes/merge.html)
- [Merge Operations](https://learn.foundry.com/nuke/content/comp_environment/merging/merge_operations.html)
- [Transform Node](https://learn.foundry.com/nuke/content/reference_guide/transform_nodes/transform.html)
- [Blur Node](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/blur.html)
- [Grade Node](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/grade.html)
- [Premult Node](https://learn.foundry.com/nuke/content/reference_guide/merge_nodes/premult.html)
- [Unpremult Node](https://learn.foundry.com/nuke/content/reference_guide/merge_nodes/unpremult.html)
- [Shuffle Node](https://learn.foundry.com/nuke/content/reference_guide/channel_nodes/shuffle.html)
- [ColorCorrect Node](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/colorcorrect.html)
- [Erode (filter) Node](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/erode_filter.html)
- [Erode (fast) Node](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/erode_fast.html)

### Fusion Documentation & Tutorials
- [Fusion Merge Node](https://jayaretv.com/fusion/merge-node/)
- [Merge & Apply Alpha Channel Operations](https://dvresolve.com/tutorial/merge-apply-alpha-channel-blend-modes/)
- [Fusion ColorCorrector Node](https://jayaretv.com/fusion/color-corrector-node/)
- [Basic Color Correction Maths](http://www.designimage.co.uk/basic-colour-correction-maths-for-compositors/)

### Technical Resources
- [Nuke Grade Node Demystified](https://www.chrisbturner.com/blog/nukes-grade-node-demystified)
- [Nuke Premult Explained](https://www.lifestylebytes.com/nuke-en/nuke-premult-explained-why-its-essential-in-compositing-file/)
- [Understanding Nuke's Channel System](http://www.nukepedia.com/written-tutorials/understanding-nukes-unique-layer-and-channel-system-including-the-shuffle-nodes/)
- [Erode Dilate Technique](https://www.keheka.com/erode-dilate-technique/)

---

**Document Version:** 1.0
**Last Updated:** 2025-01-22
**Status:** Priority Tier 1 Complete - Ready for Implementation
