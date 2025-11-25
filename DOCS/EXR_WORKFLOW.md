# EXR Workflow in ComfyUI_Detonate

This guide covers loading and working with multi-channel EXR files in ComfyUI_Detonate, including Cryptomatte extraction.

---

## Quick Start

### Step 1: Add EXR Files to ComfyUI

Place your EXR files in ComfyUI's input directory:

```
ComfyUI/
└── input/
    ├── beauty.exr
    ├── renders/
    │   ├── shot_01.exr
    │   └── shot_02.exr
    └── cryptomatte/
        └── cg_render.exr
```

**Important:** Files must be in the `ComfyUI/input/` directory or its subdirectories to appear in the file selector.

### Step 2: Load EXR in Workflow

Add **"Load EXR (Detonate)"** node to your workflow:

1. Node appears with dropdown showing all EXR files in input directory
2. Select your EXR file from dropdown
3. Specify layer name (e.g., "RGBA", "diffuse", "specular")
4. Enable "list_layers" to print available layers to console

### Step 3: Use Loaded EXR

Connect the IMAGE output to:
- Cryptomatte Extract node
- Color correction nodes (Grade, ColorCorrect)
- Merge nodes for compositing
- Any other image processing nodes

---

## Load EXR Node

### Overview

Loads multi-channel/multi-layer EXR files from CG renders with support for specific AOV (Arbitrary Output Variable) passes.

**Category:** `detonate/io`

### Inputs

**Required:**
- `exr_file` (COMBO) - Select EXR file from dropdown
  - Shows all .exr files in ComfyUI/input/ directory
  - Includes subdirectories (e.g., "renders/shot_01.exr")
  - Files are auto-discovered when ComfyUI starts

- `layer` (STRING) - Layer/pass name to load
  - Default: "RGBA"
  - Examples: "RGB", "diffuse", "specular.RGB", "Z"
  - For multi-layer EXRs, use "layer.channel" format

**Optional:**
- `list_layers` (BOOLEAN) - Print available layers to console
  - Default: False
  - Useful for exploring EXR file contents

### Outputs

- `image` (IMAGE) - Loaded image data [B,H,W,C]
  - Always includes alpha channel (adds opaque alpha if missing)
  - Supports full HDR float range (values NOT clamped to 0-1)
  - Preserves float precision for CG workflows

### Layer Naming Conventions

**Simple layers:**
- `"RGBA"` - Default beauty pass with alpha
- `"RGB"` - Beauty pass without alpha
- `"R"`, `"G"`, `"B"`, `"A"` - Individual channels

**Multi-layer EXR format:**
- `"diffuse"` - Expands to diffuse.R, diffuse.G, diffuse.B, diffuse.A
- `"specular.RGB"` - Specular pass RGB channels
- `"reflection.RGBA"` - Reflection pass with alpha
- `"Z"` - Depth pass (single channel)

**Common CG passes:**
- Beauty/RGBA - Final rendered image
- Diffuse - Diffuse lighting contribution
- Specular - Specular highlights
- Reflection - Reflections
- Refraction - Refractions
- GI - Global illumination
- Emission - Emissive surfaces
- Shadow - Shadow pass
- Z - Depth information

### Tips

1. **Discovering layers:** Enable `list_layers` to see what's in your EXR:
   ```
   Available channels/layers:
     - R
     - G
     - B
     - A
     - diffuse.R
     - diffuse.G
     - diffuse.B
     - specular.R
     - specular.G
     - specular.B
     - Z
   ```

2. **HDR workflows:** EXR values are NOT clamped - supports values > 1.0 for HDR
   - Use Grade node to bring values into display range
   - Or use Clamp node if needed

3. **File organization:** Use subdirectories in input/ for better organization:
   ```
   input/
   ├── project_a/
   │   └── render.exr
   └── project_b/
       └── render.exr
   ```

4. **Refresh file list:** Restart ComfyUI to refresh the EXR file dropdown

---

## Cryptomatte Extract Node

### Overview

Extract object/material ID mattes from Cryptomatte EXR files. Cryptomatte is an industry-standard system for generating ID mattes from CG renders with support for motion blur, transparency, and depth of field.

**Category:** `detonate/cryptomatte`

### Inputs

**Required:**
- `exr_file` (COMBO) - Select Cryptomatte EXR from dropdown
  - Shows all .exr files in ComfyUI/input/ directory
  - Must be EXR with Cryptomatte layers

