# ColorCorrect Node

**Category:** Color
**Complexity:** ⭐⭐ Intermediate
**Also Known As:** Color Correction, Quick Color Adjust, ColorCorrector (Fusion)

## 🎯 What Does This Do?

The **ColorCorrect node** provides quick, intuitive color adjustments - think of it as Photoshop's adjustment layers or Lightroom's basic panel in a single node!

**Think of it like:**
- Photoshop's Hue/Saturation + Brightness/Contrast combined
- Lightroom's Basic panel
- Instagram filter controls (but with precision!)
- "Quick fix" color adjustments

**Key difference from Grade:**
- **Grade:** Film-style color grading (Lift/Gamma/Gain workflow) - surgical precision
- **ColorCorrect:** Layer matching (Saturation/Contrast/Gamma) - quick adjustments

Use ColorCorrect for fast tweaks, Grade for serious color work!

## 🤔 When Would I Use This?

**Everyday uses:**
- 🎨 **Quick color tweaks** - Fast saturation, contrast adjustments
- 🌈 **Match composite layers** - Make foreground match background colors
- 💡 **Brighten/darken images** - Simple exposure adjustments
- 🎭 **Desaturate for B&W** - Quick grayscale conversion
- 🔄 **Hue shifts** - Change color temperature or create stylistic looks
- ⚡ **Fix flat images** - Add punch with contrast
- 🔧 **Before serious grading** - Get image "in the ballpark" first

**Real examples:**
- AI-generated person too saturated → Saturation: 0.7
- Image looks flat → Contrast: 1.3
- Colors too cool (bluish) → Hue Shift: +10 (warmer)
- Too dark → Gamma: 0.8 (brighter)
- Need B&W → Saturation: 0.0
- Quick Instagram-style look → Saturation: 1.3, Contrast: 1.2, Offset: +0.05

## 🎛️ Parameters Explained

ColorCorrect applies adjustments in this order:
1. **Contrast**
2. **Saturation**
3. **Hue Shift** (Detonate exclusive!)
4. **Gamma**
5. **Gain** (multiply)
6. **Offset** (add)

Understanding this order helps predict results!

---

### **Saturation** ⭐⭐⭐ Most Used!
- **Range:** 0.0 to 4.0
- **Default:** 1.0 (no change)
- **What it does:** Controls color intensity
  - **0.0:** Grayscale (no color)
  - **0.5:** Desaturated (muted, pastel)
  - **1.0:** Original colors
  - **1.5:** Vibrant (punchy colors)
  - **2.0+:** Hyper-saturated (unrealistic, stylistic)

**Think of it as:** The "color volume" knob

**Examples:**
- Black & white: `Saturation: 0.0`
- Vintage muted look: `Saturation: 0.7`
- Instagram vibrant: `Saturation: 1.3`
- Candy colors: `Saturation: 2.0`

💡 **Beginner Tip:** Most adjustments are in 0.7-1.3 range. Beyond that gets extreme!

**Common uses:**
- **Desaturate** backgrounds to make foreground pop (Saturation: 0.6)
- **Increase saturation** on flat AI images (Saturation: 1.2-1.3)
- **Match saturation** between composite elements

---

### **Hue Shift** ⭐⭐⭐ Detonate Exclusive!
- **Range:** -180 to +180 degrees
- **Default:** 0.0 (no shift)
- **What it does:** Rotates all colors around the color wheel
- **Positive values:** Shift toward warmer (red/yellow)
- **Negative values:** Shift toward cooler (blue/cyan)

**Think of it as:** Rotating the color wheel

**Examples:**
- Slightly warmer: `Hue Shift: +10`
- Slightly cooler: `Hue Shift: -10`
- Creative color swap: `Hue Shift: +60` (greens → blues)
- Full inversion: `Hue Shift: +180` (opposite colors!)

**What happens:**
- Red → shifts toward orange/yellow (+) or magenta/purple (-)
- Blue → shifts toward cyan/green (+) or magenta/violet (-)
- Green → shifts toward yellow (+) or cyan (-)

