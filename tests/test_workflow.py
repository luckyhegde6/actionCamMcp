"""
End-to-end integration test for ActionCam MCP core workflow.
Tests Reference Decoder, Cut Matcher, Audio Engine, and FCPXML Generator.
"""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core import (
    ReferenceDecoder,
    CutMatcher,
    AudioEngine,
    ExportManager,
    generate_fcpxml,
)

def run_test():
    test_dir = ROOT / "tests" / "sample_media"
    test_dir.mkdir(parents=True, exist_ok=True)

    dummy_ref = str(test_dir / "reference_action.mp4")
    if not os.path.exists(dummy_ref):
        with open(dummy_ref, "wb") as f:
            f.write(b"\x00" * 1024)

    dummy_clips = [
        {
            "name": "DJI_0001.MP4",
            "path": str(test_dir / "DJI_0001.MP4"),
            "type": "video",
            "duration_sec": 12.0,
            "fps": 25.0,
            "is_slowmo": False,
        },
        {
            "name": "DJI_0002_120fps.MP4",
            "path": str(test_dir / "DJI_0002_120fps.MP4"),
            "type": "video",
            "duration_sec": 8.0,
            "fps": 120.0,
            "is_slowmo": True,
        },
        {
            "name": "DJI_0003_120fps.MP4",
            "path": str(test_dir / "DJI_0003_120fps.MP4"),
            "type": "video",
            "duration_sec": 15.0,
            "fps": 120.0,
            "is_slowmo": True,
        },
    ]

    print("\n--- 1. Testing Reference Decoder ---")
    decoder = ReferenceDecoder()
    blueprint = decoder.decode_reference(dummy_ref, target_fps=25.0)
    print(f"Decoded {len(blueprint.shots)} shots, total duration: {blueprint.total_duration_sec}s, pacing: {blueprint.pacing_style}")
    assert len(blueprint.shots) > 0, "Blueprint must contain shots"

    print("\n--- 2. Testing Cut Matcher ---")
    matcher = CutMatcher(camera_preset_key="dji_action4_dlog_m")
    matched = matcher.match_clips_to_blueprint(blueprint, dummy_clips)
    print(f"Matched {len(matched)} cuts across source clips:")
    for m in matched[:4]:
        print(f"  Shot #{m['shot_index']}: {m['clip_name']} ({m['pacing']}) | "
              f"Frames: {m['source_start_frame']} -> {m['source_end_frame']} | "
              f"Speed: {m['speed_multiplier']}x | LUT: {m['lut_path']}")
    assert len(matched) == len(blueprint.shots), "Every blueprint shot must be matched"

    print("\n--- 3. Testing Audio Engine ---")
    audio_engine = AudioEngine()
    dummy_bgm = str(test_dir / "action_bgm.wav")
    with open(dummy_bgm, "wb") as f:
        f.write(b"\x00" * 512)

    dummy_sfx = [str(test_dir / "whoosh_01.wav"), str(test_dir / "impact_heavy.wav")]
    for s in dummy_sfx:
        with open(s, "wb") as f:
            f.write(b"\x00" * 256)

    audio_plan = audio_engine.plan_sound_design(matched, bgm_path=dummy_bgm, available_sfx_files=dummy_sfx)
    print(f"Audio plan generated: BGM={bool(audio_plan['bgm'])}, SFX Cues={len(audio_plan['sfx_cues'])}")
    assert audio_plan["bgm"] is not None

    print("\n--- 4. Testing FCPXML 1.9 Generator ---")
    xml_out = str(test_dir / "ActionCam_Test_Timeline.fcpxml")
    gen_path = generate_fcpxml("ActionCam_Test_Timeline", matched, xml_out, fps=25.0, bgm_path=dummy_bgm)
    assert os.path.exists(gen_path), "FCPXML must exist"
    size = os.path.getsize(gen_path)
    print(f"FCPXML generated successfully: {gen_path} ({size} bytes)")

    print("\n--- 5. Testing Export Manager ---")
    exp_mgr = ExportManager()
    profiles = exp_mgr.get_available_profiles()
    print(f"Available Deliver export profiles: {list(profiles.keys())}")
    assert "youtube_4k" in profiles
    assert "reels_shorts_9_16" in profiles

    render_job = exp_mgr.queue_render(
        output_dir=str(test_dir / "exports"),
        filename_prefix="Test_Action_Export",
        profile_key="youtube_4k",
    )
    print(f"Prepared render job: {render_job}")

    print("\nALL CORE INTEGRATION TESTS PASSED!\n")

if __name__ == "__main__":
    run_test()

