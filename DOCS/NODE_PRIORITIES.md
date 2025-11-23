# ComfyUI_Detonate - Node Implementation Priority List

This document outlines the priority order for implementing nodes based on professional compositor workflows and daily usage patterns.

---

## Priority Tier 1: Essential Daily Tools (Must Have)

These nodes are used in virtually every compositing session and form the foundation of all workflows.

### 1. Merge (Compositing)
**Nuke:** Merge | **Fusion:** Merge
- **Operations:** Over, Under, Plus, Screen, Multiply, Stencil, Mask, Atop
- **Importance:** Core of all compositing work
- **Complexity:** Medium (alpha math, multiple blend modes)

### 2. Transform
**Nuke:** Transform | **Fusion:** Transform
- **Features:** Translate, Rotate, Scale, Skew, Motion Blur
- **Importance:** Every shot needs positioning/scaling
- **Complexity:** Medium (2D transforms, motion blur optional first pass)

### 3. Blur
**Nuke:** Blur | **Fusion:** Blur
- **Features:** Gaussian blur with X/Y separation, quality controls
- **Importance:** Used constantly for softening, glows, depth
- **Complexity:** Low (standard Gaussian implementation)

### 4. Grade
**Nuke:** Grade | **Fusion:** ColorCorrector
- **Features:** Lift/Gamma/Gain for Master + RGB channels
- **Importance:** Primary color correction tool
- **Complexity:** Medium (proper color math with shadows/mids/highlights)

### 5. Premultiply / Unpremultiply
**Nuke:** Premult/Unpremult | **Fusion:** (built into Merge)
- **Features:** Multiply/divide RGB by alpha
- **Importance:** Critical for proper alpha handling
- **Complexity:** Low (simple math operation)

### 6. Shuffle
**Nuke:** Shuffle/Shuffle2 | **Fusion:** ChannelBooleans
- **Features:** Reorder channels, copy between layers
- **Importance:** Constant channel manipulation needs
- **Complexity:** Medium (channel routing logic)

### 7. ColorCorrect
**Nuke:** ColorCorrect | **Fusion:** ColorCorrector (basic mode)
- **Features:** Saturation, Contrast, Gamma, Gain, Offset
- **Importance:** Quick color adjustments
- **Complexity:** Low (basic color math)

### 8. Erode / Dilate
**Nuke:** Erode/Dilate | **Fusion:** ErodeDilate
- **Features:** Matte expansion/contraction
- **Importance:** Essential for matte cleanup
- **Complexity:** Low (morphological operations)

---

## Priority Tier 2: High-Frequency Professional Tools

Used in most professional compositing shots, especially for keying and effects work.

### 9. ChromaKeyer (Basic)
**Nuke:** Keyer | **Fusion:** ChromaKeyer
- **Features:** Green/blue screen keying with spill suppression
- **Importance:** Greenscreen work is extremely common
- **Complexity:** High (color space keying, spill removal)

### 10. LumaKeyer
**Nuke:** Keyer (luma mode) | **Fusion:** LumaKeyer
- **Features:** Luminance-based key generation
- **Importance:** Quick matte creation from brightness
- **Complexity:** Low (threshold-based)

### 11. MatteControl
**Nuke:** (FilterErode + Blur combination) | **Fusion:** MatteControl
- **Features:** Contract, Expand, Blur, Gamma for mattes
- **Importance:** All-in-one matte refinement
- **Complexity:** Medium (combines multiple operations)

### 12. Clamp
**Nuke:** Clamp | **Fusion:** (in ColorCorrector)
- **Features:** Constrain values to min/max range
- **Importance:** Prevent out-of-range values
- **Complexity:** Low (simple clamping)

### 13. Saturation
**Nuke:** Saturation | **Fusion:** ColorCorrector (saturation)
- **Features:** Direct saturation control
- **Importance:** Frequent color adjustment
- **Complexity:** Low (HSV conversion and adjustment)

### 14. Invert
**Nuke:** Invert | **Fusion:** Channel Booleans (invert)
- **Features:** Invert color/channel values
- **Importance:** Quick matte/color inversion
- **Complexity:** Low (1 - value)

