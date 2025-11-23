# ChromaKeyer Node

**Category:** Keying
**Complexity:** ⭐⭐⭐ Advanced
**Also Known As:** Greenscreen Removal, Chroma Key, Keylight (Nuke), Delta Keyer (Fusion)

## 🎯 What Does This Do?

The **ChromaKeyer node** removes solid-color backgrounds (like greenscreens or bluescreens) from footage and creates clean transparency - the same technique used in every Hollywood movie!

**What's happening:**
- You film a person in front of a bright green (or blue) screen
- ChromaKeyer analyzes the image and finds all the green pixels
- It removes the green and creates an **alpha channel** (transparency)
- Now you can put the person on ANY background!

**This is THE most important VFX technique** - it's how weather forecasters appear in front of maps, how superheroes fly, and how actors visit alien planets!

## 🤔 When Would I Use This?

**Essential uses:**
- 🎬 **Remove greenscreen backgrounds** - Classic VFX workflow
- 🎥 **Interview/talking head compositing** - Put speakers on custom backgrounds
- 📸 **Product photography** - Remove studio backgrounds from products
- 🎮 **Virtual production** - Real-time background replacement
- 🎭 **Portrait compositing** - Blend people into AI-generated scenes
- 🎪 **YouTube/streaming** - Replace your room with a virtual background

**Real example:** You want to put an AI-generated person into a real photo. Film them (or generate them) on a greenscreen, use ChromaKeyer to remove the green, then composite onto your background with the Merge node!

## 🎛️ Parameters Explained

### **Screen Color** ⭐⭐⭐
- **Options:** Green / Blue / Custom
- **What it does:** Tells ChromaKeyer what color to remove
- **Choose:**
  - **Green:** Most common! Bright, easy to light, different from skin tones
  - **Blue:** Use when subject has green clothing or props
  - **Custom:** Advanced - for unusual colored backgrounds (red, yellow, etc.)

💡 **Beginner Tip:** Always use Green unless you have a specific reason not to!