💡 **Pro Tip:** Small shifts (±5-15°) adjust color temperature. Large shifts (±60°+) create stylistic effects!

**Color temperature adjustment:**
- Too cool/blue? `Hue Shift: +10 to +20` (add warmth)
- Too warm/orange? `Hue Shift: -10 to -20` (add coolness)

---

### **Contrast** ⭐⭐⭐
- **Range:** 0.0 to 4.0
- **Default:** 1.0 (no change)
- **What it does:** Adjusts difference between lights and darks
  - **< 1.0:** Lower contrast (flat, washed out)
  - **1.0:** Original contrast
  - **> 1.0:** Higher contrast (punchy, dramatic)

**Think of it as:** The "punch" control

**Contrast math:** Works around 0.5 pivot (middle gray)
- Pixels brighter than 0.5 → get brighter
- Pixels darker than 0.5 → get darker
- Result: More separation between lights and darks

**Examples:**
- Reduce contrast (soft, vintage): `Contrast: 0.8`
- Increase contrast (dramatic): `Contrast: 1.3`
- Extreme contrast (graphic): `Contrast: 2.0`

💡 **Common workflow:** Flat image → Contrast: 1.2-1.4 = instant improvement!

**When to use:**
- Flat-looking AI images → Increase contrast
- Over-contrasted images → Decrease contrast
- Matching composite layers → Adjust to match background contrast

---

### **Gamma** ⭐⭐⭐
- **Range:** 0.1 to 4.0
- **Default:** 1.0 (no change)
- **What it does:** Adjusts midtone brightness
  - **< 1.0:** Brighter midtones (lightens image)
  - **1.0:** Original brightness
  - **> 1.0:** Darker midtones (darkens image)

**Think of it as:** The "brightness" control (but better than simple brightness!)

**Why gamma instead of offset?**
- Gamma affects midtones most, preserves pure black/white
- Offset shifts everything equally (crude)
- Gamma is more natural-looking

**Examples:**
- Brighten: `Gamma: 0.7-0.9`
- Darken: `Gamma: 1.1-1.3`
- Extreme brighten: `Gamma: 0.5`
- Extreme darken: `Gamma: 2.0`

💡 **Remember:** Gamma < 1.0 = brighter (counterintuitive but standard!)

---

### **Gain** ⭐⭐
- **Range:** 0.0 to 4.0
- **Default:** 1.0 (no change)
- **What it does:** Multiplies all RGB values
- **< 1.0:** Darkens overall
- **> 1.0:** Brightens overall

**Think of it as:** Overall exposure multiplier

**Difference from Gamma:**
- **Gamma:** Non-linear, affects midtones most
- **Gain:** Linear, multiplies everything equally

**Examples:**
- Reduce brightness: `Gain: 0.8`
- Increase brightness: `Gain: 1.2`
- Double brightness: `Gain: 2.0`

💡 **When to use:** Use Gamma for most adjustments, Gain for final tweaks!

---

### **Offset** ⭐
- **Range:** -1.0 to +1.0
- **Default:** 0.0 (no change)
- **What it does:** Adds/subtracts value to all RGB
- **Negative:** Darkens (but can crush blacks)
- **Positive:** Brightens (but can blow highlights)

**Think of it as:** Crude brightness (shifts everything equally)

**Examples:**
- Slight brighten: `Offset: +0.05`
- Slight darken: `Offset: -0.05`
- Lift shadows: `Offset: +0.1`

💡 **Use sparingly!** Gamma is usually better for brightness adjustments.

**Why Offset is less useful:**
- Shifts everything equally (blacks become gray, whites clip)
- Doesn't preserve tonal relationships
- Better to use Gamma or Gain!

## 💡 Tips & Tricks

### **Beginner Quick Fixes:**

**Flat, boring image:**
```
Contrast: 1.3
Saturation: 1.2
```
Instant improvement!

**Too dark:**
```
Gamma: 0.8
Gain: 1.1 (if still too dark)
```

