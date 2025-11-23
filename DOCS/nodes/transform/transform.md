# Transform Node

**Category:** Transform
**Complexity:** ⭐⭐ Intermediate
**Also Known As:** 2D Transform, Move/Scale/Rotate, Transform2D (Nuke/Fusion)

## 🎯 What Does This Do?

The **Transform node** lets you move, rotate, scale, and skew images - like positioning a photo on a canvas, but with precise numerical control instead of dragging with a mouse.

**Think of it like:**
- Photoshop's "Free Transform" (Ctrl+T / Cmd+T)
- Moving/resizing a layer in After Effects
- Positioning a sticker on a photo

This is an absolutely essential node for positioning elements in your composite!

## 🤔 When Would I Use This?

**Everyday uses:**
- 📐 **Position elements** - Move your AI-generated person to the right spot
- 🔄 **Rotate images** - Straighten a crooked photo or tilt for style
- 📏 **Scale images** - Make things bigger or smaller
- 🎬 **Match perspectives** - Use skew for basic perspective matching
- 🔧 **Fine-tune composites** - Nudge elements into perfect alignment
- 🎨 **Creative effects** - Rotate for dynamic angles, scale for emphasis

**Real examples:**
- Composite person on background but they're too large → Scale down to 0.7
- AI-generated object needs to be 50 pixels to the right → Translate X: 50
- Horizon line crooked → Rotate: -2.5 degrees
- Sign needs perspective correction → Skew X: 0.3

## 🎛️ Parameters Explained

### **Translate X & Y** ⭐⭐⭐
- **Range:** -4096 to +4096 pixels
- **Default:** 0.0 (no movement)
- **What it does:** Moves the image horizontally (X) or vertically (Y)
- **Positive values:**
  - X: Moves RIGHT
  - Y: Moves DOWN
- **Negative values:**
  - X: Moves LEFT
  - Y: Moves UP

**Examples:**
- Move 100 pixels right: `Translate X: 100`
- Move 50 pixels up: `Translate Y: -50`
- Move diagonally: `Translate X: 100, Translate Y: 75`

💡 **Tip:** Use small values (1-10) for fine-tuning, large values (100+) for repositioning!

---

### **Rotate** ⭐⭐⭐
- **Range:** -360 to +360 degrees
- **Default:** 0.0 (no rotation)
- **What it does:** Rotates the image around the center point
- **Positive values:** Clockwise rotation
- **Negative values:** Counter-clockwise rotation

**Examples:**
- Quarter turn right: `Rotate: 90`
- Slight tilt left: `Rotate: -5`
- Upside down: `Rotate: 180`

💡 **Beginner Tip:** Small rotations (±1-5 degrees) can make compositions feel more dynamic!

---

### **Scale X & Y** ⭐⭐⭐
- **Range:** 0.01 to 10.0
- **Default:** 1.0 (original size)
- **What it does:** Changes the size horizontally (X) or vertically (Y)
- **Less than 1.0:** Shrinks (0.5 = half size)
- **Greater than 1.0:** Enlarges (2.0 = double size)
- **Same X and Y:** Uniform scaling (maintains aspect ratio)
- **Different X and Y:** Non-uniform scaling (stretches)

**Examples:**
- Half size: `Scale X: 0.5, Scale Y: 0.5`
- Double size: `Scale X: 2.0, Scale Y: 2.0`
- Wide screen squish: `Scale X: 1.5, Scale Y: 0.8`
- Slight shrink: `Scale X: 0.9, Scale Y: 0.9`

💡 **Critical:** Keep X and Y the same for natural scaling! Different values stretch/squash unnaturally.

---

### **Skew X & Y** ⭐⭐ (Advanced)
- **Range:** -2.0 to +2.0
- **Default:** 0.0 (no skew)
- **What it does:** Slants the image (shears it)
- **Skew X:** Horizontal skew (makes image lean left/right)
- **Skew Y:** Vertical skew (makes image lean forward/backward)

**Think of it as:** Pushing the top of a rectangle while the bottom stays fixed

**Examples:**
- Italic text effect: `Skew X: 0.3`
- Perspective correction: `Skew X: -0.2, Skew Y: 0.1`

💡 **Beginner Tip:** Skew is tricky! Start with small values (±0.1-0.3). For serious perspective correction, use **CornerPin** instead!

---

### **Center X & Y** ⭐⭐
- **Range:** 0.0 to 1.0 (normalized, 0.5 = center)
- **Default:** 0.5, 0.5 (image center)
- **What it does:** Sets the pivot point for rotation, scale, and skew
- **0.0:** Left (X) or Top (Y)
- **0.5:** Center (default)
- **1.0:** Right (X) or Bottom (Y)