**Why green?**
- Farthest from human skin tones (won't accidentally key out skin)
- Brightest color sensors can capture (cleanest key)
- Cheap green fabric readily available

---

### **Threshold** ⭐⭐⭐ Most Important!
- **Range:** 0.0 to 1.0 (default: 0.5)
- **What it does:** Sets how different from green a pixel must be to KEEP it
- **Think of it as:** "How picky am I about what's green?"
  - **Low (0.2):** Aggressive - removes lots of stuff (may eat into your subject!)
  - **High (0.8):** Conservative - only removes very green stuff (may leave green fringe)

**How to adjust:**
1. Start at 0.5 (middle)
2. Too much green left? → Lower threshold
3. Eating into your subject? → Raise threshold

💡 **Pro Tip:** View the "Alpha" output mode while adjusting - you want pure white (keep) and pure black (remove)!

---

### **Tolerance** ⭐⭐
- **Range:** 0.0 to 1.0 (default: 0.2)
- **What it does:** Expands the range of colors to remove
- **Think of it as:** "How much variation in the green do I accept?"
  - **Low (0.1):** Only removes exactly the greenscreen color
  - **High (0.5):** Removes variations (shadows, wrinkles in the fabric)

**Threshold vs Tolerance analogy:**
- **Threshold:** The center of the bullseye
- **Tolerance:** How big the bullseye is

**Workflow:** Set Threshold first to find the center, then increase Tolerance to catch variations!

---

### **Softness** ⭐⭐⭐
- **Range:** 0.0 to 1.0 (default: 0.1)
- **What it does:** Feathers (softens) the edges of the alpha
- **Think of it as:** "How blurry should the edge be?"
  - **0.0:** Hard edge (looks cut out with scissors - BAD!)
  - **0.1:** Slight softness (natural, most common)
  - **0.3+:** Very soft (blurry edge, use for motion blur or artistic effects)

💡 **Critical for realism!** Hard edges = amateur. Soft edges = professional. Always use at least 0.05!

**Signs you need more softness:**
- Subject looks "pasted on"
- Can see a hard outline around the person
- Edge looks jaggy/pixelated

---

### **Despill** ⭐⭐⭐ Critical for Quality!
- **Range:** 0.0 to 1.0 (default: 0.5)
- **What it does:** Removes green (or blue) color cast from the edges
- **The problem:** Greenscreens reflect green light onto your subject (like a green glow)
- **The fix:** Despill removes this reflected green color

**What is "spill"?**
When you film on greenscreen, the green bounces light onto your subject - especially on:
- Blonde/light hair (gets green tint)
- Edges of clothing
- Shoulders and arms
- Reflective surfaces (glasses, jewelry)

**Without despill:** Subject has a green fringe/glow (looks fake!)
**With despill:** Clean edges with natural colors

💡 **Always use despill!** Start at 0.5, increase if you still see green fringe.

**Troubleshooting:**
- Still see green edges? → Increase despill to 0.7 or 0.8
- Subject looks desaturated? → Decrease despill to 0.3

---

### **Custom Color (RGB)** - Advanced
- **When to use:** Keying unusual colored backgrounds (not green or blue)
- **How to use:**
  - Set Screen Color to "Custom"
  - Adjust custom_color_r/g/b to match your background color
  - Example: Yellow screen = R:1.0, G:1.0, B:0.0

💡 **Beginner Tip:** Ignore these unless you have a weird colored background!

---

### **Output Mode** ⭐⭐
- **Options:** Alpha / Foreground / Raw Key / Despilled
- **What each shows:**

**Foreground** (Default) ⭐⭐⭐
- Shows the keyed result with alpha channel
- Use this for final compositing!
- Connect to Merge node to composite onto background

**Alpha**
- Shows only the transparency (white = keep, black = remove)
- Use this while ADJUSTING the key!
- Makes it easy to see if your key is clean

**Raw Key**
- Shows the key before softness is applied
- Technical view for debugging

**Despilled**
- Shows the image with despill applied but without alpha
- Use to check if despill is working correctly

💡 **Workflow:** Use "Alpha" mode while adjusting Threshold/Tolerance/Softness. Switch to "Foreground" when done!

## 💡 Tips & Tricks

### **Beginner Workflow (Step-by-Step):**

1. **Set Screen Color** - Choose Green (or Blue if needed)
2. **Switch to "Alpha" output mode** - So you can see what you're doing!
3. **Adjust Threshold:**
   - Start at 0.5
   - Lower until most green is BLACK (removed)
   - If subject starts turning black, raise it back up
4. **Adjust Tolerance:**
   - Increase to catch shadows and variations in the green
   - Stop when you get clean black (fully removed green)
5. **Add Softness:**
   - Set to 0.1 or 0.2 for natural edges
   - More softness if subject has motion blur or fine details (hair!)
6. **Enable Despill:**
   - Set to 0.5
   - Increase if you see green fringe on edges
7. **Switch to "Foreground" mode** - You're done!

---

### **Professional Secrets:**

1. **The Perfect Key Has Three Qualities:**
   - **Clean alpha:** Pure white (opaque) and pure black (transparent), no gray "noise"
   - **Soft edges:** Natural feathering, not hard cuts
   - **No spill:** No green/blue color cast on subject

2. **Hair is the Hardest!**
   - Fine hair needs more softness (0.15-0.25)
   - May need to adjust tolerance higher to catch semi-transparent hair
   - Consider using **MatteControl** node after ChromaKeyer to refine hair edges

3. **Dealing with Bad Greenscreens:**
   - **Wrinkled fabric?** → Increase Tolerance
   - **Uneven lighting?** → May need multiple ChromaKeyers with masks
   - **Green spill everywhere?** → Increase Despill to 0.8+, or use **Despill** node after

4. **The Two-Pass Technique** (Advanced)
   - Pass 1: Aggressive key (low threshold) to get core matte
   - Pass 2: Gentle key (high threshold) to get edge detail
   - Merge both passes for maximum quality

5. **After ChromaKeyer, ALWAYS:**
   - Use **MatteControl** to refine edges (erode/blur/cleanup)
   - Use **Grade** to color-match subject to new background
   - Use **EdgeDefringe** if you see any color halos
   - Use **Premultiply** before compositing with Merge

---

### **Common Mistakes:**

❌ **Using Threshold too low** - Eats into your subject, especially semi-transparent areas (hair, motion blur)
❌ **Forgetting Softness** - Hard edges look amateur! Always add softness
❌ **Ignoring Despill** - Green fringe ruins the shot
❌ **Bad greenscreen lighting** - Uneven lighting makes keying nearly impossible (fix at source!)
❌ **Working in wrong color space** - Always work in linear/straight alpha, not sRGB
❌ **Not checking the alpha!** - Switch to "Alpha" output mode to verify your key is clean

---

### **When Keying Goes Wrong:**

**Problem: Subject has holes (transparent patches)**
- **Cause:** Threshold too low, or subject has colors similar to greenscreen
- **Fix:** Raise Threshold, or use Custom Color to key exact green shade

**Problem: Green fringe around edges**
- **Cause:** Not enough Despill
- **Fix:** Increase Despill to 0.7-1.0, or add **Despill** node after

**Problem: Hard, jaggy edges**
- **Cause:** No Softness
- **Fix:** Add Softness (0.1-0.2)

**Problem: Some green still visible**
- **Cause:** Tolerance too low
- **Fix:** Increase Tolerance to catch variations

**Problem: Everything is keyed out!**
- **Cause:** Threshold way too low
- **Fix:** Reset to 0.5 and start over

## 📖 Example Workflow

**Goal:** Remove greenscreen from portrait and composite onto sunset background

**Step 1: Load Your Images**
- Load greenscreen portrait
- Load sunset background

**Step 2: Add ChromaKeyer Node**
- Connect portrait → ChromaKeyer

**Step 3: Set Up ChromaKeyer**
- **Screen Color:** Green
- **Output Mode:** Alpha (for now, to see what we're doing)

**Step 4: Adjust the Key**
- **Threshold:** Start at 0.5
  - Greenscreen mostly black? Good!
  - Still some gray/green? Lower to 0.4
  - Subject getting holes? Raise to 0.6
- **Tolerance:** Increase to 0.25
  - Catches variations in green
  - Should see uniform black now
- **Softness:** Set to 0.15
  - Gives natural edge softness
- **Despill:** Set to 0.5
  - Switch Output Mode to "Foreground" to check
  - See green fringe? Increase to 0.7

**Step 5: Refine (Optional)**
- Add **MatteControl** node after ChromaKeyer
  - Erode: -1.0 (shrink matte slightly to remove any fringe)
  - Blur: 2.0 (soften edges even more)

**Step 6: Color Match**
- Add **Unpremultiply** → **Grade** → **Premultiply** nodes
- Adjust Grade to match subject to sunset lighting:
  - Lift: -0.05 (darken shadows)
  - Gamma_R: 1.1 (add warmth)
  - Gamma_B: 0.9 (reduce blue)

**Step 7: Composite**
- Add **Merge** node
- Connect:
  - Keyed/graded subject → Foreground
  - Sunset background → Background
  - Operation: Over
- Done!

**Troubleshooting:**
- Green fringe still visible? → Increase Despill more, or add **EdgeDefringe** node
- Edges look too sharp? → Increase Softness in ChromaKeyer or Blur in MatteControl
- Subject too bright for background? → Adjust Grade node

## 🔗 Works Great With

**Before ChromaKeyer (prepare footage):**
- **ColorCorrect** - Fix badly lit greenscreens (increase brightness/saturation of green)
- **Blur** - Slight blur can help with noisy/compressed footage

**After ChromaKeyer (refine the key):**
- **MatteControl** ⭐⭐⭐ - Essential! Erode/dilate/blur to perfect the matte
- **EdgeDefringe** - Remove any remaining color halos
- **Despill** (node) - Additional spill suppression if needed
- **Unpremultiply → Grade → Premultiply** - Color match to new background

**For Compositing:**
- **Merge** - Composite keyed subject onto new background (use "Over" mode)
- **Premultiply** - Always premultiply before final Merge!

**Advanced Refinement:**
- **RotoBezier** - Manually refine difficult areas (like fine hair)
- **EdgeBlur** - Soften edges without affecting interior
- **Blur** - Add motion blur if subject was moving

## 📚 Learn More

### **Key Concepts:**

**Color Difference Keying:**
- ChromaKeyer uses **Euclidean distance** in RGB color space
- Measures how "different" each pixel is from the key color
- Close to key color = transparent (black alpha)
- Far from key color = opaque (white alpha)

**Why Green (or Blue)?**
- **Green:** Farthest from skin tones, brightest in digital cameras
- **Blue:** Use when subject has green clothing/props
- **Never red:** Too close to skin tones!

**Spill Suppression Math:**
For green key, despill algorithm:
1. Find how much green exceeds average of red+blue
2. Subtract that excess × despill amount
3. Result: Green reduced to natural levels

**Premultiplied vs Straight Alpha (Critical!):**
- **ChromaKeyer outputs STRAIGHT alpha** (RGB not affected by alpha)
- **Before final compositing:** Use Premultiply node!
- **Why:** Merge node expects premultiplied alpha for correct compositing

### **Nuke/Fusion Users:**

If you're coming from professional compositing tools:
- **Nuke Keylight/IBKColour** = This ChromaKeyer
- **Nuke "Screen Color"** = ChromaKeyer Screen Color
- **Nuke "Pre-blur"** = Apply Blur node before ChromaKeyer
- **Fusion Delta Keyer** = Similar to ChromaKeyer
- **Fusion Primatte** = More advanced (ChromaKeyer is simplified)

### **Shooting Greenscreen Tips:**

For best results, shoot greenscreen properly:
1. **Even lighting on greenscreen** - No hotspots or shadows
2. **Separate subject from screen** - At least 6 feet to reduce spill
3. **Light the subject separately** - Don't rely on greenscreen bounce light
4. **Use proper greenscreen paint/fabric** - Cheap stuff doesn't key well
5. **Avoid motion blur if possible** - Makes keying harder (or shoot higher shutter speed)

### **Want to go deeper?**

- Learn about **Luma Keying** (DetonateLumaKeyer) - Remove based on brightness
- Study **Advanced Keying** - Edge matte techniques, holdout mattes
- Read: [The Art and Science of Digital Compositing](https://www.amazon.com/Art-Science-Digital-Compositing/dp/0123706386)
- Practice with **Screen Subtraction** - Professional technique using different passes

---

**Keying is an art!** ChromaKeyer gives you professional tools, but great keys require practice. Start simple (good greenscreen, even lighting), then work your way up to challenging shots (hair, motion blur, reflections). 🎬