**Too bright:**
```
Gamma: 1.2
```

**Washed out colors:**
```
Saturation: 1.3
Contrast: 1.2
```

**Too saturated (Instagram overload):**
```
Saturation: 0.7-0.8
```

**Wrong color temperature (too blue):**
```
Hue Shift: +10 to +15
```

---

### **Professional Secrets:**

1. **The "Instagram Filter" Recipe**
   - **Saturation:** 1.25 (vibrant)
   - **Contrast:** 1.15 (punchy)
   - **Offset:** +0.03 (slight lift)
   - **Hue Shift:** +5 (warmth)
   - Result: Social media-ready look!

2. **The "Faded Film" Look**
   - **Contrast:** 0.85 (soften)
   - **Saturation:** 0.75 (muted)
   - **Offset:** +0.08 (lift shadows)
   - Result: Vintage, film-like appearance!

3. **Matching Composite Elements**
   - Compare foreground and background
   - Match **saturation** first (most obvious difference)
   - Then **contrast** (punch level)
   - Then **hue** (color temperature)
   - Finally **gamma** (overall brightness)

4. **Creative Color Shifts**
   - **Teal & Orange:** Hue +15, Saturation 1.3 (blockbuster look!)
   - **Vintage Warm:** Hue +10, Saturation 0.8, Contrast 0.9
   - **Cool Futuristic:** Hue -15, Saturation 1.2, Contrast 1.3

5. **ColorCorrect vs Grade**
   - **ColorCorrect first** → Get image "in the ballpark" (rough adjustments)
   - **Grade second** → Surgical precision (shadows/midtones/highlights separately)
   - Don't try to do everything with ColorCorrect!

6. **Order Matters!**
   - ColorCorrect applies: Contrast → Saturation → Hue → Gamma → Gain → Offset
   - Example: Contrast increases before Saturation is applied
   - This means: High contrast + High saturation = VERY punchy colors!

---

### **Common Mistakes:**

❌ **Saturation: 2.0+** - Looks fake unless intentional stylistic choice
❌ **Using Offset for brightness** - Use Gamma instead!
❌ **Extreme contrast (2.0+)** - Crushes shadows and blows highlights
❌ **Not adjusting saturation after contrast** - High contrast needs saturation adjustment
❌ **Forgetting to Unpremult first** - Always Unpremult → ColorCorrect → Premult!
❌ **Using ColorCorrect for serious grading** - Use Grade node for precision work!

## 📖 Example Workflow

**Goal:** Make flat AI-generated image look punchy

**Step 1: Identify Problem**
- Image looks flat (low contrast)
- Colors look dull (low saturation)

**Step 2: Add ColorCorrect**
- Connect image → **ColorCorrect**

**Step 3: Increase Contrast**
- **Contrast:** 1.3
- (Image now has more separation between lights/darks)

**Step 4: Boost Saturation**
- **Saturation:** 1.2
- (Colors now more vivid)

**Step 5: Fine-Tune**
- Still slightly dark? **Gamma:** 0.9
- Result: Punchy, vibrant image!

---

**Goal:** Match AI person to warm sunset background

**Step 1: Analyze**
- Person: Cool-toned (bluish), saturated, high contrast
- Background: Warm (orange), slightly desaturated, soft contrast

**Step 2: Prepare Person**
- Use **Unpremultiply** on person (if has alpha)
- Connect → **ColorCorrect**

**Step 3: Match Color Temperature**
- **Hue Shift:** +12 (add warmth to match sunset)

**Step 4: Match Saturation**
- **Saturation:** 0.85 (reduce to match softer background)

**Step 5: Match Contrast**
- **Contrast:** 0.9 (soften to match background)

**Step 6: Match Brightness**
- **Gamma:** 1.05 (darken slightly for sunset mood)

**Step 7: Finalize**
- **Premultiply** if unpremultiplied earlier
- **Merge** onto background
- Done!

**Result:** Person matches warm sunset lighting!

---

**Goal:** Create B&W with contrast boost

