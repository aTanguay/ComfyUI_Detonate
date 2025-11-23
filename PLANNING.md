# ComfyUI_Detonate - Planning Document

## Vision

### Project Overview
ComfyUI_Detonate is a comprehensive custom node package for ComfyUI that brings traditional compositing workflows from industry-standard software (Nuke and DaVinci Fusion) to the ComfyUI platform. The project aims to bridge the gap between traditional VFX compositing and modern AI-powered image generation workflows by implementing familiar node-based compositing tools within ComfyUI's ecosystem.

**Core Goals:**
- Provide professional compositors with familiar tools in ComfyUI
- Enable traditional compositing techniques alongside AI workflows
- Maintain naming conventions and workflows from Nuke/Fusion where possible
- Create a comprehensive, production-ready compositing toolkit

### Target Users
**Primary Audience:**
- Professional compositors transitioning from Nuke or DaVinci Fusion to ComfyUI
- VFX artists seeking to combine traditional compositing with AI generation
- Motion designers and video editors familiar with node-based workflows
- Technical directors building hybrid AI/traditional pipelines

**User Needs:**
- Familiar node names and behaviors from traditional compositing software
- Professional-grade color correction, keying, and masking tools
- Robust transform, tracking, and warping capabilities
- Industry-standard merge/blend operations
- Seamless integration with existing ComfyUI workflows

### Key Features
**Core Compositing Nodes:**
- Advanced merge operations (Over, Under, Plus, Screen, Multiply, Stencil, etc.)
- Professional color correction tools (Grade, ColorCorrect, Hue controls)
- Industry-standard keying nodes (Primatte, Keylight-style, Delta keying)
- Transform and geometric manipulation (Transform, CornerPin, Stabilize)
- Comprehensive filter operations (Blur, Defocus, Sharpen, Directional blur)

**Matte & Masking:**
- Edge operations (Erode/Dilate, MatteControl)
- Rotoscoping and shape tools
- Advanced matte refinement

**Channel Operations:**
- Channel shuffle and manipulation
- Premultiply/Unpremultiply operations
- Channel copy and removal

**Time & Tracking:**
- 2D point tracking
- Frame hold and time manipulation
- Motion blur and vector operations

**3D Compositing:**
- 3D scene integration
- Camera and light support
- Basic 3D geometry handling

### Success Metrics
- **Adoption:** Number of installations via ComfyUI Manager
- **Completeness:** Coverage of top 50 most-used Nuke/Fusion nodes
- **Usability:** Positive feedback from professional compositors
- **Performance:** Nodes execute efficiently without blocking ComfyUI workflows
- **Documentation:** Comprehensive examples and tutorials for each node category
- **Community:** Active user base contributing feedback and use cases

---

## Architecture

### High-Level Architecture
ComfyUI_Detonate follows ComfyUI's standard custom node architecture pattern:

```
ComfyUI/
└── custom_nodes/
    └── ComfyUI_Detonate/
        ├── __init__.py                 # Node registration
        ├── nodes/                      # Node implementations
        │   ├── compositing/            # Merge operations
        │   ├── color/                  # Color correction nodes
        │   ├── keying/                 # Keying operations
        │   ├── transform/              # Transform & geometry
        │   ├── filter/                 # Blur, sharpen, etc.
        │   ├── matte/                  # Matte operations
        │   ├── channel/                # Channel manipulation
        │   ├── time/                   # Time operations
        │   └── 3d/                     # 3D compositing
        ├── utils/                      # Shared utilities
        │   ├── image_processing.py     # Common image ops
        │   ├── color_math.py           # Color space utilities
        │   └── tensor_utils.py         # PyTorch helpers
        ├── web/                        # Frontend extensions
        │   └── js/
        │       └── detonate.js         # Custom UI behaviors
        ├── tests/                      # Unit tests
        ├── examples/                   # Example workflows
        ├── pyproject.toml              # Package metadata
        ├── requirements.txt            # Dependencies
        └── README.md                   # Documentation
```

### Component Structure

**Node Categories:**
1. **Compositing** (`nodes/compositing/`)
   - Merge nodes with blend modes
   - Alpha operations
   - Layer blending

2. **Color** (`nodes/color/`)
   - Grade node (lift/gamma/gain)
   - ColorCorrect (basic adjustments)
   - Saturation, Hue, Clamp
   - Color space conversions

3. **Keying** (`nodes/keying/`)
   - Chroma keyers (green/blue screen)
   - Luma keying
   - Difference keying
   - Key refinement tools

