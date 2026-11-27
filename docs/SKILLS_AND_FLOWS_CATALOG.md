# ActionCam MCP Studio — Master Skills & Production Flows Catalog

This encyclopedia details the complete catalog of video production flows, editing templates, motion graphics styles, and AI tools supported by the **ActionCam MCP Studio** ecosystem. It bridges **DaVinci Resolve Studio 21**, **Model Context Protocol (MCP)**, and the **Workflow Integration Plugin** system.

---

## Table of Contents
1. [Architecture: MCP cum Workflow Integration Plugin](#1-architecture-mcp-cum-workflow-integration-plugin)
2. [Official Built-in Resolve MCP vs Open-Source MCP](#2-official-built-in-resolve-mcp-vs-open-source-mcp)
3. [DaVinci Resolve Studio Neural Engine & Studio Infrastructure](#3-davinci-resolve-studio-neural-engine--studio-infrastructure)
4. [Core AI Video Editing Skills](#4-core-ai-video-editing-skills)
5. [Motion Graphics Styles](#5-motion-graphics-styles)
6. [Product Ads & UGC Video Flows](#6-product-ads--ugc-video-flows)
7. [Product TV Commercials (TVC)](#7-product-tv-commercials-tvc)
8. [App Promo & SaaS Video Styles](#8-app-promo--saas-video-styles)
9. [Viral Visual Effects (VFX)](#9-viral-visual-effects-vfx)
10. [Explainer Video Styles](#10-explainer-video-styles)
11. [Product Images, Posters & AI Post-Production Tools](#11-product-images-posters--ai-post-production-tools)
12. [MCP Agent Command Reference](#12-mcp-agent-command-reference)

---

## 1. Architecture: MCP cum Workflow Integration Plugin

ActionCam MCP is designed as a hybrid system:
- **As an MCP Server**: Exposes structured JSON-RPC 2.0 tools to AI assistants (Claude Desktop, Antigravity, Cursor, Codex).
- **As a DaVinci Resolve Workflow Integration Plugin**: Embedded directly inside DaVinci Resolve Studio under `Workspace > Workflow Integrations > ActionCam MCP Studio Workflow`.

```text
                               +-------------------------------------+
                               | AI Client (Claude / Antigravity)   |
                               +-------------------------------------+
                                                 |
                                     (MCP Tools via stdio / HTTP)
                                                 v
+-----------------------------------------------------------------------------------+
|                        ActionCam MCP Core Engine (Python 3.14/3.15)               |
|                                                                                   |
|  - Resolve Scripting Bridge (fusionscript.dll)  - Scene Cut Decoder (Neural Engine) |
|  - Media & Bin Organizer (ISO BMFF Parser)      - Sound Design & Fairlight Layout   |
|  - Cut Matcher & Speed Warp Retimer            - Deliver Preset Queue Manager      |
+-----------------------------------------------------------------------------------+
       |                                                                     ^
       |                                                                     |
(Direct DLL / Scripting API)                         (Local REST API on http://127.0.0.1:8765)
       |                                                                     |
       v                                                                     v
+--------------------------------------------------+   +-------------------------------------+
| DaVinci Resolve Studio 21                        |   | ActionCam Desktop UI                |
| - Neural Engine (DetectSceneCuts, Magic Mask)    |   | - Run standalone via python run.py  |
| - Workflow Integration Plugins                   |<--| - OR loaded inside Resolve Studio   |
|   (%PROGRAMDATA%\...\Workflow Integration Plugins) |   |   (WorkflowIntegration.node)        |
+--------------------------------------------------+   +-------------------------------------+
```

---

## 2. Official Built-in Resolve MCP vs Open-Source MCP

DaVinci Resolve Studio 21.1+ introduces official native support for Model Context Protocol (MCP), creating two complementary ways to integrate AI assistants:

### 2.1 Official Built-in Resolve MCP (Resolve Studio 21.1+)
* **Setup Path**: Go to **File > Setup AI Assistants** inside DaVinci Resolve Studio.
* **Mechanism**: Resolve scans local tool paths, detects supported AI assistants (Claude Desktop, Cursor, Codex, Windsurf), and automatically registers its native MCP server executable (`resolve.mcp.exe` / `ResolveMCP`).
* **Permissions**: Configured inside your AI client (approve read-only checks first before enabling project/timeline write permissions).
* **Location**: Pre-packaged inside `C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolveMCP\`.

### 2.2 Open-Source `davinci-resolve-mcp` & ActionCam MCP
* **Setup Path**: Run `python run.py mcp` or `npx davinci-resolve-mcp setup`.
* **Mechanism**: Runs external automation via `DaVinciResolveScript` / `fusionscript.dll` and local HTTP API.
* **Advantages**:
  1. Works across older Resolve Studio builds (18.x, 19.x, 20.x, 21.x).
  2. Adds advanced action camera pipelines (DJI D-Log M conversion, 120fps slow-motion retiming, automatic sound design cues).
  3. Provides an interactive visual **Desktop UI window** and **FCPXML 1.9** offline interchange.

---

## 3. DaVinci Resolve Studio Neural Engine & Studio Infrastructure

| Studio Feature | What It Does in DaVinci Resolve | How ActionCam MCP Automates It |
| :--- | :--- | :--- |
| **Facial Recognition** | Scans clips to identify recurring faces and creates automated people tags. | Builds automated Smart Bins (`Lead Creator`, `Guest`) for dialogue sorting. |
| **Bin Locking** | In multi-user collaborative environments, locks specific bins while an editor or AI agent modifies them. | Calls `timeline.SetTrackLock()` and project collaboration flags to avoid edit collisions. |
| **Super Scale** | AI upscaling (2x Enhanced, 3x, 4x) with edge reconstruction and noise reduction. | `item.SetProperty("Super Scale", 2)` to upscale 1080p high-speed clips to crisp 4K UHD. |
| **Timeline Comparison** | Visual side-by-side and difference wipe comparison between two timeline versions. | Generates versioned comparison timelines (`_v1_Rough`, `_v2_Matched`) for review. |
| **Speed Warp** | State-of-the-art Neural Engine motion vector interpolation for slow motion. | Sets `Retime Process = Optical Flow` and `Motion Estimation = Speed Warp` on 120fps action clips. |
| **Multi-User Timelines** | Multiple editors working concurrently in the same project via DaVinci Resolve Project Server. | Configures `liveCollaborationMode = 1` for shared network timelines. |
| **Object Isolation & Tracking (Magic Mask)** | Neural rotoscoping that tracks people, hair, clothing, or custom objects across frames. | Generates isolate alpha mattes in the Color node graph for background removal and relighting. |
| **3D Depth Map** | Generates an AI-driven dense 3D Z-depth pass from any 2D video clip. | Injects `ResolveFX Depth Map` for volumetric fog, depth-of-field blur, and behind-subject 3D text. |

---

## 4. Core AI Video Editing Skills

### 4.1 Speech Cleanup ([chatcut.io/skills/speech-cleanup](https://chatcut.io/skills/speech-cleanup))
- **Objective**: Clean raw vocal takes, remove filler words (um, uh), eliminate pauses, and suppress background noise.
- **DaVinci Resolve Pipeline**:
  - Fairlight: `Voice Isolation` set to 80-90% to eliminate room reverberation and wind rumble.
  - Fairlight: `Dialogue Leveler` to smooth out spoken volume swings.
  - Edit Page: Automatic ripple delete of gaps where silence exceeds 0.4 seconds.

### 4.2 Viral Video Cloner ([chatcut.io/viralvideocloner](https://chatcut.io/viralvideocloner))
- **Objective**: Reverse-engineer a viral reference video and recreate its pacing, rhythm, camera energy, and cut points using user clips.
- **DaVinci Resolve Pipeline**:
  - Neural Engine `DetectSceneCuts()` extracts every shot boundary and duration.
  - Energy Matcher categorizes cuts into *fast montage* (<0.9s), *dynamic movement* (1-2.5s), and *establishing* (>2.5s).
  - High-frame-rate (120fps) source clips are retimed to slow motion (0.208x speed) at beat drops.

### 4.3 Long Video to Shorts ([chatcut.io/skills/long-video-to-shorts](https://chatcut.io/skills/long-video-to-shorts))
- **Objective**: Convert a horizontal 16:9 long-form video (podcast, tutorial, webinar) into multiple viral 9:16 vertical shorts.
- **DaVinci Resolve Pipeline**:
  - Timeline settings changed to vertical `1080x1920`.
  - DaVinci Neural Engine `Smart Reframe` tracks the speaking subject in the center.
  - Creates 30s to 60s highlight timelines with animated captions on Subtitle Track 1.

### 4.4 Add Captions ([chatcut.io/skills/add-captions](https://chatcut.io/skills/add-captions))
- **Objective**: Generate animated, word-by-word highlighted captions (Hormozi style) on the timeline.
- **DaVinci Resolve Pipeline**:
  - Studio Speech-to-Text transcription generates subtitle markers.
  - Fusion Text+ node applies bounce animations, stroke outlines, and active word color shifts.

### 4.5 Background Remover ([chatcut.io/skills/replace-video-background](https://chatcut.io/skills/replace-video-background))
- **Objective**: Isolate creator from messy room or studio without a physical green screen.
- **DaVinci Resolve Pipeline**:
  - Color Page: Neural Engine `Magic Mask` (Person mode) tracks the creator.
  - Alpha Output connected to Track V2 over virtual studio background on Track V1.

### 4.6 Talking-Head Edit Recreation ([chatcut.io/skills/recreate-a-video](https://chatcut.io/skills/recreate-a-video))
- **Objective**: Match the shot cadence, B-roll timing, and graphic overlay cues of a reference creator.
- **DaVinci Resolve Pipeline**:
  - Clones cut cadence from reference video.
  - Alternates A-roll (talking head) with 1.5s - 2.5s B-roll cutaways on Track V2.

### 4.7 Video Translation & Dubbing ([chatcut.io/skills/video-translation](https://chatcut.io/skills/video-translation))
- **Objective**: Generate localized audio dub tracks and translated subtitle languages.
- **DaVinci Resolve Pipeline**:
  - Multilingual Fairlight tracks: Track A1 (Original), Track A2 (Translated Dub).
  - Auto-ducking (-12dB) applied to original track during translated speech segments.

### 4.8 AI Multicam Editor ([chatcut.io/skills/multicam-edit](https://chatcut.io/skills/multicam-edit))
- **Objective**: Synchronize multiple camera angles and switch camera views based on who is speaking.
- **DaVinci Resolve Pipeline**:
  - `mediaPool.AutoSyncAudio()` synchronizes camera takes via waveform matching.
  - Generates Multicam Clip and automates angle cuts on sentence beginnings.

### 4.9 Edit to Script ([chatcut.io/skills/edit-to-script](https://chatcut.io/skills/edit-to-script))
- **Objective**: Takes a written script and assembles the rough cut automatically by matching dialogue to footage takes.
- **DaVinci Resolve Pipeline**:
  - Matches script lines to transcribed audio timecodes in Media Pool clips.
  - Trims top/tail mistakes and appends best takes to timeline.

---

## 5. Motion Graphics Styles

| Motion Style | Reference Template | Visual Characteristics & DaVinci Fusion Pipeline |
| :--- | :--- | :--- |
| **Runway Rebel** | `mg-packaging-runway-rebel` | High-fashion editorial look. Monochromatic black & white with fluorescent cyan/pink text accents. Text+ nodes with FastBlur motion blur and chromatic aberration split on cuts. |
| **Redline Tech** | `mg-packaging-redline-tech` | Blueprint lines, red targeting reticles, technical telemetry HUD. Vector strokes with animated `WriteOn` length keyframes linked to tracker points. |
| **Electric Impact Type** | `mg-packaging-electric-impact-type` | Bold kinetic text slamming onto screen with screen shake and particle discharge. Camera shake modifier on Video Track 2; Fairlight sub-bass impact aligned at frame 0. |
| **Highlight Moments** | `mg-packaging-highlight-moments` | Neon yellow / green marker stroke highlighting key words as they are spoken. Animated polygon mask over yellow solid on composite mode `Multiply`. |
| **Editorial Explainer** | `mg-packaging-editorial-explainer` | Paper cutout cards, torn borders, clean Swiss typography, 12fps stop-motion posterize time effect. |
| **Brainstorm Breeze** | `mg-packaging-brainstorm-breeze` | Floating concept cards, organic rounded rectangles, smooth spring physics keyframing. |
| **Red-Pen Rewind** | `mg-packaging-red-pen-rewind` | Hand-drawn red circled items, arrows, and strikethrough corrections over video. |
| **Orange Unfiltered** | `mg-packaging-orange-unfiltered` | Warm analog film grain, vibrant orange title cards, Kodak 2383 print film emulation LUT. |
| **Real Footage to Handpainted** | `handpaint-talking-head-packaging` | Cel-shading / watercolor line art pass over live-action video using Fusion EdgeDetect and Watercolor ResolveFX. |

---

## 6. Product Ads & UGC Video Flows

| Flow Name | Template Key | Structure & Editing Strategy |
| :--- | :--- | :--- |
| **Cozy Selfie Product Review** | `cozy-selfie-product-review` | Warm ambient lighting, natural handheld camera motion, creator holding product to lens. Hook (0-2s) &rarr; Problem (2-6s) &rarr; Routine (6-20s) &rarr; CTA discount badge. |
| **Quiet Creator Unboxing** | `quiet-creator-unboxing` | Aesthetic minimalist framing, soft ambient lighting, high dynamic range color grade. |
| **Window-Light ASMR Unboxing** | `window-light-asmr-unboxing` | Natural window side-lighting, micro-detail macro close-ups, +4dB high-shelf EQ boost on packaging textures. |
| **On-Foot Try-On** | `on-foot-try-on` | Low-angle camera perspective, dynamic 120fps speed ramping on foot movement, impact SFX on shoe ground contact. |
| **Mirror Outfit Try-On** | `mirror-outfit-try-on` | Snap zoom cuts on outfit transitions. Quick whip pan or snap-finger transition between looks. |
| **Mystery-Box Product Reveal** | `mystery-box-product-reveal` | Tension build-up with slow push-in zoom &rarr; rapid tape-peel cut &rarr; explosive light ray reveal inside the box. |
| **Satisfying Product Restock** | `satisfying-product-restock` | Fast rhythmic montage (0.4s cuts), synchronized audio clicks and snaps, top-down 90-degree flat-lay angle. |
| **Before and After** | `before-and-after` | Dynamic wipe transition across center frame with text labels indicating "Day 1" vs "Day 30". |
| **Hidden-Feature Demo** | `hidden-feature-product-demo` | Slow macro pan over product chassis &rarr; callout circle zooms in on unexpected mechanism. |
| **Product in Times Square** | `product-in-times-square` | Planar Tracker in Fusion attaches user's product video to Times Square electronic billboard with relighting. |

---

## 7. Product TV Commercials (TVC)

| TVC Campaign Style | Reference Template | Visual Style & Resolve Color/VFX Recipe |
| :--- | :--- | :--- |
| **Citrus Storm** | `tvc-citrus-storm` | High-speed liquid splash (120fps), lemon/orange slice flying through frame, vibrant yellow/cyan grading, droplet specular highlights. |
| **Tropical Gummy Swirl** | `tvc-tropical-gummy-swirl` | Saturated candy pastel color palette, 3D rotating confectionery, glossy reflections, playful bouncy soundtrack. |
| **Sugar Crystal Storm** | `tvc-sugar-crystal-storm` | Dark premium background with floating macro sugar crystals illuminated by rim lighting. Fusion particle emitter for glittering dust. |
| **Sparkling Can Showcase** | `tvc-sparkling-can` | 360-degree turntable can spin, water condensation droplets sliding down aluminum, condensation fog via ResolveFX Depth Map. |
| **Summer Fashion Campaign** | `tvc-summer-fashion` | Sun-drenched golden hour warm highlights, wide-open aperture shallow depth of field, slow-motion fabric flow. |
| **Golden-Hour Poolside** | `tvc-golden-hour-poolside` | Water caustic light reflections, warm skin tones, teal water contrast, luxury lifestyle vacation grading. |
| **Mixed-Media Snack Ad** | `tvc-mixed-media-snack` | Stop-motion paper packaging cutout mixed with 60fps live-action crunch shots and animated sticker popups. |
| **Food / Skincare / Beverage** | `food-ad-recreation` | Steam rising from hot dish, slow honey drizzle, glossy cosmetic cream swipe across glass plate. |

---

## 8. App Promo & SaaS Video Styles

| SaaS & App Style | Reference Key | Visual Execution & Animation Mechanics |
| :--- | :--- | :--- |
| **AI Assistant Feature Tour** | `app-promo-ai-feature-tour` | Screen recording inside clean 3D MacBook mockup, animated cursor with glowing purple click pulses, floating feature pills. |
| **SaaS Kinetic Type Launch** | `app-promo-kinetic-type` | High-tempo kinetic typography synced to 135 BPM electronic beat, rapid problem &rarr; solution text switches. |
| **Flat-Card SaaS Explainer** | `app-promo-flat-cards` | Rounded card UI modules sliding onto screen with 0.3s spring damping, dark-mode software interfaces. |
| **Aurora SaaS** | `app-saas-aurora-saas` | Subtle animated chromatic gradient mesh in background (purple/teal/indigo) behind crisp glassmorphic dashboard panels. |
| **3D Isometric Card Flight** | `app-saas-isometric-card-flight` | 2.5D software UI layers extruded in Fusion 3D space, showing depth between navigation, cards, and modal dialogs. |
| **Ink & Ribbon** | `app-saas-ink-ribbon` | Smooth flowing vector ribbons guiding the viewer's eye between UI feature cards. |
| **Chalk Blueprint** | `app-saas-chalk-blueprint` | Architectural dark slate background with white animated wireframe diagrams. |
| **Velocity & Push-In** | `app-saas-velocity` | Continuous forward camera push through successive browser frames into feature details. |

---

## 9. Viral Visual Effects (VFX)

| Viral Effect | Visual Outcome | How It's Built in DaVinci Resolve & Fusion |
| :--- | :--- | :--- |
| **Hanging Orbit** | Creator floats suspended in mid-air while camera orbits 360&deg;. | Magic Mask isolates the body; Fusion 3D camera reconstructs background parallax. |
| **Gravity Takes a Break** | Objects or the creator suddenly float upwards toward the ceiling. | Separate layers with reverse vertical Y-position transform keyframes and shadow falloff. |
| **Clones on the Street** | Multi-subject clone army interacting with each other. | Tripod-locked multi-take filming stacked on Tracks V1-V5 with feathered masks. |
| **Folding Streets** | Horizon bends 90 degrees upward into an Inception-like cube. | Fusion 3D workspace folds top half of image 90&deg; on the X-axis with drop shadowing. |
| **Time Pause** | Everything freezes mid-motion while creator continues walking. | Freeze frame on Track V1; moving creator isolated on Track V2 with Magic Mask. |
| **One-Shot City Dive** | Camera plunges from high satellite altitude into a creator's handheld camera. | Zoom transition linking Google Earth 3D zoom to drone shot to action cam take with motion blur. |

---

## 10. Explainer Video Styles

- **Paper Atlas** (`paper-atlas-explainer`): Textured cartography paper maps, animated dashed transit lines, vintage stamp icons.
- **Pastel Flat 2D** (`animated-explainer-pastel-flat-2d`): Soft corporate Memphis color palette, clean geometric vector character shapes.
- **Claymotion** (`animated-explainer-claymotion`): Hand-modeled plasticine clay appearance, 12fps stop-motion frame jitter, fingerprint surface bump maps.
- **Whiteboard Doodle** (`animated-explainer-whiteboard-doodle`): Hand-drawn black marker doodles appearing in real time on a whiteboard texture.
- **Pixel Art** (`animated-explainer-pixel-art`): Retro 8-bit / 16-bit video game aesthetic with chiptune 8-bit sound effects.
- **Archive Collage** (`archive-collage-explainer`): Historic black-and-white photographs with colorized subject cutouts sliding along 3D parallax planes.

---

## 11. Product Images, Posters & AI Post-Production Tools

### 11.1 Studio Still & Poster Styles
- **Color Pop & Juicy Splash**: High-key studio photography with high-speed water/liquid splashes.
- **Clean Studio & Dark Premium**: Minimalist podium lighting with soft gradient reflections.
- **Retro Print & Clean Editorial Posters**: Swiss typography layouts with grain and halftone screen textures.

### 11.2 AI Post-Production Tools
- **Face Swap Video**: Magic Mask tracks face geometry; Fusion Planar Tracker composites replacement faceplate with color matching.
- **AI Clothes Changer**: Magic Mask isolates clothing area; Hue/Saturation and texture mapping swaps color and fabric.
- **Video Background Remover**: Magic Mask separates foreground person, replacing background with 3D set or motion graphic.

---

## 12. MCP Agent Command Reference

AI assistants can directly execute any of the above workflows using the ActionCam MCP tool suite:

```json
// Example: Run Viral Video Cloner Flow
{
  "name": "actioncam_assemble_timeline",
  "arguments": {
    "timeline_name": "Viral_Sports_Reel_01",
    "reference_path": "F:/Edits/References/viral_action_reel.mp4",
    "source_dir": "F:/Edits/DJI_Action4_Raw",
    "camera_preset": "dji_action4_dlog_m",
    "export_fcpxml": true
  }
}

// Example: Apply Studio Neural Speed Warp & Super Scale
{
  "name": "actioncam_apply_studio_effects",
  "arguments": {
    "effect_type": "speed_warp",
    "track_index": 1,
    "clip_index": 2
  }
}

// Example: Queue Deliver Page Export for Instagram Reels
{
  "name": "actioncam_queue_export",
  "arguments": {
    "output_dir": "F:/Edits/Exports",
    "filename_prefix": "Reel_Edit_Final",
    "profile": "reels_shorts_9_16",
    "start_render_now": false
  }
}
```

