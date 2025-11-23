# Constant Node

**Category:** Generator
**Complexity:** ⭐ Beginner
**Also Known As:** Solid Color, Background, Color Generator

## 🎯 What Does This Do?

The **Constant node** creates a solid color image - every single pixel is exactly the same RGBA color. It's like painting an entire canvas with one color!

**Think of it like:**
- Photoshop's "New Layer → Fill with Color"
- A blank colored piece of paper
- The simplest image possible (no detail, just one color)

This is the starting point for many composites!

## 🤔 When Would I Use This?

**Everyday uses:**
- 🎨 **Solid backgrounds** - Create colored backgrounds for composites
- 🧪 **Testing** - Quick test pattern to verify workflows
- 🎭 **Mattes** - Create full white/black alpha masks
- 📏 **Color references** - Generate specific colors for matching
- 🌟 **HDR effects** - Create super-bright values for glows (>1.0)
- 📐 **Placeholders** - Temporary backgrounds while building composites

**Real examples:**
- Need white background for product shot → Red:1.0, Green:1.0, Blue:1.0
- Create full white matte → Red:1.0, Green:1.0, Blue:1.0, Alpha:1.0
- Black background → Red:0.0, Green:0.0, Blue:0.0 (default!)
- Green for testing → Red:0.0, Green:1.0, Blue:0.0
- HDR super-white for glow → Red:5.0, Green:5.0, Blue:5.0

## 🎛️ Parameters Explained

### **Width & Height** ⭐⭐⭐
- **Range:** 1 to 16384 pixels
- **Default:** 1920 x 1080 (Full HD)
- **What it does:** Sets the image dimensions
- **Common sizes:**
  - 1920x1080 (Full HD)
  - 3840x2160 (4K)
  - 1024x1024 (Square, common for AI)
  - 512x512 (Small square)

💡 **Tip:** Match your comp resolution! If compositing 4K, use 3840x2160.

---

### **Batch Size**
- **Range:** 1 to 4096
- **Default:** 1
- **What it does:** Creates multiple identical images
- **Use when:** Need repeated backgrounds or testing with batches

💡 **Beginner Tip:** Leave at 1 unless specifically needed!

---

### **Red, Green, Blue** ⭐⭐⭐
- **Range:** 0.0 to 10.0 (supports HDR!)
- **Default:** 0.0, 0.0, 0.0 (black)
- **What it does:** Sets the RGB color values

**Color mixing:**
- **Black:** R:0.0, G:0.0, B:0.0
- **White:** R:1.0, G:1.0, B:1.0
- **Red:** R:1.0, G:0.0, B:0.0
- **Green:** R:0.0, G:1.0, B:0.0
- **Blue:** R:0.0, G:0.0, B:1.0
- **Yellow:** R:1.0, G:1.0, B:0.0
- **Cyan:** R:0.0, G:1.0, B:1.0
- **Magenta:** R:1.0, G:0.0, B:1.0
- **Gray (50%):** R:0.5, G:0.5, B:0.5

💡 **HDR Values:** Values above 1.0 create "super-bright" colors for glow effects!

---

### **Alpha** ⭐⭐
- **Range:** 0.0 to 1.0
- **Default:** 1.0 (fully opaque)
- **What it does:** Sets transparency
  - **1.0:** Completely opaque (solid)
  - **0.5:** Half transparent
  - **0.0:** Completely transparent

**When to adjust:**
- Full matte (for masking) → Alpha: 1.0
- Transparent → Alpha: 0.0
- Semi-transparent overlay → Alpha: 0.3-0.7

💡 **Usually leave at 1.0** unless creating transparent backgrounds!

## 💡 Tips & Tricks

### **Common Color Recipes:**

**Standard Backgrounds:**
```
Black: R:0.0, G:0.0, B:0.0
White: R:1.0, G:1.0, B:1.0
Gray (18%): R:0.18, G:0.18, B:0.18 (photography middle gray)
Gray (50%): R:0.5, G:0.5, B:0.5
```

**Primary Colors:**
```
Red: R:1.0, G:0.0, B:0.0
Green: R:0.0, G:1.0, B:0.0
Blue: R:0.0, G:0.0, B:1.0
```

**Full Mattes:**
```
White Matte: R:1.0, G:1.0, B:1.0, Alpha:1.0
Black Matte: R:0.0, G:0.0, B:0.0, Alpha:1.0
```

---

### **Professional Secrets:**

1. **HDR Glow Effect**
   - Create super-bright Constant (R:5.0, G:5.0, B:5.0)
   - Blur it heavily (Size: 50-100)
   - Merge with Screen mode over image
   - Result: Brilliant glow/bloom!

2. **Quick Background Match**
   - Sample color from background (use eyedropper in image editor)
   - Enter RGB values in Constant
   - Use as placeholder while building composite
   - Replace with real background later

3. **Testing Composites**
   - Bright green (R:0.0, G:1.0, B:0.0) to test alpha edges
   - Bright magenta (R:1.0, G:0.0, B:1.0) to spot missing coverage
   - Any bright, ugly color makes problems obvious!

4. **Color Reference Card**
   - Create Constant with specific color
   - Save as reference for color matching
   - Composite next to image for comparison

