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

## Priority Tier 2: Essential Utilities

### 1. Clamp Node (Color Utility)

**Nuke:** Clamp | **Natron:** Clamp
**Category:** `detonate/color`

#### Purpose
Constrain pixel values to a specified min/max range. Essential for managing float images with HDR values, preventing extreme overbright pixels, and creating binary masks.

#### Core Behavior
- Default: Clamps all channels to 0-1 range
- Can clamp to custom min/max values
- Optional "clamp to" values for remapping outside range
- Per-channel control (RGBA individually)

#### Parameters

**minimum** (float)
- Default: 0.0
- Range: -∞ to ∞
- Values below this are clamped

**maximum** (float)
- Default: 1.0
- Range: -∞ to ∞
- Values above this are clamped

**min_clamp_to_enabled** (bool)
- Default: false
- If true, values below minimum are set to min_clamp_to instead of minimum

**min_clamp_to** (float)
- Default: 0.0
- Replacement value for pixels below minimum (when enabled)

**max_clamp_to_enabled** (bool)
- Default: false
- If true, values above maximum are set to max_clamp_to instead of maximum

**max_clamp_to** (float)
- Default: 1.0
- Replacement value for pixels above maximum (when enabled)

**channels** (enum)
- Options: ["rgba", "rgb", "alpha"]
- Default: "rgba"
- Which channels to clamp

#### Algorithm

```python
for each pixel in image:
    for each channel in selected_channels:
        if pixel[channel] < minimum:
            if min_clamp_to_enabled:
                pixel[channel] = min_clamp_to
            else:
                pixel[channel] = minimum
        elif pixel[channel] > maximum:
            if max_clamp_to_enabled:
                pixel[channel] = max_clamp_to
            else:
                pixel[channel] = maximum
```

#### Common Use Cases
1. **Clamp to 0-1:** Fix overbright HDR pixels before operations requiring 0-1 range
2. **Binary Masks:** Set min=threshold, max=threshold-epsilon, enable clamp_to with 0 and 1
3. **Safe Premult:** Clamp to 0-1 before premultiply to avoid negative alpha issues
4. **Depth Normalization:** Clamp depth passes to reasonable near/far range

