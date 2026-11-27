---
name: viral-vfx-and-ai-tools
description: "Viral visual effects (Hanging Orbit, Time Pause, Street Clones, Folding Streets) and DaVinci Resolve Studio AI Neural Engine features (3D Depth Map, Magic Mask, Super Scale, Facial Recognition)."
tags: [viral-vfx, neural-engine, magic-mask, depth-map, super-scale, fusion, resolve-studio]
author: "ActionCam MCP / ChatCut Compatible"
version: "1.0.0"
---

# Viral Visual Effects & DaVinci Resolve Studio AI Tools

This playbook guides agents and editors in implementing advanced viral visual effects and utilizing DaVinci Resolve Studio's AI Neural Engine tools.

---

## 1. DaVinci Resolve Studio Neural Engine Tools

### 1.1 3D Depth Map (ResolveFX Depth Map)
- **What it does**: AI creates an automatic 3D depth grayscale map from a 2D camera clip without requiring stereo or LiDAR.
- **Applications**:
  - *Atmospheric Depth*: Add realistic volumetric fog between subject and background.
  - *Depth-of-Field Blur*: Apply Gaussian blur that falls off with distance.
  - *Behind-the-Subject Text*: Place 3D typography behind the creator in a single click without rotoscoping.
- **Python / Scripting**:
  ```python
  timeline_item.AddEffect("ResolveFX", "com.blackmagicdesign.resolvefx.depthmap")
  ```

### 1.2 Object Isolation & Tracking (Magic Mask)
- **What it does**: Neural Engine rotoscoping that tracks persons, limbs, clothing, or custom objects across frames.
- **Applications**:
  - Background replacement without green screen.
  - Applying color grades selectively to the subject or background.
  - AI Clothes Changer & Face Swap composite masking.

### 1.3 Neural Super Scale (AI Upscaling)
- **Multipliers**: 2x Enhanced, 3x, 4x.
- **Application**: Upscales 1080p high-speed action camera footage to crisp 4K UHD with AI edge reconstruction and sharpness tuning.
- **Python / Scripting**:
  ```python
  timeline_item.SetProperty("Super Scale", 2)
  timeline_item.SetProperty("SuperScale Noise Reduction", "Medium")
  timeline_item.SetProperty("SuperScale Sharpness", "Medium")
  ```

### 1.4 Facial Recognition & Smart Bins
- Scans clips in the Media Pool and automatically identifies recurring actors/faces.
- Generates categorized Smart Bins (e.g. `Actor A - Lead`, `Actor B - Guest`) for automated casting and dialogue cutting.

---

## 2. Viral VFX Recipes

### 2.1 Hanging Orbit
- **Effect**: Creator appears suspended in mid-air while the camera smoothly orbits 360 degrees around them.
- **Recipe**: Magic Mask isolates the person; Fusion 3D Camera Tracker recreates parallax camera movement with an extruded 3D background sphere.

### 2.2 Time Pause / Freeze Frame Effect
- **Effect**: The world freezes in place while the subject walks or moves through the frozen scene.
- **Recipe**: Duplicate video layer. Cut background layer at timestamp, apply `Change Speed: 0%` (Freeze Frame). Magic Mask cuts out the moving subject on Video Track 2 over the frozen background.

### 2.3 Street Clones (Multi-Subject Clone Army)
- **Effect**: Multiple instances of the same person interacting across a city street.
- **Recipe**: Locked-tripod filming across multiple takes. In DaVinci Resolve Edit page, stack takes across Tracks V1 through V5; apply horizontal gradient wipes or Magic Mask to seamlessly reveal each clone simultaneously.

### 2.4 Folding Streets (Inception-Style City Fold)
- **Effect**: The horizon bends upwards 90 degrees or folds in half.
- **Recipe**: Fusion 3D workspace. Take background plate, split into top and bottom planes using Matte masks, rotate top plane 90 degrees along the X-axis in 3D space with ambient occlusion shadowing.

