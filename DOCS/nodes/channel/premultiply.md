# Premultiply & Unpremultiply Nodes

**Category:** Channel
**Complexity:** ⭐⭐ Intermediate (concept is tricky, usage is simple!)
**Also Known As:** Premult/Unpremult, Straight vs Associated Alpha

## 🎯 What Do These Do?

These nodes convert between two different ways of storing transparency in images:

- **Premultiply:** Multiply RGB by alpha (prepare for compositing)
- **Unpremultiply:** Divide RGB by alpha (prepare for color correction)

**Think of it like:**
- Converting between different "formats" for transparency
- Like converting between Celsius and Fahrenheit - same temperature, different representation
- Essential plumbing for professional compositing!

**Critical to understand:** This is NOT optional when working with transparency! Using the wrong format causes edge halos and color shifts.

## 🤔 When Would I Use These?

### **Unpremultiply** - Use BEFORE:
- ✏️ **Color correction** (Grade, ColorCorrect nodes)
- 🎨 **Painting/editing transparent areas**
- 🔧 **Any RGB manipulation** on images with alpha

### **Premultiply** - Use BEFORE:
- 🎬 **Compositing** (Merge operations)
- 🔄 **Transforms** (rotating, scaling images with alpha)
- 🌫️ **Blurring/filtering** images with alpha

### **The Golden Rule:**
**Unpremult → Edit RGB → Premult → Composite**

This is THE most important workflow in compositing!

## 🎛️ What's the Difference? (Premult vs Straight Alpha)

### **Straight Alpha** (Unpremultiplied)
- RGB and Alpha stored separately
- RGB contains "original" colors, even in transparent areas
- Formula: Just RGB and A as separate channels
- **Use for:** Editing, color correction, painting

**Example:**
- Pixel: Red=1.0, Green=0.0, Blue=0.0, Alpha=0.5
- You see: Bright red, half transparent
- RGB values independent of alpha

### **Premultiplied Alpha** (Associated Alpha)
- RGB already multiplied by Alpha
- RGB darkened based on transparency
- Formula: RGB_premult = RGB_straight × Alpha
- **Use for:** Compositing, filtering, transforms

**Same example premultiplied:**
- Original: R=1.0, G=0.0, B=0.0, A=0.5
- Premultiplied: R=0.5, G=0.0, B=0.0, A=0.5
- Notice RGB is now 0.5 (half as bright because half transparent!)

## 🔍 Why Does This Matter?

### **Problem 1: Color Correction on Premult = Halos!**

Scenario: You have a keyed person (premultiplied) and want to Grade them brighter.

**Wrong way** (causes halos):
```
ChromaKeyer → Grade (brighten) → Merge
```
- Grade brightens the already-dark edge pixels
- Creates bright fringe/halo around edges!
- Looks terrible!

**Right way:**
```
ChromaKeyer → Unpremultiply → Grade (brighten) → Premultiply → Merge
```
- Unpremult restores original RGB
- Grade adjusts original colors correctly
- Premult prepares for compositing
- Perfect edges!

### **Problem 2: Compositing Straight Alpha = Wrong Colors!**

Scenario: You want to composite a straight alpha image.

**Wrong way** (incorrect blending):
```
Straight Alpha Image → Merge
```
- Merge expects premultiplied!
- Gets wrong RGB values for edges
- Color shifts, too-bright edges!

**Right way:**
```
Straight Alpha Image → Premultiply → Merge
```
- Premult converts to expected format
- Merge composites correctly
- Clean edges!

## 🎛️ Parameters Explained

### **Premultiply Node**
- **Input:** Image (RGB or RGBA)
- **Output:** Premultiplied RGBA
- **No parameters** - just does the multiplication!

**What it does:**
```
result.r = input.r × input.a
result.g = input.g × input.a
result.b = input.b × input.a
result.a = input.a (unchanged)
```

**If input is RGB (no alpha):**
- Adds alpha channel of 1.0 (fully opaque)
- Result is premultiplied RGBA (but looks same since alpha=1.0)

---

### **Unpremultiply Node**

**Parameters:**

#### **Epsilon** (Advanced)
- **Range:** 1e-10 to 1e-5
- **Default:** 1e-7
- **What it does:** Prevents division by zero
- **When alpha=0:** Division would be infinity! Epsilon prevents this.

💡 **Beginner Tip:** Leave at default! Only adjust if you see artifacts.

#### **Clamp Output**
- **Type:** Checkbox (True/False)
- **Default:** False
- **What it does:** Limits RGB values to max_value
- **Why:** Unpremultiply can create >1.0 values in edge pixels

