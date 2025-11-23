# MatteControl Node

**Category:** Matte
**Complexity:** ⭐⭐⭐ Advanced
**Also Known As:** Matte Refinement, FilterErode (Nuke), MatteControl (Fusion)

## 🎯 What Does This Do?

The **MatteControl node** is an all-in-one professional tool for cleaning up and refining alpha mattes (transparency masks) - it's like Photoshop's Levels + Blur + Refine Edge all in one node!

**Think of it like:**
- Photoshop's "Select and Mask" refinement tools
- After Effects' "Matte Choker"
- A complete matte cleanup workshop in a single node

This is THE node professional compositors use after keying to perfect their mattes!

## 🤔 When Would I Use This?

**Essential uses:**
- 🔑 **After greenscreen keying** - Clean up ChromaKeyer output
- ✂️ **Fix keying edges** - Remove green fringe, soften hard edges
- 🎭 **Refine AI-generated masks** - Clean up imperfect AI masks
- 🖌️ **After rotoscoping** - Polish hand-drawn mattes
- 🔧 **Matte manipulation** - Shrink/expand transparency areas
- 🌟 **Edge quality** - Make amateur keys look professional

**Real examples:**
- ChromaKeyer left slight green fringe → Erode: -2 to shrink matte, removing fringe
- Keyed matte has hard, jaggy edges → Blur: 3 to soften edges naturally
- Matte has gray/semi-transparent noise → Black Point: 0.1, White Point: 0.9 to clean it up
- Rotoscoped matte too thin → Dilate: +3 to expand matte slightly

## 🎛️ Parameters Explained

MatteControl applies operations in this specific order:
1. **Erode/Dilate** (shrink/expand)
2. **Blur** (soften edges)
3. **Gamma** (adjust density)
4. **Black/White Point** (clip values)

Understanding this order is key to using the node effectively!

---

### **Erode/Dilate** ⭐⭐⭐ Most Powerful!
- **Range:** -100.0 to +100.0
- **Default:** 0.0 (no change)
- **What it does:**
  - **Negative values (Erode):** Shrinks the matte (eats away edges)
  - **Positive values (Dilate):** Expands the matte (grows outward)

**Think of it as:** A "choke" control for transparency

**When to use Erode (negative):**
- ❌ **Remove edge contamination** - Green/blue fringe from keying
- ❌ **Tighten loose mattes** - AI masks that are too generous
- ❌ **Remove edge noise** - Cleanup rough keying
- Example: `Erode/Dilate: -2.0` (shrinks matte by ~2 pixels)

**When to use Dilate (positive):**
- ✅ **Expand thin mattes** - Rotoscoping that's too tight
- ✅ **Recover lost edges** - Keying that ate into subject
- ✅ **Grow mattes** - Need more coverage
- Example: `Erode/Dilate: +3.0` (expands matte by ~3 pixels)

💡 **Pro Tip:** Start with small values (±0.5-2.0), large values (±10+) create obvious effects!

**Common workflow:**
1. Key with ChromaKeyer
2. See slight green edge? → Erode: -1.5 (shrinks matte slightly, removes fringe!)
3. Perfect!

---

### **Blur** ⭐⭐⭐
- **Range:** 0.0 to 100.0 pixels
- **Default:** 0.0 (no blur)
- **What it does:** Softens matte edges with Gaussian blur

**Why soften matte edges?**
- Hard edges look "cut out with scissors" (amateur!)
- Soft edges blend naturally (professional!)
- Real photography has soft focus transitions

**Blur amounts:**
- **0.5-2.0:** Subtle softening (most common)
- **3.0-5.0:** Noticeable softening (for motion blur or soft subjects)
- **10.0+:** Heavy softening (artistic, or very out-of-focus edges)

💡 **Critical:** Blur AFTER Erode/Dilate! That's why this node does them in that order.

**Example workflow:**
1. Erode: -1.5 (remove fringe)
2. Blur: 2.0 (soften the now-tight edge)
3. Result: Clean, soft edge!

