# Grade Node

**Category:** Color
**Complexity:** ⭐⭐⭐ Advanced
**Also Known As:** Color Grading, Lift/Gamma/Gain (Nuke), Color Corrector (Fusion)

## 🎯 What Does This Do?

The **Grade node** is a professional color grading tool that gives you precise control over shadows, midtones, and highlights separately - the same tool used in Hollywood films!

**Key Difference from Simple Adjustments:**
- **Photoshop Brightness/Contrast:** Affects the whole image equally (crude)
- **Instagram Filters:** Preset adjustments with no control
- **Grade Node:** Separate control over shadows (Lift), midtones (Gamma), and highlights (Gain) - surgical precision!

This is THE most important color correction tool in professional compositing. Master this, and you can match any shot!

## 🤔 When Would I Use This?

**Essential uses:**
- 🎬 **Match colors between shots** - Make AI-generated person match the background lighting
- 🌅 **Change time of day** - Make a daytime shot look like golden hour or night
- 🎨 **Create mood/atmosphere** - Warm and cozy vs cold and clinical
- 🔧 **Fix bad lighting** - Rescue underexposed or overexposed images
- 🎭 **Color grading for film look** - Teal/orange Hollywood look, vintage film, etc.
- 🌈 **Match skin tones** - Make people from different sources look consistent

**Real example:** You AI-generated a person but they look too bright and cool-toned for the warm sunset background. Use Grade to darken their shadows (Lift), warm up midtones (Gamma), and match the golden highlights (Gain).

## 🎛️ Parameters Explained

### **The Big Three (Core Controls)**

These are the controls you'll use 90% of the time. They work in a specific order:

#### **Lift** ⭐⭐⭐ Most Important!
- **What it does:** Raises or lowers the **shadows** (dark parts)
- **Range:** -0.5 to +0.5
- **Think of it as:** "Lifting" the black level up (or pushing it down)
- **Use when:**
  - Shadows too dark/crushed? → Increase Lift
  - Shadows washed out? → Decrease Lift
  - Adding color to shadows (use per-channel controls)

💡 **Tip:** Start here! Lift sets the foundation for your grade.

#### **Gamma** ⭐⭐⭐
- **What it does:** Adjusts **midtones** (everything between shadows and highlights)
- **Range:** 0.1 to 4.0 (1.0 = no change)
- **Think of it as:** The "brightness" control that's actually good
- **Use when:**
  - Image too dark overall? → Lower Gamma (e.g., 0.7)
  - Image too bright overall? → Raise Gamma (e.g., 1.3)
  - Changing the "feel" of the image