**When to enable:**
- Getting super-bright edge pixels after unpremult
- Want to limit "hot" edge values
- Preparing for 8-bit export

💡 **Usually leave unchecked!** Only enable if you see problems.

#### **Max Value** (Advanced)
- **Range:** 1.0 to 100.0
- **Default:** 10.0
- **What it does:** Maximum RGB value when clamping
- **Only active if Clamp Output = True**

💡 **Beginner Tip:** Ignore unless using Clamp Output!

**What Unpremultiply does:**
```
result.r = input.r / (input.a + epsilon)
result.g = input.g / (input.a + epsilon)
result.b = input.b / (input.a + epsilon)
result.a = input.a (unchanged)
```

## 💡 Tips & Tricks

### **Beginner Workflow - The Standard Pipeline:**

**For Keying:**
```
1. ChromaKeyer (outputs premult)
2. Unpremultiply
3. Grade (color correct)
4. Premultiply
5. Merge (composite)
```

This is THE standard greenscreen workflow!

---

**For Loading Images:**
```
1. Load image (might be straight or premult - check!)
2. If straight: Premultiply before compositing
3. Merge
```

---

**For Editing:**
```
1. Premultiplied image
2. Unpremultiply
3. Edit/paint/adjust
4. Premultiply
5. Composite
```

---

### **Professional Secrets:**

1. **How to Tell if Image is Premult or Straight?**
   - **Look at edges:** Premult has dark edge fringe, straight has full-color edges
   - **Zoom into transparent area:** Premult = dark RGB, straight = visible RGB colors
   - **Check source:** Keyers output premult, painters output straight
   - **When in doubt:** Assume premult from compers, straight from painters!

2. **The "Unpremult Before Grade" Rule**
   - **ALWAYS unpremult before Grade/ColorCorrect!**
   - Even slight adjustments on premult cause edge issues
   - Workflow: Unpremult → Grade → Premult (sacred rule!)

3. **Premult for Transforms/Filters**
   - Rotating straight alpha = color smearing at edges!
   - Blurring straight alpha = wrong edge colors!
   - **Always premult before Transform/Blur if image has alpha!**