---

### **Gamma** ⭐⭐
- **Range:** 0.1 to 10.0
- **Default:** 1.0 (no change)
- **What it does:** Adjusts overall matte density
  - **< 1.0:** Lighter matte (more opaque/white)
  - **> 1.0:** Darker matte (more transparent/black)

**Think of it as:** Matte "density" or "strength"

**When to use:**
- **Gamma: 0.7-0.9** - Strengthen weak mattes (semi-transparent areas become more opaque)
- **Gamma: 1.1-1.5** - Weaken strong mattes (reduce opacity overall)

**Common uses:**
- Keyed subject too transparent → Gamma: 0.8 (makes matte stronger)
- Matte too aggressive → Gamma: 1.2 (makes matte weaker)

💡 **Beginner Tip:** Usually leave at 1.0 unless matte density is wrong!

---

### **Black Point** ⭐⭐
- **Range:** 0.0 to 1.0
- **Default:** 0.0
- **What it does:** Values below this become pure black (0.0 = fully transparent)

**Think of it as:** "Anything darker than X becomes completely transparent"

**Why use it:**
- Clean up gray noise in transparent areas
- Force semi-transparent pixels to full transparency
- Remove subtle keying artifacts

**Example:**
- Matte has values 0.0-0.05 in background (should be 0.0)
- Set **Black Point: 0.05**
- Now anything ≤ 0.05 becomes 0.0 (pure transparent)

💡 **Use sparingly!** Typically 0.0-0.1 range. Higher values eat into your matte!

---

### **White Point** ⭐⭐
- **Range:** 0.0 to 1.0
- **Default:** 1.0
- **What it does:** Values above this become pure white (1.0 = fully opaque)

**Think of it as:** "Anything brighter than X becomes completely opaque"

**Why use it:**
- Clean up near-white values that should be pure white
- Force semi-opaque pixels to full opacity
- Solidify mattes

**Example:**
- Matte has values 0.95-1.0 in solid areas (should be 1.0)
- Set **White Point: 0.95**
- Now anything ≥ 0.95 becomes 1.0 (pure opaque)

💡 **Use sparingly!** Typically 0.9-1.0 range.

**Black + White Point Together:**
Create a "levels" adjustment:
- **Black Point: 0.1, White Point: 0.9**
- Remaps 0.1-0.9 range to 0.0-1.0
- Result: Increased contrast in matte, cleaner blacks and whites!

---

### **Preview Mode** ⭐⭐⭐
- **Options:** Final / After Erode/Dilate / After Blur / After Gamma
- **Default:** Final
- **What it does:** Shows intermediate stages of processing

**Why this is amazing:**
- See exactly what each stage does!
- Debug matte problems
- Understand the processing pipeline

**How to use:**
1. Set to "After Erode/Dilate" → See if erode/dilate is correct
2. Set to "After Blur" → See if blur amount is right
3. Set to "After Gamma" → See gamma effect
4. Set to "Final" → See complete result

💡 **Pro Workflow:** Use preview modes while adjusting, switch to Final when done!

## 💡 Tips & Tricks

### **Beginner Workflow (After Keying):**

Standard matte cleanup after ChromaKeyer:

1. **Remove edge fringe**
   - **Erode/Dilate:** -1.0 to -2.0 (shrinks matte slightly)
   - (Removes green/blue fringe pixels)

2. **Soften edges**
   - **Blur:** 1.5 to 3.0
   - (Makes edges natural and soft)

3. **Clean up values**
   - **Black Point:** 0.02 (force dark gray to black)
   - **White Point:** 0.98 (force light gray to white)
   - (Cleaner, punchier matte)

4. **Check result**
   - **Preview Mode:** Final
   - (Inspect final matte)

Done! Professional-quality matte!

---

### **Professional Secrets:**

1. **The "Choke and Blur" Technique** (Most Common!)
   - Erode (choke) to remove fringe: -1.5
   - Blur to soften the chokeoned edge: 2.0
   - Result: Clean, soft edge with no fringe!
   - This is THE standard matte refinement workflow!

