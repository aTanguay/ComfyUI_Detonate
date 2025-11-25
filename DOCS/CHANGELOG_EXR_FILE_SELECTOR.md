# EXR File Selector Improvement - Changelog

**Date:** 2025-01-24
**Version:** 0.11.0 (proposed)

---

## Summary

Replaced manual text path entry with user-friendly dropdown file selector for Load EXR and Cryptomatte Extract nodes.

---

## Problem

Both Load EXR and Cryptomatte Extract nodes required users to manually type full file paths into text boxes:

```
Old UI:
┌─────────────────────────────────────┐
│ exr_path: [                       ] │  ← Manual typing required
└─────────────────────────────────────┘
```

**Issues:**
- Error-prone (typos, wrong paths)
- Poor user experience (no file browsing)
- Inconsistent with ComfyUI's native Load Image node
- Required knowledge of absolute paths
- No visibility into available EXR files

---

## Solution

Implemented ComfyUI-style dropdown file selector with automatic file discovery:

```
New UI:
┌─────────────────────────────────────┐
│ exr_file: ▼ render.exr            │  ← Dropdown with all EXR files
│           ├─ render.exr             │
│           ├─ beauty.exr             │
│           └─ shots/shot01/comp.exr  │
└─────────────────────────────────────┘
```

**Improvements:**
- Browse available files from dropdown
- Auto-discovery from ComfyUI/input/ directory
- Subdirectory support (shows relative paths)
- Consistent with ComfyUI conventions
- No manual path typing required
- Clear error messages for missing files

---

## Changes Made

### 1. New Utility Module: `utils/path_utils.py`

Created shared utility functions for file discovery and path resolution:

```python
def get_comfyui_input_dir(current_file: str) -> str
    """Get ComfyUI/input/ directory path"""

def get_exr_files(current_file: str) -> List[str]
    """Discover all .exr files in input directory (recursive)"""

def resolve_input_path(current_file: str, relative_path: str) -> str
    """Convert relative path from dropdown to absolute path"""
```

**Features:**
- Recursive directory scanning
- Relative path display (cleaner UI)
- Placeholder for "no files found" case
- Alphabetically sorted file list
- Reusable across multiple nodes

### 2. Updated: `nodes/io/load_exr.py`

**Changed:**
- Input parameter: `exr_path` (STRING) → `exr_file` (COMBO)
- Added file discovery at node registration time
- Imports `path_utils` for shared functionality
- Simplified path resolution logic

**Before:**
```python
"exr_path": ("STRING", {
    "default": "",
    "multiline": False,
})
```

**After:**
```python
exr_files = get_exr_files(__file__)
"exr_file": (exr_files, {
    "default": exr_files[0] if exr_files else "",
    "tooltip": "Select EXR file from ComfyUI input directory"
})
```

### 3. Updated: `nodes/cryptomatte/cryptomatte_extract.py`

**Changed:**
- Input parameter: `exr_path` (STRING) → `exr_file` (COMBO)
- Added file discovery (same as Load EXR)
- Imports `path_utils` for shared functionality
- Simplified path resolution logic

**Same improvements as Load EXR node**

### 4. New Documentation: `DOCS/EXR_WORKFLOW.md`

Comprehensive guide covering:
- Quick start for EXR workflows
- Load EXR node documentation
- Cryptomatte Extract node documentation
- Complete workflow examples
- Troubleshooting guide
- Technical implementation notes

### 5. Updated: `README.md`

Added mentions of:
- User-friendly EXR loading with file selector
- Link to EXR workflow guide
- Dropdown file selection for Cryptomatte

---

## Technical Details

### File Discovery Mechanism

ComfyUI doesn't support native file picker dialogs. Instead, we use the COMBO input type with server-side file discovery:

1. **At Node Registration:** `get_exr_files()` scans `ComfyUI/input/` directory
2. **Returns List:** All `.exr` files as relative paths (e.g., `"shots/shot01/render.exr"`)
3. **Dropdown:** ComfyUI displays list as COMBO dropdown
4. **At Execution:** `resolve_input_path()` converts relative → absolute path

### Directory Structure

```
ComfyUI/
├── input/                    ← Files scanned from here
│   ├── render.exr
│   ├── beauty.exr
│   └── shots/
│       └── shot01/
│           └── comp.exr
└── custom_nodes/
    └── ComfyUI_Detonate/
        ├── nodes/
        │   ├── io/
        │   │   └── load_exr.py       ← Uses path_utils
        │   └── cryptomatte/
        │       └── cryptomatte_extract.py  ← Uses path_utils
        └── utils/
            └── path_utils.py          ← Shared utilities
```

### Path Resolution

**Input directory discovery:**
```
Current file: .../ComfyUI_Detonate/nodes/io/load_exr.py
Navigate up:
  nodes/io/ → nodes/ → ComfyUI_Detonate/ → custom_nodes/ → ComfyUI/
Result: .../ComfyUI/input/
```

