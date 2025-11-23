# Guide for Claude - ComfyUI_Detonate Project

This document provides context for future Claude sessions working on this project.

---

## Project Summary

**ComfyUI_Detonate** is a custom node package for ComfyUI that brings professional compositing tools from Nuke and DaVinci Fusion to the ComfyUI platform. The goal is to provide VFX compositors with familiar, industry-standard nodes for traditional compositing workflows alongside AI image generation.

---

## Key Project Documents

### Primary References
1. **[PLANNING.md](PLANNING.md)** - Complete project vision, architecture, and roadmap
2. **[TASKS.md](TASKS.md)** - Detailed task checklist for implementation
3. **[NODE_PRIORITIES.md](NODE_PRIORITIES.md)** - 43 nodes prioritized by importance

### Quick Reference
- **Language:** Python 3.8+
- **Framework:** ComfyUI Custom Node API
- **Core Libraries:** PyTorch, NumPy, Pillow
- **Target:** Professional compositors and VFX artists

---

## Project Status

**Current Phase:** Phase 1 - Planning Complete ✓

**Completed:**
- Project vision and goals defined
- Architecture designed
- Technology stack selected
- 43 nodes researched and prioritized
- Development roadmap created

**Next Steps:**
1. Create directory structure
2. Set up `pyproject.toml` and `requirements.txt`
3. Implement utility modules (`tensor_utils.py`, `image_processing.py`, `color_math.py`)
4. Create `__init__.py` with node registration system
5. Begin implementing Priority 1 nodes (Merge, Transform, Blur, Grade, Premult/Unpremult)

---

## Technical Architecture

### Directory Structure
```
ComfyUI_Detonate/
├── __init__.py                 # Node registration
├── nodes/                      # Node implementations
│   ├── compositing/            # Merge operations
│   ├── color/                  # Color correction
│   ├── keying/                 # Keying tools
│   ├── transform/              # Transforms
│   ├── filter/                 # Blur, sharpen, etc.
│   ├── matte/                  # Matte operations
│   ├── channel/                # Channel ops
│   ├── time/                   # Time operations
│   └── 3d/                     # 3D compositing
├── utils/                      # Shared utilities
│   ├── tensor_utils.py
│   ├── image_processing.py
│   └── color_math.py
├── tests/                      # Unit tests
├── examples/                   # Example workflows
├── web/js/                     # Frontend extensions
├── pyproject.toml              # Package metadata
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

### ComfyUI Node Structure
Every node must implement:
```python
class NodeName:
    CATEGORY = "detonate/category"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"

    def process(self, image):
        # Processing logic
        return (image,)
```

### Image Tensor Format
- **Shape:** `[B, H, W, C]` (Batch, Height, Width, Channels)
- **Type:** `torch.Tensor` (Float32)
- **Range:** 0.0 - 1.0
- **Channels:** C=3 (RGB) or C=4 (RGBA)

---

## Development Guidelines

### Code Standards
- Use **black** for formatting
- Use **flake8** for linting
- Add docstrings to all public functions
- Include type hints where helpful
- Keep functions focused and modular

### Node Implementation Pattern
1. Create node class in appropriate `nodes/` subdirectory
2. Implement required class attributes (CATEGORY, INPUT_TYPES, RETURN_TYPES, FUNCTION)
3. Implement processing method
4. Handle batch processing correctly
5. Add validation and error handling
6. Register node in `__init__.py`
7. Write unit tests
8. Create example workflow

### Testing
- Write unit tests for all nodes
- Test with various image sizes (1080p, 4K)
- Test batch processing
- Test edge cases (1x1 images, empty batches)
- Verify alpha channel handling

### Performance
- Use PyTorch operations (vectorized)
- Avoid Python loops over pixels
- Leverage GPU when available
- Target: <100ms for 1080p, <500ms for 4K

---

## Common Operations Reference

### Alpha Handling
```python
# Premultiply
result_rgb = rgb * alpha

