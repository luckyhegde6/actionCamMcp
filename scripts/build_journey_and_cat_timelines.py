"""
Builds, color-grades, mixes audio from , and exports two timelines
in DaVinci Resolve Studio 21 (project 'test1'):
1. Journey_Edit  (Sunrise & soothing visuals: original audio removed, warm sunrise grade + nature ambience)
2. Into_My_Cat   (Pintu's showcase: 'MEET PINTU' intro, vibrant grade, playful SFX/bed from )
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core.resolve_client import ResolveClient
from actioncam_mcp.core.audio_engine import AudioEngine
from actioncam_mcp.core.export_manager import ExportManager

LUT_DLOG = "DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube"

JOURNEY_SUNRISE_CDL = {
    "Slope": "1.05 1.01 0.94",
    "Offset": "0.00 0.00 0.00",
    "Power": "0.98 1.00 1.03",
    "Saturation": "1.08",
}

PINTU_CAT_CDL = {
    "Slope": "1.03 1.02 1.00",
    "Offset": "0.01 0.01 0.01",
    "Power": "0.99 1.00 0.99",
    "Saturation": "1.14",
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


def clear_audio_only(tl):
    """Removes all clips from all audio tracks (e.g. stripping noisy camera audio)."""
    removed = 0
    for t_idx in range(1, (tl.GetTrackCount("audio") or 0) + 1):
        items = tl.GetItemListInTrack("audio", t_idx) or []
        if items:
            tl.DeleteClips(items, False)
            removed += len(items)
    return removed


def assemble_timeline(
    client: ResolveClient,
    proj,
    mp,
    name: str,
    shots: list,
    intro_text: str,
    outro_text: str,
    cdl_grade: dict,
    remove_original_audio: bool = False,
    audio_entries: list = None,
):
    tl = get_or_create_clean_timeline(client, proj, mp, name)
    print(f"\n=== Building & Grading Timeline: {tl.GetName()} ===")

    # Opening Fusion Text+ Title
    client.insert_fusion_text_plus(tl, intro_text, fps=100.0, at_end=True)

    append_list = []
    configs = []
    for s in shots:
        item = client.find_media_item_by_name(s["clip"])
        if not item:
            print(f"[WARN] Clip {s['clip']} not found, skipping.")
            continue
        append_list.append({
            "mediaPoolItem": item,
            "startFrame": float(s["in"]),
            "endFrame": float(s["out"]),
        })
        configs.append(s)

    appended = mp.AppendToTimeline(append_list) or []
    print(f"Appended {len(appended)} clips after intro title.")

    tl_items = tl.GetItemListInTrack("video", 1) or []
    video_items = [it for it in tl_items if it.GetName() != "Text+"]

    for idx, item in enumerate(video_items):
        cfg = configs[idx] if idx < len(configs) else {}
        lut = cfg.get("lut", LUT_DLOG)
        grade_ok = client.apply_color_grade(item, lut_path=lut, cdl=cdl_grade, node_index=1)
        sw_ok = client.apply_studio_speed_warp(item) if cfg.get("speed_warp") else False
        if cfg.get("zoom"):
            item.SetProperty("DynamicZoomEnabled", True)
        print(f"  Shot #{idx+1} ({item.GetName()}): Grade={grade_ok} | SpeedWarp={sw_ok} | Zoom={cfg.get('zoom', False)}")

    # Outro Fusion Text+ Title
    client.insert_fusion_text_plus(tl, outro_text, fps=100.0, at_end=True)

    # Strip original camera audio if requested (e.g. sunrise soothing visuals)
    if remove_original_audio:
        stripped = clear_audio_only(tl)
        print(f"Removed {stripped} original camera audio clips.")

    # Mix in curated audio from 
    if audio_entries:
        added_audio = client.append_audio_clips(tl, audio_entries, bin_name="03 Audio & SFX")
        print(f"Added {added_audio} audio/SFX clips from default Sounds library.")

    tl.AddMarker(360000, "Cyan", f"{name} Intro", intro_text.replace("\n", " - "), 150)
    tl.AddMarker(int(tl.GetEndFrame() - 500), "Green", f"{name} Outro", "End Title Card", 150)

    v1 = tl.GetItemListInTrack("video", 1) or []
    a1 = tl.GetItemListInTrack("audio", 1) or []
    a2 = tl.GetItemListInTrack("audio", 2) or []
    dur_s = (tl.GetEndFrame() - tl.GetStartFrame()) / 100.0
    print(f"Verified {name}: Start={tl.GetStartFrame()} End={tl.GetEndFrame()} ({dur_s:.2f}s) | V1={len(v1)} A1={len(a1)} A2={len(a2)}")
    return tl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-render", action="store_true", help="Skip Deliver page rendering")
    args = parser.parse_args()

    client = ResolveClient()
    if not client.is_connected():
        print("[ERROR] DaVinci Resolve Studio is not connected.")
        return False

    proj = client.get_current_project()
    mp = proj.GetMediaPool()

    audio_engine = AudioEngine()
    sounds_dir = audio_engine.sfx_library_dir
    print(f"Default audio mixin source: {sounds_dir}")

    ambience_wav = str(sounds_dir / "mixkit-crickets-and-insects-in-the-wild-ambience-39.wav")
    reverb_woosh = str(sounds_dir / "mixkit-cinematic-tunnel-reverb-woosh-1486.wav")
    cinematic_swoosh = str(sounds_dir / "mixkit-cinematic-transition-swoosh-heartbeat-trailer-488.wav")
    chime_wav = str(sounds_dir / "mixkit-retro-game-notification-212.wav")
    small_sweep = str(sounds_dir / "mixkit-fast-small-sweep-transition-166.wav")
    rocket_whoosh = str(sounds_dir / "mixkit-fast-rocket-whoosh-1714.wav")
    playful_bed = str(sounds_dir / "mixkit-game-show-suspense-waiting-667.wav")

    journey_shots = [
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 48,   "out": 240,  "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 200,  "out": 800,  "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 320,  "out": 480,  "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 1800, "out": 2500, "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 4200, "out": 4900, "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261109063747_0038_D.MP4", "in": 540,  "out": 720,  "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
        {"clip": "DJI_20261109064017_0039_D.MP4", "in": 7200, "out": 8200, "zoom": True,  "speed_warp": True,  "lut": LUT_DLOG},
    ]

    journey_audio = [
        {"path": ambience_wav,     "track_index": 1, "record_frame": 360000},
        {"path": ambience_wav,     "track_index": 1, "record_frame": 362605},
        {"path": reverb_woosh,     "track_index": 2, "record_frame": 360480},
        {"path": cinematic_swoosh, "track_index": 2, "record_frame": 362550},
    ]

    cat_shots = [
        {"clip": "DJI_20261022132939_0015_D.MP4", "in": 300,  "out": 800,  "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
        {"clip": "DJI_20261022133201_0016_D.MP4", "in": 200,  "out": 650,  "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261022133619_0017_D.MP4", "in": 400,  "out": 900,  "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
        {"clip": "DJI_20261022134456_0018_D.MP4", "in": 300,  "out": 750,  "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261022150936_0019_D.MP4", "in": 200,  "out": 600,  "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261022183553_0020_D.MP4", "in": 500,  "out": 1050, "zoom": True,  "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261023151935_0023_D.MP4", "in": 400,  "out": 900,  "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261022132939_0015_D.MP4", "in": 2500, "out": 2950, "zoom": False, "speed_warp": True,  "lut": LUT_DLOG},
        {"clip": "DJI_20261022133619_0017_D.MP4", "in": 2200, "out": 2700, "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
        {"clip": "DJI_20261022183553_0020_D.MP4", "in": 3200, "out": 3800, "zoom": True,  "speed_warp": False, "lut": LUT_DLOG},
    ]

    cat_audio = [
        {"path": chime_wav,     "track_index": 2, "record_frame": 360000},
        {"path": small_sweep,   "track_index": 2, "record_frame": 360980},
        {"path": small_sweep,   "track_index": 2, "record_frame": 361930},
        {"path": rocket_whoosh, "track_index": 2, "record_frame": 363200},
        {"path": playful_bed,   "track_index": 3, "record_frame": 360500},
    ]

    tl_journey = assemble_timeline(
        client, proj, mp, "Journey_Edit", journey_shots,
        intro_text="THE JOURNEY\nSunrise & Stillness",
        outro_text="ILLUMEN DEV\nThe Journey Continues...",
        cdl_grade=JOURNEY_SUNRISE_CDL,
        remove_original_audio=True,
        audio_entries=journey_audio,
    )
    tl_cat = assemble_timeline(
        client, proj, mp, "Into_My_Cat", cat_shots,
        intro_text="MEET PINTU\nInto My Cat",
        outro_text="PINTU & ILLUMEN DEV\nSubscribe for more!",
        cdl_grade=PINTU_CAT_CDL,
        remove_original_audio=False,
        audio_entries=cat_audio,
    )

    client.save_project()
    print("\nProject saved.")

    if not args.no_render:
        yt_dir = str(ExportManager.classify_export_dir(str(ROOT / "exports"), profile_key="youtube_1080p"))
        print(f"\nExporting both timelines to YouTube folder: {yt_dir}")
        st1 = client.render_timeline(tl_journey, yt_dir, "Illumen_Dev_Journey", preset_name="YouTube - 1080p", wait=True)
        print("Journey_Edit Render:", st1)
        st2 = client.render_timeline(tl_cat, yt_dir, "Illumen_Dev_Pintu_Into_My_Cat", preset_name="YouTube - 1080p", wait=True)
        print("Into_My_Cat Render:", st2)

    return True


if __name__ == "__main__":
    main()