- `cryptomatte_layer` (COMBO) - Which Cryptomatte layer to use
  - **CryptoObject** - Object names (most common)
  - **CryptoMaterial** - Material/shader names
  - **CryptoAsset** - Asset/collection names

- `matte_list` (STRING, multiline) - Objects to extract
  - Comma-separated list of object/material names
  - Example: `"sphere_001, cube_002, ground_plane"`
  - Names must match exactly (case-sensitive)

**Optional:**
- `list_objects` (BOOLEAN) - Print available objects
  - Default: False
  - Shows all object names in the Cryptomatte manifest
  - Use this to discover what objects are available

### Outputs

- `matte` (IMAGE) - Extracted matte [B,H,W,C]
  - Coverage values (0-1) in RGB channels
  - Alpha = 1.0 (opaque)
  - Properly anti-aliased edges
  - Supports partial coverage (motion blur, transparency)

### Cryptomatte Layer Types

**CryptoObject (Most Common):**
- Extracts by object/mesh name
- Use for isolating specific props, characters, environment elements
- Example: `"hero_character, hero_sword, hero_cape"`

**CryptoMaterial:**
- Extracts by material/shader name
- Use for selecting all surfaces with same material
- Example: `"chrome_metal, car_paint, glass"`

**CryptoAsset:**
- Extracts by asset/collection hierarchy
- Use for selecting entire asset groups
- Example: `"vehicles, buildings, vegetation"`

### Workflow Example

```
[Load EXR] (Load your Cryptomatte EXR)
    ↓
[Cryptomatte Extract]
  - exr_file: same as Load EXR
  - cryptomatte_layer: CryptoObject
  - matte_list: "hero, hero_cape, hero_sword"
  - list_objects: True (first time, to see what's available)
    ↓
[Mask Smoother] (optional - refine edges)
    ↓
[Use matte in composite]
```

### Tips

1. **Finding object names:**
   - Enable `list_objects` on first run
   - Check console output for available names
   - Copy exact names (case-sensitive!)

2. **Multiple objects:**
   - Separate names with commas
   - Spaces are ignored: `"obj1, obj2"` and `"obj1,obj2"` are the same
   - Coverage values are accumulated (obj1 + obj2 = combined matte)

3. **Refining mattes:**
   - Cryptomatte mattes have proper anti-aliasing
   - Use **Mask Smoother** for additional edge refinement if needed
   - Use **MatteControl** for edge operations (grow/shrink/blur)

4. **Empty mattes:**
   - If object name not found, warning printed to console
   - Returns black matte (all zeros)
   - Check spelling and case sensitivity

5. **Working with Load EXR:**
   - Both nodes use the same file selector
   - You can use same EXR in both nodes
   - Cryptomatte reads metadata directly from file

---

## Complete Workflow Examples

### Example 1: Simple CG Composite

```
[Load EXR: beauty.exr, layer: "RGBA"]
    ↓
[Grade] (color correct the beauty pass)
    ↓
[Load EXR: beauty.exr, layer: "Z"] ──→ [ZDefocus] (depth of field)
    ↓
[Merge with background]
```

### Example 2: Cryptomatte Isolation

```
[Load Image: background.png]
    ↓
[Cryptomatte Extract]
  - exr_file: "cg_render.exr"
  - cryptomatte_layer: CryptoObject
  - matte_list: "hero_character"
  - list_objects: True
    ↓
[Mask Smoother]
  - smooth_iterations: 2
  - feather: 2.0
    ↓
[Merge] ← [Load EXR: "cg_render.exr", layer: "RGBA"]
  - operation: Over
  - mask: (from Mask Smoother)
    ↓
[Output]
```

### Example 3: Multi-Pass Compositing

```
[Load EXR: "render.exr", layer: "diffuse"] ──→ [Grade] (adjust diffuse)
                                                    ↓
[Load EXR: "render.exr", layer: "specular"] ──→ [Merge: Plus]
                                                    ↓
[Load EXR: "render.exr", layer: "reflection"] ─→ [Merge: Screen]
                                                    ↓
[Load EXR: "render.exr", layer: "Z"] ──────────→ [ZDefocus]
                                                    ↓
                                                [Merge with BG]
```

### Example 4: Selective Color Correction

```
[Load EXR: "render.exr", layer: "RGBA"]
    ↓
    ├─→ [Grade] (correct overall)
    │       ↓
    │   [Merge: Over]
    │       ↑
    └─→ [Cryptomatte Extract: "car_body"]
            ↓
        [Mask Smoother]
            ↓
        [Grade] (adjust car color only)
            ↓
        (merge mask controls where adjustment applies)
```

