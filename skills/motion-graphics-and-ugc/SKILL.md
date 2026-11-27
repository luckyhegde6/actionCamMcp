---
name: motion-graphics-and-ugc
description: "High-impact motion graphics templates (Runway Rebel, Redline Tech, Electric Impact Type) and UGC product review flows for DaVinci Resolve & Fusion."
tags: [motion-graphics, fusion, ugc, product-review, unboxing, kinetic-type, resolve-studio]
author: "ActionCam MCP / ChatCut Compatible"
version: "1.0.0"
---

# Motion Graphics Styles & UGC Product Ads

This skill playbook provides recipes for applying stylized motion graphics packages and producing high-converting User Generated Content (UGC) product ads.

---

## 1. Motion Graphics Styles

### 1.1 Runway Rebel
- **Aesthetic**: High-fashion, edgy editorial typography, high-contrast monochrome with fluorescent accents.
- **Fusion Recipe**: Text+ node with fast motion blur (`MotionBlur = 1`, `Quality = 4`), glitch displacement, and chromatic aberration split on cut points.

### 1.2 Redline Tech
- **Aesthetic**: Blueprint lines, red targeting reticles, technical telemetry HUD overlays.
- **Fusion Recipe**: Polygon vector strokes with animated `WriteOn` length keyframes, tracking coordinates linked to subject movement.

### 1.3 Electric Impact Type
- **Aesthetic**: Bold kinetic text that slams onto screen with screen shake and particle discharge.
- **Fairlight & Edit Recipe**: Sub-bass boom impact SFX aligned on frame 0 of text appearance; camera shake modifier on Video Track 2.

### 1.4 Editorial Explainer & Handpainted Style
- **Aesthetic**: Paper cutouts, torn edges, marker underlines, stop-motion frame rate reduction (12fps posterize time effect).
- **Resolve Recipe**: Composite mode `Multiply` on paper texture overlays with animated `Transform` jitter.

---

## 2. UGC Product Ads & Commercial Workflows

### 2.1 Cozy Selfie Product Review & ASMR Unboxing
- **Shot List**:
  1. *Hook (0-2s)*: Close-up product reveal with natural window lighting.
  2. *Problem/Pain Point (2-6s)*: Creator speaking to camera; audio leveled with Fairlight Voice Isolation.
  3. *Unboxing & Texture (6-15s)*: Macro lens B-roll with ASMR audio amplification (+4dB high-shelf EQ).
  4. *Demo & Before/After (15-25s)*: Split screen wipe (Resolve Wipe Transition).
  5. *Call to Action (25-30s)*: Dynamic discount code badge overlay on Video Track 2.

### 2.2 Product in Times Square (3D Billboard Composite)
- **Technique**:
  1. Planar Tracker on Times Square digital screen footage in Fusion.
  2. Corner Pin composite user's product video onto the billboard surface.
  3. Relighting and screen glow using SoftGlow and ColorCorrector nodes.

