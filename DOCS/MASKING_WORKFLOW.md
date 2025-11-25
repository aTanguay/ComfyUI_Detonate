# Professional Masking Workflow in ComfyUI_Detonate

## The Better Approach: Use Native Tools + Professional Refinement

Instead of trying to build a complex interactive rotoscoping tool, ComfyUI_Detonate provides **professional-grade mask refinement** that works with ComfyUI's existing mask drawing capabilities.

---

## Recommended Workflow

### Step 1: Create Your Mask (ComfyUI Native Tools)

Use ComfyUI's built-in mask creation tools:

**Option A: Manual Drawing**
- Right-click on image → "Open in MaskEditor"
- Draw your mask using ComfyUI's brush tools
- Save and use the mask output

**Option B: AI Segmentation**
- Use SAM (Segment Anything Model) nodes
- Use other AI segmentation custom nodes
- Get mask from any source (keyers, generators, etc.)

**Option C: Color Selection**
- Use **Mask From Color (Detonate)** node
- Select a color and tolerance
- Quick selections similar to Photoshop's Color Range

### Step 2: Refine with Mask Smoother (NEW!)

Connect your rough mask to **Mask Smoother (Detonate)** for professional edge quality:

```
[Draw Mask] → [Mask Smoother] → [Use in Comp]
    ↓
Parameters:
- smooth_iterations: 2-5 (removes jagged edges)
- edge_adjust: ±pixels (grow/shrink mask)
- feather: pixels (soft edge)
- feather_type: Smooth/Linear/Gaussian
- antialias_quality: Medium/High
```

### Step 3: Use in Compositing

Apply refined mask to your composite:
- As alpha channel (ChannelCopy)
- As merge mask (Merge node)
- For color corrections (Grade, ColorCorrect)
- For effects (Blur, Glow, etc.)

---

## Node Reference

### Mask Smoother (Detonate)

**Purpose:** Refine mask edges to professional quality

**Inputs:**
- `mask` (MASK) - Input mask from any source

**Parameters:**

**Smoothing:**
- `smooth_iterations` (0-10) - Number of edge smoothing passes
  - 0 = No smoothing (useful if you just want feathering)
  - 2 = Good balance (removes most jaggies)
  - 5+ = Very smooth, organic edges
  - Uses morphological closing/opening + gentle blur

**Edge Adjustment:**
- `edge_adjust` (-50 to +50 pixels)
  - Negative values: Contract (shrink) mask
  - Positive values: Expand (grow) mask
  - Uses circular kernel for natural results

**Feathering:**
- `feather` (0-100 pixels) - Soft edge width
- `feather_type`:
  - **Smooth** - Natural S-curve falloff (recommended)
  - **Linear** - Even linear falloff
  - **Gaussian** - Soft, blur-like falloff

**Quality:**
- `antialias_quality`:
  - **Off** - No AA (1x sampling)
  - **Low** - 2x supersampling
  - **Medium** - 4x supersampling (recommended)
  - **High** - 8x supersampling (highest quality, slower)

**Output:**
- `invert` - Invert mask after processing

### Mask From Color (Detonate)

**Purpose:** Create mask by selecting a color range

**Inputs:**
- `image` (IMAGE) - Source image

**Parameters:**
- `color` (hex string) - Target color (e.g., "#00FF00" for green)
- `tolerance` (0-1) - Color matching tolerance
  - 0.0 = Exact color match only
  - 0.1 = Similar colors (recommended for greenscreen)
  - 0.5 = Broad color range
  - 1.0 = Everything matches
- `feather` (0-50 pixels) - Edge feathering
- `invert` - Invert selection

**Common Uses:**
- Quick greenscreen selections
- Sky selections (select blue)
- Skin tone selections
- Object isolation by color

---

## Workflow Examples

### Example 1: Clean Up Hand-Drawn Mask

```
[Load Image]
    ↓
[MaskEditor] (draw rough mask)
    ↓
[Mask Smoother]
  - smooth_iterations: 3
  - edge_adjust: -1.0 (contract slightly to avoid edge spill)
  - feather: 2.0
  - feather_type: Smooth
  - antialias_quality: High
    ↓
[Use in composite]
```

**Result:** Professional-quality mask from quick rough drawing

### Example 2: Refine AI Segmentation

```
[Load Image]
    ↓
[SAM Segmentation] (or other AI mask)
    ↓
[Mask Smoother]
  - smooth_iterations: 1 (AI masks are already smooth)
  - edge_adjust: 0.5 (expand slightly for safety)
  - feather: 3.0 (soft edge for natural comp)
  - feather_type: Gaussian
  - antialias_quality: Medium
    ↓
[Merge with background]
```

**Result:** AI mask with professional comp-ready edges

### Example 3: Quick Color Selection

```
[Load Image] (greenscreen footage)
    ↓
[Mask From Color]
  - color: "#00FF00" (green)
  - tolerance: 0.15
  - feather: 2.0
    ↓
[Invert] (if needed)
    ↓
[Mask Smoother] (optional refinement)
  - smooth_iterations: 1
  - feather: 1.0
    ↓
[Use as alpha]
```