2. **Fixing "Gray Matte" Problem**
   - Problem: Matte looks washed out (too many gray values)
   - Solution:
     - **Black Point:** 0.1 (darken transparent areas)
     - **White Point:** 0.9 (solidify opaque areas)
     - **Gamma:** 0.9 (strengthen overall)
   - Result: Punchy, clean matte!

3. **The "Grow and Soften" for Hair**
   - Fine hair needs EXPANSION not contraction
   - **Erode/Dilate:** +1.0 to +2.0 (grows matte outward)
   - **Blur:** 3.0 to 5.0 (soft for fine detail)
   - Result: Hair mattes preserved!

4. **Dealing with Noise**
   - Problem: Matte has speckles/noise
   - Solution:
     - **Blur:** 2.0-3.0 (smooths noise)
     - **Black Point:** 0.15 (kills dark noise)
     - **White Point:** 0.85 (kills light noise)
   - Then use **Median** filter if noise persists

5. **Preview Mode Debugging**
   - Matte looks wrong? Use Preview Modes!
   - Check "After Erode/Dilate" → Is shrink/expand correct?
   - Check "After Blur" → Is blur the right amount?
   - Check "After Gamma" → Is density OK?
   - Find the problem stage, adjust that parameter!

6. **When to Skip Parameters**
   - **No fringe?** → Leave Erode/Dilate at 0.0
   - **Edges already soft?** → Leave Blur at 0.0
   - **Matte density good?** → Leave Gamma at 1.0
   - **Clean values?** → Leave Black/White Point at 0.0/1.0
   - Don't adjust what doesn't need fixing!

---

### **Common Mistakes:**

❌ **Too much erode** - Eats into subject (loss of detail, especially hair!)
❌ **No blur after erode** - Hard, unnatural edges
❌ **Extreme black/white points** - Loss of edge softness (kills semi-transparency)
❌ **Forgetting preview mode** - Not understanding what each stage does
❌ **Using MatteControl on RGB images** - This is for MASKS only! Use on alpha channel or mask!

## 📖 Example Workflow

**Goal:** Clean up greenscreen key with edge fringe

**Step 1: Key the Greenscreen**
- Use **ChromaKeyer** on greenscreen footage
- Get initial matte (has slight green fringe!)

**Step 2: Add MatteControl**
- Connect keyed image → **MatteControl**
- (MatteControl works on IMAGE with alpha channel - automatically processes the alpha!)

**Wait - MatteControl takes MASK input!**

**Correct Step 2: Extract Alpha to MASK**
- Use **Shuffle** node to extract alpha channel to MASK
- Connect MASK → **MatteControl**

**Step 3: Remove Fringe**
- **Erode/Dilate:** -1.5 (shrink matte by ~1.5 pixels)
- **Preview Mode:** After Erode/Dilate
- (Check that fringe is removed but subject not eaten away)

**Step 4: Soften Edge**
- **Blur:** 2.5 (soften the tightened edge)
- **Preview Mode:** After Blur
- (Check edges are naturally soft)

**Step 5: Clean Up Values**
- **Black Point:** 0.03 (clean background to pure black)
- **White Point:** 0.97 (solid foreground to pure white)
- **Preview Mode:** Final
- (Check final result - should be clean!)

**Step 6: Apply to Image**
- Use **SetAlpha** to put refined matte back on keyed RGB
- (Now have clean keyed image!)

**Step 7: Composite**
- Use **Merge** to composite onto new background
- Done!

**Result:** Professional greenscreen composite with no fringe!

---

**Goal:** Fix weak, washed-out matte

**Problem:** Matte from AI mask tool has lots of gray, not punchy

**Step 1: Add MatteControl**
- Connect weak MASK → **MatteControl**

**Step 2: Increase Contrast**
- **Black Point:** 0.2 (force dark gray to black)
- **White Point:** 0.8 (force light gray to white)
- (This remaps 0.2-0.8 range to 0.0-1.0 = more contrast!)