# Unpremultiply (handle division by zero)
result_rgb = rgb / (alpha + 1e-7)
```

### Blend Modes
```python
# Over compositing
result = fg + bg * (1 - fg_alpha)

# Screen
result = 1 - (1 - fg) * (1 - bg)

# Multiply
result = fg * bg
```

### Color Space Conversion
```python
# RGB to HSV
hsv = torch.tensor(cv2.cvtColor(rgb.numpy(), cv2.COLOR_RGB2HSV))

# HSV to RGB
rgb = torch.tensor(cv2.cvtColor(hsv.numpy(), cv2.COLOR_HSV2RGB))
```

---

## Nuke/Fusion Equivalents

Quick reference for compositor familiarity:

| Function | Nuke | Fusion | Detonate |
|----------|------|--------|----------|
| Compositing | Merge | Merge | Merge |
| Color Grading | Grade | ColorCorrector | Grade |
| Blur | Blur | Blur | Blur |
| Keying | Keylight | DeltaKeyer | ChromaKeyer |
| Transform | Transform | Transform | Transform |
| Matte Ops | FilterErode | MatteControl | MatteControl |
| Channels | Shuffle | ChannelBooleans | Shuffle |
| Premult | Premult | (in Merge) | Premult |

---

## Priority 1 Nodes (Implement First)

These 8 nodes form the core toolkit:

1. **Merge** - Compositing with blend modes (Over, Under, Plus, Screen, Multiply)
2. **Transform** - Translate, rotate, scale, skew
3. **Blur** - Gaussian blur with X/Y controls
4. **Grade** - Lift/Gamma/Gain color correction
5. **Premultiply** - Multiply RGB by alpha
6. **Unpremultiply** - Divide RGB by alpha
7. **Shuffle** - Channel reordering
8. **ColorCorrect** - Quick saturation/contrast/gamma adjustments

---

## Dependencies

### Required
```
torch>=2.0.0
numpy>=1.23.5,<2.0.0        # CRITICAL: Must be <2.0 for ComfyUI compatibility
pillow>=9.0.0,<11.0.0       # CRITICAL: Must be <11.0 for gradio compatibility
OpenImageIO>=2.4.0          # Multi-channel EXR support
mmh3>=3.0.0                 # Cryptomatte support
```

**⚠️ IMPORTANT - Windows/ComfyUI Compatibility:**
- **numpy <2.0.0** - Many ComfyUI packages (dctorch, langchain, mediapipe, scipy, unstructured) break with numpy 2.x
- **pillow <11.0.0** - ComfyUI's gradio UI breaks with pillow 11+
- **DO NOT remove these version constraints** without testing on Windows with full ComfyUI environment
- These constraints were added in 2025-01 to fix Windows installation conflicts

### Optional (for advanced features)
```
opencv-python>=4.5.0        # Advanced image processing (keying, advanced filters)
scikit-image>=0.19.0        # Scientific image processing
scipy>=1.7.0                # Scientific computing utilities
```

---

## Workflow for New Sessions

1. **Check TASKS.md** - See what's completed and what's next
2. **Review relevant nodes in NODE_PRIORITIES.md** - Understand priority and complexity
3. **Reference PLANNING.md** - For architecture and design decisions
4. **Implement incrementally** - One node at a time, with tests
5. **Update TASKS.md** - Mark completed items

---

## Common Pitfalls to Avoid

### Image Handling
- ❌ Don't assume C=3 (check for alpha channel)
- ❌ Don't modify input tensors in-place
- ❌ Don't forget batch dimension
- ✅ Always return tuple matching RETURN_TYPES
- ✅ Handle edge cases (empty images, 1x1 pixels)

### Performance
- ❌ Don't use Python loops over pixels
- ❌ Don't load entire image to CPU unnecessarily
- ✅ Use PyTorch operations (vectorized)
- ✅ Keep tensors on GPU when possible

### Alpha Compositing
- ❌ Don't assume images are premultiplied
- ❌ Don't ignore alpha channel in blend modes
- ✅ Document premult requirements
- ✅ Handle straight vs premultiplied correctly

### Node Registration
- ❌ Don't forget to add to NODE_CLASS_MAPPINGS
- ❌ Don't use spaces in CATEGORY names
- ✅ Use consistent naming conventions
- ✅ Provide meaningful display names

### Dependencies & Version Constraints
- ❌ **DO NOT remove version constraints from requirements.txt** (numpy <2.0, pillow <11.0)
- ❌ Don't upgrade numpy or pillow without testing on Windows ComfyUI environment
- ❌ Don't use numpy 2.x specific APIs (stick to numpy 1.x APIs)
- ❌ Don't use pillow 11+ specific features
- ✅ Test all dependency changes on Windows before committing
- ✅ Keep compatibility with ComfyUI ecosystem (gradio, dctorch, langchain, mediapipe)
- ✅ Document any new required dependencies and their version constraints

**Why these constraints matter:**
- Many ComfyUI packages haven't updated to numpy 2.x (dctorch, langchain, mediapipe, scipy, unstructured)
- ComfyUI's gradio interface breaks with pillow 11+
- Windows has stricter dependency resolution than Linux/Mac
- Installation failures frustrate users and reduce adoption

---

## Questions to Ask the User

When implementing nodes:
1. "Should this node expect premultiplied or straight alpha?"
2. "What edge behavior do you want? (black/clamp/repeat)"
3. "Do you want GPU acceleration for this operation?"
4. "Should this support batch processing?"
5. "Any specific Nuke/Fusion behavior to match?"

---

## Useful Resources

- **ComfyUI Docs:** https://docs.comfy.org/
- **PyTorch Docs:** https://pytorch.org/docs/stable/
- **Nuke Docs:** https://learn.foundry.com/nuke/
- **Fusion Docs:** https://documents.blackmagicdesign.com/UserManuals/Fusion_Manual.pdf
- **Porter-Duff Compositing:** https://en.wikipedia.org/wiki/Alpha_compositing

---

## Development Phases Timeline

- **Phase 1:** Foundation (2 weeks) - Directory structure, utils, registration
- **Phase 2:** Core Nodes (3 weeks) - Merge, Transform, Blur, Grade, etc.
- **Phase 3:** Keying (2 weeks) - ChromaKeyer, LumaKeyer, MatteControl
- **Phase 4:** Advanced (2 weeks) - Color curves, filters
- **Phase 5:** Transforms (2 weeks) - CornerPin, GridWarp, Displace
- **Phase 6:** Time Ops (1 week) - FrameHold, TimeOffset
- **Phase 7:** Testing (2 weeks) - Comprehensive tests, docs
- **Phase 8:** Release (1 week) - Publishing, community

**Total estimated time to v1.0: ~16 weeks**

---

## Success Criteria

**Phase 1 Complete:** Package loads in ComfyUI without errors
**Phase 2 Complete:** Can composite basic greenscreen shot with color correction
**Phase 3 Complete:** Professional keying workflow functional
**v1.0 Release:** 30+ nodes implemented, tested, and documented

---

## Notes for Claude

- Always check [TASKS.md](TASKS.md) and update checkboxes as you complete work
- Reference [NODE_PRIORITIES.md](NODE_PRIORITIES.md) for node complexity estimates
- Follow the architecture defined in [PLANNING.md](PLANNING.md)
- Write clean, modular, well-documented code
- Test thoroughly before marking tasks complete
- Ask for clarification when Nuke/Fusion behavior is ambiguous
- Keep the user informed of progress and any blockers

---

**Last Updated:** 2025-01-21
**Current Phase:** Planning Complete, Ready for Phase 1 Implementation