**Result:** Quick greenscreen mask without complex keying

### Example 4: Multiple Mask Operations

```
[Load Image]
    ↓
[Draw Mask 1] (main subject)
    ↓
[Mask Smoother]
  - smooth_iterations: 2
  - feather: 2.0
    ↓        ↓
    │    [Draw Mask 2] (detail area)
    │        ↓
    │    [Mask Smoother]
    │      - smooth_iterations: 3
    │      - feather: 1.0
    │        ↓
    └────[Combine Masks] (multiply/max/etc)
            ↓
        [Final composite]
```

**Result:** Complex multi-layer masking with professional edges

---

## Comparison with Traditional Compositing Software

### Nuke Workflow:
```
Roto node → Draw splines → FilterErode/Dilate → Blur → Use mask
```

### ComfyUI Detonate Workflow:
```
Native MaskEditor → Mask Smoother → Use mask
(Simpler, faster, same quality!)
```

### Advantages of This Approach:

✅ **No complex widget issues** - Uses ComfyUI's proven mask tools
✅ **Professional edge quality** - Better than simple blur
✅ **Fast iteration** - Adjust parameters in real-time
✅ **Works with any mask source** - AI, manual, generated
✅ **Familiar workflow** - Similar to Nuke's post-roto refinement
✅ **Batch compatible** - Process multiple masks

### Why This is Better Than Interactive Roto:

1. **ComfyUI's mask editor already works** - Don't reinvent the wheel
2. **AI segmentation is often faster** - SAM, etc. are very good
3. **Focus on refinement** - Where Detonate adds the most value
4. **More flexible** - Accepts masks from anywhere
5. **Easier to maintain** - No complex JavaScript widgets

---

## Tips & Best Practices

### Smoothing Tips:

- **Start with fewer iterations** - You can always add more
- **2-3 iterations** is usually perfect for hand-drawn masks
- **1 iteration** for AI masks (they're already smooth)
- **5+ iterations** for very rough sketches or pixel-art style

### Feathering Tips:

- **Feather size depends on resolution:**
  - 1080p: 2-5 pixels typical
  - 4K: 4-10 pixels typical
  - 8K: 8-20 pixels typical

- **Feather type guidelines:**
  - **Smooth** - Best for most organic subjects (people, animals, plants)
  - **Linear** - Good for hard surfaces, geometric shapes
  - **Gaussian** - Very soft, good for atmospheric effects, glows

### Edge Adjust Tips:

- **Contract by 0.5-1px** before feathering to avoid edge spill
- **Expand if mask is too tight** on subject
- **Use with caution** - Can distort fine detail

### Anti-Aliasing Tips:

- **Medium (4x)** is the sweet spot for most work
- **High (8x)** for final delivery, fine detail
- **Low (2x)** for iterative work, draft comps
- **Off** only if you want pixel-perfect hard edges

---

## Troubleshooting

### Issue: Mask edges still look jagged
**Solution:**
- Increase `smooth_iterations` to 3-5
- Set `antialias_quality` to High
- Add small `feather` (1-2 pixels)

### Issue: Mask lost fine detail
**Solution:**
- Reduce `smooth_iterations` to 1-2
- Reduce `feather` amount
- Check if you over-contracted with `edge_adjust`

### Issue: Edge spill in composite
**Solution:**
- Contract mask with `edge_adjust: -0.5` to `-1.0`
- Use edge defringe tools after composite
- Consider premultiplying after masking

### Issue: Mask too soft
**Solution:**
- Reduce `feather` amount
- Change `feather_type` from Gaussian to Linear
- Increase contrast of source mask before smoothing

---

## Advanced Techniques

### Creating Garbage Mattes

```
[Rough polygon mask] → [Mask Smoother]
  - smooth_iterations: 5 (very smooth for garbage matte)
  - feather: 10-20 (soft edge to hide boundaries)
  - feather_type: Gaussian
```

### Hair/Fur Masking

```
[AI segmentation mask] → [Mask Smoother]
  - smooth_iterations: 0 (preserve detail!)
  - edge_adjust: 0
  - feather: 0.5-1.0 (very subtle)
  - antialias_quality: High
```

### Hard Surface Masking

```
[Drawn mask] → [Mask Smoother]
  - smooth_iterations: 1-2
  - feather: 1-2
  - feather_type: Linear (maintains harder edge)
  - antialias_quality: Medium
```

---

## Future Enhancements

Planned improvements to the masking workflow:

- **Mask Combine** node (add, subtract, intersect multiple masks)
- **Mask Tracker** (track masks over time for video)
- **Smart Edge Detect** (find edges in image, snap mask to them)
- **Mask Deform** (warp masks with grids/curves)

---

## Conclusion

By combining ComfyUI's native mask drawing with Detonate's professional refinement tools, you get:

- **Best of both worlds** - Easy drawing + professional quality
- **Faster workflow** - No complex setup needed
- **Better results** - Professional edge quality every time
- **More flexible** - Works with any mask source

**The RotoBezier node remains available for JSON-based spline work**, but for most users, the **Mask Smoother workflow is simpler, faster, and more practical**.