**Step 3: Strengthen Matte**
- **Gamma:** 0.85 (makes matte denser overall)

**Step 4: Soften Edges**
- **Blur:** 1.5 (slight softness)

Done! Matte is now punchy and clean!

## 🔗 Works Great With

**Before MatteControl:**
- **ChromaKeyer** ⭐⭐⭐ - Key first, then refine matte
- **LumaKeyer** - Any keying tool, then MatteControl
- **RotoBezier** - Hand-drawn mattes, then refine
- **Shuffle** - Extract alpha to MASK for MatteControl

**After MatteControl:**
- **SetAlpha** ⭐⭐⭐ - Put refined matte back on RGB image
- **Merge** - Composite with refined matte
- **Median** - If matte still has noise, use Median filter after
- **Erode** - If need more precise control, use dedicated Erode node

**Matte Workflow Chain:**
Typical professional workflow:
1. **ChromaKeyer** → Extract initial key
2. **Shuffle** → Extract alpha to MASK
3. **MatteControl** → Refine matte
4. **SetAlpha** → Put refined matte back on RGB
5. **Premultiply** → Prepare for compositing
6. **Merge** → Final composite

**For Advanced Mattes:**
- **MatteControl + Erode** - Use MatteControl for initial cleanup, Erode for precise control
- **MatteControl + MatteControl** - Chain two for complex refinement (rare but powerful!)
- **MatteControl + EdgeBlur** - Refine overall matte, then blur only edges

## 📚 Learn More

### **Key Concepts:**

**Erosion vs Dilation:**
- Mathematical morphology operations
- **Erosion:** Shrinks white areas, expands black areas
- **Dilation:** Expands white areas, shrinks black areas
- Uses structuring element (kernel) - MatteControl uses ellipse/circle
- Iterative: larger values = multiple passes

**Why Erode Before Blur?**
- Erode removes fringe pixels (contaminated edge)
- Then blur softens the new (clean) edge
- If you blur first, then erode, the blurred fringe gets pulled inward!
- Order matters!

**Black/White Point (Levels):**
- Same math as Photoshop/Grade Levels
- Remaps input range to 0-1 output
- Formula: `output = clamp((input - black) / (white - black), 0, 1)`
- Increases contrast by crushing blacks and whites

**Gamma on Mattes:**
- Gamma < 1.0: Brightens midtones (matte becomes more opaque)
- Gamma > 1.0: Darkens midtones (matte becomes more transparent)
- Non-linear! Affects semi-transparent areas most
- Useful for adjusting edge softness density

### **Photoshop Users:**

MatteControl combines several Photoshop tools:
- **Erode/Dilate** = Select → Modify → Contract/Expand
- **Blur** = Gaussian Blur on mask
- **Black/White Point** = Levels on mask (input black/white sliders)
- **Gamma** = Levels on mask (middle slider)

**Key difference:** MatteControl does all in proper order automatically! In Photoshop, you'd need to manually chain these operations.

### **Professional Keying Workflow:**

Industry standard for greenscreen:
1. **Key** - ChromaKeyer for initial extraction
2. **Core Matte** - MatteControl with slight erode (clean core)
3. **Edge Matte** - Second key for edges (more tolerance)
4. **Combine** - Merge core + edge mattes
5. **Final Refinement** - MatteControl on combined matte
6. **Despill** - Remove color contamination from RGB
7. **Composite** - Merge onto background

MatteControl is used at least twice in pro workflows!

### **Want to go deeper?**

- Learn **mathematical morphology** (erosion, dilation, opening, closing)
- Study **edge detection** and how to use it with mattes
- Practice **matte painting** techniques
- Read about **garbage mattes** and **holdout mattes**
- Experiment with **edge mattes** vs **core mattes** separation

---

**MatteControl is the matte refinement powerhouse!** Master the "choke and blur" technique (erode + blur) and you'll fix 90% of keying problems. Use preview modes to understand what each stage does. 🎭
