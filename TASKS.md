# ComfyUI_Detonate - Development Tasks

This is a working task list for tracking implementation progress. Check off items as they're completed.

---

## Phase 1: Foundation & Infrastructure

### Project Setup
- [ ] Initialize directory structure
  - [ ] Create `nodes/` directory
  - [ ] Create `nodes/compositing/` directory
  - [ ] Create `nodes/color/` directory
  - [ ] Create `nodes/keying/` directory
  - [ ] Create `nodes/transform/` directory
  - [ ] Create `nodes/filter/` directory
  - [ ] Create `nodes/matte/` directory
  - [ ] Create `nodes/channel/` directory
  - [ ] Create `nodes/time/` directory
  - [ ] Create `nodes/3d/` directory
  - [ ] Create `utils/` directory
  - [ ] Create `tests/` directory
  - [ ] Create `examples/` directory
  - [ ] Create `web/js/` directory

### Package Configuration
- [ ] Create `pyproject.toml` with project metadata
- [ ] Create `requirements.txt` with dependencies
- [ ] Create `README.md` with project overview
- [ ] Create `LICENSE` file
- [ ] Create `.gitignore` for Python/ComfyUI

### Core Infrastructure
- [ ] Implement `__init__.py` with node registration system
- [ ] Create `utils/tensor_utils.py`
  - [ ] Batch handling utilities
  - [ ] Type conversion functions
  - [ ] Tensor validation helpers
- [ ] Create `utils/image_processing.py`
  - [ ] Common image operations
  - [ ] Alpha channel handling
  - [ ] Image format conversions
- [ ] Create `utils/color_math.py`
  - [ ] RGB/HSV conversions
  - [ ] Premultiply/unpremultiply utilities
  - [ ] Color space conversion helpers

### Testing Setup
- [ ] Set up pytest configuration
- [ ] Create test utilities and fixtures
- [ ] Create sample test images
- [ ] Document testing procedures

### Documentation
- [ ] Create coding standards document
- [ ] Create contribution guidelines
- [ ] Document node development template

---

## Phase 2: Core Compositing Nodes (Priority 1)

### 1. Merge Node ✅
- [x] Implement base Merge node class
- [x] Add "Over" blend mode (A over B)
- [x] Add "Under" blend mode
- [x] Add "Plus" blend mode (additive)
- [x] Add "Screen" blend mode
- [x] Add "Multiply" blend mode
- [x] Add "Stencil" blend mode
- [x] Add "Mask" blend mode
- [x] Add "Atop" blend mode
- [x] Add mix/opacity control
- [x] Handle alpha channels correctly
- [ ] Add unit tests for Merge node
- [ ] Create example workflow

### 2. Transform Node
- [ ] Implement base Transform node class
- [ ] Add translate (X/Y position)
- [ ] Add rotate (degrees)
- [ ] Add scale (uniform and X/Y separate)
- [ ] Add center point control
- [ ] Add skew controls
- [ ] Add filter quality options (nearest, bilinear, bicubic)
- [ ] Add motion blur (optional for v1)
- [ ] Handle edge modes (black, clamp, repeat)
- [ ] Add unit tests for Transform node
- [ ] Create example workflow

### 3. Blur Node ✅
- [x] Implement base Blur node class
- [x] Add Gaussian blur algorithm
- [x] Add separate X/Y blur size controls
- [x] Add quality/iteration controls
- [x] Optimize for performance (GPU acceleration)
- [x] Handle alpha channels correctly
- [ ] Add unit tests for Blur node
- [ ] Create example workflow

### 4. Grade Node
- [ ] Implement base Grade node class
- [ ] Add Lift controls (Master + RGB)
- [ ] Add Gamma controls (Master + RGB)
- [ ] Add Gain controls (Master + RGB)
- [ ] Add Offset controls (Master + RGB)
- [ ] Implement proper color math (shadows/mids/highlights)
- [ ] Add black point/white point clamps
- [ ] Add reverse toggle
- [ ] Add unit tests for Grade node
- [ ] Create example workflow