4. **Edge Artifacts from Unpremult**
   - Very thin alpha edges can create >1.0 RGB values when unpremulted
   - Caused by: RGB > Alpha in edge pixels (shouldn't happen, but does!)
   - Fix: Enable **Clamp Output: True**, **Max Value: 2.0-5.0**
   - Rare issue, but good to know!

5. **Premult is NOT Lossy!**
   - Premult → Unpremult → back to original (in theory)
   - In practice: Epsilon and precision mean tiny differences
   - **Don't premult/unpremult unnecessarily!**
   - Only when changing between edit and composite modes

6. **Alpha=0 Areas Don't Matter!**
   - Fully transparent areas: RGB values don't matter (not visible!)
   - Unpremult creates "weird" RGB values in transparent areas - that's OK!
   - Only edges (0.0 < alpha < 1.0) matter for compositing

---

### **Common Mistakes:**

❌ **Grading premultiplied images** - Creates edge halos (always unpremult first!)
❌ **Compositing straight alpha** - Wrong colors (premult before Merge!)
❌ **Premult/unpremult repeatedly** - Unnecessary, adds precision errors
❌ **Worrying about RGB in alpha=0 areas** - Doesn't matter, not visible!
❌ **Forgetting to premult after unpremult** - Breaks compositing!

## 📖 Example Workflow

**Goal:** Color grade a greenscreen-keyed person

**Wrong Way (causes halos):**
```
ChromaKeyer → Grade → Merge
```
❌ **Result:** Bright fringe around person!

**Right Way:**
```
1. ChromaKeyer (keyed person, premultiplied)
2. Unpremultiply (convert to straight alpha)
3. Grade (adjust Lift: -0.05, Gamma: 1.1, etc.)
4. Premultiply (convert back to premult)
5. Merge (composite onto background)
```
✅ **Result:** Clean edges, perfect color!

**Why this works:**
- ChromaKeyer outputs premultiplied alpha (edge RGB already darkened)
- Unpremultiply restores full RGB values for editing
- Grade adjusts the "real" colors
- Premultiply darkens edges again correctly
- Merge composites with proper edge blending

---

**Goal:** Composite a straight alpha image from a painter

**Problem:** You have a painted image (Photoshop, Krita, etc.) - straight alpha!

**Wrong Way:**
```
Load Image → Merge
```
❌ **Result:** Weird color shifts, bright edges!

**Right Way:**
```
1. Load Image (straight alpha from painter)
2. Premultiply (convert to premult for compositing)
3. Merge (composite onto background)
```
✅ **Result:** Perfect composite!

---

**Goal:** Transform (rotate) an image with alpha

**Wrong Way (straight alpha):**
```
Straight Alpha → Transform (Rotate: 45) → Merge
```
❌ **Result:** Color smearing at edges!

**Right Way:**
```
1. Straight Alpha Image
2. Premultiply
3. Transform (Rotate: 45)
4. Merge
```
✅ **Result:** Clean rotation with correct edge blending!

**Why?** Transform interpolates pixel values. Interpolating premultiplied alpha maintains correct edge darkening. Interpolating straight alpha blends full-color edge pixels incorrectly!

## 🔗 Works Great With

**Unpremultiply BEFORE:**
- **Grade** ⭐⭐⭐ - ALWAYS unpremult before grading!
- **ColorCorrect** ⭐⭐⭐ - ALWAYS unpremult before color adjusting!
- **HSVAdjust** - ALWAYS unpremult before HSV manipulation!
- **Any color edit nodes!** - General rule: unpremult first!

**Premultiply AFTER:**
- Above color corrections (after editing, premult again!)

**Premultiply BEFORE:**
- **Merge** ⭐⭐⭐ - Merge expects premult!
- **Transform** - Prevents edge smearing
- **Blur** - Correct edge blurring
- **Any filtering** - Prevents color contamination

**Complete Workflows:**
```
ChromaKeyer → Unpremult → Grade → Premult → Merge
Load Straight → Premult → Transform → Merge
Premult Image → Unpremult → Paint/Edit → Premult → Merge
```

## 📚 Learn More

### **Key Concepts:**

**Mathematical Definition:**

**Premultiply (Straight → Premult):**
```
R_premult = R_straight × A
G_premult = G_straight × A
B_premult = B_straight × A
A_premult = A (unchanged)
```

**Unpremultiply (Premult → Straight):**
```
R_straight = R_premult / (A + ε)
G_straight = G_premult / (A + ε)
B_straight = B_premult / (A + ε)
A_straight = A (unchanged)
```
Where ε (epsilon) prevents division by zero.

---

**Why Premultiplied Exists:**

**Mathematical correctness for blending:**
- Porter-Duff compositing equations assume premult alpha!
- Formula: `C_out = C_fg + C_bg × (1 - A_fg)`
- This ONLY works if C_fg is premultiplied!

**Filtering correctness:**
- Blurring mixes neighboring pixels
- If straight alpha: Mixes full-color transparent pixels = color contamination!
- If premult: Transparent pixels are dark, mixing works correctly!

---

**Industry Standards:**

- **3D renders:** Usually premultiplied (correct for compositing)
- **Paint programs:** Usually straight alpha (easier to edit)
- **Keyers:** Always premultiplied (mathematically correct)
- **Compositors:** Expect premultiplied for Merge operations
- **When in doubt:** Assume premult for comp, straight for paint!

### **Nuke/Fusion/After Effects Users:**

Coming from other software:
- **Nuke "Premult" node** = This Premultiply node
- **Nuke "Unpremult" node** = This Unpremultiply node
- **After Effects "Straight/Premult" interpretation** = Same concept!
- **Fusion "Premultiply/Unpremultiply"** = Same nodes

**Workflow is identical across all professional compositors!**

### **Deep Dive - Edge Cases:**

**"Inverse Premultiply" Problem:**
```
Unpremult a pixel: R=0.5, A=0.1
Result: R = 0.5 / 0.1 = 5.0 (!!)
```
- RGB value explodes to 5.0 (way above 1.0!)
- This is why **Clamp Output** option exists
- Shouldn't happen with proper keying, but can occur with bad mattes

**"Black-Halo" Problem:**
- Straight alpha with RGB=0 in transparent areas
- Premult makes edge pixels darker than they should be
- Fix: Paint transparent areas with nearby colors (matte painting technique)
- Or: Use "Remove Black Matte" / "Remove White Matte" nodes

### **Want to go deeper?**

- Study **Porter-Duff compositing equations** (foundational alpha math)
- Learn **associated vs unassociated alpha** (technical terms)
- Read **"Compositing Digital Images" by Tom Porter & Tom Duff** (original paper!)
- Understand **pre-multiplication in linear vs sRGB color space**
- Research **edge matte contamination** and how to fix it

---

**Premult/Unpremult are essential but invisible!** Learn the golden rule: **Unpremult → Edit → Premult → Composite**. Get this right and you'll never have edge halos! 🎨