4. **Transform** (`nodes/transform/`)
   - 2D transforms (translate, rotate, scale)
   - Corner pinning
   - Stabilization
   - Lens distortion

5. **Filter** (`nodes/filter/`)
   - Blur variants (Gaussian, defocus, directional)
   - Sharpen and unsharp mask
   - Edge detection
   - Median filtering

6. **Matte** (`nodes/matte/`)
   - Erode/Dilate operations
   - Matte control (contract, expand, blur, gamma)
   - Edge operations

7. **Channel** (`nodes/channel/`)
   - Shuffle operations
   - Channel copy/merge
   - Premultiply/Unpremultiply
   - Channel removal

8. **Time** (`nodes/time/`)
   - Frame hold
   - Time offset
   - Speed changes
   - Optical flow (if feasible)

9. **3D** (`nodes/3d/`)
   - Basic 3D scene support
   - Camera integration
   - Card/plane geometry

**Utility Layer:**
- Shared image processing functions
- Color mathematics and conversions
- Tensor manipulation helpers
- Common validation routines

### Data Flow

**Standard Node Processing Pattern:**
```
Input (IMAGE tensor [B,H,W,C])
    ↓
Validation & Type Checking
    ↓
Premultiply (if needed)
    ↓
Processing Logic
    ↓
Unpremultiply (if needed)
    ↓
Output (IMAGE tensor [B,H,W,C])
```

**ComfyUI Integration Flow:**
```
User creates workflow in ComfyUI UI
    ↓
Detonate nodes process IMAGE tensors
    ↓
Nodes can connect to/from native ComfyUI nodes
    ↓
Output to Save Image or other nodes
```

**Data Types:**
- Primary: `IMAGE` (torch.Tensor [B,H,W,C] with C=3 RGB or C=4 RGBA)
- Secondary: `MASK` (torch.Tensor [H,W] or [B,C,H,W])
- Auxiliary: `FLOAT`, `INT`, `STRING` for parameters

### Integration Points

**ComfyUI Core:**
- Uses standard ComfyUI IMAGE tensor format
- Follows ComfyUI node registration pattern
- Compatible with ComfyUI's execution engine
- Integrates with ComfyUI Manager for installation

**Native ComfyUI Nodes:**
- Receives output from LoadImage, VAEDecode, etc.
- Outputs to SaveImage, VAEEncode, etc.
- Works alongside existing custom node packages

**External Libraries:**
- PyTorch for tensor operations
- NumPy for mathematical operations
- OpenCV for advanced image processing (optional)
- Pillow for image I/O utilities

**Frontend:**
- JavaScript extensions for enhanced UI
- Custom widgets for complex parameters
- Visual feedback for processing state

---

## Technology Stack

### Backend (Primary Development)
- **Language:** Python 3.8+
- **Core Framework:** ComfyUI Custom Node API
- **Tensor Operations:** PyTorch 2.0+
- **Numerical Computing:** NumPy 1.20+
- **Image Processing:**
  - Pillow 9.0+ (basic I/O)
  - OpenCV (optional, for advanced operations)
  - scikit-image (optional, for specific filters)

### Frontend (Optional Extensions)
- **Language:** JavaScript (ES6+)
- **Framework:** ComfyUI's built-in extension system
- **UI Integration:** ComfyUI's LiteGraph-based node editor
- **APIs Used:**
  - `app.js` - Core application API
  - `api.js` - Backend communication
  - Custom widget creation

### ComfyUI Integration
- **Node Registration:** `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`
- **Data Types:**
  - IMAGE (torch.Tensor [B,H,W,C])
  - MASK (torch.Tensor)
  - FLOAT, INT, STRING, BOOLEAN
- **Execution:** ComfyUI's graph execution engine
- **Installation:** ComfyUI Manager compatible

### Core Libraries & Dependencies

**Required:**
```
torch>=2.0.0
numpy>=1.23.5,<2.0.0       # CRITICAL: <2.0 for ComfyUI compatibility (Windows/Linux)
pillow>=9.0.0,<11.0.0      # CRITICAL: <11.0 for gradio compatibility
OpenImageIO>=2.4.0         # Multi-channel EXR support (CG pipelines)
mmh3>=3.0.0                # Cryptomatte hash support
```

**⚠️ Version Constraints - DO NOT MODIFY:**
- **numpy <2.0.0** - Required for compatibility with ComfyUI ecosystem packages (dctorch, langchain, mediapipe, scipy, unstructured)
- **pillow <11.0.0** - Required for compatibility with ComfyUI's gradio web interface
- These constraints ensure Windows/Linux compatibility across typical ComfyUI installations
- Removing these constraints will cause dependency conflicts during installation

