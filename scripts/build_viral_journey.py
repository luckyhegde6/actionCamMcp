"""
Builds the Viral International-Style Journey Edit in DaVinci Resolve Studio 21 (project 'test1'):
- Clip 1 Hook: DJI_20261109063747_0038_D.MP4 strictly from 0:02 to 0:14 (frames 48 -> 336 @ 23.976fps)
  capturing Sunrise, Stream, and moving Bus Window view.
- Remaining cuts: Fast-paced viral travel clippings from 0038_D (0:14+) and 0039_D (100fps Speed Warp).
- Original noisy camera/bus audio completely removed.
- Color Grade: DJI D-Log M to Rec.709 V1.cube + brightened warm CDL keeping the natural original look.
- Audio Mix from : Nature ambience + cinematic trailer swoosh/heartbeat + fast cut sweeps.
- Exported to exports/YouTube/Illumen_Dev_Journey_Viral.mp4
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core.resolve_client import ResolveClient
from actioncam_mcp.core.audio_engine import AudioEngine
from actioncam_mcp.core.export_manager import ExportManager

LUT_DLOG = "DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube"

# Keep original natural look with a gentle brightness lift and subtle sunrise warmth
VIRAL_JOURNEY_CDL = {
    "Slope": "1.08 1.07 1.04",
    "Offset": "0.025 0.025 0.022",
    "Power": "0.97 0.98 1.00",
    "Saturation": "1.10",
}


def get_or_create_clean_timeline(client: ResolveClient, proj, mp, name: str):
    tl_count = proj.GetTimelineCount() or 0
    tl = None
    for idx in range(1, tl_count + 1):
        candidate = proj.GetTimelineByIndex(idx)
        if candidate and candidate.GetName() == name:
            tl = candidate
            break
    if tl is None:
        tl = mp.CreateEmptyTimeline(name)
        if not tl:
            raise RuntimeError(f"Failed to create timeline '{name}'")
    else:
        proj.SetCurrentTimeline(tl)
        client.clear_timeline_tracks(tl)
    proj.SetCurrentTimeline(tl)
    return tl


def strip_all_audio(tl) -> int:
    removed = 0
    for t_idx in range(1, (tl.GetTrackCount("audio") or 0) + 1):
        items = tl.GetItemListInTrack("audio", t_idx) or []
        if items:
            tl.DeleteClips(items, False)
            removed += len(items)
    return removed


def main():
    client = ResolveClient()
    if not client.is_connected():
        print("[ERROR] DaVinci Resolve Studio is not connected.")
        return False

    proj = client.get_current_project()
    mp = proj.GetMediaPool()
    tl = get_or_create_clean_timeline(client, proj, mp, "Journey_Edit")

    # 0038_D is 23.976fps: 0:02 = frame 48, 0:14 = frame 336 (12.01s hook)
    # Remaining clippings from 0038_D (336..795) and 0039_D (100fps, 0..9930)
    shots = [
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 48,   "out": 336,  "zoom": True,  "speed_warp": False, "label": "Intro Hook (0:02-0:14 Sunrise/Stream/Bus)"},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 250,  "out": 600,  "zoom": False, "speed_warp": True,  "label": "Fast Travel Glide 1"},
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 360,  "out": 480,  "zoom": True,  "speed_warp": False, "label": "Bus Window Beat"},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 1600, "out": 1950, "zoom": False, "speed_warp": True,  "label": "Momentum Cut"},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 3400, "out": 3750, "zoom": False, "speed_warp": True,  "label": "Scenic Sweep"},
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 520,  "out": 660,  "zoom": True,  "speed_warp": False, "label": "Stream & Horizon"},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 5400, "out": 5800, "zoom": False, "speed_warp": True,  "label": "High-Energy Reveal"},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 7600, "out": 8100, "zoom": True,  "speed_warp": True,  "label": "Golden Climax"},
    ]

    append_list = []
    for s in shots:
        item = client.find_media_item_by_name(s["clip"])
        if not item:
            raise RuntimeError(f"Clip {s['clip']} not found in Media Pool")
        append_list.append({
            "mediaPoolItem": item,
            "startFrame": float(s["in"]),
            "endFrame": float(s["out"]),
        })

    appended = mp.AppendToTimeline(append_list) or []
    print(f"Appended {len(appended)} clips to Journey_Edit.")

    v1_items = tl.GetItemListInTrack("video", 1) or []
    cut_frames = []
    for idx, item in enumerate(v1_items):
        cfg = shots[idx]
        grade_ok = client.apply_color_grade(item, lut_path=LUT_DLOG, cdl=VIRAL_JOURNEY_CDL, node_index=1)
        sw_ok = client.apply_studio_speed_warp(item) if cfg["speed_warp"] else False
        if cfg["zoom"]:
            item.SetProperty("DynamicZoomEnabled", True)
        cut_frames.append(item.GetStart())
        print(f"  Shot #{idx+1} [{cfg['label']}]: start={item.GetStart()} dur={item.GetDuration()/100:.2f}s | Grade={grade_ok} | SpeedWarp={sw_ok}")

    # Outro Fusion Text+ Card
    client.insert_fusion_text_plus(tl, "ILLUMEN DEV\nThe Journey Continues...", fps=100.0, at_end=True)

    # Remove all original noisy camera/bus audio
    stripped = strip_all_audio(tl)
    print(f"Removed {stripped} original camera audio clips.")

    # Mix curated SFX/ambience from 
    sounds_dir = AudioEngine().sfx_library_dir
    ambience = str(sounds_dir / "mixkit-crickets-and-insects-in-the-wild-ambience-39.wav")
    trailer_swoosh = str(sounds_dir / "mixkit-cinematic-transition-swoosh-heartbeat-trailer-488.wav")
    reverb_woosh = str(sounds_dir / "mixkit-cinematic-tunnel-reverb-woosh-1486.wav")
    small_sweep = str(sounds_dir / "mixkit-fast-small-sweep-transition-166.wav")
    rocket_whoosh = str(sounds_dir / "mixkit-fast-rocket-whoosh-1714.wav")

    audio_entries = [
        {"path": ambience,       "track_index": 1, "record_frame": 360000},
        {"path": ambience,       "track_index": 1, "record_frame": 362605},
        {"path": trailer_swoosh, "track_index": 2, "record_frame": max(360000, cut_frames[1] - 40)},
        {"path": small_sweep,    "track_index": 2, "record_frame": max(360000, cut_frames[2] - 20)},
        {"path": reverb_woosh,   "track_index": 2, "record_frame": max(360000, cut_frames[4] - 35)},
        {"path": small_sweep,    "track_index": 2, "record_frame": max(360000, cut_frames[5] - 20)},
        {"path": rocket_whoosh,  "track_index": 2, "record_frame": max(360000, cut_frames[7] - 30)},
    ]
    added_audio = client.append_audio_clips(tl, audio_entries, bin_name="03 Audio & SFX")
    print(f"Added {added_audio} audio/SFX clips from {sounds_dir}.")

    tl.AddMarker(360000, "Cyan", "Journey Hook (0:02-0:14)", "Sunrise, Stream, Bus Window", 150)
    tl.AddMarker(cut_frames[1], "Yellow", "Viral Montage Cuts", "Speed Warp + Transition Sweeps", 150)

    dur_s = (tl.GetEndFrame() - tl.GetStartFrame()) / 100.0
    print(f"Timeline Journey_Edit ready: {dur_s:.2f}s ({tl.GetStartFrame()} -> {tl.GetEndFrame()})")

    yt_dir = str(ExportManager.classify_export_dir(str(ROOT / "exports"), profile_key="youtube_1080p"))
    res = client.render_timeline(tl, yt_dir, "Illumen_Dev_Journey", preset_name="YouTube - 1080p", wait=True)
    print("Render Result:", res)
    return True


if __name__ == "__main__":
    main()