**Why it matters:**
- Rotating around center (0.5, 0.5) = spins in place
- Rotating around corner (0.0, 0.0) = orbits around top-left
- Scaling from center (0.5, 0.5) = grows equally in all directions
- Scaling from corner (0.0, 0.0) = grows right/down only

**Examples:**
- Rotate door around left edge: `Center X: 0.0, Center Y: 0.5`
- Scale from bottom-center: `Center X: 0.5, Center Y: 1.0`

💡 **Beginner Tip:** Leave at default (0.5, 0.5) unless you have a specific reason!

---

### **Filter** ⭐⭐
- **Options:** Nearest / Bilinear / Bicubic
- **Default:** Bilinear
- **What it does:** Quality of image resampling when transforming

**Filter types:**
- **Nearest:** Fastest, pixelated/blocky (use for pixel art only!)
- **Bilinear:** Fast, smooth, good quality (default - use this!)
- **Bicubic:** Highest quality, slower, sharpest (use for final renders)

💡 **Recommendation:** Use Bilinear for working, Bicubic for final output!

---

### **Edge Mode** ⭐⭐
- **Options:** Black / Clamp / Repeat
- **Default:** Black
- **What it does:** How to fill empty areas when image is moved/rotated

**Edge modes:**
- **Black:** Fill empty areas with black/transparent (most common!)
- **Clamp:** Stretch edge pixels outward (good for subtle extends)
- **Repeat:** Tile the image (rarely used, can create interesting effects)

**Examples:**
- Rotate 45 degrees, black corners: `Edge Mode: Black`
- Extend edges naturally: `Edge Mode: Clamp`

💡 **Beginner Tip:** Use Black for most compositing work!

## 💡 Tips & Tricks

### **Beginner Workflow:**

1. **Start with Translate** - Position the image where you want it
2. **Add Rotation** - If needed, rotate to match angle
3. **Adjust Scale** - Size it correctly
4. **Fine-tune** - Small adjustments to Translate for perfect alignment

**Skip Skew and Center unless you have specific needs!**

---

### **Professional Secrets:**

1. **Transform Order Matters!**
   - ComfyUI applies: Translate → Rotate → Scale → Skew (from center)
   - This means rotation happens around the center, THEN translation moves everything
   - For complex moves, you may need multiple Transform nodes

2. **Matching Elements to Background**
   - Load reference background
   - Overlay your element with Transform
   - Adjust Scale first (get size right)
   - Then Translate (get position right)
   - Then fine-tune Rotate if needed

3. **Uniform vs Non-Uniform Scaling**
   - **Uniform:** Same Scale X and Scale Y (preserves aspect ratio - natural!)
   - **Non-uniform:** Different Scale X and Scale Y (stretches - looks weird!)
   - **Rule:** Almost always use uniform scaling!

4. **The "Nudge" Technique**
   - For pixel-perfect positioning, use small Translate values
   - Try increments of 1-5 pixels for fine adjustments
   - Compare before/after by toggling the node

5. **Filter Quality for Different Tasks**
   - **Previewing/working:** Bilinear (fast)
   - **Scaling UP a lot (>2x):** Bicubic (sharper)
   - **Scaling DOWN a lot (<0.5x):** Bilinear is fine
   - **Final output:** Bicubic if you want max quality

6. **Center Point Tricks**
   - **Rotate around bottom:** `Center Y: 1.0` (person spinning on feet)
   - **Rotate around left edge:** `Center X: 0.0` (door opening)
   - **Zoom from top-left:** `Center X: 0.0, Center Y: 0.0` (classic zoom)

---

### **Common Mistakes:**

❌ **Using different Scale X and Scale Y** - Stretches unnaturally (unless intentional!)
❌ **Forgetting about Center point** - Unexpected rotation/scale behavior
❌ **Using Nearest filter** - Unless pixel art, this looks terrible!
❌ **Rotating without checking edges** - Black corners may be visible (use Merge to composite onto background!)
❌ **Over-rotating** - Use values beyond ±360 (just use -180 to +180 range)

## 📖 Example Workflow

**Goal:** Position and scale an AI-generated person onto a background photo

**Step 1: Load Images**
- Background photo (1920x1080)
- AI-generated person (2048x2048, too large!)

**Step 2: Add Transform Node**
- Connect person → Transform

**Step 3: Scale Down**
- Person is twice as large as needed
- **Scale X:** 0.5
- **Scale Y:** 0.5
- (Person is now 1024x1024)