**Optional (for advanced features):**
```
opencv-python>=4.5.0       # Advanced image processing
scikit-image>=0.19.0       # Scientific image processing
scipy>=1.7.0               # Scientific computing
colour-science>=0.4.0      # Color space conversions
```

### Development & Testing
- **Version Control:** Git
- **Package Management:** pip, pyproject.toml
- **Testing Framework:** pytest
- **Code Quality:**
  - black (formatting)
  - flake8 (linting)
  - mypy (type checking - optional)

### Image Processing Pipeline
- **Color Spaces:** RGB, RGBA, HSV, LAB support
- **Bit Depth:** Float32 (0.0-1.0 range, matching ComfyUI standard)
- **Alpha Handling:** Premultiplied and straight alpha support
- **Batch Processing:** Full batch dimension support for efficiency

---

## Required Tools & Dependencies

### Development Environment
- [ ] **Python 3.8+** - Core development language
- [ ] **Git** - Version control
- [ ] **Code Editor** - VS Code recommended with Python extension
- [ ] **ComfyUI CLI** - `pip install comfy-cli` for scaffolding

### ComfyUI Setup
- [ ] **ComfyUI** - Latest stable version from [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ ] **ComfyUI Manager** (optional) - For easy installation/updates
- [ ] **Test Images** - Sample images for node testing
- [ ] **Python Environment** - Virtual environment (venv/conda) recommended

### Python Dependencies (Development)
```bash
# Core dependencies
pip install torch>=2.0.0
pip install numpy>=1.20.0
pip install pillow>=9.0.0

# Development tools
pip install pytest           # Testing
pip install black            # Code formatting
pip install flake8           # Linting
pip install mypy             # Type checking (optional)

# Optional for advanced features
pip install opencv-python    # Advanced image ops
pip install scikit-image     # Scientific image processing
pip install scipy            # Math operations
```

### Testing Tools
- [ ] **pytest** - Unit testing framework
- [ ] **pytest-cov** - Code coverage reporting
- [ ] **Test workflows** - ComfyUI workflow JSON files for integration testing
- [ ] **Sample images** - Test assets (green screen footage, mattes, etc.)

### Development Workflow Tools
- [ ] **comfy node scaffold** - CLI tool for generating node boilerplate
- [ ] **Hot reload** - ComfyUI restart required for code changes
- [ ] **Browser DevTools** - For frontend debugging (if adding JS extensions)

### Documentation Tools
- [ ] **Markdown editor** - For documentation
- [ ] **Workflow screenshots** - For example documentation
- [ ] **Docstrings** - In-code documentation following Python standards

### Distribution & Publishing
- [ ] **GitHub repository** - For version control and distribution
- [ ] **pyproject.toml** - Modern Python packaging metadata
- [ ] **ComfyUI Manager submission** - For easy user installation
- [ ] **ComfyUI Registry** - Optional registration at registry.comfy.org

### Reference Materials
- [ ] **Nuke documentation** - For node behavior reference
- [ ] **Fusion documentation** - For node behavior reference
- [ ] **ComfyUI docs** - https://docs.comfy.org/
- [ ] **Example custom nodes** - Study existing implementations

---

## Development Phases

### Phase 1: Foundation & Infrastructure (Week 1-2)
**Goal:** Set up project structure and core utilities

- [ ] Initialize repository structure with proper directories
- [ ] Create `pyproject.toml` and `requirements.txt`
- [ ] Set up `__init__.py` with node registration system
- [ ] Implement `utils/` module:
  - `tensor_utils.py` - Batch handling, type conversions
  - `image_processing.py` - Common image operations
  - `color_math.py` - Color space utilities
- [ ] Create base test framework
- [ ] Document coding standards and contribution guidelines

**Deliverable:** Working project skeleton that loads in ComfyUI

### Phase 2: Core Compositing Nodes (Week 3-5)
**Goal:** Implement essential daily-use nodes

**Priority 1 - Most Critical:**
- [ ] Merge node with blend modes (Over, Under, Plus, Screen, Multiply)
- [ ] Transform (translate, rotate, scale with motion blur)
- [ ] Blur (Gaussian with separate X/Y)
- [ ] Grade (lift/gamma/gain with master + RGB controls)
- [ ] Premultiply/Unpremultiply

**Priority 2 - High Usage:**
- [ ] ColorCorrect (saturation, contrast, gamma, offset)
- [ ] Erode/Dilate
- [ ] Shuffle (channel operations)
- [ ] Clamp (min/max value control)