5. **Full Frame Matte**
   - Instead of complex masking, use Constant
   - R:1.0, G:1.0, B:1.0 = full white matte
   - Use with Merge to isolate image

---

### **Common Mistakes:**

❌ **Forgetting HDR values** - Using 1.0 when 5.0+ would create better effects
❌ **Wrong resolution** - Creating 1920x1080 for a 4K comp (mismatched!)
❌ **Alpha confusion** - Setting Alpha:0.0 then wondering why output is transparent!
❌ **Not using for testing** - Building complex comp without simple test background first

## 📖 Example Workflow

**Goal:** Create simple composite with colored background

**Step 1: Create Background**
- Add **Constant** node
- **Width:** 1920, **Height:** 1080
- **Red:** 0.2, **Green:** 0.3, **Blue:** 0.5 (nice blue-gray)
- **Alpha:** 1.0
- (Created solid blue-gray background)

**Step 2: Composite Foreground**
- Have: Keyed person (from ChromaKeyer)
- Add **Merge** node
- Connect Person → Foreground
- Connect Constant → Background
- **Operation:** Over
- Done!

**Result:** Person on solid colored background!

---

**Goal:** Create HDR glow effect

**Step 1: Create Super-Bright Constant**
- Add **Constant** node
- **Width/Height:** Match your image
- **Red:** 5.0, **Green:** 4.0, **Blue:** 3.0 (warm super-bright!)
- (Way brighter than normal!)

**Step 2: Blur the Glow**
- Connect Constant → **Blur**
- **Size X:** 100, **Size Y:** 100
- (Creates huge soft glow)

**Step 3: Composite with Screen**
- Add **Merge** node
- Connect Original Image → Background
- Connect Blurred Constant → Foreground
- **Operation:** Screen
- **Mix:** 0.3 (30% glow)
- Done!

**Result:** Beautiful warm glow overlay!

---

**Goal:** Quick testing background (bright green to spot issues)

**Step 1: Create Test Background**
- Add **Constant** node
- **Width/Height:** Match comp
- **Red:** 0.0, **Green:** 1.0, **Blue:** 0.0 (bright green)
- **Alpha:** 1.0

**Step 2: Composite Your Work**
- Connect your composite → **Merge** Foreground
- Connect Green Constant → **Merge** Background
- **Operation:** Over

**Step 3: Check for Problems**
- Any green showing through? → Alpha matte has holes!
- Green fringe around edges? → Need MatteControl!
- All green hidden? → Perfect matte!

**Result:** Obvious test background makes problems visible!

## 🔗 Works Great With

**After Constant:**
- **Merge** ⭐⭐⭐ - Use Constant as background for composites
- **Blur** - Blur Constant for soft colored backgrounds or glows
- **Grade** - Adjust Constant color after creation
- **Noise** → **Merge (Screen)** - Add texture to flat Constant background

**Creating Mattes:**
- **Constant** (white) → Use as full-frame matte
- **Constant** → **Shuffle** → Use as mask source

**Testing Workflows:**
- **Constant** (bright color) → Test backgrounds
- **Constant** → **Merge** → Verify alpha coverage

**HDR Effects:**
- **Constant** (>1.0) → **Blur** → **Merge (Screen)** = Glow effect
- **Constant** (>1.0) → Light leaks, lens flares

## 📚 Learn More

### **Key Concepts:**

**RGB Color Mixing:**
- **Additive color:** Red + Green = Yellow
- **All three:** Red + Green + Blue = White
- **None:** No color = Black
- Colors are light, not paint!

**HDR (High Dynamic Range):**
- Normal images: 0.0 to 1.0
- HDR images: Can go above 1.0 (super-bright!)
- Use for: Glows, blooms, light effects
- Constant supports up to 10.0 (way overbright!)

**Premultiplied Alpha:**
- Constant outputs premultiplied alpha by default
- RGB already multiplied by Alpha
- If Alpha < 1.0, RGB values are darkened
- This is correct for Merge operations!

### **Photoshop/After Effects Users:**

Coming from other software:
- **Photoshop "New Layer → Fill"** = Constant node
- **Photoshop "Solid Color Fill Layer"** = Constant node
- **After Effects "Solid Layer"** = Constant node
- **Constant + Merge** = Photoshop background layer

**Key difference:** In node compositing, you create background THEN composite. In Photoshop, layers composite automatically!

### **When NOT to Use Constant:**

- **For gradients** → Use **Gradient** node instead
- **For noise/grain** → Use **Noise** node instead
- **For complex backgrounds** → Load actual image
- **For patterns** → Use **Checkerboard** or procedural generators

### **Want to go deeper?**

- Learn **RGB color theory** (additive vs subtractive)
- Study **HDR imaging** and why values >1.0 are useful
- Practice **color matching** (sampling and recreating colors)
- Experiment with **HDR glows** and light effects
- Read about **premultiplied vs straight alpha** (why Constant outputs premult)

---

**Constant is the simplest generator!** Perfect for solid backgrounds, testing, and HDR effects. Master color values (0.0-1.0 for normal, >1.0 for HDR) and you're set! 🎨