#### Reference
- [Nuke Clamp Documentation](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/clamp.html)
- [Natron Clamp Documentation](https://natron.readthedocs.io/en/v2.3.15/plugins/net.sf.openfx.Clamp.html)

---

### 2. Invert Node (Color Utility)

**Nuke:** Invert | **Natron:** Invert
**Category:** `detonate/color`

#### Purpose
Invert selected channels (RGB and/or alpha). Essential for flipping mattes, creating negative images, and channel manipulation.

#### Core Behavior
- Inverts selected channels using `1 - value` formula
- Can invert RGB and Alpha independently
- Preserves float range (values > 1.0 become negative)

#### Parameters

**channels** (multi-select or individual bools)
- Options: R, G, B, A
- Default: R, G, B (RGB only, preserve alpha)
- Which channels to invert

**clamp** (bool)
- Default: false
- If true, clamp result to 0-1 range after inversion
- Useful for float images that might go negative

#### Algorithm

```python
for each pixel in image:
    if invert_red:
        pixel.r = 1.0 - pixel.r
    if invert_green:
        pixel.g = 1.0 - pixel.g
    if invert_blue:
        pixel.b = 1.0 - pixel.b
    if invert_alpha:
        pixel.a = 1.0 - pixel.a

    if clamp:
        pixel = max(0.0, min(pixel, 1.0))
```

#### Common Use Cases
1. **Flip Matte:** Invert alpha to reverse matte (inside↔outside)
2. **Create Negative:** Invert RGB for artistic negative effect
3. **Invert Mask:** Flip mask channel for opposite selection
4. **Channel Math:** Part of channel manipulation workflows

#### Edge Cases
- Float values > 1.0 become negative when inverted (use clamp if unwanted)
- Premultiplied alpha: invert alpha will break premult (unpremult first!)

#### Reference
- [Natron Invert Documentation](https://natron.readthedocs.io/en/v2.3.15/plugins/net.sf.openfx.Invert.html)
- [Natron OpenFX Invert Plugin Walkthrough](https://github.com/NatronGitHub/Natron/wiki/OpenFX-plugin-programming-guide-(Invert-plugin-walkthrough))

---

### 3. Constant Node (Image Generator)

**Nuke:** Constant | **Fusion:** Background
**Category:** `detonate/generator`

#### Purpose
Generate solid color image with specified dimensions and RGBA values. Essential for backgrounds, test patterns, and color references.

#### Core Behavior
- Creates image where every pixel is the same color
- Fills entire frame including outside pixels
- Can create any RGBA color including HDR values (>1.0)

#### Parameters

**width** (int)
- Default: 1920
- Range: 1 to 16384
- Image width in pixels

**height** (int)
- Default: 1080
- Range: 1 to 16384
- Image height in pixels

**color** (RGBA color)
- Default: [0.0, 0.0, 0.0, 1.0] (black with full alpha)
- Range per channel: 0.0 to ∞ (supports HDR)
- RGBA values for the constant color

**red** (float)
- Default: 0.0
- Individual red channel control

**green** (float)
- Default: 0.0
- Individual green channel control

**blue** (float)
- Default: 0.0
- Individual blue channel control

**alpha** (float)
- Default: 1.0
- Individual alpha channel control

#### Algorithm

```python
image = torch.full((batch, height, width, 4),
                   [red, green, blue, alpha],
                   dtype=torch.float32)
```

#### Common Use Cases
1. **Solid Background:** Black or white background for compositing
2. **Test Pattern:** Specific color for testing pipeline
3. **Color Reference:** Create color chip for matching
4. **Matte Generation:** White constant to use as full matte
5. **HDR Colors:** Generate >1.0 values for bloom/glow effects

#### Reference
- [Nuke Constant Documentation](https://learn.foundry.com/nuke/content/reference_guide/image_nodes/constant.html)

---

### 4. Saturation Node (Color Correction)

**Nuke:** Saturation | **Fusion:** ColorCorrector (saturation parameter)
**Category:** `detonate/color`

#### Purpose
Adjust color saturation (intensity of color) without affecting luminance. Simpler than ColorCorrect when only saturation adjustment is needed.

#### Core Behavior
- Converts RGB to HSV, adjusts S channel, converts back to RGB
- 0.0 = fully desaturated (grayscale)
- 1.0 = no change (original saturation)
- >1.0 = increased saturation (more vivid)

#### Parameters

**saturation** (float)
- Default: 1.0
- Range: 0.0 to 4.0 (UI slider), technically 0 to ∞
- Saturation multiplier
  - 0.0: Complete desaturation (grayscale)
  - 1.0: Original colors
  - 2.0: Double saturation (very vivid)

#### Algorithm

```python
# Convert RGB to HSV
hsv = rgb_to_hsv(image[:, :, :, :3])

# Adjust saturation
hsv[:, :, :, 1] = hsv[:, :, :, 1] * saturation

# Clamp saturation to valid range
hsv[:, :, :, 1] = torch.clamp(hsv[:, :, :, 1], 0.0, 1.0)

# Convert back to RGB
rgb = hsv_to_rgb(hsv)

# Preserve alpha
result = torch.cat([rgb, alpha], dim=3)
```

#### RGB to HSV Conversion
Using standard conversion where:
- V = max(R, G, B)
- S = (max - min) / max  (if max ≠ 0)
- H = hue angle based on which channel is maximum

#### Common Use Cases
1. **Desaturation:** Reduce to grayscale (saturation=0.0)
2. **Enhance Colors:** Boost vibrancy (saturation=1.5-2.0)
3. **Partial Desat:** Subtle reduction (saturation=0.7-0.9)
4. **Stylistic Look:** Create washed-out or hyper-saturated looks

#### Edge Cases
- Works on straight (unpremultiplied) alpha images
- Saturation at 0.0 creates perfect grayscale using Rec. 709 luminance
- Values >1.0 can push colors out of gamut

#### Reference
- [Nuke HSV Correction](https://learn.foundry.com/nuke/content/comp_environment/color_correction/making_hsv_corrections.html)

---

### 5. MatteControl Node (Matte Refinement)

**Nuke:** FilterErode (blur mode) + gamma | **Fusion:** Matte Control
**Category:** `detonate/matte`

#### Purpose
All-in-one matte refinement combining contract/expand, blur, and gamma in proper order. Essential for cleaning up keyed mattes or adjusting roto.

#### Core Behavior
- Operates on alpha channel (or selected channels)
- Process order: Contract/Expand → Blur → Gamma
- Single node replaces Erode → Blur → Grade workflow

#### Parameters

**size** (int)
- Default: 0
- Range: -100 to 100
- Negative: Contract matte (erode, choke)
- Positive: Expand matte (dilate, spread)
- 0: No change

**blur** (float)
- Default: 0.0
- Range: 0.0 to 100.0
- Gaussian blur size (in pixels)
- Softens matte edges

**gamma** (float)
- Default: 1.0
- Range: 0.1 to 4.0
- Adjusts semi-transparent areas
- <1.0: Darkens/thins matte
- >1.0: Lightens/thickens matte

**channels** (enum)
- Options: ["alpha", "rgb", "rgba"]
- Default: "alpha"
- Which channels to process

#### Algorithm

```python
# Step 1: Contract/Expand (morphological operation)
if size < 0:
    result = erode(image, abs(size), channels)
elif size > 0:
    result = dilate(image, size, channels)
else:
    result = image

# Step 2: Blur
if blur > 0:
    result = gaussian_blur(result, blur, channels)

# Step 3: Gamma
if gamma != 1.0:
    result_channels = torch.pow(result_channels + 1e-7, 1.0 / gamma)
```

#### Common Use Cases
1. **Choke Matte:** size=-2, blur=1.0 (shrink and soften)
2. **Spread Matte:** size=2, blur=1.0 (expand and soften)
3. **Thicken Thin Matte:** gamma=1.5-2.0 (boost semi-transparent)
4. **Clean Noisy Matte:** blur=2.0, gamma=0.8 (smooth and darken)
5. **Edge Refinement:** size=-1, blur=0.5, gamma=1.2 (tight clean edge)

#### Order Matters!
- Contract/Expand BEFORE blur (otherwise blur changes size result)
- Gamma AFTER blur (to adjust the blurred edge density)

#### Reference
- [Nuke Erode (blur)](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/erode_blur.html)
- [Fusion Matte Control](https://jayaretv.com/fusion/matte-control-node/)
- [Alpha Density Technique](https://www.keheka.com/alpha-density-matte-control-tool-for-nuke/)

---

### 6. EdgeDetect Node (Filter)

**Nuke:** EdgeDetect | **Natron:** EdgeDetect
**Category:** `detonate/filter`

#### Purpose
Detect edges in image using Sobel operator. Creates edge mattes for effects, selections, or stylistic looks.

#### Core Behavior
- Uses Sobel edge detection (gradient magnitude)
- Optional pre-blur for noise reduction
- Optional post-erode to thin edges
- Outputs grayscale edge intensity

#### Parameters

**channels** (enum)
- Options: ["rgb", "red", "green", "blue", "alpha", "luminance"]
- Default: "luminance"
- Which channel(s) to detect edges from

**pre_blur** (float)
- Default: 0.0
- Range: 0.0 to 20.0
- Blur applied BEFORE edge detection (reduces noise)

**erode** (int)
- Default: 0
- Range: 0 to 10
- Erode applied AFTER edge detection (thins edges)

**output_mode** (enum)
- Options: ["replace_alpha", "replace_rgb", "multiply_alpha"]
- Default: "replace_alpha"
- How to output edge matte

#### Algorithm

```python
# Step 1: Pre-blur (optional)
if pre_blur > 0:
    image = gaussian_blur(image, pre_blur)

# Step 2: Sobel edge detection
# Horizontal Sobel kernel:
# [-1  0  1]
# [-2  0  2]
# [-1  0  1]

# Vertical Sobel kernel:
# [-1 -2 -1]
# [ 0  0  0]
# [ 1  2  1]

Gx = convolve(image, sobel_horizontal)
Gy = convolve(image, sobel_vertical)

# Edge magnitude
edges = sqrt(Gx^2 + Gy^2)

# Normalize to 0-1 range
edges = edges / edges.max()

# Step 3: Post-erode (optional)
if erode > 0:
    edges = morphological_erode(edges, erode)

# Step 4: Output based on mode
if output_mode == "replace_alpha":
    result = cat([image_rgb, edges], dim=3)
elif output_mode == "replace_rgb":
    result = cat([edges.repeat(3), alpha], dim=3)
elif output_mode == "multiply_alpha":
    result = cat([image_rgb, image_alpha * edges], dim=3)
```

#### Sobel Operator Details
- Detects both horizontal and vertical edges
- Returns gradient magnitude (edge strength)
- More sensitive to diagonal edges than Prewitt operator
- Standard in professional compositing

#### Common Use Cases
1. **Edge Matte:** Detect object edges for effects (glow, outline)
2. **Stylistic:** Create line art / sketch effect
3. **Masking:** Use edges as selection for targeted corrections
4. **Sharpening:** Detect edges to guide sharpening

#### Parameters Interaction
- pre_blur reduces noise but softens edges (trade-off)
- erode makes edges thinner/sharper after detection
- Recommended: pre_blur=1.0-2.0 for noisy images, erode=0-1 to refine

#### Reference
- [Nuke EdgeDetect Documentation](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/edgedetect.html)
- [Sobel Operator (Wikipedia)](https://en.wikipedia.org/wiki/Sobel_operator)

---

### 7. ChannelCopy Node (Channel Operations)

**Nuke:** Copy | **Fusion:** ChannelBooleans
**Category:** `detonate/channel`

#### Purpose
Copy channels from one input stream (B) to another input stream (A). Essential for multi-stream workflows where you need to replace specific channels.

#### Core Behavior
- Two inputs: A (base) and B (source)
- Copy selected channels from B to A
- All other channels from A are preserved

#### Parameters

**copy_red** (bool)
- Default: false
- Copy red channel from B to A

**copy_green** (bool)
- Default: false
- Copy green channel from B to A

**copy_blue** (bool)
- Default: false
- Copy blue channel from B to A

**copy_alpha** (bool)
- Default: true
- Copy alpha channel from B to A

**from_channels** (dict/mapping, advanced)
- Map channels: {"red": "red", "green": "green", "blue": "blue", "alpha": "alpha"}
- Default: identity mapping
- Advanced: Can copy from different channels (e.g., copy B.red to A.alpha)

#### Algorithm

```python
result = A.clone()

if copy_red:
    result[:, :, :, 0] = B[:, :, :, 0]
if copy_green:
    result[:, :, :, 1] = B[:, :, :, 1]
if copy_blue:
    result[:, :, :, 2] = B[:, :, :, 2]
if copy_alpha:
    result[:, :, :, 3] = B[:, :, :, 3]
```

#### Common Use Cases
1. **Replace Alpha:** Copy clean alpha from B to RGB from A
2. **Channel Swap:** Copy B's red channel to A's alpha
3. **Selective Replace:** Replace only RGB, keep A's original alpha
4. **Multi-Pass Compositing:** Combine different render passes

#### Example Workflows

**Replace Alpha from Clean Matte:**
```
ImageA (RGB with bad alpha) ──┐
                               └→ ChannelCopy (copy alpha only) → Output
CleanMatte (good alpha) ───────┘
```

**Combine Render Passes:**
```
BeautyPass (RGB) ──────────┐
                           └→ ChannelCopy (copy RGB only) → Output
AlphaPass (clean alpha) ───┘
```

---

## Testing & Validation (Tier 2)

All Tier 2 nodes should pass these validation tests:

1. **Clamp:**
   - Verify values clamped correctly to 0-1
   - Test custom min/max ranges
   - Test binary mask creation (threshold)
   - Test float HDR values (>1.0, <0.0)

2. **Invert:**
   - Verify 1-x formula for each channel
   - Test independent channel inversion
   - Test float values >1.0 (become negative)
   - Test matte flipping (alpha invert)

3. **Constant:**
   - Verify uniform color across all pixels
   - Test various resolutions
   - Test HDR color values (>1.0)
   - Test batch generation

4. **Saturation:**
   - Verify 0.0 produces grayscale
   - Verify 1.0 produces no change
   - Test extreme values (>2.0)
   - Compare to Nuke/Fusion HSV output

5. **MatteControl:**
   - Verify operation order (size → blur → gamma)
   - Test size negative (contract) and positive (expand)
   - Test blur softening
   - Test gamma density adjustment

6. **EdgeDetect:**
   - Verify Sobel kernel implementation
   - Test pre-blur noise reduction
   - Test post-erode edge thinning
   - Compare to Nuke EdgeDetect output

7. **ChannelCopy:**
   - Verify correct channels copied
   - Test with 2 input streams
   - Test selective channel copy
   - Verify preserved channels unchanged

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

## Cryptomatte: Object/Material ID Mattes

### CryptomatteExtract Node

**Category:** `detonate/cryptomatte`
**Developer:** Psyop (Open Source)

#### Purpose
Extract object or material ID mattes from Cryptomatte-encoded EXR files. Cryptomatte is the industry standard for generating accurate ID mattes with proper anti-aliasing, transparency, motion blur, and depth of field support.

#### Core Behavior
- Reads Cryptomatte layers from multi-channel EXR files
- Parses manifest (object/material name → ID mapping) from EXR metadata
- Converts selected object/material names to ID floats using MurmurHash3
- Samples Cryptomatte layers to extract coverage for matching IDs
- Outputs combined coverage matte with proper anti-aliasing

#### Cryptomatte Layer Types
1. **CryptoObject** - Object/geometry names (most common)
2. **CryptoMaterial** - Material/shader names
3. **CryptoAsset** - Asset/collection names

#### Cryptomatte Channel Structure
Cryptomatte stores data in multiple layers with ID/coverage pairs:
- `CryptoObject00.R` = ID1 (float-encoded hash)
- `CryptoObject00.G` = Coverage1 (0-1 opacity)
- `CryptoObject00.B` = ID2 (second sample)
- `CryptoObject00.A` = Coverage2 (second sample opacity)

Additional layers (`CryptoObject01`, `CryptoObject02`, etc.) handle more samples per pixel for complex transparency, motion blur, and depth of field.

#### Algorithm

**Manifest Parsing:**
```
1. Read EXR metadata key: "cryptomatte/{hash}/manifest"
2. Parse JSON: {"object_name": "hex_id", ...}
3. Convert hex IDs to float32:
   - packed = struct.pack("=I", int(hex_id, 16))
   - id_float = struct.unpack("=f", packed)[0]
```

**ID Hashing (MurmurHash3):**
```python
def mm3hash_float(name):
    hash_32 = mmh3.hash(name)
    # Handle edge cases (exponent 0 or 255)
    exp = hash_32 >> 23 & 255
    if (exp == 0) or (exp == 255):
        hash_32 ^= 1 << 23
    # Reinterpret uint32 as float32
    packed = struct.pack('<L', hash_32 & 0xffffffff)
    return struct.unpack('<f', packed)[0]
```

**Coverage Extraction:**
```
For each Cryptomatte layer (00, 01, 02, ...):
    Read 4 channels: R, G, B, A

    # Two ID/coverage pairs per layer
    id1 = R channel
    coverage1 = G channel
    id2 = B channel
    coverage2 = A channel

    For each target_id in selected objects:
        If abs(id1 - target_id) < epsilon:
            total_coverage += coverage1
        If abs(id2 - target_id) < epsilon:
            total_coverage += coverage2

Clamp total_coverage to 0-1
Return as grayscale matte
```

#### Parameters
- **exr_path:** Path to Cryptomatte EXR file
- **cryptomatte_layer:** Layer type (CryptoObject, CryptoMaterial, CryptoAsset)
- **matte_list:** Comma-separated object/material names to extract
  - Example: `"sphere_001, cube_002, ground_plane"`
- **list_objects:** Print available objects to console (for discovery)

#### Output
- **matte:** IMAGE tensor [1,H,W,4]
  - Coverage in RGB (for visualization)
  - Alpha = 1.0 (opaque)
  - Values 0-1 representing pixel coverage

#### Edge Cases
- **Missing objects:** Print warning, skip that object
- **No manifest:** Error - file not Cryptomatte-encoded
- **Empty matte_list:** Return black matte
- **Floating point comparison:** Use epsilon (1e-6) for ID matching
- **Overlapping coverage:** Can exceed 1.0 (then clamped)

#### Common Use Cases
1. **Selective Color Correction:**
   ```
   EXR → CryptomatteExtract("car") → Matte
                                      ↓
   ColorCorrect (only affects car) ←─┘
   ```

2. **Object Isolation:**
   ```
   Extract specific objects as holdout mattes for compositing
   ```

3. **Multi-Object Selection:**
   ```
   CryptomatteExtract("hero, sidekick, props") → Combined matte
   ```

4. **Material-Based Grading:**
   ```
   CryptoMaterial("metal") → Adjust metallic surfaces only
   ```

#### Cryptomatte Specification
- **Version:** 1.2.0
- **Hash Algorithm:** MurmurHash3_32
- **Conversion:** uint32_to_float32
- **Storage:** Multi-channel EXR with JSON manifest in metadata
- **Anti-aliasing:** Preserved through coverage values
- **Reference:** https://github.com/Psyop/Cryptomatte

#### Dependencies
- **OpenImageIO** - EXR reading with metadata access
- **mmh3** - MurmurHash3 implementation for ID hashing

#### Testing & Validation
1. Load Cryptomatte EXR from Blender/Maya/Houdini render
2. Print available objects with `list_objects=True`
3. Extract single object, verify coverage matches render
4. Extract multiple objects, verify combined matte
5. Test anti-aliased edges (should be smooth, not binary)
6. Test transparency (overlapping objects)
7. Compare to Nuke Cryptomatte node output

#### References
- [Psyop Cryptomatte GitHub](https://github.com/Psyop/Cryptomatte)
- [Cryptomatte Specification PDF](https://github.com/Psyop/Cryptomatte/blob/master/specification/cryptomatte_specification.pdf)
- [Nuke Cryptomatte Documentation](https://learn.foundry.com/nuke/content/comp_environment/cryptomatte/)
- [Blender Cryptomatte](https://docs.blender.org/manual/en/latest/render/shader_nodes/output/aov.html)
- [Houdini Cryptomatte](https://www.sidefx.com/docs/houdini/render/cryptomatte.html)

---

## Priority Tier 3: Effects & Color (Production Tools)

### 1. Glow Node (Luminous Effects)

**Nuke:** Glow | **Natron:** Glow (based on Bloom)
**Category:** `detonate/filter`

#### Purpose
Add luminous glow effect to bright areas of an image. Essential for light effects, magic spells, UI elements, energy effects, and highlight enhancement.

#### Core Behavior
- Extract bright pixels above threshold
- Apply multi-scale blur (geometric progression)
- Composite glowing result back onto original
- Preserve original brightness while adding bloom

#### Algorithm (Improved Over Nuke/Natron)

**Standard Approach:**
```
1. Threshold image to isolate bright pixels
   mask = max(0, (luminance - threshold) / (1 - threshold))

2. Multi-scale blur (geometric progression):
   For i in range(bloom_iterations):
       blur_size = size * (ratio ^ i)
       blurred_layer = gaussian_blur(masked_image, blur_size)
       accumulator += blurred_layer * (1 / bloom_iterations)

3. Composite:
   result = original + (glow_accumulator * intensity)
```

**Detonate Improvements:**
- **Adaptive threshold**: Automatically adjust based on image brightness
- **Blur falloff**: Exponential falloff for more natural glow
- **Saturation boost**: Slightly boost saturation in glow for more vibrant results
- **Edge preservation**: Optional mask to limit glow to specific areas

#### Parameters
- **size:** Glow radius (0-100, default 10)
- **threshold:** Brightness threshold (0-1, default 0.7)
  - Only pixels brighter than this contribute to glow
- **intensity:** Glow strength multiplier (0-5, default 1.0)
- **iterations:** Number of blur passes (1-10, default 5)
  - More iterations = smoother, more expensive glow
- **ratio:** Blur size progression ratio (1.0-3.0, default 2.0)
  - Higher = more spread-out glow
- **saturation_boost:** Boost glow saturation (0-2, default 1.1)
  - Makes glow more vibrant
- **mask:** Optional mask input to limit glow regions

#### Edge Cases
- Very dark images (threshold too high): Return original
- Extreme size values: Clamp to reasonable max (200 pixels)
- HDR values > 1.0: Handle correctly, don't clamp before glow

#### Use Cases
1. **Light rays and glows** - Sunlight through windows
2. **Magic effects** - Spell casting, energy blasts
3. **UI elements** - Glowing buttons, holograms
4. **Automotive** - Headlight bloom
5. **Sci-fi** - Laser beams, energy weapons

#### References
- [Nuke Glow](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/glow.html)
- [Natron Bloom (CImg)](https://natron.readthedocs.io/en/master/plugins/net.sf.cimg.CImgBloom.html)
- Masaki Kawase, "Practical Implementation of High Dynamic Range Rendering", GDC 2004

---

### 2. Defocus Node (Lens-Style Blur)

**Nuke:** Defocus | **Fusion:** SoftGlow
**Category:** `detonate/filter`

#### Purpose
Simulate realistic lens defocus (out-of-focus blur) with bokeh effects. Different from Gaussian blur - mimics actual camera lens characteristics.

#### Core Behavior
- Circular or shaped bokeh kernel
- Adjustable defocus amount
- Optional depth map input (for basic DOF)
- Preserves edge characteristics better than Gaussian

#### Algorithm

**Simple Defocus (No Depth):**
```
1. Create circular bokeh kernel:
   kernel = circular_disk(radius=size)
   OR
   kernel = hexagonal_aperture(radius=size, blades=6)

2. Convolve image with kernel:
   result = convolve2d(image, kernel)

3. Normalize to preserve brightness
```

**Depth-Aware Defocus (Optional):**
```
If depth_map provided:
    focus_distance = user_specified

    For each pixel:
        depth_diff = abs(depth_map[pixel] - focus_distance)
        blur_amount = depth_diff * defocus_multiplier
        apply blur_amount to this pixel region
```

#### Parameters
- **size:** Defocus radius (0-100, default 5)
- **bokeh_shape:** Kernel shape
  - "circular" (default) - Smooth disk
  - "hexagonal" - 6-blade aperture
  - "octagonal" - 8-blade aperture
- **quality:** Sampling quality (1-5, default 3)
  - Higher = slower but smoother
- **depth_map:** Optional depth input (IMAGE)
- **focus_distance:** Z-depth focus point (0-1, default 0.5)
  - Only used if depth_map connected
- **aspect_ratio:** Bokeh aspect ratio (0.1-10, default 1.0)
  - Create anamorphic/oval bokeh

#### Detonate Improvements
- **Multiple bokeh shapes**: Not just circular
- **Aspect ratio control**: Anamorphic lens simulation
- **Quality presets**: Fast/Medium/High for user convenience

#### Use Cases
1. **Background defocus** - Isolate subject
2. **Cinematic look** - Shallow depth of field
3. **Lens simulation** - Match real camera footage
4. **Soft focus** - Beauty/glamour effects

---

### 3. Sharpen Node (Detail Enhancement)

**Nuke:** Sharpen | **Fusion:** Sharpen
**Category:** `detonate/filter`

#### Purpose
Enhance edge detail and recover sharpness from soft images using unsharp mask technique.

#### Algorithm (Unsharp Mask - Industry Standard)

```
1. Create blurred version:
   blurred = gaussian_blur(image, radius)

2. Extract high-frequency detail:
   detail = image - blurred

3. Add detail back with multiplier:
   sharpened = image + (detail * amount)

4. Optional threshold (avoid noise amplification):
   If abs(detail) < threshold:
       sharpened = image  # Don't sharpen subtle areas
```

#### Parameters
- **size:** Blur radius for detection (0.5-5, default 1.0)
  - Smaller = sharpen fine details
  - Larger = sharpen broader edges
- **amount:** Sharpening intensity (0-5, default 1.0)
  - 0 = no effect, 1 = normal, >1 = aggressive
- **threshold:** Noise suppression (0-0.5, default 0.0)
  - Avoid sharpening noise/grain
- **channels:** Which channels to sharpen (rgb, rgba, luminance)
- **clamp:** Clamp output to 0-1 (default False)
  - Useful for avoiding overshoots

#### Detonate Improvements
- **Luminance-only mode**: Sharpen detail without color artifacts
- **Threshold control**: Industry-standard feature often missing
- **Preview mode**: Show only the detail being added

#### Use Cases
1. **Recover soft renders** - Fix over-blurred CG
2. **Enhance textures** - Bring out detail in materials
3. **Upscaling prep** - Pre-sharpen before scaling
4. **Match footage** - Match sharp camera plates

#### References
- [Nuke Sharpen](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/sharpen.html)
- [Unsharp Mask Wikipedia](https://en.wikipedia.org/wiki/Unsharp_masking)
- [Cambridge in Colour: Unsharp Mask](https://www.cambridgeincolour.com/tutorials/unsharp-mask.htm)

---

### 4. ZDefocus Node (Depth-Based DOF)

**Nuke:** ZDefocus
**Category:** `detonate/filter`

#### Purpose
Realistic depth-of-field simulation using Z-depth channel from CG renders. More accurate than simple Defocus - uses actual scene depth information.

#### Core Behavior (Nuke Algorithm)
- Split image into depth layers
- Apply different blur amounts per layer based on distance from focus
- Composite layers back-to-front preserving depth order
- Use FFT for large kernel convolutions

#### Algorithm

```
1. Read depth channel (usually from EXR):
   depth = image[:, :, depth_channel]

2. Calculate blur amount per pixel:
   focus_diff = abs(depth - focus_distance)
   blur_radius = focus_diff * max_blur_size * focal_range

3. Layer-based processing:
   - Quantize depth into discrete layers (e.g., 10-50 layers)
   - Each layer gets uniform blur size
   - Blur each layer with calculated radius

4. Composite layers back-to-front:
   result = background
   For layer in sorted_layers (back to front):
       result = composite(layer, result, layer_alpha)
```

#### Parameters
- **depth_channel:** Which channel contains depth (default "depth.Z")
- **focus_distance:** Z-depth to keep in focus (0-∞, default 5.0)
- **focal_range:** Controls DOF falloff (0.1-10, default 1.0)
  - Smaller = sharper falloff (shallow DOF)
  - Larger = gradual falloff (deep DOF)
- **max_blur:** Maximum blur size (0-100, default 20)
- **num_layers:** Depth layer count (5-100, default 20)
  - More layers = smoother but slower
  - Fewer layers = faster but may show banding
- **bokeh_shape:** Kernel shape (circular, hexagonal, octagonal)

#### Detonate Improvements
- **Auto-detect depth channel**: Search for common names (depth.Z, Z, depth)
- **Depth normalization**: Auto-normalize depth to 0-1 if needed
- **Bokeh shape control**: Not just circular blur
- **Quality presets**: Low/Medium/High layer counts

#### Use Cases
1. **CG depth-of-field** - Add DOF to renders without re-rendering
2. **Focus pulling** - Animate focus distance for rack focus effects
3. **Miniature faking** - Tilt-shift effect using depth
4. **Atmospheric depth** - Emphasize foreground/background separation

#### References
- [Nuke ZDefocus](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/zdefocus.html)
- [Simulating Depth-of-Field Blurring (Nuke)](https://learn.foundry.com/nuke/content/comp_environment/filters/applying_blurs.html)
- [Photography for Compositing - Calculating Real Defocus](https://jianyu.blog/photography_for_compositing_part_5_calculating_real_defocus_in_nuke/)

---

### 5. ZMerge Node (Depth Compositing)

**Nuke:** ZMerge
**Category:** `detonate/compositing`

#### Purpose
Composite multiple CG layers using Z-depth information. Automatically handles occlusion based on which pixels are closer to camera.

#### Core Behavior
- Compare depth values pixel-by-pixel
- Closer pixels (smaller Z) win
- Essential for compositing separate CG render layers

#### Algorithm

```
1. Read depth channels from both inputs:
   depth_A = imageA[:, :, depth_channel]
   depth_B = imageB[:, :, depth_channel]

2. Create selection mask:
   # Smaller depth = closer to camera
   mask_A = (depth_A < depth_B).float()
   mask_B = 1.0 - mask_A

3. Composite based on depth:
   result_RGB = imageA_RGB * mask_A + imageB_RGB * mask_B
   result_depth = torch.minimum(depth_A, depth_B)
   result_alpha = imageA_alpha * mask_A + imageB_alpha * mask_B
```

#### Parameters
- **depth_channel_A:** Depth channel for input A (default "depth.Z")
- **depth_channel_B:** Depth channel for input B (default "depth.Z")
- **depth_tolerance:** Epsilon for depth comparison (default 0.001)
  - Handles floating-point precision issues
- **antialias:** Edge antialiasing (default True)
  - Smooth transitions at depth boundaries
- **output_depth:** Include depth in output (default True)

#### Detonate Improvements
- **Auto-detect depth channels**: Find depth automatically
- **Edge antialiasing**: Smooth hard depth edges (Nuke ZMerge has issues here)
- **Depth visualization mode**: Preview depth buffer
- **Multiple input support**: Composite 3+ layers in one node (future enhancement)

#### Use Cases
1. **CG layer compositing** - Combine character + environment renders
2. **Separate pass compositing** - Merge lighting passes with correct occlusion
3. **Interactive object compositing** - Foreground/background automatic sorting
4. **Render layer optimization** - Render heavy objects separately, composite by depth

#### References
- [Nuke ZMerge](https://learn.foundry.com/nuke/content/reference_guide/merge_nodes/zmerge.html)
- [Deep Compositing in VFX (PDF)](http://www.diva-portal.org/smash/get/diva2:1325032/FULLTEXT01.pdf)
- [The Art of Deep Compositing (fxguide)](https://www.fxguide.com/fxfeatured/the-art-of-deep-compositing/)

---

### 6. ColorCurves Node (Professional Grading)

**Nuke:** ColorLookup | **Natron:** ColorLookup
**Category:** `detonate/color`

#### Purpose
Professional color grading using Bezier curves. Industry-standard tool for precise tonal control across highlights, midtones, and shadows.

#### Core Behavior
- Adjustable Bezier curves for Master, R, G, B channels
- Curve points define input→output mapping
- Smooth interpolation between points
- Stack multiple curve adjustments

#### Algorithm

```
1. Define curves (one per channel: Master, R, G, B):
   curve_points = [(0, 0), (0.5, 0.5), (1, 1)]  # Default linear

2. Interpolate curve using cubic Bezier:
   For each input value x:
       output = bezier_interpolate(curve_points, x)

3. Apply curves in order:
   # Apply master curve to all channels
   temp = apply_curve(image, master_curve)

   # Apply per-channel curves
   result[:, :, 0] = apply_curve(temp[:, :, 0], red_curve)
   result[:, :, 1] = apply_curve(temp[:, :, 1], green_curve)
   result[:, :, 2] = apply_curve(temp[:, :, 2], blue_curve)
```

#### Parameters
- **master_curve:** Points list [(x, y), ...] for master curve
  - Affects all channels simultaneously
- **red_curve:** Points for red channel
- **green_curve:** Points for green channel
- **blue_curve:** Points for blue channel
- **luma_curve:** Optional luminance-only curve
- **interpolation:** Curve interpolation method
  - "cubic" (default) - Smooth Bezier
  - "linear" - Sharp corners
  - "monotonic" - Prevent overshoot

#### Detonate Improvements
- **Curve presets**: S-curve, contrast boost, film look, etc.
- **Visual curve editor** (if ComfyUI supports custom widgets)
- **Luma curve**: Adjust brightness without color shift
- **Before/after preview**: Toggle to see effect
- **Load/save curves**: Import curves from LUTs or other tools (future)

#### Curve Presets (Smart Defaults)
1. **Linear**: `[(0,0), (1,1)]` - No change
2. **S-Curve Contrast**: `[(0,0), (0.25,0.2), (0.75,0.8), (1,1)]` - Boost midtone contrast
3. **Lift Shadows**: `[(0,0.1), (0.5,0.5), (1,1)]` - Brighten shadows
4. **Crush Blacks**: `[(0,0), (0.1,0), (1,1)]` - Deepen blacks
5. **Filmic**: `[(0,0.02), (0.18,0.18), (0.9,0.95), (1,0.98)]` - Film-like rolloff

#### Use Cases
1. **Contrast enhancement** - S-curve for punch
2. **Shadow/highlight recovery** - Lift or crush specific ranges
3. **Color grading looks** - Film emulation, stylized grades
4. **Matching footage** - Match different camera sources
5. **Selective tonal control** - Precise highlights/mids/shadows adjustment

#### References
- [Natron ColorLookup](https://natron.readthedocs.io/en/master/plugins/net.sf.openfx.ColorLookupPlugin.html)
- [Working with Color (Natron)](https://natron.readthedocs.io/en/rb-2.5/guide/compositing-color.html)
- [Blender RGB Curves](https://docs.blender.org/manual/en/latest/render/shader_nodes/color/rgb_curves.html)

---

### 7. Ramp Node (Gradient Generator)

**Nuke:** Ramp | **Fusion:** FastNoise (Gradient)
**Category:** `detonate/generator`

#### Purpose
Generate procedural gradients for masks, lighting effects, and backgrounds. Essential utility for creating smooth transitions and falloffs.

#### Gradient Types

**Linear:**
```
gradient = (position - start_point) · direction_vector
normalized = (gradient - min) / (max - min)
```

**Radial:**
```
center_distance = length(position - center_point)
normalized = center_distance / max_radius
```

**Angle:**
```
angle = atan2(position.y - center.y, position.x - center.x)
normalized = (angle + π) / (2π)  # Map -π to π → 0 to 1
```

**Box:**
```
# Distance to edge from center
distance = max(abs(position.x - center.x), abs(position.y - center.y))
normalized = distance / max_distance
```

#### Parameters
- **type:** Gradient type (linear, radial, angle, box)
- **width, height:** Output dimensions
- **color_start:** Starting color (RGBA, default black)
- **color_end:** Ending color (RGBA, default white)
- **start_point:** Gradient start position (0-1, 0-1)
- **end_point:** Gradient end position (for linear)
- **center_point:** Center position (for radial/angle/box)
- **falloff:** Gradient curve
  - "linear" - Uniform
  - "smooth" - Ease in/out
  - "exponential" - Sharp near edges
  - "logarithmic" - Sharp in center

#### Detonate Improvements
- **Falloff curves**: More control than basic linear
- **Color gradients**: Not just grayscale, full RGBA support
- **HDR support**: Colors can exceed 1.0
- **Noise overlay**: Optional noise for organic gradients (future)

#### Use Cases
1. **Vignettes** - Radial gradient for edge darkening
2. **Lighting ramps** - Simulate directional light falloff
3. **Mask generation** - Soft falloff masks for effects
4. **Backgrounds** - Simple gradient backgrounds
5. **Displacement maps** - Drive other effects with gradients

---

### 8. Noise Node (Procedural Textures)

**Nuke:** Noise (removed in modern versions) | **Blender:** Noise Texture
**Category:** `detonate/generator`

#### Purpose
Generate procedural Perlin/Simplex noise for textures, displacement, grain, and breakup patterns.

#### Noise Types

**Perlin Noise:**
```
# Classic gradient noise
value = perlin(position * scale + offset, octaves, persistence)
```

**Simplex Noise:**
```
# Improved Perlin with better performance
value = simplex(position * scale + offset, octaves, persistence)
```

**Cellular/Worley Noise:**
```
# Voronoi-style cellular patterns
value = worley(position * scale, distance_metric)
```

#### Algorithm (Perlin)

```
1. Generate base octave:
   noise = perlin_2d(x * scale, y * scale)

2. Add higher frequency octaves (fractal):
   amplitude = 1.0
   frequency = 1.0

   For i in range(octaves):
       noise += perlin_2d(x * scale * frequency, y * scale * frequency) * amplitude
       amplitude *= persistence  # Each octave contributes less
       frequency *= lacunarity   # Each octave has higher frequency

3. Normalize to 0-1 range
```

#### Parameters
- **width, height:** Output dimensions
- **noise_type:** Type of noise (perlin, simplex, cellular, white)
- **scale:** Noise frequency (0.1-10, default 1.0)
  - Smaller = larger features
  - Larger = finer detail
- **octaves:** Fractal detail layers (1-8, default 4)
  - More octaves = more detail
- **persistence:** Octave amplitude falloff (0-1, default 0.5)
  - Higher = rougher noise
- **lacunarity:** Octave frequency multiplier (1-4, default 2.0)
- **seed:** Random seed for reproducibility
- **output_mode:** Output format
  - "grayscale" - Single channel noise in RGB
  - "rgb" - Independent noise per channel (color noise)
  - "normal_map" - Convert to normal map

#### Detonate Improvements
- **Multiple noise types**: Not just one algorithm
- **Tileable option**: Seamless tiling for textures
- **Animated noise**: Time parameter for animated textures
- **Normal map output**: Direct conversion to normal maps
- **HDR range**: Output can exceed 0-1

#### Use Cases
1. **Texture generation** - Procedural cloud, marble, wood textures
2. **Displacement** - Drive deformations with noise
3. **Grain simulation** - Add film grain or sensor noise
4. **Matte breakup** - Make clean edges more organic
5. **Turbulence** - Distortion/warp maps

#### References
- [Perlin Noise (Wikipedia)](https://en.wikipedia.org/wiki/Perlin_noise)
- [Simplex Noise (Wikipedia)](https://en.wikipedia.org/wiki/Simplex_noise)
- [Blender Noise Texture](https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/noise.html)

---

## Testing & Validation (Tier 3)

All Tier 3 nodes should pass these validation tests:

1. **Glow:**
   - Verify threshold correctly isolates bright pixels
   - Test multi-scale blur progression
   - Compare to Nuke Glow output
   - Test HDR glow (values > 1.0)

2. **Defocus:**
   - Verify circular bokeh kernel
   - Test different bokeh shapes
   - Compare to Nuke Defocus
   - Test with/without depth map

3. **Sharpen:**
   - Verify unsharp mask formula
   - Test threshold noise suppression
   - Compare to Photoshop Unsharp Mask
   - Test amount scaling

4. **ZDefocus:**
   - Load EXR with depth channel
   - Verify layer-based processing
   - Test focus distance animation
   - Compare to Nuke ZDefocus

5. **ZMerge:**
   - Composite two depth images
   - Verify closer pixels win
   - Test edge antialiasing
   - Compare to Nuke ZMerge

6. **ColorCurves:**
   - Test curve point interpolation
   - Verify master curve affects all channels
   - Test S-curve contrast boost
   - Load curve presets

7. **Ramp:**
   - Test all gradient types
   - Verify smooth falloffs
   - Test HDR color support
   - Check tiling (if implemented)

8. **Noise:**
   - Test all noise types
   - Verify octave stacking
   - Test reproducibility (same seed = same noise)
   - Compare to Blender noise output

---

## Sources & References (Tier 3)

### Nuke Documentation
- [Glow](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/glow.html)
- [Defocus](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/defocus.html)
- [Sharpen](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/sharpen.html)
- [ZDefocus](https://learn.foundry.com/nuke/content/reference_guide/filter_nodes/zdefocus.html)
- [ZMerge](https://learn.foundry.com/nuke/content/reference_guide/merge_nodes/zmerge.html)
- [Simulating Depth-of-Field](https://learn.foundry.com/nuke/content/comp_environment/filters/applying_blurs.html)

### Natron Documentation
- [Glow](https://natron.readthedocs.io/en/master/plugins/fr.inria.Glow.html)
- [Bloom (CImg)](https://natron.readthedocs.io/en/master/plugins/net.sf.cimg.CImgBloom.html)
- [ColorLookup](https://natron.readthedocs.io/en/master/plugins/net.sf.openfx.ColorLookupPlugin.html)
- [Working with Color](https://natron.readthedocs.io/en/rb-2.5/guide/compositing-color.html)

### Technical Resources
- [Unsharp Mask Wikipedia](https://en.wikipedia.org/wiki/Unsharp_masking)
- [Cambridge in Colour: Unsharp Mask Tutorial](https://www.cambridgeincolour.com/tutorials/unsharp-mask.htm)
- [Perlin Noise](https://en.wikipedia.org/wiki/Perlin_noise)
- [Simplex Noise](https://en.wikipedia.org/wiki/Simplex_noise)
- [fxguide: The Art of Deep Compositing](https://www.fxguide.com/fxfeatured/the-art-of-deep-compositing/)

### Implementation References
- Masaki Kawase, "Practical Implementation of High Dynamic Range Rendering", GDC 2004
- Ken Perlin, "Improving Noise", SIGGRAPH 2002
- [Photography for Compositing - Calculating Real Defocus in Nuke](https://jianyu.blog/photography_for_compositing_part_5_calculating_real_defocus_in_nuke/)

---

## Priority Tier 4: Production Finishing

### 1. Crop Node (Framing & Composition)

**Nuke:** Crop | **DaVinci Resolve:** Crop
**Category:** `detonate/transform`

#### Purpose
Crop images to specific dimensions with optional soft edges for creative framing and aspect ratio changes.

#### Core Behavior
- Define rectangular crop region
- Optional soft edge feathering
- Aspect ratio presets (Detonate improvement!)
- Center crop mode

#### Parameters
- **left, top, right, bottom:** Crop box in pixels
- **aspect_ratio:** Preset aspect ratios (Detonate improvement!)
  - "custom", "16:9", "2.39:1", "2.35:1", "1.85:1", "4:3", "1:1", "9:16"
- **center_crop:** Automatically center the crop box (bool)
- **feather:** Soft edge width in pixels (0-500)
- **feather_mode:** Feather falloff shape (Detonate improvement!)
  - "linear" - Linear falloff
  - "smooth" - Smoothstep (3x²-2x³)
  - "gaussian" - Gaussian falloff
- **outside_black:** Fill outside crop with black vs clamp (bool)

#### Algorithm
```python
# Create feather matte
dist_to_edge = minimum distance from any edge
if feather_mode == "smooth":
    matte = smoothstep(dist_to_edge / feather)
elif feather_mode == "gaussian":
    matte = exp(-(feather - dist_to_edge)² / (2σ²))

# Apply crop with soft edges
result = cropped_image * matte
```

#### Detonate Improvements
1. **Aspect ratio presets**: Industry-standard aspect ratios
2. **Center crop mode**: One-click centered framing
3. **Multiple feather modes**: Linear, smooth, gaussian

#### Use Cases
1. **Aspect ratio conversion** - 16:9 to 2.39:1 for cinematic look
2. **Creative framing** - Remove unwanted edges
3. **Soft vignettes** - Feathered crop for gradual edge darkening
4. **Format changes** - Vertical to horizontal for different platforms

---

### 2. Exposure Node (Photographic Control)

**Nuke:** EXPTool | **DaVinci Resolve:** Exposure
**Category:** `detonate/color`

#### Purpose
Photographic stops-based exposure adjustment. More intuitive than gain/multiply for photographers and cinematographers.

#### Core Formula
```
output = (input - pivot) * 2^stops + pivot
```

Where:
- **stops**: f-stop exposure adjustment
  - +1 = double exposure
  - -1 = half exposure
- **pivot**: Value that remains unchanged (default 0.18 = middle gray)

#### Parameters
- **stops:** Master exposure in f-stops (-10 to +10, default 0)
- **offset:** Black point shift (-1 to +1)
- **pivot:** Unchanged value point (0-1, default 0.18)
- **stops_r, stops_g, stops_b:** Per-channel stops (Detonate improvement!)
  - Allows creative color grading via selective channel exposure
- **highlight_rolloff:** Soft clipping for highlights (Detonate improvement!)
  - Prevents blown-out highlights (0-1, default 0)
- **response_curve:** Exposure response curve (Detonate improvement!)
  - "linear" - Standard exposure
  - "logarithmic" - For HDR/log footage
  - "filmic" - ACES-like S-curve compression

#### Algorithm
```python
# Apply per-channel stops
exposure_mult = 2^(stops + stops_rgb)
result = (input - pivot) * exposure_mult + pivot

# Apply highlight rolloff
if highlight_rolloff > 0:
    threshold = 1.0 - (rolloff * 0.5)
    compressed = threshold + (rgb - threshold) / (1 + (rgb - threshold))
    result = where(rgb > threshold, compressed, result)
```

#### Detonate Improvements
1. **Per-channel stops**: Separate R/G/B exposure for color grading
2. **Highlight rolloff**: Prevent harsh clipping
3. **Response curves**: Linear, log, filmic for different workflows

#### Use Cases
1. **Exposure matching** - Match different camera exposures
2. **HDR tone mapping** - Prepare HDR for SDR display
3. **Creative grading** - Photographic-style exposure adjustments
4. **Highlight protection** - Prevent blown highlights

---

### 3. Vignette Node (Lens Effects)

**DaVinci Resolve:** Vignette | **Photoshop:** Lens Correction Vignette
**Category:** `detonate/filter`

#### Purpose
Lens vignetting effect - darken or lighten image edges for photographic looks and focus control.

#### Core Behavior
- Creates radial falloff from center
- Darkens edges (positive amount) or lightens edges (negative amount)
- Multiple shapes and falloff curves (Detonate improvement!)

#### Parameters
- **amount:** Vignette intensity (-2 to +2, default 0.5)
  - Positive = darken edges
  - Negative = lighten edges
- **size:** Vignette size (0-2, default 0.5)
  - Controls where vignetting begins
- **feather:** Edge softness (0-1, default 0.5)
- **center_x, center_y:** Vignette center (0-1 normalized coordinates)
- **shape:** Vignette shape (Detonate improvement!)
  - "circular" - Round vignette
  - "oval" - Elliptical
  - "rectangular" - Box-shaped
- **aspect_ratio:** Shape aspect ratio (0.1-10, default 1.0)
- **falloff:** Falloff curve (Detonate improvement!)
  - "linear", "quadratic", "cubic", "smooth"
- **tint_r, tint_g, tint_b:** Color tint at edges (Detonate improvement!)
  - Add color to vignette for stylistic effects

#### Algorithm
```python
# Calculate distance from center
if shape == "circular":
    dist = sqrt((x - center_x)² + (y - center_y)²)
elif shape == "rectangular":
    dist = max(abs(x - center_x), abs(y - center_y))

# Apply falloff curve
t = clamp((dist - inner_radius) / (outer_radius - inner_radius), 0, 1)
if falloff == "quadratic":
    matte = t²
elif falloff == "smooth":
    matte = t² * (3 - 2t)  # smoothstep

# Apply vignette
vignette_mult = 1.0 - matte * amount
result = rgb * vignette_mult + matte * tint_rgb
```

#### Detonate Improvements
1. **Multiple shapes**: Circular, oval, rectangular
2. **Multiple falloffs**: Linear, quadratic, cubic, smooth
3. **Color tinting**: Add color to edges for stylistic effects
4. **Inverse vignette**: Lighten edges instead of darken

#### Use Cases
1. **Photographic vignette** - Classic lens darkening
2. **Focus attention** - Draw viewer to center
3. **Stylistic grading** - Color-tinted edges
4. **Frame composition** - Subtle edge darkening

---

### 4. Grain Node (Film Emulation)

**Nuke:** Grain | **DaVinci Resolve:** Film Grain
**Category:** `detonate/filter`

#### Purpose
Add procedural film grain and texture for matching CG to live action and photorealistic finishing.

#### Core Behavior
- Generate procedural noise patterns
- Apply to image with luminance-dependent distribution
- Multiple grain types and color modes (Detonate improvement!)

#### Parameters
- **intensity:** Grain strength (0-1, default 0.1)
- **size:** Grain size/frequency (0.1-10, default 1.0)
  - Smaller = finer grain
- **grain_type:** Grain pattern (Detonate improvement!)
  - "film" - Gaussian distribution (classic film grain)
  - "digital" - Uniform distribution (sensor noise)
  - "organic" - Multi-octave (layered texture)
  - "halftone" - Dot pattern (print simulation)
- **color:** Use color grain vs monochrome (bool)
- **shadow_bias, highlight_bias:** Luminance-dependent grain (Detonate improvement!)
  - Controls where grain appears most
  - shadow_bias: -1 (more in shadows) to +1 (less in shadows)
  - highlight_bias: +1 (more in highlights) to -1 (less in highlights)
- **red_intensity, green_intensity, blue_intensity:** Per-channel grain (Detonate improvement!)
  - Adjust grain per color channel
- **seed:** Random seed for reproducibility

#### Algorithm
```python
# Generate grain noise
if grain_type == "film":
    grain = randn(H, W, channels) * 0.5  # Gaussian
elif grain_type == "digital":
    grain = (rand(H, W, channels) * 2 - 1) * 0.5  # Uniform
elif grain_type == "organic":
    grain = randn() * 0.7 + randn() * 0.3  # Multi-scale

# Apply size (downsample/upsample for coarser grain)
if size != 1.0:
    grain = resize(grain, 1/size) → resize(grain, size)

# Luminance-dependent masking
luma = 0.2126*R + 0.7152*G + 0.0722*B
luma_mask = 1.0 + shadow_mask * (-shadow_bias) + highlight_mask * highlight_bias

# Add grain to image
result = image + grain * intensity * luma_mask
```

#### Detonate Improvements
1. **Multiple grain types**: Film, digital, organic, halftone
2. **Luminance-dependent**: Shadow/highlight bias controls
3. **Per-channel intensity**: Separate R/G/B grain strength
4. **Color vs monochrome**: Full color grain or grayscale

#### Use Cases
1. **Match CG to film** - Add grain to renders
2. **Texture addition** - Add detail to flat renders
3. **Digital noise simulation** - Camera sensor noise
4. **Photographic authenticity** - Film emulation

---

### 5. HueSatVal Node (HSV Manipulation)

**Photoshop:** Hue/Saturation | **DaVinci Resolve:** HSL
**Category:** `detonate/color`

#### Purpose
Direct HSV (Hue/Saturation/Value) color space manipulation for precise color adjustments.

#### Core Behavior
- Convert RGB → HSV
- Adjust H, S, V independently
- Convert HSV → RGB
- Selective hue ranges (Detonate improvement!)

#### Parameters
- **hue:** Hue rotation in degrees (-180 to +180)
- **saturation:** Saturation adjustment (-1 to +1)
  - -1 = fully desaturate
  - 0 = no change
  - +1 = double saturation
- **value:** Value/brightness adjustment (-1 to +1)
  - -1 = black
  - 0 = no change
  - +1 = double brightness
- **hue_range:** Selective hue targeting (Detonate improvement!)
  - "all", "reds", "yellows", "greens", "cyans", "blues", "magentas"
  - Only affects selected color range
- **range_softness:** Feathering for selective hue ranges (0-1)
- **preserve_luminance:** Maintain original luminance (Detonate improvement!)
  - Useful when adjusting hue/saturation without brightness change

#### Algorithm
```python
# RGB to HSV conversion
V = max(R, G, B)
S = (V - min(R, G, B)) / V  if V != 0
H = hue angle based on which channel is maximum

# Apply adjustments
H = (H + hue_shift) % 1.0
S = S * (1 + saturation_adjustment)
V = V * (1 + value_adjustment)

# Selective hue range masking
if hue_range != "all":
    hue_distance = abs(H - range_center)
    mask = smooth_falloff(hue_distance, range_softness)
    # Apply adjustments only where mask is high

# HSV to RGB conversion
Convert back using standard HSV→RGB formula

# Restore luminance if requested
if preserve_luminance:
    new_luma = calculate_luminance(result_rgb)
    result_rgb *= (original_luma / new_luma)
```

#### Detonate Improvements
1. **Selective hue ranges**: Target specific colors (reds, blues, etc.)
2. **Range softness**: Feathered transitions between selected/unselected
3. **Preserve luminance**: Maintain brightness while adjusting hue/sat

#### Use Cases
1. **Precise hue shifts** - Rotate specific color ranges
2. **Saturation boosting** - Enhance specific colors
3. **Selective desaturation** - Remove color from specific hues
4. **Creative color grading** - Stylized color adjustments

---

### 6. Denoise Node (Noise Reduction)

**DaVinci Resolve:** Spatial Noise Reduction
**Category:** `detonate/filter`

#### Purpose
Edge-preserving noise reduction using bilateral filtering and other algorithms.

#### Core Behavior
- Reduce noise while preserving edges
- Multiple denoising algorithms (Detonate improvement!)
- Separate luma/chroma denoising

#### Parameters
- **algorithm:** Denoising algorithm (Detonate improvement!)
  - "bilateral" - Edge-preserving (spatial + range filtering)
  - "median" - Good for salt-and-pepper noise
  - "gaussian" - Simple smoothing (not edge-preserving)
- **strength:** Overall denoising strength (0-1, default 0.5)
- **spatial_size:** Spatial filter size (1-20, default 5)
  - Larger = more smoothing
- **color_range:** Color similarity threshold (bilateral only, 0.01-1, default 0.1)
  - How similar colors must be to be blurred together
- **preserve_detail:** Detail preservation (Detonate improvement!)
  - Adds back high-frequency detail (0-1, default 0.5)
- **denoise_luminance, denoise_chrominance:** Luma/chroma separation (Detonate improvement!)
  - Denoise brightness and color independently

#### Algorithm (Bilateral Filter)
```python
# Simplified bilateral filter (full version too slow)
# Approximated with separable Gaussian

# Spatial Gaussian kernel
spatial_kernel = gaussian(sigma=spatial_size)

# Apply separable blur (approximation)
blurred = gaussian_blur(image, spatial_size)

# Mix with original based on strength
result = image * (1 - strength) + blurred * strength

# Preserve detail if requested
if preserve_detail > 0:
    detail = image - average_blur(image, 3)
    result += detail * preserve_detail
```

#### Detonate Improvements
1. **Multiple algorithms**: Bilateral, median, gaussian
2. **Detail preservation**: Control how much high-frequency detail to keep
3. **Luma/chroma separation**: Denoise brightness and color independently

#### Use Cases
1. **Noise cleanup** - Remove camera sensor noise
2. **Compression artifact reduction** - Clean up blocky compression
3. **Skin smoothing** - Beauty/glamour effects
4. **Pre-keying cleanup** - Reduce noise before keying

---

### 7. LUT Node (Color Transformation)

**Nuke:** OCIOFileTransform | **DaVinci Resolve:** LUT
**Category:** `detonate/color`

#### Purpose
Apply 1D/3D color lookup tables from industry-standard .cube files.

#### Core Behavior
- Parse .cube LUT files
- Support 1D and 3D LUTs
- Trilinear interpolation for 3D LUTs
- LUT caching for performance (Detonate improvement!)

#### .cube File Format
```
LUT_3D_SIZE 32
0.0 0.0 0.0
0.0 0.0 0.033
...
1.0 1.0 1.0
```

#### Parameters
- **lut_file:** Path to .cube LUT file (string)
- **strength:** LUT application strength (0-1, default 1.0)
  - Mix between original and LUT-processed
- **interpolation:** Interpolation mode (Detonate improvement!)
  - "trilinear" - High quality, smooth
  - "nearest" - Fast, lower quality
- **inverse:** Apply inverse LUT (Detonate improvement!)
  - Approximate inverse transformation

#### Algorithm (3D LUT with Trilinear Interpolation)
```python
# Clamp input to 0-1
rgb = clamp(rgb, 0, 1)

# Scale to LUT coordinate space
coords = rgb * (lut_size - 1)

# Get surrounding cube corners
r0, g0, b0 = floor(coords)
r1, g1, b1 = clamp(r0 + 1, max=lut_size - 1)

# Interpolation weights
dr = coords.r - r0
dg = coords.g - g0
db = coords.b - b0

# Lookup 8 corners of cube
c000 = lut[r0, g0, b0]
c001 = lut[r0, g0, b1]
...
c111 = lut[r1, g1, b1]

# Trilinear interpolation
c00 = c000 * (1-db) + c001 * db
c01 = c010 * (1-db) + c011 * db
c10 = c100 * (1-db) + c101 * db
c11 = c110 * (1-db) + c111 * db

c0 = c00 * (1-dg) + c01 * dg
c1 = c10 * (1-dg) + c11 * dg

result = c0 * (1-dr) + c1 * dr
```

#### Detonate Improvements
1. **LUT caching**: Parse .cube files once, cache for performance
2. **Multiple interpolation**: Trilinear (quality) vs nearest (speed)
3. **Strength control**: Mix with original image

#### Use Cases
1. **Film emulation** - Apply film stock LUTs
2. **Camera matching** - Match different camera looks
3. **Creative grading** - Apply stylized color grades
4. **Technical conversions** - Log to Rec.709

---

### 8. CornerPin Node (Perspective Transform)

**Nuke:** CornerPin2D | **After Effects:** Corner Pin
**Category:** `detonate/transform`

#### Purpose
4-point perspective transform for screen replacements, match-moving, and perspective correction.

#### Core Behavior
- Define 4 source corner points
- Define 4 destination corner points
- Calculate homography matrix (3x3)
- Apply perspective warp using homography

#### Homography Mathematics
Homography H maps (x, y) → (x', y') using:
```
[x']   [h11 h12 h13]   [x]
[y'] = [h21 h22 h23] * [y]
[1 ]   [h31 h32  1 ]   [1]
```

Solved using Direct Linear Transform (DLT) from 4 point correspondences.

#### Parameters
- **from_x1, from_y1...from_x4, from_y4:** Source corners (pixels)
  - Corner 1: Top-left
  - Corner 2: Top-right
  - Corner 3: Bottom-right
  - Corner 4: Bottom-left
- **to_x1, to_y1...to_x4, to_y4:** Destination corners (pixels)
- **filter:** Interpolation mode (Detonate improvement!)
  - "bilinear" - Fast, good quality
  - "bicubic" - Slower, high quality
  - "nearest" - Fastest, pixelated
- **invert:** Invert transformation (Detonate improvement!)
  - Swap source and destination

#### Algorithm (Homography Calculation)
```python
# Build DLT matrix A (8x9 for 4 point pairs)
For each point correspondence (x, y) → (u, v):
    [-x, -y, -1,  0,  0,  0, u*x, u*y, u]
    [ 0,  0,  0, -x, -y, -1, v*x, v*y, v]

# Solve using SVD
U, S, Vt = svd(A)
h = Vt[-1, :]  # Last row of Vt (null space)

# Reshape to 3x3 matrix
H = h.reshape(3, 3)
H = H / H[2, 2]  # Normalize

# Apply perspective transform
For each output pixel (x, y):
    # Find source pixel using inverse homography
    src_coords = H_inv @ [x, y, 1]
    src_x = src_coords[0] / src_coords[2]
    src_y = src_coords[1] / src_coords[2]

    # Sample source image at (src_x, src_y) using interpolation
    result[x, y] = sample(source, src_x, src_y, filter_mode)
```

#### Detonate Improvements
1. **Complete homography**: Full SVD-based DLT implementation
2. **Multiple filter modes**: Bilinear, bicubic, nearest
3. **Inverse transformation**: Swap source/destination easily

#### Use Cases
1. **Screen replacements** - Phone screens, monitors, billboards
2. **Match-moving** - Integrate CG into tracked footage
3. **Perspective correction** - De-keystone images
4. **Planar tracking** - Apply tracked corner data

---

## Testing & Validation (Tier 4)

All Tier 4 nodes should pass these validation tests:

1. **Crop:**
   - Verify aspect ratio presets calculate correctly
   - Test center crop mode
   - Test feather modes (linear, smooth, gaussian)
   - Verify soft edges are smooth

2. **Exposure:**
   - Verify 2^stops formula (1 stop = 2x exposure)
   - Test per-channel stops
   - Test highlight rolloff prevents clipping
   - Compare to camera/Resolve exposure tools

3. **Vignette:**
   - Test all shapes (circular, oval, rectangular)
   - Test all falloff curves
   - Verify color tinting works
   - Test inverse vignette (negative amount)

4. **Grain:**
   - Test all grain types produce different patterns
   - Verify luminance-dependent bias works
   - Test reproducibility (same seed = same grain)
   - Compare to Resolve Film Grain

5. **HueSatVal:**
   - Test RGB↔HSV conversion accuracy
   - Test selective hue ranges
   - Verify range softness creates smooth transitions
   - Test preserve luminance mode

6. **Denoise:**
   - Test all algorithms
   - Verify edge preservation (bilateral)
   - Test detail preservation control
   - Compare to dedicated denoise tools

7. **LUT:**
   - Load various .cube files (1D and 3D)
   - Verify trilinear interpolation is smooth
   - Test LUT caching (second load should be instant)
   - Compare to Nuke OCIOFileTransform output

8. **CornerPin:**
   - Test homography calculation with known point pairs
   - Verify perspective warp is correct
   - Test all filter modes
   - Compare to Nuke CornerPin2D

---

## Sources & References (Tier 4)

### Nuke Documentation
- [Crop](https://learn.foundry.com/nuke/content/reference_guide/transform_nodes/crop.html)
- [EXPTool](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/exptool.html)
- [CornerPin2D](https://learn.foundry.com/nuke/content/reference_guide/transform_nodes/cornerpin.html)
- [Grain](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/grain.html)
- [OCIOFileTransform](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/ociofiletransform.html)

### DaVinci Resolve / Other Tools
- DaVinci Resolve: Exposure, Vignette, Film Grain, LUT
- Photoshop: Lens Correction, Hue/Saturation
- After Effects: Corner Pin Effect

### Technical Resources
- [Bilateral Filter Wikipedia](https://en.wikipedia.org/wiki/Bilateral_filter)
- [.cube LUT Format Specification](https://www.adobe.com/support/downloads/icc_eula_mac_distribute.html)
- [Homography Estimation](https://en.wikipedia.org/wiki/Homography_(computer_vision))
- [Direct Linear Transform (DLT)](https://www.uio.no/studier/emner/matnat/its/nedlagte-emner/UNIK4690/v16/forelesninger/lecture_4_3-estimating-homographies-from-feature-correspondences.pdf)

---

**Document Version:** 1.4
**Last Updated:** 2025-01-22
**Status:** Tier 1 Complete | Tier 2 Complete | Cryptomatte Complete | Tier 3 Complete | Tier 4 Complete