**Step 4: Position**
- Need person on right side of frame
- **Translate X:** 400 (moves right)
- **Translate Y:** -50 (moves up slightly)

**Step 5: Fine-Tune**
- Person slightly tilted? Add **Rotate:** -2.5
- Not quite right position? Adjust Translate X: 420, Y: -45

**Step 6: Composite**
- Add **Merge** node
- Connect Transform → Foreground
- Connect Background → Background
- **Operation:** Over
- Done!

**Troubleshooting:**
- Person edges visible (black corners)? → That's normal after rotation! Merge onto background to hide.
- Person looks stretched? → Check Scale X and Scale Y are the same!
- Rotating around wrong point? → Adjust Center X/Y

---

**Goal:** Rotate an image to straighten a crooked horizon

**Step 1: Identify Tilt**
- Horizon line is tilted 3 degrees clockwise

**Step 2: Add Transform**
- Connect image → Transform

**Step 3: Rotate**
- **Rotate:** -3.0 (counter-clockwise to fix)
- (Horizon is now level!)

**Step 4: Handle Black Corners**
- Rotation creates black triangles in corners
- Option A: Crop the image (use Transform scale to zoom in slightly)
  - **Scale X:** 1.1, **Scale Y:** 1.1
- Option B: Use **Edge Mode: Clamp** to extend edges
- Option C: Leave black and crop later

Done! Horizon is straight!

## 🔗 Works Great With

**Before Transform:**
- **ChromaKeyer** - Key first, then position the keyed foreground
- **Premultiply** - If image has alpha, premultiply before transform (prevents edge artifacts)
- **Blur** - Blur before transforming (softening then positioning)

**After Transform:**
- **Merge** ⭐⭐⭐ - Composite the transformed element onto background
- **Blur** - Add motion blur or defocus after positioning
- **Grade** - Color correct after positioning
- **MatteControl** - Refine edges after transform

**Chaining Transforms:**
You can use multiple Transform nodes in sequence for complex movements:
- Transform 1: Rotate 45 degrees
- Transform 2: Scale 0.5
- Transform 3: Translate X: 100

**Works with Masks:**
- Transform a mask to reposition it
- Transform an alpha channel for alignment

## 📚 Learn More

### **Key Concepts:**

**Affine Transformations:**
- Transform node uses affine transformations (linear transformations + translation)
- Preserves parallel lines (won't create perspective distortion)
- Can do: translate, rotate, scale, skew, flip
- Cannot do: true perspective (use CornerPin for that!)

**Transform Order:**
- Order matters! Rotate-then-translate ≠ Translate-then-rotate
- Transform node order: Translate → Rotate → Scale → Skew (around Center)
- For different orders, chain multiple Transform nodes

**Interpolation (Filters):**
- **Nearest neighbor:** Just picks closest pixel (fast, blocky)
- **Bilinear:** Averages 4 nearest pixels (smooth, good quality)
- **Bicubic:** Averages 16 nearest pixels with cubic weighting (sharpest, slower)

**Normalized Coordinates:**
- Center X/Y use 0-1 range (normalized) not pixels
- 0.0 = left/top edge
- 0.5 = center
- 1.0 = right/bottom edge
- Works at any resolution!

### **Photoshop/After Effects Users:**

Coming from other software:
- **Photoshop "Free Transform" (Ctrl+T)** = This Transform node
- **Photoshop "Move Tool"** = Transform Translate only
- **After Effects "Position/Scale/Rotation"** = Transform parameters
- **Photoshop "Skew"** = Transform Skew X/Y
- **Photoshop "Transform → Rotate"** = Transform Rotate

**Key difference:** In node compositing, you transform THEN composite. In Photoshop, layers automatically composite as you transform!

### **When NOT to Use Transform:**

- **For perspective correction** → Use **CornerPin** instead (4-point perspective warp)
- **For lens distortion** → Use **DisplacementMap** with lens distortion maps
- **For organic warping** → Use **GridWarp** for free-form mesh deformation
- **For tracking/stabilization** → Use tracking data with Transform (or CornerPin)

### **Want to go deeper?**

- Learn **CornerPin** for screen replacement and perspective matching
- Study **affine transformation matrices** (how Transform actually works)
- Practice **transform hierarchies** (parent-child relationships)
- Read about **gimbal lock** in 3D rotations (not an issue in 2D!)
- Experiment with **Center point animation** for orbital motion

---

**Transform is your positioning workhorse!** Master translate, rotate, and scale, and you can position anything anywhere. Skew is optional until you need it. 🎯