### 5. Premultiply / Unpremultiply Nodes ✅
- [x] Implement Premultiply node
  - [x] Multiply RGB by alpha
  - [x] Handle edge cases (alpha = 0)
- [x] Implement Unpremultiply node
  - [x] Divide RGB by alpha
  - [x] Handle division by zero
  - [x] Add clipping options
- [ ] Add unit tests
- [ ] Create example workflow

---

## Phase 2: Core Compositing Nodes (Priority 2)

### 6. ColorCorrect Node
- [ ] Implement base ColorCorrect node class
- [ ] Add Saturation control
- [ ] Add Contrast control
- [ ] Add Gamma control
- [ ] Add Gain control
- [ ] Add Offset control
- [ ] Add unit tests for ColorCorrect node
- [ ] Create example workflow

### 7. Erode / Dilate Node
- [ ] Implement Erode node
  - [ ] Add size parameter
  - [ ] Implement morphological erosion
  - [ ] Optimize for performance
- [ ] Implement Dilate node
  - [ ] Add size parameter
  - [ ] Implement morphological dilation
  - [ ] Optimize for performance
- [ ] Add unit tests
- [ ] Create example workflow

### 8. Shuffle Node ✅
- [x] Implement base Shuffle node class
- [x] Add channel selection (R, G, B, A, 0, 1)
- [x] Add output channel mapping
- [x] Support multi-channel operations
- [x] Handle missing alpha channels
- [ ] Add unit tests for Shuffle node
- [ ] Create example workflow

### 9. Clamp Node
- [ ] Implement base Clamp node class
- [ ] Add minimum value control
- [ ] Add maximum value control
- [ ] Add per-channel clamping option
- [ ] Add unit tests for Clamp node
- [ ] Create example workflow

---

## Phase 3: Keying & Matte Operations

### 10. ChromaKeyer Node (Basic)
- [ ] Implement base ChromaKeyer node class
- [ ] Add key color picker
- [ ] Add acceptance (tolerance) control
- [ ] Add suppression angle control
- [ ] Implement basic chroma keying algorithm
- [ ] Add spill suppression
- [ ] Add edge softness/blur
- [ ] Add unit tests for ChromaKeyer node
- [ ] Create example workflow with green screen

### 11. LumaKeyer Node
- [ ] Implement base LumaKeyer node class
- [ ] Add threshold controls (min/max)
- [ ] Add softness/falloff controls
- [ ] Add invert option
- [ ] Add unit tests for LumaKeyer node
- [ ] Create example workflow

### 12. MatteControl Node
- [ ] Implement base MatteControl node class
- [ ] Add contract control
- [ ] Add expand control
- [ ] Add blur control
- [ ] Add gamma control
- [ ] Combine operations efficiently
- [ ] Add unit tests for MatteControl node
- [ ] Create example workflow

### 13. DifferenceKeyer Node
- [ ] Implement base DifferenceKeyer node class
- [ ] Add clean plate input
- [ ] Add threshold control
- [ ] Add softness control
- [ ] Implement difference matte generation
- [ ] Add unit tests for DifferenceKeyer node
- [ ] Create example workflow

---

## Phase 4: Advanced Color & Filters

### 14. Saturation Node
- [ ] Implement base Saturation node class
- [ ] Add saturation amount control
- [ ] Use HSV color space conversion
- [ ] Preserve luminance correctly
- [ ] Add unit tests for Saturation node
- [ ] Create example workflow

### 15. Invert Node
- [ ] Implement base Invert node class
- [ ] Add per-channel invert options
- [ ] Add RGB/Alpha separate controls
- [ ] Add unit tests for Invert node
- [ ] Create example workflow

