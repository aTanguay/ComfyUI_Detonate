# RotoBezier Node - Usage Guide

## Current Status

The RotoBezier node is currently **functional but requires manual JSON editing** for custom shapes. The interactive drawing widget is not yet compatible with ComfyUI's rendering system.

## How to Use RotoBezier (Current Method)

###  1. Using the Default (Empty Mask)

If you don't provide spline data, the node will output an empty (black) mask.

### 2. Creating Simple Shapes via Buttons

The node has buttons to create preset shapes:
- **Start Drawing** - Begins a new spline (currently non-functional in UI)
- **Clear All** - Removes all splines
- **Add Circle** - Adds a circle shape
- **Add Rectangle** - Adds a rectangle shape
- **Add Star** - Adds a 5-pointed star

**Note:** These buttons create shapes in canvas coordinates (300x300), so you'll need to scale them appropriately.

### 3. Manual JSON Editing (Advanced)

You can manually create custom splines by editing the `spline_data` JSON string.

**JSON Format:**
```json
{
  "splines": [
    {
      "points": [
        {
          "x": 100,
          "y": 100,
          "handleIn": {"x": 0, "y": 0},
          "handleOut": {"x": 0, "y": 0},
          "smooth": true
        },
        {
          "x": 200,
          "y": 100,
          "handleIn": {"x": 0, "y": 0},
          "handleOut": {"x": 0, "y": 0},
          "smooth": true
        }
      ],
      "closed": true,
      "feather": 2.0,
      "operation": "add",
      "invert": false
    }
  ]
}
```

**Point Structure:**
- `x`, `y`: Point coordinates (pixels from top-left)
- `handleIn`: Left tangent handle offset (for Bezier curves)
- `handleOut`: Right tangent handle offset (for Bezier curves)
- `smooth`: Auto-align handles for smooth curves

**Spline Properties:**
- `closed`: Whether to close the shape (true for filled shapes)
- `feather`: Per-spline feather amount (currently uses global feather instead)
- `operation`: Shape operation - `"add"`, `"subtract"`, or `"intersect"`
- `invert`: Invert this spline's mask

### 4. Example: Simple Triangle

```json
{
  "splines": [
    {
      "points": [
        {"x": 960, "y": 200, "handleIn": {"x": 0, "y": 0}, "handleOut": {"x": 0, "y": 0}, "smooth": false},
        {"x": 1400, "y": 880, "handleIn": {"x": 0, "y": 0}, "handleOut": {"x": 0, "y": 0}, "smooth": false},
        {"x": 520, "y": 880, "handleIn": {"x": 0, "y": 0}, "handleOut": {"x": 0, "y": 0}, "smooth": false}
      ],
      "closed": true,
      "operation": "add",
      "invert": false
    }
  ]
}
```

This creates a triangle centered at (960, 540) for a 1920x1080 image.

### 5. Example: Circle with Subtract

```json
{
  "splines": [
    {
      "points": [
        {"x": 960, "y": 40, "handleIn": {"x": -331, "y": 0}, "handleOut": {"x": 331, "y": 0}, "smooth": true},
        {"x": 1460, "y": 540, "handleIn": {"x": 0, "y": -276}, "handleOut": {"x": 0, "y": 276}, "smooth": true},
        {"x": 960, "y": 1040, "handleIn": {"x": 331, "y": 0}, "handleOut": {"x": -331, "y": 0}, "smooth": true},
        {"x": 460, "y": 540, "handleIn": {"x": 0, "y": 276}, "handleOut": {"x": 0, "y": -276}, "smooth": true}
      ],
      "closed": true,
      "operation": "add",
      "invert": false
    },
    {
      "points": [
        {"x": 960, "y": 290, "handleIn": {"x": -165, "y": 0}, "handleOut": {"x": 165, "y": 0}, "smooth": true},
        {"x": 1210, "y": 540, "handleIn": {"x": 0, "y": -138}, "handleOut": {"x": 0, "y": 138}, "smooth": true},
        {"x": 960, "y": 790, "handleIn": {"x": 165, "y": 0}, "handleOut": {"x": -165, "y": 0}, "smooth": true},
        {"x": 710, "y": 540, "handleIn": {"x": 0, "y": 138}, "handleOut": {"x": 0, "y": -138}, "smooth": true}
      ],
      "closed": true,
      "operation": "subtract",
      "invert": false
    }
  ]
}
```

This creates a ring (circle with inner circle subtracted).

## Workaround: Using Constant + Crop

For simple shapes, you may find it easier to use:
1. **Constant (Detonate)** - Create a solid color
2. **Native ComfyUI mask drawing** - Draw masks directly
3. **MatteControl (Detonate)** - Feather and refine edges

## Future Improvements

The RotoBezier node is being redesigned to work better with ComfyUI:

**Planned Options:**
1. **External Web Tool** - Separate webpage for drawing splines, exports JSON
2. **Integration with ComfyUI Mask Editor** - Use native mask tools as input
3. **Simplified Preset Library** - More preset shapes with better parameters

**Why the current interactive widget doesn't work:**
- ComfyUI's node rendering system doesn't support custom canvas widgets well
- Absolute positioning conflicts with ComfyUI's dynamic layout
- ComfyUI widgets need to integrate with the LiteGraph rendering pipeline

## Recommendations

**For Production Work:**
1. Use **RotoBezier From Image** variant - automatically matches image resolution
2. Start with preset shapes (Circle/Rectangle/Star buttons)
3. Adjust feather and feather_type for desired edge quality
4. For custom shapes, consider using:
   - External vector drawing tools (export coordinates)
   - Python scripts to generate spline JSON
   - ComfyUI's native mask drawing + MatteControl for feathering

**Simpler Alternative:**
- Use native ComfyUI mask nodes
- Apply **MatteControl (Detonate)** for professional edge control
- Use **Blur (Detonate)** for softening

---

## Technical Note

The RotoBezier backend is fully functional and produces high-quality anti-aliased masks with proper feathering. The limitation is purely in the interactive editing interface, which requires deeper integration with ComfyUI's widget system than currently implemented.

For batch/automated workflows (e.g., generating consistent shapes), the JSON approach is actually quite powerful and scriptable.
