---
name: edits-1
description: "Iteration 1 baseline edit playbook for Illumen dev YouTube showcase in DaVinci Resolve Studio 21 (project test1, DJI Osmo Action 4 D-Log M footage, Speed Warp retiming, Fusion Text+ outro, YouTube 1080p export)."
tags: [edits-1, illumen-dev, davinci-resolve, dji-action-4, d-log-m, speed-warp, youtube, iteration]
author: "ActionCam MCP"
version: "1.0.0"
---

# Edits 1 — Illumen dev DJI Action 4 YouTube Showcase (Baseline Iteration)

This skill documents the complete end-to-end **Iteration 1 (`edits-1`)** production workflow executed against **DaVinci Resolve Studio 21.2** on project `test1` for the **Illumen dev** YouTube channel. Use this as the reproducible baseline for future fine-tuning iterations (`edits-2`, `edits-3`, etc.).

---

## 1. Environment & Project Baseline

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Host App** | DaVinci Resolve Studio 21.2.0.5 | External scripting set to `Local` |
| **Project Name** | `test1` | Existing project (do not overwrite with a new project) |
| **Timeline Name** | `Illumen_Dev_Showcase` | Renamed from `Timeline 1` |
| **Resolution** | `1920x1080` | Sized for NVIDIA GTX 1650 (4GB VRAM) |
| **Frame Rate** | `100.0 fps` | Locked by Media Pool import of 100fps Action 4 footage |
| **Source Directory** | `<source-footage-dir>/` | DJI Osmo Action 4 MP4 + DNG/JPG stills |
| **Export Directory** | `./exports\` | Workspace-writable output folder |
| **Script Entrypoint** | `scripts/build_illumen_dev_video.py` | Idempotent full-timeline rebuild & render script |

---

## 2. Media Pool Organization

Clips in `test1` are organized into structured bins:

- `01 Raw Footage/SlowMo 100fps` — 18 high-speed 100fps clips (1920x1080)
- `01 Raw Footage/Realtime 24-50fps` — 7 real-time clips (24fps, 30fps, 50fps)
- `02 Stills and DNG` — 2 items (JPG + 4000x2256 DNG)
- `03 Timelines` — `Illumen_Dev_Showcase`
- `03 Audio & SFX` *(reserved for `edits-2`+)* — BGM, impact hits, whooshes

---

## 3. Curated 16-Shot Sequence Structure (Acts I–V)

The baseline edit assembles 16 curated shots on Track `V1` (`25,554` frames video + `Text+` outro):

| Act | Shots | Creative Purpose | Retiming / Motion |
| :--- | :--- | :--- | :--- |
| **Act I: Hook & Intro** | `#1`–`#2` | Sunrise scenery hook & trail movement | Dynamic Zoom on `#1` |
| **Act II: High-Speed Action** | `#3`–`#8` | Fast action passes, terrain sprint, mid-day burst | `RetimeProcess=3` (Optical Flow), `MotionEstimation=4` (Speed Warp) |
| **Act III: Golden Hour & Travel** | `#9`–`#12` | Travel handheld, golden hour action, evening run | Dynamic Zoom on `#9`; Speed Warp on `#10`–`#12` |
| **Act IV: Night Climax** | `#13`–`#15` | Night atmospheric take, sprint, hero climax | Speed Warp on `#14`–`#15`; Dynamic Zoom on `#15` |
| **Act V: Outro Card** | `#16` + `Text+` | Channel outro hero view + Fusion `Text+` CTA | Dynamic Zoom on `#16`; Fusion `Text+` (`ILLUMEN DEV\nSubscribe for more!`) |

### Timeline Markers
- `360000` (**Cyan**): `Illumen dev Intro` — Channel Hook & Showcase Intro
- `362000` (**Yellow**): `Action Climax` — High-Energy 100fps Action Montage
- `360000 + total_dur - 450` (**Green**): `Illumen dev Outro` — Subscribe to Illumen dev - CTA Card

---

## 4. Critical Resolve 21.2 Scripting Rules Discovered

1. **LUT Path Must Be Relative**:
   - `item.SetLUT(1, abs_path)` returns `False`.
   - Always pass a path relative to `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`:
     ```python
     item.SetLUT(1, "DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube")
     ```
2. **Speed Warp Uses Integer Enums**:
   - Display strings fail; use integer enum values:
     ```python
     item.SetProperty("RetimeProcess", 3)     # Optical Flow
     item.SetProperty("MotionEstimation", 4) # Speed Warp
     ```
