# Merge Node

**Category:** Compositing  
**Complexity:** ⭐⭐ Intermediate  
**Also Known As:** Composite, Layer, Blend (Photoshop)

## 🎯 What Does This Do?

The **Merge node** combines two images together - like stacking photos on top of each other. Think of it as the ComfyUI equivalent of Photoshop's **layers**, but with way more control!

**Key Difference from Photoshop:**
- **Photoshop:** You stack layers in a list (top layers cover bottom layers)
- **ComfyUI/Nuke:** You explicitly connect images with nodes, deciding exactly how they combine

This node is THE MOST IMPORTANT compositing tool - you'll use it in almost every workflow!

## 🤔 When Would I Use This?

**Everyday uses:**
- 🖼️ **Put a person on a new background** (classic greenscreen workflow)
- ✨ **Add glow effects** to lights or magic spells
- 🎨 **Blend AI-generated elements** into existing photos
- 🌈 **Add color grading** by blending color layers
- 💫 **Create light leaks** and lens flares
- 🎭 **Combine multiple AI generations** into one image

**Real example:** You generated an AI character but the background is boring. Use Merge to put them on a beautiful landscape!

## 🎛️ Parameters Explained

### **Foreground & Background**
Think of these as two photos you're stacking:
- **Foreground (A):** The image ON TOP (usually the important subject)
- **Background (B):** The image UNDERNEATH (usually the scene/backdrop)

💡 **Tip:** In greenscreen work, the foreground is the person (after removing green), background is the new scene.

### **Operation (Blend Mode)**
How the two images mix together. Here are the most useful ones:

#### **For Beginners (Start Here!):**

**Over** ⭐⭐⭐ - Most common!
- Puts foreground ON TOP of background
- Uses alpha (transparency) to show through
- **Use when:** Compositing people, objects, or any layer on top of another
- **Example:** Person on new background (greenscreen result)

**Plus** ⭐⭐
- ADDS the colors together (makes things brighter)
- Great for glow effects and light
- **Use when:** Adding fire, glows, lens flares, light effects
- **Example:** Make a sword glow by adding a blurred white layer

**Screen** ⭐⭐
- Like Plus but doesn't blow out to pure white as easily
- Perfect for light effects
- **Use when:** Lightning, lens flares, sparks, light rays
- **Example:** Add realistic light streaks to a sci-fi scene

#### **For Special Effects:**

**Multiply**
- Makes things DARKER (like stacking transparencies)
- **Use when:** Creating shadows, darkening areas, vintage looks
- **Example:** Add a subtle shadow gradient to edges

**Overlay**
- Combines Multiply (dark) and Screen (light) - increases contrast
- **Use when:** Adding texture overlays, increasing drama
- **Example:** Add film grain or dust textures

**Difference**
- Shows the DIFFERENCE between two images (weird psychedelic look)
- **Use when:** Creating trippy effects, displacement maps
- **Example:** Glitch art, creative distortions

### **Mix (Opacity)**
- **Range:** 0.0 to 1.0 (0% to 100%)
- **0.0:** Only see background (foreground invisible)
- **1.0:** Full effect (default)
- **0.5:** 50/50 blend between the two

💡 **Pro Tip:** Use Mix to fade effects in/out! Start at 0.5 if an effect is too strong.

### **Mask (Optional)**
An optional black & white image that controls WHERE the merge happens:
- **White areas:** Foreground shows through 100%
- **Black areas:** Background shows through 100%
- **Gray areas:** Blend between them

**Use when:** You want to blend only certain areas, like a vignette or transition.

## 💡 Tips & Tricks

### **Beginner Tips:**

1. **Start with "Over"** - It's the most intuitive blend mode
2. **Foreground needs alpha!** - For "Over" to work, your foreground needs transparency (alpha channel). If it doesn't, everything will be a rectangle!
3. **Mix is your friend** - Effect too strong? Lower the Mix value
4. **White = Opaque, Black = Transparent** - Remember this for alpha channels

### **Professional Secrets:**

1. **Premultiply matters!** - If edges look weird (dark halos), your alpha might be "straight" when it should be "premultiplied" (use Premultiply node first)
2. **Blend modes stack** - Use multiple Merge nodes in series for complex looks (e.g., Multiply for shadow + Screen for highlights)
3. **Screen for light, Multiply for shadows** - Professional color grading trick!
4. **Plus mode for ADDITIVE effects** - Fire, explosions, energy beams all use Plus/Screen

### **Common Mistakes:**

❌ **Using "Plus" for people** - They'll look like ghosts! Use "Over" instead  
❌ **Forgetting alpha channel** - Your foreground must have transparency  
❌ **Wrong input order** - Foreground/Background switched? Swap the connections!  

## 📖 Example Workflow

**Goal:** Put an AI-generated person on a new background

1. **Generate person** with ComfyUI (or remove background)
2. **Generate/load background** image
3. **Add Merge node**
4. Connect:
   - Person image → **Foreground**
   - Background → **Background**
5. **Set Operation** to "Over"
6. **Set Mix** to 1.0
7. Done! Person now on new background!

**Troubleshooting:**
- Person has black box around them? → They don't have proper alpha! Use ChromaKeyer or background removal first
- Person too bright/dark? → Add ColorCorrect node to person BEFORE merging
- Edges look weird? → Add Premultiply node to person BEFORE merging

## 🔗 Works Great With

**Before Merge (prepare images):**
- **ChromaKeyer** - Remove greenscreen to create alpha
- **RotoBezier** - Draw custom alpha masks
- **Grade / ColorCorrect** - Match colors before compositing
- **Premultiply** - Fix alpha channel issues

**After Merge (finishing touches):**
- **Grade** - Color correct the final composite
- **Blur** - Add depth of field (blur background)
- **Glow** - Add magic to the result

**Multiple Merges (complex compositing):**
Chain Merge nodes together! Each one adds another layer.

Example: Background → Merge (add person) → Merge (add glow) → Merge (add text)

## 📚 Learn More

**Key Concepts:**
- **Alpha Channel** - The transparency information (4th channel: RGBA)
- **Premultiply vs Straight Alpha** - Two ways to store transparency
- **Blend Modes** - Different math for combining images

**Photoshop Users:**
If you're coming from Photoshop:
- Photoshop "Normal" = ComfyUI "Over"
- Photoshop "Linear Dodge (Add)" = ComfyUI "Plus"
- Photoshop layers = ComfyUI Merge nodes chained together

**Want to go deeper?**
- Try all 16 blend modes - experiment!
- Learn about premultiplied alpha (makes edges perfect)
- Study "Porter-Duff compositing" (the math behind "Over")

---

**You've got this!** The Merge node seems complex but it's just "put image A on top of image B" - the blend modes just change HOW they combine. Start with "Over" and experiment from there! 🚀