### 16. HueCorrect / ColorCurves Node
- [ ] Implement base HueCorrect node class
- [ ] Add hue range selection
- [ ] Add saturation adjustment per hue
- [ ] Add value/lightness adjustment per hue
- [ ] Implement curve-based controls
- [ ] Add unit tests
- [ ] Create example workflow

### 17. Defocus Node
- [ ] Implement base Defocus node class
- [ ] Add defocus amount control
- [ ] Implement bokeh-style blur
- [ ] Add quality controls
- [ ] Optimize for performance
- [ ] Add unit tests for Defocus node
- [ ] Create example workflow

### 18. DirectionalBlur Node
- [ ] Implement base DirectionalBlur node class
- [ ] Add angle control
- [ ] Add distance control
- [ ] Add quality/samples control
- [ ] Add unit tests for DirectionalBlur node
- [ ] Create example workflow

### 19. Sharpen Node
- [ ] Implement base Sharpen node class
- [ ] Add amount control
- [ ] Implement unsharp mask algorithm
- [ ] Add size control
- [ ] Add unit tests for Sharpen node
- [ ] Create example workflow

### 20. EdgeDetect Node
- [ ] Implement base EdgeDetect node class
- [ ] Add Sobel edge detection
- [ ] Add Laplacian option
- [ ] Add threshold control
- [ ] Add unit tests for EdgeDetect node
- [ ] Create example workflow

### 21. Median Filter Node
- [ ] Implement base Median node class
- [ ] Add kernel size control
- [ ] Implement median filtering
- [ ] Optimize for performance
- [ ] Add unit tests for Median node
- [ ] Create example workflow

---

## Phase 5: Transform & Warping

### 22. CornerPin Node
- [ ] Implement base CornerPin node class
- [ ] Add 4 corner point controls
- [ ] Implement perspective transform
- [ ] Add filter quality options
- [ ] Add unit tests for CornerPin node
- [ ] Create example workflow

### 23. GridWarp Node
- [ ] Implement base GridWarp node class
- [ ] Add grid resolution controls
- [ ] Implement mesh deformation
- [ ] Add control point manipulation
- [ ] Add unit tests for GridWarp node
- [ ] Create example workflow

### 24. LensDistortion Node
- [ ] Implement base LensDistortion node class
- [ ] Add distortion amount control
- [ ] Implement barrel/pincushion distortion
- [ ] Add center point control
- [ ] Add unit tests for LensDistortion node
- [ ] Create example workflow

### 25. Displace Node
- [ ] Implement base Displace node class
- [ ] Add displacement map input
- [ ] Add X/Y scale controls
- [ ] Add channel mapping options
- [ ] Add unit tests for Displace node
- [ ] Create example workflow

---

## Phase 6: Time Operations

### 26. FrameHold Node
- [ ] Implement base FrameHold node class
- [ ] Add frame number control
- [ ] Implement frame caching
- [ ] Add unit tests for FrameHold node
- [ ] Create example workflow

### 27. TimeOffset Node
- [ ] Implement base TimeOffset node class
- [ ] Add offset amount control
- [ ] Add loop mode options
- [ ] Add unit tests for TimeOffset node
- [ ] Create example workflow

### 28. VectorBlur Node (Advanced)
- [ ] Implement base VectorBlur node class
- [ ] Add motion vector input
- [ ] Add blur amount control
- [ ] Implement vector-based sampling
- [ ] Add unit tests for VectorBlur node
- [ ] Create example workflow

---

## Phase 7: Additional Utilities

### 29. Constant/Background Node
- [ ] Implement base Constant node class
- [ ] Add color picker
- [ ] Add width/height controls
- [ ] Add gradient options (optional)
- [ ] Add unit tests for Constant node
- [ ] Create example workflow

### 30. Copy/ChannelCopy Node
- [ ] Implement base ChannelCopy node class
- [ ] Add source/target channel selection
- [ ] Support multiple channel copies
- [ ] Add unit tests for ChannelCopy node
- [ ] Create example workflow

