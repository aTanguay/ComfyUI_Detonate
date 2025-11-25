# RotoBezier Node - Deprecated

## Status: EXPERIMENTAL / LOW PRIORITY

The RotoBezier node is currently **not recommended for production use** due to fundamental limitations with ComfyUI's widget system.

---

## Why RotoBezier Isn't Practical

### The Problem:
- **Interactive drawing widget doesn't work** - ComfyUI's LiteGraph system doesn't support the complex canvas-based widget needed for interactive spline drawing
- **JSON editing is impractical** - Manually writing Bezier curve coordinates defeats the purpose of a drawing tool
- **Better alternatives exist** - ComfyUI's native mask tools work well and can be refined with Detonate's professional nodes

### What Was Attempted:
1. Custom JavaScript canvas widget for interactive drawing
2. Absolute positioning for widget placement
3. JSON-based spline data storage

### Why It Failed:
- ComfyUI widgets must integrate with LiteGraph's rendering pipeline
- Absolute positioning conflicts with ComfyUI's dynamic layout
- No clean way to embed interactive canvas in node UI
- Would require deep modifications to ComfyUI core

---

## Recommended Alternatives

### For Interactive Masking:

**Option 1: Use ComfyUI's Native MaskEditor** ✅ RECOMMENDED
```
1. Load image in ComfyUI
2. Right-click → "Open in MaskEditor"
3. Draw mask with built-in tools
4. Use mask output in your workflow
```

**Why this is better:**
- Actually works (interactive drawing)
- Integrated with ComfyUI
- No complex setup needed
- Familiar interface

### For Professional Edge Quality:

**Option 2: Native Mask + Detonate Refinement** ✅ BEST WORKFLOW
```
[ComfyUI MaskEditor]
    ↓
[Mask Smoother (Detonate)] ← Use this for professional edges!
    ↓
[Your composite]
```

**Settings for professional quality:**
- `smooth_iterations`: 2-3 (removes hand-drawn jaggies)
- `feather`: 2-5 pixels (soft edge)
- `feather_type`: Smooth (natural falloff)
- `antialias_quality`: Medium or High

**Why this workflow is better:**
- You get interactive drawing (MaskEditor works)
- You get professional edge quality (Mask Smoother)
- Fast iteration
- No complex JSON editing

### For AI-Based Masking:

**Option 3: SAM or Segmentation + Refinement** ✅ FASTEST
```
[Load Image]
    ↓
[SAM Segmentation / Other AI mask tool]
    ↓
[Mask Smoother (Detonate)] ← Refine AI mask edges
    ↓
[Use in composite]
```

**Why this is better:**
- AI segmentation is often faster than manual drawing
- Mask Smoother makes AI masks comp-ready
- No manual drawing needed for many cases

### For Color-Based Selection:

**Option 4: Mask From Color (Detonate)** ✅ QUICK & EASY
```
[Load Image]
    ↓
[Mask From Color (Detonate)]
  - color: "#00FF00" (greenscreen)
  - tolerance: 0.1-0.2
  - feather: 2.0
    ↓
[Optional: Mask Smoother for refinement]
    ↓
[Use in composite]
```

**Use cases:**
- Quick greenscreen selections
- Sky replacements (select blue)
- Simple object isolation

---

## If You Still Want to Use RotoBezier

### Current Limitations:
1. No interactive drawing interface
2. Must manually create JSON with spline coordinates
3. Only practical for programmatic/scripted workflows
4. Advanced users only

### JSON Format (For Reference):
```json
{
  "splines": [
    {
      "points": [
        {"x": 100, "y": 100, "handleIn": {"x": 0, "y": 0}, "handleOut": {"x": 0, "y": 0}},
        {"x": 200, "y": 100, "handleIn": {"x": 0, "y": 0}, "handleOut": {"x": 0, "y": 0}}
      ],
      "closed": true,
      "operation": "add"
    }
  ]
}
```

**When to use this approach:**
- Generating shapes programmatically
- Batch processing with scripted splines
- You enjoy writing JSON (no judgment!)

---

## What Detonate Provides Instead

**Focus on Professional Refinement, Not Drawing:**

Detonate's strength is in **professional-grade compositing operations**, not reinventing interactive drawing tools.

### Use Detonate For:
✅ **Mask Smoother** - Professional edge quality and feathering
✅ **Mask From Color** - Quick color-based selections
✅ **MatteControl** - Professional matte refinement
✅ **ChromaKeyer** - Professional greenscreen keying
✅ **Merge** - Proper alpha compositing with blend modes
✅ **Grade** - Professional color correction

### Use ComfyUI Native For:
✅ **MaskEditor** - Interactive mask drawing
✅ **Basic mask operations** - Grow, shrink, invert
✅ **Image loading** - File I/O

**The combination of ComfyUI's interactive tools + Detonate's professional refinement = Best workflow**

---

## Future Plans

### Not Planned:
- ❌ Complex interactive drawing widget
- ❌ Reinventing mask drawing tools
- ❌ Duplicating working ComfyUI features

### Might Consider:
- ⚠️ Simple shape presets (circle, rectangle, star) as utility
- ⚠️ External web-based spline editor (separate tool)
- ⚠️ Integration with vector file formats (SVG import)

**But honestly:** ComfyUI's MaskEditor + Detonate's refinement tools is probably the better long-term solution.

---

## Conclusion

**Don't use RotoBezier for now.**

**Instead:**
1. Draw masks with ComfyUI's MaskEditor (it works!)
2. Refine with Mask Smoother (Detonate) for professional quality
3. Use AI segmentation when appropriate
4. Use Mask From Color for quick selections

This workflow is:
- ✅ Easier
- ✅ Faster
- ✅ More reliable
- ✅ Better quality
- ✅ Actually works

---

**For questions or suggestions:** Open an issue on GitHub
**For alternative workflows:** See [MASKING_WORKFLOW.md](../../DOCS/MASKING_WORKFLOW.md)