**Step 1: Add ColorCorrect**
- Connect image → **ColorCorrect**

**Step 2: Remove Color**
- **Saturation:** 0.0
- (Image now grayscale)

**Step 3: Boost Drama**
- **Contrast:** 1.4
- (High-contrast B&W)

**Step 4: Optional Fine-Tuning**
- Too dark? **Gamma:** 0.9
- Too bright? **Gamma:** 1.1

Done! Dramatic B&W image!

## 🔗 Works Great With

**Before ColorCorrect:**
- **Unpremultiply** ⭐⭐⭐ - ALWAYS unpremult before color correction!
- **Blur** - Soften before color adjusting
- **ChromaKeyer** - Key first, then color match

**After ColorCorrect:**
- **Premultiply** ⭐⭐⭐ - Re-premult after color correction!
- **Merge** - Composite color-corrected elements
- **Grade** - ColorCorrect for rough adjustments, Grade for precision

**Combining Color Nodes:**
```
Unpremult → ColorCorrect (rough match) → Grade (fine-tune) → Premult → Merge
```

**Quick Adjustment Workflow:**
```
Image → ColorCorrect (saturation, contrast) → Merge
```

**Creative Effects:**
```
Image → ColorCorrect (extreme hue shift, high saturation) → Blur → Merge (Screen)
(Creates colored glow effect!)
```

## 📚 Learn More

### **Key Concepts:**

**Saturation Math:**
- Converts RGB → HSV (Hue, Saturation, Value)
- Multiplies Saturation channel
- Converts back to RGB
- 0.0 = no saturation (grayscale), 2.0 = double saturation

**Hue Shift Math:**
- Converts RGB → HSV
- Adds/subtracts from Hue (wraps around at 360°)
- Converts back to RGB
- Rotates all colors around color wheel

**Contrast Math:**
- Formula: `output = (input - 0.5) × contrast + 0.5`
- Pivots around middle gray (0.5)
- Values below 0.5 get darker, above 0.5 get brighter
- Higher multiplier = more separation

**Gamma Math:**
- Formula: `output = input ^ (1/gamma)`
- Non-linear adjustment
- Gamma < 1: Brightens (lifts midtones)
- Gamma > 1: Darkens (lowers midtones)
- Preserves pure black (0.0) and pure white (1.0)

### **Photoshop/Lightroom Users:**

ColorCorrect combines several familiar tools:
- **Saturation slider** = Photoshop Hue/Saturation, Lightroom Saturation
- **Hue Shift** = Photoshop Hue slider, Lightroom Temperature (similar)
- **Contrast** = Photoshop/Lightroom Contrast slider
- **Gamma** = Lightroom Exposure (similar concept)
- **Gain** = Lightroom Exposure or Photoshop Exposure adjustment
- **Offset** = Like adding a Solid Color layer in Photoshop (crude!)

**Key difference:** In node compositing, color correction is a node in the chain, not a layer adjustment!

### **ColorCorrect vs Grade:**

**Use ColorCorrect when:**
- Quick adjustments needed
- Matching composite layers roughly
- Saturation/contrast are main concerns
- Simple brightness tweaks

**Use Grade when:**
- Precise color grading
- Need shadow/midtone/highlight separation
- Film-style color grading
- Per-channel RGB control

**Often use both:**
1. **ColorCorrect** → Get rough match (saturation, contrast, hue)
2. **Grade** → Fine-tune (lift, gamma, gain per channel)
3. Result: Perfect color!

### **Want to go deeper?**

- Study **HSV color space** (how hue shift works mathematically)
- Learn **color theory** (complementary colors, color temperature)
- Practice **shot matching** (match two different images)
- Read about **LUTs** (Look-Up Tables for color grading)
- Experiment with **color harmony** (analogous, complementary, triadic)

---

**ColorCorrect is your quick-fix toolkit!** Master Saturation, Contrast, and Hue Shift, and you can fix 80% of color problems fast. Then use Grade for the final 20% precision work. 🌈