### 31. Remove Channels Node
- [ ] Implement base Remove node class
- [ ] Add channel selection options
- [ ] Add unit tests for Remove node
- [ ] Create example workflow

### 32. Noise Generator Node
- [ ] Implement base Noise node class
- [ ] Add Perlin/Simplex noise options
- [ ] Add frequency/scale controls
- [ ] Add octaves/detail controls
- [ ] Add unit tests for Noise node
- [ ] Create example workflow

### 33. Ramp/Gradient Node
- [ ] Implement base Ramp node class
- [ ] Add linear gradient
- [ ] Add radial gradient
- [ ] Add color controls
- [ ] Add direction/angle controls
- [ ] Add unit tests for Ramp node
- [ ] Create example workflow

---

## Phase 8: Testing & Documentation

### Comprehensive Testing
- [ ] Write unit tests for all utility functions
- [ ] Write integration tests for common workflows
- [ ] Test with various image sizes (1080p, 4K)
- [ ] Test batch processing functionality
- [ ] Performance profiling and benchmarking
- [ ] Memory leak testing
- [ ] Edge case testing (1x1 images, huge images, etc.)

### Documentation
- [ ] Complete README.md with installation instructions
- [ ] Document each node with parameters and examples
- [ ] Create tutorial workflows for common use cases
  - [ ] Basic compositing workflow
  - [ ] Green screen keying workflow
  - [ ] Color grading workflow
  - [ ] Matte refinement workflow
- [ ] Create comparison guide (Nuke → Detonate)
- [ ] Create comparison guide (Fusion → Detonate)
- [ ] Record video demonstrations (optional)

### Code Quality
- [ ] Run black formatter on all Python files
- [ ] Run flake8 linter and fix issues
- [ ] Add docstrings to all public functions
- [ ] Add type hints (optional)
- [ ] Code review and refactoring

---

## Phase 9: Publishing & Release

### Pre-Release
- [ ] Final testing pass
- [ ] Update version to 1.0.0
- [ ] Create CHANGELOG.md
- [ ] Write comprehensive README.md
- [ ] Create example workflow gallery

### GitHub Setup
- [ ] Create release v1.0.0
- [ ] Tag release in git
- [ ] Create issue templates
- [ ] Create pull request template
- [ ] Add contributing guidelines

### Distribution
- [ ] Submit to ComfyUI Manager
- [ ] Register on ComfyUI Registry (optional)
- [ ] Announce on ComfyUI Discord/Reddit
- [ ] Monitor for bug reports and feedback

### Post-Release
- [ ] Address initial bug reports
- [ ] Gather user feedback
- [ ] Plan next features based on requests
- [ ] Regular maintenance and updates

---

## Future Phases (Post v1.0)

### Advanced Features (v2.0)
- [ ] Tracking nodes (2D Point Tracker)
- [ ] Planar tracking
- [ ] Stabilization
- [ ] Optical flow retiming
- [ ] 3D compositing nodes
- [ ] Advanced keyers (Primatte-style)
- [ ] ACES/OCIO color management
- [ ] EXR multi-channel support

### Community Features
- [ ] User-submitted node requests
- [ ] Preset library system
- [ ] Node macro/gizmo system
- [ ] Expression support

---

## Notes

**Priority Levels:**
- Phase 1-2: Critical for basic functionality (MVP)
- Phase 3-4: Professional features
- Phase 5-6: Advanced capabilities
- Phase 7-9: Polish and release
- Future: Enhancement and expansion

**Completion Tracking:**
Mark items as complete using `[x]` as you finish them.

**Estimated Timeline:**
- Phase 1: 2 weeks
- Phase 2: 3 weeks
- Phase 3-4: 4 weeks
- Phase 5-6: 4 weeks
- Phase 7-9: 3 weeks
- **Total: ~16 weeks to v1.0**
