"""
Cut Matcher and Assembly Manifest Generator.
Maps raw camera clips from chosen directories to reference shots in an EditBlueprint,
handling in/out trimming, slow-motion speed retiming, and LUT assignments.
"""

import os
import random
import logging
from typing import Dict, List, Optional, Any

from .reference_decoder import EditBlueprint
from ..config import CAMERA_PRESETS

logger = logging.getLogger("actioncam_mcp.matcher")

class CutMatcher:
    """Matches raw clips to reference shots and generates timeline cut lists."""

    def __init__(self, camera_preset_key: str = "dji_action4_dlog_m", custom_lut_path: Optional[str] = None):
        self.preset_info = CAMERA_PRESETS.get(camera_preset_key, CAMERA_PRESETS["dji_action4_dlog_m"])
        self.lut_path = custom_lut_path or self.preset_info.get("recommended_lut")

    def match_clips_to_blueprint(
        self,
        blueprint: EditBlueprint,
        source_clips: List[Dict[str, Any]],
        strategy: str = "smart_pacing",  # 'smart_pacing', 'chronological', 'random_shuffle'
    ) -> List[Dict[str, Any]]:
        """
        Creates a 1-to-1 mapping of timeline shots to trimmed source clips.
        """
        if not source_clips:
            raise ValueError("No source clips provided for matching.")

        slowmo_clips = [c for c in source_clips if c.get("is_slowmo") or c.get("fps", 0) >= 59.0]
        realtime_clips = [c for c in source_clips if not (c.get("is_slowmo") or c.get("fps", 0) >= 59.0)]
        all_clips = list(source_clips)

        # Fallback if categories are empty
        if not slowmo_clips:
            slowmo_clips = all_clips
        if not realtime_clips:
            realtime_clips = all_clips

        matched_shots: List[Dict[str, Any]] = []
        clip_usage_counts: Dict[str, int] = {c["path"]: 0 for c in all_clips}

        for idx, shot in enumerate(blueprint.shots):
            req_frames = shot["duration_frames"]
            pacing = shot["pacing"]
            pref_asset = shot["preferred_asset"]

            # Choose candidate pool based on shot requirements
            if pref_asset == "slowmo" and slowmo_clips:
                candidates = slowmo_clips
            elif pref_asset == "realtime" and realtime_clips:
                candidates = realtime_clips
            else:
                candidates = all_clips

            # Select clip with lowest usage to maximize variety
            candidates_sorted = sorted(candidates, key=lambda c: clip_usage_counts.get(c["path"], 0))
            selected_clip = candidates_sorted[0]
            clip_usage_counts[selected_clip["path"]] = clip_usage_counts.get(selected_clip["path"], 0) + 1

            # Determine in/out frame trimming
            # Skip the first 1-2 seconds (25-50 frames) to avoid camera shake
            clip_dur_sec = selected_clip.get("duration_sec", 10.0)
            clip_total_frames = int(clip_dur_sec * blueprint.fps)
            
            # Speed retiming for slow-motion clips (e.g. 120fps clip on 25fps timeline = 0.208x speed)
            clip_fps = selected_clip.get("fps", blueprint.fps)
            if selected_clip.get("is_slowmo") and clip_fps > blueprint.fps:
                speed_ratio = round(blueprint.fps / clip_fps, 3)
                source_frames_needed = int(req_frames / speed_ratio)
            else:
                speed_ratio = 1.0
                source_frames_needed = req_frames

            # Calculate safe in/out points
            safe_head = min(50, max(0, clip_total_frames - source_frames_needed))
            start_frame = safe_head
            end_frame = start_frame + source_frames_needed

            if end_frame > clip_total_frames and clip_total_frames > 0:
                start_frame = 0
                end_frame = min(source_frames_needed, clip_total_frames)

            matched_shots.append({
                "shot_index": shot["shot_index"],
                "record_frame": shot["start_frame"],
                "record_end_frame": shot["end_frame"],
                "timeline_duration": req_frames,
                "clip_name": selected_clip.get("name"),
                "clip_path": selected_clip["path"],
                "source_start_frame": start_frame,
                "source_end_frame": end_frame,
                "source_fps": clip_fps,
                "speed_multiplier": speed_ratio,
                "lut_path": self.lut_path,
                "suggested_vfx": shot.get("suggested_vfx", "none"),
                "audio_cue": shot.get("audio_cue", "none"),
                "pacing": pacing,
            })

        logger.info(f"Successfully matched {len(matched_shots)} shots to source clips")
        return matched_shots

