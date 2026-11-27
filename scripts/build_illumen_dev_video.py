"""
Automated YouTube Video Assembly Script for Channel 'Illumen dev'
Executes inside DaVinci Resolve Studio 21 on project 'test1'.
"""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core.resolve_client import ResolveClient
from actioncam_mcp.core.export_manager import ExportManager

def build_video():
    print("=======================================================")
    print("  ActionCam MCP Studio: YouTube Video Assembly")
    print("  Channel: Illumen dev")
    print("  Project: test1 (DaVinci Resolve Studio 21)")
    print("=======================================================\n")

    client = ResolveClient()
    if not client.is_connected():
        print("[ERROR] DaVinci Resolve Studio is not connected.")
        return False

    proj = client.get_current_project()
    print(f"Connected to project: {proj.GetName()}")

    mp = proj.GetMediaPool()
    tl = proj.GetCurrentTimeline()
    if not tl:
        print("[ERROR] No active timeline found.")
        return False

    # 1. Ensure timeline is named 'Illumen_Dev_Showcase'
    tl.SetName("Illumen_Dev_Showcase")
    print(f"Timeline active: {tl.GetName()}")

    # 2. Clear any existing items on ALL video and audio tracks so timeline starts cleanly at 01:00:00:00
    for track_type in ("video", "audio"):
        track_count = tl.GetTrackCount(track_type) or 0
        for track_idx in range(1, track_count + 1):
            items = tl.GetItemListInTrack(track_type, track_idx) or []
            if items:
                tl.DeleteClips(items, False)
                print(f"Cleared {len(items)} old clips from {track_type} track {track_idx}.")

    # 3. Curated 16-Shot Sequence for Illumen dev
    curated_shots = [
        # Act I: Hook & Intro
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 100, "out": 500, "pacing": "Hook Sunrise Scenery", "zoom": True, "speed_warp": False},
        {"clip": "DJI_20261016154437_0001_D.MP4", "in": 200, "out": 600, "pacing": "Trail Movement", "zoom": False, "speed_warp": False},
        
        # Act II: High-Speed Action
        {"clip": "DJI_20261022133201_0016_D.MP4", "in": 100, "out": 350, "pacing": "Fast Action Pass", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261022134456_0018_D.MP4", "in": 150, "out": 450, "pacing": "Terrain Sprint", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261022150936_0019_D.MP4", "in": 100, "out": 320, "pacing": "Subject Follow", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261023101330_0021_D.MP4", "in": 100, "out": 300, "pacing": "Mid-Day Burst", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261023151935_0023_D.MP4", "in": 150, "out": 400, "pacing": "High Velocity Run", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261024175127_0024_D.MP4", "in": 100, "out": 280, "pacing": "Punchy Action Cut", "zoom": False, "speed_warp": True},

        # Act III: Golden Hour & Travel Scenery
        {"clip": "DJI_20261108195342_0029_D.MP4", "in": 200, "out": 600, "pacing": "Cinematic Travel Handheld", "zoom": True, "speed_warp": False},
        {"clip": "DJI_20261022183553_0020_D.MP4", "in": 200, "out": 550, "pacing": "Golden Hour Action", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261024193735_0025_D.MP4", "in": 200, "out": 600, "pacing": "Extended Landscape Run", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261024210942_0027_D.MP4", "in": 150, "out": 400, "pacing": "Evening High-Contrast Action", "zoom": False, "speed_warp": True},

        # Act IV: Night High-Speed Climax
        {"clip": "DJI_20261108221550_0037_D.MP4", "in": 100, "out": 450, "pacing": "Night Atmospheric Take", "zoom": False, "speed_warp": False},
        {"clip": "DJI_20261108221511_0036_D.MP4", "in": 100, "out": 320, "pacing": "Night Action Sprint", "zoom": False, "speed_warp": True},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 200, "out": 750, "pacing": "Epic Hero Climax Take", "zoom": True, "speed_warp": True},

        # Act V: Outro Card
        {"clip": "DJI_20261108202712_0033_D.MP4", "in": 300, "out": 750, "pacing": "Channel Outro Hero View", "zoom": True, "speed_warp": False},
    ]

    # Map MediaPoolItems
    append_list = []
    shot_configs = []

    for idx, s in enumerate(curated_shots):
        item = client.find_media_item_by_name(s["clip"])
        if not item:
            print(f"[WARN] Clip {s['clip']} not found in media pool, skipping.")
            continue

        append_list.append({
            "mediaPoolItem": item,
            "startFrame": float(s["in"]),
            "endFrame": float(s["out"]),
        })
        shot_configs.append(s)

    print(f"Appending {len(append_list)} curated shots to timeline...")
    appended = mp.AppendToTimeline(append_list)
    print(f"[SUCCESS] Appended {len(appended)} clips to timeline.")

    # 4. Color Grading: Apply DJI D-Log M to Rec.709 LUT
    lut_rel_path = "DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube"
    print(f"\nApplying official LUT: {lut_rel_path} to all timeline clips...")

    timeline_items = tl.GetItemListInTrack("video", 1) or []
    for idx, item in enumerate(timeline_items):
        cfg = shot_configs[idx] if idx < len(shot_configs) else {}
        
        # Apply LUT
        res_lut = item.SetLUT(1, lut_rel_path)

        # Apply Speed Warp on 100fps action clips
        if cfg.get("speed_warp"):
            item.SetProperty("RetimeProcess", 3)      # Optical Flow
            item.SetProperty("MotionEstimation", 4)  # Speed Warp

        # Apply Dynamic Zoom on scenic / intro shots
        if cfg.get("zoom"):
            item.SetProperty("DynamicZoomEnabled", True)

        print(f"  Shot #{idx+1} ({item.GetName()[:24]}...): LUT={res_lut} | SpeedWarp={cfg.get('speed_warp')} | Zoom={cfg.get('zoom')}")

    # 5. Add Channel Outro Fusion Title (Text+)
    print("\nAdding Illumen dev Outro Fusion Title (Text+)...")
    end_tc = tl.GetEndFrame()
    # Convert end frame at 100fps to HH:MM:SS:FF (100fps -> 100 frames/sec)
    total_secs = int(end_tc // 100)
    ff = int(end_tc % 100)
    hh = total_secs // 3600
    mm = (total_secs % 3600) // 60
    ss = total_secs % 60
    tl.SetCurrentTimecode(f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}")
    title_item = tl.InsertFusionTitleIntoTimeline("Text+")
    if title_item:
        comp = title_item.GetFusionCompByIndex(1)
        if comp:
            tools = comp.GetToolList(False, "TextPlus") or {}
            for t in tools.values():
                t.SetInput("StyledText", "ILLUMEN DEV\nSubscribe for more!")
        print("[SUCCESS] Added Illumen dev Outro Text+ title.")

    # 6. Add Channel Branding Markers
    print("\nAdding channel markers to timeline...")
    tl.AddMarker(360000, "Cyan", "Illumen dev Intro", "Channel Hook & Showcase Intro", 150)
    tl.AddMarker(362000, "Yellow", "Action Climax", "High-Energy 100fps Action Montage", 200)
    
    # Calculate end marker
    total_dur = sum(item.GetDuration() for item in timeline_items)
    outro_frame = int(360000 + total_dur - 450)
    tl.AddMarker(outro_frame, "Green", "Illumen dev Outro", "Subscribe to Illumen dev - CTA Card", 150)
    print("Channel markers added.")

    # 7. Deliver Page Export Setup & Render
    print("\nConfiguring Deliver Page Render Preset for YouTube...")
    yt_preset = "YouTube - 1080p"
    custom_name = "Illumen_Dev_DJI_Action4_Showcase"
    export_dir = str(ExportManager.classify_export_dir(str(ROOT / "exports"), profile_key="youtube_1080p", preset_name=yt_preset, filename=custom_name))

    # Load YouTube preset if available
    available_presets = proj.GetRenderPresetList()
    if yt_preset in available_presets:
        proj.LoadRenderPreset(yt_preset)
        print(f"Loaded render preset: {yt_preset}")

    proj.SetRenderSettings({
        "SelectAllFrames": True,
        "TargetDir": export_dir,
        "CustomName": custom_name,
    })

    job_id = proj.AddRenderJob()
    print(f"[SUCCESS] Added Render Job ID: {job_id}")
    print(f"Target Output: {export_dir}\\{custom_name}.mp4")

    if client._project_manager:
        client._project_manager.SaveProject()
    proj.StartRendering([job_id])
    print("Render started in DaVinci Resolve Deliver queue.")

    import time
    for _ in range(90):
        st = proj.GetRenderJobStatus(job_id)
        status = st.get("JobStatus")
        pct = st.get("CompletionPercentage", 0)
        print(f"Render Status: {status} ({pct}%)", flush=True)
        if status in ("Complete", "Failed", "Cancelled"):
            print(f"Final Render Status: {st}")
            break
        time.sleep(5)

    print("\n=======================================================")
    print("  ILLUMEN DEV YOUTUBE VIDEO EDIT COMPLETE!")
    print(f"  Timeline Name: {tl.GetName()}")
    print(f"  Total Shots Assembled: {len(timeline_items)}")
    print(f"  Color Grade: DJI D-Log M to Rec.709 Applied")
    print(f"  Neural Retiming: Speed Warp Optical Flow Applied")
    print(f"  Render Queue Job: Created ({job_id})")
    print("=======================================================\n")
    return True

if __name__ == "__main__":
    build_video()