**Deliverable:** Working compositor toolkit for basic workflows

### Phase 3: Keying & Matte Operations (Week 6-7)
**Goal:** Professional keying tools

- [ ] Basic ChromaKeyer (green/blue screen)
- [ ] LumaKeyer (luminance-based)
- [ ] MatteControl (contract, expand, blur, gamma for mattes)
- [ ] DifferenceKeyer (difference matte generation)
- [ ] Key refinement utilities

**Deliverable:** Complete keying pipeline

### Phase 4: Advanced Color & Filters (Week 8-9)
**Goal:** Professional color and filter tools

**Color:**
- [ ] HueCorrect/ColorCurves
- [ ] Saturation controls
- [ ] Invert
- [ ] Color space conversions

**Filters:**
- [ ] Defocus (lens-style)
- [ ] DirectionalBlur
- [ ] Sharpen/Unsharp Mask
- [ ] Median filter
- [ ] EdgeDetect

**Deliverable:** Advanced color grading and filtering

### Phase 5: Transform & Warping (Week 10-11)
**Goal:** Geometric manipulation tools

- [ ] CornerPin (4-point perspective)
- [ ] GridWarp (manual warping)
- [ ] LensDistortion (add/remove)
- [ ] IDistort/Displace (displacement mapping)
- [ ] Stabilize (if tracking data available)

**Deliverable:** Full transform and warping toolkit

### Phase 6: Time Operations (Week 12)
**Goal:** Temporal effects

- [ ] FrameHold
- [ ] TimeOffset
- [ ] TimeSpeed (retiming)
- [ ] VectorBlur (motion vectors)

**Deliverable:** Time manipulation nodes

### Phase 7: Testing & Documentation (Week 13-14)
**Goal:** Production-ready package

- [ ] Comprehensive unit tests for all nodes
- [ ] Integration tests with example workflows
- [ ] Performance profiling and optimization
- [ ] Complete README with examples
- [ ] Per-node documentation
- [ ] Tutorial workflows
- [ ] Video demonstrations (optional)

**Deliverable:** Fully tested and documented package

### Phase 8: Publishing & Community (Week 15+)
**Goal:** Release and support

- [ ] Submit to ComfyUI Manager
- [ ] Register on ComfyUI Registry
- [ ] Create GitHub releases
- [ ] Set up issue templates
- [ ] Community feedback integration
- [ ] Bug fixes and refinements

**Deliverable:** Public release v1.0.0

---

## Notes & Considerations

### Technical Constraints

**ComfyUI Limitations:**
- Node updates require ComfyUI restart (no hot reload)
- IMAGE tensors must maintain [B,H,W,C] shape convention
- Limited UI customization compared to standalone applications
- JavaScript extensions have access restrictions

**Performance Constraints:**
- All processing must be reasonably fast for interactive use
- Batch operations should leverage vectorization
- Memory usage must be reasonable for typical image sizes (1080p-4K)
- Avoid blocking operations that freeze the UI

**Compatibility:**
- Must work with ComfyUI's PyTorch-based IMAGE format
- Should handle both RGB (3-channel) and RGBA (4-channel) images
- Need to support batch processing (batch dimension in tensors)
- Color values are 0.0-1.0 float range (not 0-255)

**Alpha/Premultiplication:**
- ComfyUI doesn't have strict premultiplication conventions
- Need explicit Premult/Unpremult nodes like Nuke
- Must document which nodes expect premultiplied vs straight alpha
- Merge operations should handle alpha correctly

### Security Considerations

**Input Validation:**
- Validate all user inputs (ranges, types, file paths)
- Prevent division by zero in mathematical operations
- Handle edge cases (empty images, single pixel images, etc.)
- Sanitize file paths if implementing file I/O

**Dependency Security:**
- Use well-maintained, trusted libraries only
- Pin dependency versions in requirements.txt
- Regularly update for security patches
- Avoid unnecessary dependencies that increase attack surface