### 15. Copy / ChannelCopy
**Nuke:** Copy/ShuffleCopy | **Fusion:** ChannelBooleans
- **Features:** Copy channels between streams
- **Importance:** Channel management in complex comps
- **Complexity:** Medium (multi-stream channel operations)

---

## Priority Tier 3: Regular Use Tools

Important tools used frequently but not in every shot.

### 16. CornerPin
**Nuke:** CornerPin2D | **Fusion:** CornerPositioner
- **Features:** 4-point perspective mapping
- **Importance:** Screen replacements, tracking integration
- **Complexity:** High (perspective transform math)

### 17. Defocus
**Nuke:** Defocus/ZDefocus | **Fusion:** Defocus
- **Features:** Lens-style defocus blur
- **Importance:** Realistic depth of field effects
- **Complexity:** High (bokeh simulation)

### 18. DirectionalBlur
**Nuke:** DirectionalBlur | **Fusion:** DirectionalBlur
- **Features:** Motion-style blur in specified direction
- **Importance:** Motion effects, speed lines
- **Complexity:** Low (directional sampling)

### 19. Sharpen
**Nuke:** Sharpen | **Fusion:** Sharpen
- **Features:** Image sharpening
- **Importance:** Detail enhancement
- **Complexity:** Low (unsharp mask variant)

### 20. HueCorrect / ColorCurves
**Nuke:** HueCorrect | **Fusion:** ColorCurves
- **Features:** Hue-based saturation/color adjustment
- **Importance:** Selective color correction
- **Complexity:** High (hue-based curves)

### 21. Glow
**Nuke:** Glow | **Fusion:** Glow
- **Features:** Highlight blooming effects
- **Importance:** Common VFX element
- **Complexity:** Medium (threshold + blur + composite)

### 22. DifferenceKeyer
**Nuke:** Difference | **Fusion:** DeltaKeyer (difference mode)
- **Features:** Difference matte generation
- **Importance:** Clean plate differencing
- **Complexity:** Low (image subtraction)

### 23. Constant / Background
**Nuke:** Constant | **Fusion:** Background
- **Features:** Solid color/gradient generation
- **Importance:** Creating mattes, backgrounds
- **Complexity:** Low (color fill)

### 24. EdgeDetect
**Nuke:** EdgeDetect | **Fusion:** Filter (Sobel/Laplacian)
- **Features:** Edge extraction
- **Importance:** Matte creation, effects
- **Complexity:** Low (edge detection filters)

---

## Priority Tier 4: Specialized Tools

Used in specific workflows or advanced compositing tasks.

### 25. FrameHold
**Nuke:** FrameHold | **Fusion:** TimeStretcher (hold)
- **Features:** Hold single frame
- **Importance:** Freeze frames in sequences
- **Complexity:** Low (frame caching)

### 26. TimeOffset
**Nuke:** TimeClip | **Fusion:** TimeStretcher
- **Features:** Time offset/loop
- **Importance:** Sequence timing adjustments
- **Complexity:** Low (frame index offset)

### 27. VectorBlur
**Nuke:** VectorBlur | **Fusion:** VectorMotionBlur
- **Features:** Motion blur from vector/motion channels
- **Importance:** Realistic motion blur from 3D renders
- **Complexity:** High (vector-based sampling)

### 28. GridWarp
**Nuke:** GridWarp | **Fusion:** GridWarp
- **Features:** Manual grid-based warping
- **Importance:** Custom distortions, warping effects
- **Complexity:** High (mesh deformation)

### 29. LensDistortion
**Nuke:** LensDistortion | **Fusion:** LensDistort
- **Features:** Add/remove lens distortion
- **Importance:** Camera matching, undistortion
- **Complexity:** High (lens model math)

### 30. IDistort / Displace
**Nuke:** IDistort | **Fusion:** Displace
- **Features:** Displace pixels using displacement map
- **Importance:** Refraction, heat distortion effects
- **Complexity:** High (displacement mapping)

### 31. Median
**Nuke:** Median | **Fusion:** Median (via Filter)
- **Features:** Noise reduction filter
- **Importance:** Despeckle, noise reduction
- **Complexity:** Low (median filtering)