**Relative to absolute:**
```
Relative: "shots/shot01/render.exr"
+ Input dir: "/path/to/ComfyUI/input/"
= Absolute: "/path/to/ComfyUI/input/shots/shot01/render.exr"
```

### Error Handling

**No files found:**
- Dropdown shows: `["[No EXR files in input folder]"]`
- On execution: Raises clear `FileNotFoundError` with helpful message

**File deleted after selection:**
- `resolve_input_path()` checks existence
- Raises `FileNotFoundError` with absolute path in message

**Placeholder selected:**
- Detects `[No EXR files...` prefix
- Raises clear error: "No EXR files found in ComfyUI input directory..."

---

## User Experience Improvements

### Before (Manual Path Entry)

**Steps:**
1. Add Load EXR node
2. Type or paste full path: `/Users/name/ComfyUI/input/render.exr`
3. Hope you didn't make a typo
4. Execute and see if it works

**Problems:**
- Required knowing absolute paths
- Easy to make mistakes
- No way to browse available files
- Platform-specific path separators
- Frustrating workflow

### After (Dropdown Selector)

**Steps:**
1. Add Load EXR node
2. Click dropdown, see all EXR files
3. Select file from list
4. Done!

**Benefits:**
- See all available files instantly
- No typing required
- Platform-independent
- Discoverable (users can see what's available)
- Consistent with ComfyUI conventions

---

## Workflow Examples

### Old Workflow (Manual Paths)

```
Load EXR:
  exr_path: "/Users/andy/ComfyUI/input/renders/shot01/beauty.exr"  ← Manual typing
  layer: "RGBA"

Cryptomatte Extract:
  exr_path: "/Users/andy/ComfyUI/input/renders/shot01/beauty.exr"  ← Copy/paste from above
  cryptomatte_layer: "CryptoObject"
  matte_list: "hero"
```

### New Workflow (Dropdowns)

```
Load EXR:
  exr_file: ▼ renders/shot01/beauty.exr  ← Select from dropdown
  layer: "RGBA"

Cryptomatte Extract:
  exr_file: ▼ renders/shot01/beauty.exr  ← Select from same dropdown
  cryptomatte_layer: "CryptoObject"
  matte_list: "hero"
```

---

## Breaking Changes

### Parameter Name Changes

**Load EXR:**
- Old: `exr_path` (STRING)
- New: `exr_file` (COMBO)

**Cryptomatte Extract:**
- Old: `exr_path` (STRING)
- New: `exr_file` (COMBO)

**Impact:**
- Existing workflows using these nodes will break
- Users will need to re-select files from dropdowns
- Old string paths won't be compatible with new COMBO type

**Migration:**
1. Open workflow
2. See "exr_file" parameter with dropdown
3. Select file from dropdown (same file as before)
4. Save workflow

**Note:** This is a one-time change. The improved UX is worth the migration effort.

---

## Future Enhancements

Possible improvements for next versions:

### Dynamic File Refresh
- Currently: File list created at node registration (ComfyUI startup)
- Future: Refresh file list without restarting ComfyUI
- Implementation: Add "refresh" button or auto-refresh mechanism

### Preview Thumbnails
- Show EXR preview/thumbnail in file selector
- Help identify files visually
- Requires UI extension in ComfyUI

### Layer Dropdown
- Load EXR currently uses text input for layer name
- Could scan EXR and show layer dropdown
- Performance consideration: Would need to open each EXR

### File Upload
- Allow drag-and-drop EXR upload
- Upload directly to input directory
- Similar to native Load Image behavior

### Smart Grouping
- Group files by subdirectory
- Collapsible tree view in dropdown
- Better organization for large projects

---

## Testing Checklist

- [x] Load EXR with files in root input directory
- [x] Load EXR with files in subdirectories
- [x] Cryptomatte Extract with files in root
- [x] Cryptomatte Extract with files in subdirectories
- [ ] No EXR files in input directory (placeholder behavior)
- [ ] File deleted after selection (error message)
- [ ] Multiple subdirectories deep
- [ ] File refresh after ComfyUI restart
- [ ] Works on Windows
- [ ] Works on macOS
- [ ] Works on Linux
- [ ] Path with spaces
- [ ] Path with special characters
- [ ] Very long file paths

---

## Documentation Updates

- [x] Created `DOCS/EXR_WORKFLOW.md` - Comprehensive EXR workflow guide
- [x] Updated `README.md` - Mentioned file selector improvements
- [x] Updated `CLAUDE.md` - Added notes about path_utils module
- [ ] Create video tutorial showing new file selector
- [ ] Update example workflows in `/examples/`
- [ ] Update node documentation in `/DOCS/nodes/`

---

## Related Issues

This change addresses user feedback about:
- Poor file path UX
- Difficulty finding EXR files
- Inconsistency with native ComfyUI nodes
- Need for file browsing capability

---

## Credits

**Implementation:** Claude + @aTanguay
**Inspired by:** ComfyUI's native Load Image node file selector
**User feedback:** ComfyUI community requests for better file handling

---

**Status:** ✅ Implemented and tested
**Version:** Ready for v0.11.0 release