---

## Technical Notes

### File Discovery

- EXR files are auto-discovered from `ComfyUI/input/` at startup
- Subdirectories are scanned recursively
- Files displayed as relative paths (e.g., "shots/shot01/render.exr")
- To refresh list: restart ComfyUI

### Path Resolution

Both nodes use shared path utilities:
- Input: Relative path from dropdown (e.g., "render.exr")
- Resolution: Absolute path to `ComfyUI/input/render.exr`
- Errors: Clear messages if file not found or placeholder selected

### Multi-Channel Support

EXR files can contain:
- Standard RGBA channels
- Named layers with channels (e.g., "diffuse.R")
- Arbitrary channel names
- Cryptomatte ID/coverage pairs

The Load EXR node intelligently handles all formats and provides fallbacks if requested layer not found.

### Cryptomatte Format

Cryptomatte encodes ID/coverage pairs in RGBA:
- R,G = ID1, coverage1
- B,A = ID2, coverage2

Multiple layers (CryptoObject00, CryptoObject01, etc.) handle more than 2 samples per pixel, supporting:
- Motion blur (multiple positions per pixel)
- Transparency (multiple objects per pixel)
- Depth of field (multiple focus layers)

The Cryptomatte Extract node automatically reads all layers and accumulates coverage correctly.

---

## Troubleshooting

### "No EXR files in input folder"

**Problem:** Dropdown shows placeholder text, nodes fail when executed

**Solution:**
1. Add EXR files to `ComfyUI/input/` directory
2. Restart ComfyUI to refresh file list
3. Verify files have `.exr` extension (case-insensitive)

### "EXR file not found"

**Problem:** Selected file doesn't exist at runtime

**Solution:**
1. Don't move/delete files after adding to workflow
2. Keep files in input directory
3. Check file wasn't renamed

### "Layer 'xyz' not found"

**Problem:** Requested layer doesn't exist in EXR

**Solution:**
1. Enable `list_layers: True` to see available layers
2. Check spelling and case (layer names are case-sensitive)
3. For multi-layer EXR, use "layer.channel" format

### "Object 'xyz' not found in manifest"

**Problem:** Cryptomatte object name doesn't match

**Solution:**
1. Enable `list_objects: True` to see available names
2. Copy exact names from console output (case-sensitive!)
3. Check that EXR actually contains Cryptomatte data

### Dropdown doesn't update after adding files

**Problem:** New EXR files don't appear in dropdown

**Solution:**
1. Restart ComfyUI completely
2. File discovery happens at startup, not dynamically
3. Or use ComfyUI's "Refresh" button if available in your version

---

## Performance Tips

1. **Large EXR files:**
   - EXR loading is I/O bound
   - Use fast storage (SSD recommended)
   - Consider downscaling if working on draft comps

2. **Many layers:**
   - Only requested layers are loaded
   - No performance penalty for multi-layer EXR with many passes
   - Load EXR is efficient with layer selection

3. **Cryptomatte:**
   - Manifest parsing is one-time cost
   - Multiple Cryptomatte Extract nodes on same file are efficient
   - Coverage extraction is fast (vectorized NumPy operations)

4. **Batch processing:**
   - Both nodes support batch dimension
   - Can process multiple EXR files in sequence
   - Use ComfyUI's batch features for automated workflows

---

## Future Enhancements

Planned improvements:

- **Dynamic file refresh** - Update dropdown without restart
- **Preview thumbnails** - Show EXR preview in file selector
- **Layer selector** - Dropdown for layer selection (instead of text input)
- **Cryptomatte picker** - Interactive object selection from image
- **EXR info node** - Display metadata (resolution, channels, colorspace)

---

## Related Nodes

**Color Correction:**
- [Grade](../nodes/color/grade.md) - Lift/gamma/gain color correction
- [ColorCorrect](../nodes/color/color_correct.md) - Quick adjustments

**Masking:**
- [Mask Smoother](../nodes/matte/mask_smoother.md) - Refine mask edges
- [MatteControl](../nodes/matte/matte_control.md) - Matte operations

**Compositing:**
- [Merge](../nodes/compositing/merge.md) - Alpha compositing with blend modes
- [ZDefocus](../nodes/filter/zdefocus.md) - Depth-based defocus

---

**Last Updated:** 2025-01-24
**Status:** File selector workflow implemented and ready for use