3. **Fusion `Text+` Title Editing**:
   - `tl.InsertFusionTitleIntoTimeline("Text+")` inserts at the current playhead on `V1`.
   - Update text via the Fusion composition tool list:
     ```python
     comp = title_item.GetFusionCompByIndex(1)
     tools = comp.GetToolList(False, "TextPlus")
     for t in tools.values():
         t.SetInput("StyledText", "ILLUMEN DEV\nSubscribe for more!")
     ```
4. **Python Module Path Precedence**:
   - Use `sys.path.insert(0, r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")` so sandbox/system `PYTHONPATH` does not shadow `DaVinciResolveScript`.
5. **Project Saving**:
   - Call `client._project_manager.SaveProject()` before starting unattended renders.
6. **Clear Both Video AND Audio Tracks Before Rebuilding**:
   - `AppendToTimeline()` appends after the latest item on **any** track (video or audio). Clearing only `video` track 1 leaves orphan audio clips that push newly appended video clips minutes downstream (causing leading black screen + audio mismatch). Always iterate all `video` and `audio` tracks and call `tl.DeleteClips(items, False)` (or `client.clear_timeline_tracks(tl)`).
7. **CDL Color Grading & Transitions**:
   - Apply per-clip CDL color grading via `item.SetCDL({"NodeIndex": "1", "Slope": ..., "Offset": ..., "Power": ..., "Saturation": ...})` (or `client.apply_color_grade(...)`).
   - Use `DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube` as the base technical LUT on D-Log M footage, then shape warmth/contrast with CDL instead of stacking creative Rec.709 LUTs.
   - DaVinci Resolve's live `Timeline` Scripting API has no `InsertTransition()` method; use Fusion `Text+` title cards (`client.insert_fusion_text_plus(...)`), `DynamicZoomEnabled`, or `fcpxml_generator.py` `<transition>` tags for cross-dissolves.
8. **Default Audio Mixin Source (``) & Camera Audio Stripping**:
   - `DEFAULT_SOUNDS_DIR` in `actioncam_mcp/config.py` defaults to `` (override via `ACTIONCAM_SOUNDS_DIR`).
   - For serene/sunrise visuals (`Journey_Edit`), strip noisy original camera audio (`clear_audio_only(tl)`) and mix ambience + transition swells via `client.append_audio_clips(...)`.
9. **Automatic Export Classification (`exports/YouTube/`)**:
   - `ExportManager.classify_export_dir()` automatically routes YouTube renders (`youtube_1080p`, `youtube_4k`, `YouTube - 1080p`) into `exports/YouTube/`.

---

## 5. Deliver Page Export Configuration

- **Preset**: `YouTube - 1080p`
- **Settings**:
  - `SelectAllFrames`: `True`
  - `TargetDir`: `./exports`
  - `CustomName`: `Illumen_Dev_DJI_Action4_Showcase`
- **Execution**: `job_id = proj.AddRenderJob()` -> `proj.StartRendering([job_id])` -> poll `proj.GetRenderJobStatus(job_id)` until `JobStatus == "Complete"`.

---

## 6. Roadmap for Fine-Tuning Iterations (`edits-2`+)

When iterating on this baseline edit:
1. **Audio & SFX Layering** (skipped in `edits-1` pending MCP connection):
   - Connect **ElevenLabs MCP** (`https://api.elevenlabs.io/v1/mcp` or `uvx elevenlabs-mcp`) or **Epidemic Sound MCP** (`https://www.epidemicsound.com/a/mcp-service/mcp`).
   - Place BGM on `A1`, impact hits on `A2` at Act II/IV cut frames, and whooshes on `A3` 6 frames before transitions using `actioncam_mcp/core/audio_engine.py`.
2. **Pacing & Trim Tuning**:
   - Adjust `in`/`out` frame ranges in `curated_shots` inside `scripts/build_illumen_dev_video.py` to tighten Act II/III durations or sync cuts to BGM beats.
3. **Color Look Variations**:
   - Swap or blend `DJI OSMO Action 4 Forest Pro.cube`, `Ice Pro.cube`, or `Nature Pro.cube` per act.
4. **4K Upscale / Shorts Cutdown**:
   - Render a `YouTube - 2160p` master or generate a 9:16 `1080x1920` Shorts cutdown from Act II + Act IV highlights.