### 32. Remove Channels
**Nuke:** Remove | **Fusion:** ChannelBooleans (remove)
- **Features:** Remove unwanted channels
- **Importance:** Clean up channel bloat
- **Complexity:** Low (channel removal)

### 33. Ramp / Gradient
**Nuke:** Ramp/Radial | **Fusion:** Background (gradient)
- **Features:** Linear and radial gradients
- **Importance:** Gradient generation for effects
- **Complexity:** Low (gradient math)

### 34. Noise
**Nuke:** Noise | **Fusion:** FastNoise
- **Features:** Procedural noise generation
- **Importance:** Grain, texture generation
- **Complexity:** Low (Perlin/simplex noise)

### 35. Text
**Nuke:** Text/Text2 | **Fusion:** Text+
- **Features:** Text generation
- **Importance:** Slates, labels, graphics
- **Complexity:** Medium (font rendering)

---

## Priority Tier 5: Advanced/Specialized (Future Phases)

Professional tools for specific advanced workflows.

### 36. Stabilize
**Nuke:** Stabilize2D | **Fusion:** Tracker (stabilize)
- **Requires:** Tracking implementation first
- **Complexity:** High

### 37. Tracker (2D Point)
**Nuke:** Tracker | **Fusion:** Tracker
- **Complexity:** Very High (tracking algorithm)

### 38. PlanarTracker
**Nuke:** PlanarTracker | **Fusion:** PlanarTracker
- **Complexity:** Very High (planar tracking)

### 39. SplineWarp
**Nuke:** SplineWarp | **Fusion:** (GridWarp variant)
- **Complexity:** High (spline-based deformation)

### 40. Kronos / OpticalFlow
**Nuke:** Kronos | **Fusion:** OpticalFlow
- **Features:** Frame interpolation via optical flow
- **Complexity:** Very High (optical flow algorithm)

### 41. 3D Nodes (Camera, Lights, Scene, Card)
**Nuke:** Camera2, Light, Scene, Card | **Fusion:** Camera3D, Lights, Merge3D, ImagePlane3D
- **Complexity:** High (3D rendering integration)

### 42. ScanlineRender / Renderer3D
**Nuke:** ScanlineRender | **Fusion:** Renderer3D
- **Complexity:** Very High (3D rendering)

### 43. Advanced Keyers (Primatte, IBK)
**Nuke:** Primatte, IBK, Keylight | **Fusion:** Primatte, UltraKeyer
- **Complexity:** Very High (professional keying algorithms)

---

## Implementation Strategy

### Phase 1 Focus: Tier 1 (Nodes 1-8)
Delivers a functional compositing toolkit suitable for basic professional work.
**Target:** 2-3 weeks

### Phase 2 Focus: Tier 2 (Nodes 9-15)
Adds professional keying and color tools.
**Target:** 2-3 weeks

### Phase 3 Focus: Tier 3 (Nodes 16-24)
Expands to advanced effects and transforms.
**Target:** 3-4 weeks

### Phase 4 Focus: Tier 4 (Nodes 25-35)
Covers specialized workflows.
**Target:** 3-4 weeks

### Phase 5+: Tier 5 (Nodes 36-43)
Advanced professional features (long-term roadmap).
**Target:** Future releases

---

## Node Complexity Reference

**Low Complexity:** 1-3 days implementation
- Direct mathematical operations
- Simple filters
- Basic channel operations

**Medium Complexity:** 3-7 days implementation
- Multiple parameters and modes
- Compound operations
- Color space conversions

**High Complexity:** 1-2 weeks implementation
- Complex algorithms
- Multiple interdependent features
- Optimization required

**Very High Complexity:** 2+ weeks implementation
- Advanced algorithms (tracking, optical flow)
- 3D rendering integration
- Patent/proprietary algorithm alternatives needed

---

## Success Criteria by Tier

**Tier 1 Complete:** Can composite basic greenscreen shot with color correction
**Tier 2 Complete:** Professional-quality keying and matte workflows
**Tier 3 Complete:** Advanced effects and transforms available
**Tier 4 Complete:** Specialized workflows covered
**Tier 5 Complete:** Feature parity with commercial compositors