💡 **Pro Tip:** Gamma < 1.0 = Brighter, Gamma > 1.0 = Darker (yes, it's backwards!)

#### **Gain** ⭐⭐
- **What it does:** Adjusts **highlights** (bright parts)
- **Range:** 0.0 to 4.0 (1.0 = no change)
- **Think of it as:** Multiplies the brightest parts
- **Use when:**
  - Highlights too dim? → Increase Gain
  - Highlights blown out? → Decrease Gain
  - Adding warmth to bright areas (use per-channel controls)

---

### **Supporting Controls (Fine-Tuning)**

#### **Blackpoint & Whitepoint**
- **What they do:** Set the input range BEFORE grading
- **Blackpoint** (default: 0.0): "This is pure black in the source"
- **Whitepoint** (default: 1.0): "This is pure white in the source"

**When to use:** You have a washed-out scan where 0.1 should be black and 0.9 should be white? Set those values here first!

💡 **Beginner Tip:** Leave these at default (0.0 and 1.0) unless you know you need them.

#### **Offset**
- **What it does:** Simply adds/subtracts from all RGB values
- **Range:** -0.5 to +0.5
- **Use when:** Final tweaks after Lift/Gamma/Gain are set

#### **Multiply**
- **What it does:** Overall multiplier for the entire image
- **Range:** 0.0 to 4.0 (1.0 = no change)
- **Use when:** Making everything brighter/darker after other adjustments

---

### **Per-Channel Controls (Advanced)** 🌈

This is a **Detonate exclusive improvement** over standard Grade nodes!

Each of the big three (Lift, Gamma, Gain) has separate **Red**, **Green**, **Blue** controls:

- **lift_r, lift_g, lift_b** - Add color casts to shadows
- **gamma_r, gamma_g, gamma_b** - Color correct midtones
- **gain_r, gain_g, gain_b** - Tint highlights

**Example uses:**
- **Teal/Orange Hollywood look:** Lift shadows toward teal (increase lift_g + lift_b), warm highlights (increase gain_r, decrease gain_b)
- **Fix color cast:** Image too blue? Decrease gamma_b, increase gamma_r + gamma_g
- **Sunset glow:** Increase gain_r and gain_g (add yellow to highlights)

💡 **Pro Secret:** Master controls apply first, then per-channel adjustments ADD on top. Start with master controls, then fine-tune with per-channel!

## 💡 Tips & Tricks

### **Beginner Workflow:**

1. **Start with Lift** - Get your shadows right (pure black or slightly lifted?)
2. **Adjust Gamma** - Get overall brightness/darkness right
3. **Tweak Gain** - Get highlights where you want them
4. **Fine-tune** - Use offset if needed

**Don't touch per-channel controls until you're comfortable with the basics!**

### **Professional Secrets:**

1. **The "S-Curve" for Film Look**
   - Lift: +0.05 to +0.1 (soften shadows, never pure black)
   - Gamma: 0.9 to 1.0 (slightly brighter midtones)
   - Gain: 0.95 (slightly compress highlights)
   - Result: Classic film look, no crushed blacks or blown highlights!

2. **Matching Shots (Color Match Workflow)**
   - Compare shots side-by-side
   - Match shadows first (Lift)
   - Match midtones second (Gamma)
   - Match highlights last (Gain)
   - Use per-channel controls to match color temperature

3. **Teal & Orange (Hollywood Blockbuster Look)**
   - Lift: +0.03 to shadows, +0.05 to lift_g and lift_b (teal shadows)
   - Gamma: 0.9 (brighten midtones)
   - Gain: +1.1 to gain_r, +1.05 to gain_g, -0.95 to gain_b (orange highlights)

4. **Always Grade in Straight Alpha!**
   - Use: **Unpremultiply → Grade → Premultiply** workflow
   - Why: Grading premultiplied images causes edge color shifts!

### **Common Mistakes:**

❌ **Adjusting too much** - Subtle changes look professional, extreme changes look amateur
❌ **Forgetting to unpremultiply** - Causes weird edge colors on composites
❌ **Using Offset instead of Lift** - Offset is crude, Lift is precise
❌ **Grading in isolation** - Always check your grade against the background/other shots
❌ **Cranking all three controls** - Usually only 1-2 controls need adjustment

## 📖 Example Workflow

**Goal:** Color grade an AI-generated person to match a warm sunset background

1. **Start with the composite**
   - Person composited on sunset background (using Merge node)
   - Person looks too cool-toned (bluish) and too bright

2. **Prepare for grading**
   - If person has alpha: Add **Unpremultiply** node BEFORE Grade
   - Connect person → Unpremultiply → Grade

3. **Set up Grade node**
   - Connect Unpremultiply → Grade → (Premultiply if needed) → Merge

4. **Grade the person:**
   - **Lift:** -0.05 (darken shadows to match sunset mood)
   - **Gamma:** 1.1 (darken midtones slightly)
   - **Gain:** 1.0 (leave highlights neutral for now)

5. **Add warmth with per-channel:**
   - **gamma_r:** 1.05 (add red to midtones)
   - **gamma_g:** 1.0 (neutral)
   - **gamma_b:** 0.95 (reduce blue in midtones)
   - **gain_r:** 1.1 (warm up highlights)
   - **gain_g:** 1.05 (slight yellow in highlights)

6. **If person had alpha:** Add **Premultiply** node AFTER Grade

7. **Check the result:**
   - Person should now match the warm sunset lighting!

**Troubleshooting:**
- Person still too bright? → Increase Gamma (e.g., 1.2)
- Shadows look muddy? → Increase Lift slightly (+0.02)
- Still too cool/blue? → Decrease gamma_b more (try 0.90)
- Looks too orange? → Reduce gain_r to 1.05

## 🔗 Works Great With

**Before Grade (prepare image):**
- **Unpremultiply** - ALWAYS use before grading images with alpha!
- **Merge** - Composite first, then grade to match
- **ChromaKeyer** - Key first, then grade the foreground

**After Grade (finishing touches):**
- **Premultiply** - If you unpremultiplied before, premultiply after!
- **Merge** - Composite the graded result
- **ColorCorrect** - Quick saturation/contrast tweaks on top
- **Clamp** - Prevent values from going out of range

**Multiple Grades (professional workflow):**
Chain Grade nodes together! Each one does a specific job:
- Grade 1: Fix exposure (basic Lift/Gamma/Gain)
- Grade 2: Color match to other shots
- Grade 3: Creative look (teal/orange, vintage, etc.)

## 📚 Learn More

### **Key Concepts:**

**Lift vs Offset:**
- **Offset:** Simple addition (crude, affects everything equally)
- **Lift:** Raises black level (precise, affects shadows most, midtones less, highlights minimally)

**Gamma Explained:**
- Gamma is a power function: `output = input ^ (1/gamma)`
- Gamma < 1.0: Curve bows upward → Brighter
- Gamma > 1.0: Curve bows downward → Darker
- Non-linear! Changes midtones more than shadows/highlights

**Premultiplied vs Straight Alpha:**
- **Straight:** RGB and Alpha stored separately
- **Premultiplied:** RGB already multiplied by Alpha
- **Why it matters:** Grading premultiplied images creates edge halos!
- **Fix:** Always Unpremultiply → Grade → Premultiply

### **Film Industry Standards:**

- **ACES (Academy Color Encoding System):** Industry standard color management
- **LUTs (Look-Up Tables):** Pre-made color grades (Grade node can create these manually!)
- **Primary vs Secondary Color Correction:**
  - Primary: Affects whole image (this Grade node)
  - Secondary: Affects specific areas (use Masks with Grade)

### **Photoshop/Lightroom Users:**

If you're coming from photo editing:
- Photoshop "Levels" Input sliders = Grade Blackpoint/Whitepoint
- Photoshop "Levels" Output sliders = Grade Lift/Gain
- Photoshop "Curves" midpoint = Grade Gamma (roughly)
- Lightroom "Exposure" = Gamma (sort of, but Gamma is more accurate)
- Lightroom "Shadows/Highlights" split control = Lift and Gain separately!

### **Want to go deeper?**

- Study **Lift/Gamma/Gain curves** - see the actual math
- Learn **ACES workflow** - professional color management
- Practice **shot matching** - match two different photos
- Try **film emulation** - recreate vintage film stocks
- Read: [Nuke's Grade Node Demystified](https://www.chrisbturner.com/blog/nukes-grade-node-demystified)

---

**Master the Grade node and you've mastered color!** This is the single most powerful color tool in your arsenal. Start simple (Lift/Gamma/Gain only), then explore per-channel controls when you're ready. 🎨