**User Safety:**
- No arbitrary code execution from user inputs
- No network requests without explicit user consent
- Clear warnings for destructive operations
- Safe error handling (don't expose system internals)

### Performance Requirements

**Target Performance:**
- 1080p images: <100ms per node operation
- 4K images: <500ms per node operation
- Batch processing: Linear scaling with batch size
- Memory usage: <2x input image size

**Optimization Strategies:**
- Use PyTorch operations instead of Python loops
- Leverage GPU acceleration where available
- Implement efficient algorithms (avoid O(n²) when O(n) exists)
- Cache expensive computations when possible
- Use in-place operations to reduce memory allocation

**Profiling:**
- Regular performance testing with various image sizes
- Memory profiling to detect leaks
- Bottleneck identification and optimization
- Comparison with reference implementations (Nuke/Fusion)

### Future Enhancements

**Phase 2 Features:**
- 3D compositing nodes (Camera, Lights, Geometry)
- Advanced keyers (Primatte, professional-grade algorithms)
- Planar tracking and transforms
- Optical flow retiming
- Lens distortion with specific camera models
- Advanced color science (ACES, OCIO integration)

**Advanced Capabilities:**
- Motion vector generation and manipulation
- Deep compositing (if ComfyUI supports depth data)
- Multi-channel EXR support
- Cryptomatte integration
- Smart matte generation using AI
- Temporal coherence for video sequences

**Workflow Improvements:**
- Preset library for common operations
- Node macros/gizmos (compound nodes)
- Expression support for parameter linking
- Curve editors for advanced controls
- Comparative viewers (A/B comparison)

**Community Features:**
- User-submitted node requests
- Community presets and workflows
- Integration with other popular ComfyUI packages
- Cross-platform workflow exchange with Nuke/Fusion

**Documentation:**
- Interactive tutorials
- Video walkthrough series
- Comparison guides (Nuke → Detonate, Fusion → Detonate)
- Best practices for hybrid AI/traditional workflows

---

## References & Resources

### Official Documentation
- [ComfyUI Documentation](https://docs.comfy.org/)
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Custom Node Walkthrough](https://docs.comfy.org/custom-nodes/walkthrough)
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [ComfyUI Registry](https://registry.comfy.org/)
- [ComfyUI CLI](https://github.com/Comfy-Org/comfy-cli)

### Node Development Resources
- [Suzie1's Custom Node Guide](https://github.com/Suzie1/ComfyUI_Guide_To_Making_Custom_Nodes)
- [Example Node Template](https://github.com/comfyanonymous/ComfyUI/blob/master/custom_nodes/example_node.py.example)
- [ComfyUI-Impact-Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack) - Reference implementation
- [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes) - Example custom nodes
- [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui) - Comprehensive example

### Traditional Compositing References
- [The Foundry Nuke Documentation](https://learn.foundry.com/nuke/)
- [Blackmagic Fusion Documentation](https://documents.blackmagicdesign.com/UserManuals/Fusion_Manual.pdf)
- [VFXPedia](https://www.vfxpedia.com/) - VFX knowledge base
- [Nuke to Fusion Translation](https://github.com/statixVFX/nuke2fusion) - Node equivalency reference

### Related Projects
- **Existing ComfyUI Packages:**
  - ComfyUI-Advanced-ControlNet
  - ComfyUI-VideoHelperSuite
  - ComfyUI_Comfyroll_CustomNodes
  - ComfyUI-Manager (for distribution)

- **Compositing Tools:**
  - Natron - Open source compositing (similar to Nuke)
  - Blender Compositor - Node-based compositing reference

### Research & Technical Resources

**Image Processing:**
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [scikit-image](https://scikit-image.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)

**Color Science:**
- [Colour Science for Python](https://www.colour-science.org/)
- [ACES Documentation](https://acescentral.com/)
- [OpenColorIO](https://opencolorio.org/)

**Compositing Algorithms:**
- "Compositing Digital Images" (Porter & Duff, 1984) - Alpha compositing paper
- "Digital Compositing for Film and Video" (Steve Wright) - Industry reference book
- [Alpha Compositing on Wikipedia](https://en.wikipedia.org/wiki/Alpha_compositing)

### Community & Support
- [ComfyUI Discord](https://discord.gg/comfyui) - Community support
- [ComfyUI Subreddit](https://www.reddit.com/r/comfyui/)
- [ComfyUI Workflows](https://comfyworkflows.com/) - Workflow sharing
- GitHub Issues - For bug reports and feature requests (when published)

---

## Appendix: Common Node Mapping

### Quick Reference: Nuke/Fusion → Detonate

| Category | Nuke | Fusion | Detonate (Planned) |
|----------|------|--------|-------------------|
| **Merge** | Merge | Merge | Merge |
| **Color** | Grade | ColorCorrector | Grade |
| **Blur** | Blur | Blur | Blur |
| **Key** | Keylight | DeltaKeyer | ChromaKeyer |
| **Transform** | Transform | Transform | Transform |
| **Matte** | FilterErode | MatteControl | MatteControl |
| **Channel** | Shuffle | ChannelBooleans | Shuffle |
| **Premult** | Premult | (in Merge) | Premult |

See full node comparison in research documentation.
