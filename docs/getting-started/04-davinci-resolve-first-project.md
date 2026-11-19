# DaVinci Resolve Studio 21.2 — Setup and First Project

This beginner guide is for DaVinci Resolve Studio 21.2 on Windows 11 with 16 GB RAM and an NVIDIA GTX 1650 4 GB GPU. It establishes a reliable 1080p workflow for DJI Osmo Action 4 footage.

This is the **setup and fundamentals** stage. Detailed editing, Fusion, Fairlight, colour science, advanced grading, custom LUT development, advanced presets, and AI/MCP automation will be introduced in later learning phases.

## 1. Install and prepare Resolve

1. Download DaVinci Resolve from the official [Blackmagic Design product page](https://www.blackmagicdesign.com/products/davinciresolve).
2. Install the Studio edition using your licensed installer.
3. Restart Windows if requested, launch Resolve, and confirm the Studio edition is activated.
4. In Preferences, check that the NVIDIA GTX 1650 is detected for GPU processing. Keep the driver current using the normal NVIDIA driver channel.
5. Start with default memory and GPU settings. Do not force CUDA or change advanced decode settings unless troubleshooting demonstrates a need.

**Hardware-friendly starting point:** edit in 1080p, close unnecessary applications, and avoid heavy noise reduction, multiple Fusion effects, and complex temporal effects during the first exercises. The GTX 1650 has 4 GB VRAM, so performance depends on source codec, effects, and driver configuration.

## 2. Create a project and set the timeline first

1. Open Project Manager and create a project named Action4_Learning_01.
2. Open Project Settings using the gear icon.
3. Set Timeline Resolution to **1920 × 1080 HD**.
4. Set Timeline Frame Rate to **25 fps**.
5. Set Playback Frame Rate to **25 fps** where available.
6. Save settings before adding clips to the Media Pool.

Resolve may lock the timeline frame rate after media has been added. Choose it before importing footage.

## 3. Connect the DJI Action 4 recording workflow

There is no assumed direct camera-control integration in this beginner workflow. The reliable first integration is file-based:

1. Stop recording and power off the camera before removing the microSD card.
2. Copy the original camera files into the project folder on the PC.
3. Verify that the copied files open and play before deleting or formatting anything on the card.
4. Keep original camera files unchanged; edit from those files or from generated proxies.
5. Use this folder structure:

~~~text
Action4_Learning_01/
├── 01_Original_Camera_Files/
├── 02_Audio/
├── 03_DaVinci_Project/
├── 04_Proxy/
├── 05_Stills_and_Thumbnails/
├── 06_LUTs/
└── 07_Exports/
~~~

For the first project, use the Action 4's **Normal** colour profile, 1080p, and 25 fps. Later, we will introduce D-Log M and colour-managed workflows.

## 4. Understand the main Resolve pages

- **Media:** browse folders, preview clips, and organize source media.
- **Cut:** a streamlined workspace for quick assembly.
- **Edit:** the main workspace for a beginner timeline, trimming, titles, and audio arrangement.
- **Fusion:** node-based visual effects and compositing; later phase.
- **Color:** exposure, white balance, contrast, saturation, and grading; begin with simple corrections only.
- **Fairlight:** detailed audio editing and mixing; later phase.
- **Deliver:** configure and render the final video.

For the first exercise, concentrate on Media, Edit, Color (basic correction only), and Deliver.

## 5. Import and organize footage

1. Open the Media page and navigate to 01_Original_Camera_Files.
2. Import selected clips into the Media Pool.
3. Create bins named 01_Establishing, 02_Detail, 03_Movement, 04_Action, 05_POV, and 06_Closing.
4. Preview each clip and identify the best usable section.
5. Rename clips or add metadata only when it helps you find them later.
6. Keep camera originals in their original folder; do not move or overwrite source media from inside the project.

## 6. Build your first edit

1. Open the Edit page.
2. Create a timeline named A_Day_Through_My_Lens.
3. Place six selected clips in story order: establishing, detail, movement, action, point of view, and closing.
4. Trim the beginning and end of each clip to remove camera handling or unwanted pauses.
5. Use straight cuts. Avoid transitions until the story works without them.
6. Add a simple title at the beginning only if it improves context.
7. Keep the first cut between 30 and 60 seconds.
8. Watch the complete timeline and fix confusing or distracting cuts.

### Simple title

Use the Effects Library's basic Text title. Add a short project title, keep it readable, and avoid complex animation. Check that it remains inside the safe visible area.

## 7. Basic audio

- Listen to camera audio before adding music.
- Keep dialogue intelligible and avoid clipping (distorted audio caused by levels that are too high).
- Lower music beneath speech; do not let it compete with the voice.
- Use a short fade at the beginning or end only when it helps.
- Use appropriately licensed music and retain its licence/source information.

Detailed Fairlight mixing, dialogue repair, noise reduction, and sound design are later topics.

## 8. Basic colour correction

For Normal footage, start with small corrections:

1. Select a representative clip on the Color page.
2. Check the image for obvious overexposure or underexposure.
3. Adjust white balance only if the image has a clear unwanted colour cast.
4. Make modest contrast and saturation adjustments.
5. Compare before and after, and check that adjacent clips look consistent.

Do not begin with a creative LUT. Do not apply a DJI D-Log M-to-Rec.709 conversion LUT to Normal footage. A conversion LUT is intended for footage recorded using the matching D-Log M profile.

Scopes, colour management, skin tones, matching mixed lighting, and advanced grading will be taught in later phases.

## 9. Install and use LUTs — beginner workflow

A LUT (Look-Up Table) is a preset mapping from input colours to output colours. Some LUTs perform a technical conversion; others create a creative look. They are not interchangeable.

1. Obtain a LUT from a trusted source, such as the official [DJI downloads/support page](https://www.dji.com/osmo-action-4/downloads), and check which camera profile it is designed for.
2. Extract the downloaded archive if necessary.
3. In Resolve, open Preferences and locate the Color Management / Lookup Tables section (the exact label can vary by release).
4. Use **Open LUT Folder** if available, copy LUT files into that folder, then return to Resolve.
5. Select **Update Lists** or the equivalent refresh action.
6. Find the LUT in the LUT browser and preview/apply it to a test clip.
7. Check the result and remove it if contrast, saturation, or skin tones become unnatural.

**Critical profile rule**
- DJI D-Log M conversion LUT: only for footage recorded in D-Log M and for the matching conversion.
- Normal footage: do not apply a D-Log M conversion LUT. Use basic manual correction or a creative look explicitly designed for Normal/Rec.709 footage.
- Never stack multiple technical conversion LUTs without understanding the colour pipeline.

Keep a copy of downloaded LUTs in the project's 06_LUTs folder and record the source and intended input profile.

## 10. Save reusable project and export presets

Start with simple, clearly named templates. These are workflow conventions; they do not require a custom LUT.

| Preset name | Purpose | Baseline |
|---|---|---|
| ILLUMEN_1080P25_NORMAL | Everyday Action 4 footage | 1920×1080, 25 fps, Normal colour |
| ILLUMEN_YOUTUBE_1080P25_H264 | Standard YouTube upload | MP4, H.264, 1920×1080, 25 fps |
| ILLUMEN_REVIEW_1080P25 | Small review/export copy | MP4, H.264, 1080p25, moderate bitrate |

To reuse a project setup, create a clean project with correct timeline settings and save it as a project template or duplicate it before starting a new edit. For exports, configure the Deliver page once, save a custom preset if available, and verify its settings before every render.

### First YouTube export

On the Deliver page, start with:

| Setting | Value |
|---|---|
| Format | MP4 |
| Codec | H.264 |
| Resolution | 1920 × 1080 |
| Frame rate | 25 fps |
| Quality | Restrict to approximately 10–15 Mb/s for this first review export |
| Audio | AAC, 48 kHz |
| Filename | Action4_Learning_01_v1.mp4 |

Render to 07_Exports. Watch the rendered file from beginning to end outside Resolve.

## 11. Playback performance on the GTX 1650

If playback stutters:

- Try Playback → Timeline Proxy Resolution → Half or Quarter.
- Generate Proxy Media for source clips that are difficult to decode.
- Close unnecessary applications.
- Avoid heavy noise reduction and multiple demanding effects.
- Use render cache for specific sections that need it.

Timeline Proxy Resolution changes preview quality; Proxy Media creates alternate editing files. They are different tools.

## 12. First-project quality checklist

- [ ] Project and timeline are 1920×1080 at 25 fps.
- [ ] Original Action 4 files are safely copied and verified.
- [ ] Clips are organized into useful bins.
- [ ] The six-shot story is understandable without effects.
- [ ] Titles are readable and not distracting.
- [ ] Dialogue/music levels are comfortable and not clipped.
- [ ] Basic colour correction looks natural.
- [ ] No incorrect D-Log M conversion LUT is applied to Normal footage.
- [ ] Export is H.264 MP4, 1080p25, with AAC audio.
- [ ] The exported file has been watched from start to finish.

## 13. Learning phases after setup

1. **Resolve basics:** trimming, timeline navigation, titles, audio and exports.
2. **Editing craft:** pacing, continuity, B-roll, transitions and storytelling.
3. **Colour fundamentals:** scopes, exposure, white balance, Rec.709 and colour management.
4. **DJI D-Log M:** technical conversion and controlled comparison against Normal.
5. **LUT development:** technical LUT validation, creative looks, .cube export and testing.
6. **Advanced Resolve:** Fusion, Fairlight, advanced grading and performance optimization.
7. **ActionCam MCP integration:** metadata, proxies, scene detection, transcription, searchable media, and supported Resolve automation.

## Official references

- [Blackmagic Design — DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve)
- [Blackmagic Design — Training](https://www.blackmagicdesign.com/products/davinciresolve/training)
- [DJI Osmo Action 4 — Downloads and manuals](https://www.dji.com/osmo-action-4/downloads)
- [DJI Osmo Action 4 — Specifications](https://www.dji.com/osmo-action-4/specs)
