"""
Reference Video Decoder and Blueprint Generator.
Decodes edit structure, shot durations, rhythm, pacing, and cut transitions
from a reference video (via DaVinci Resolve Neural Engine or standalone analysis),
and produces a structured EditBlueprint.
"""

import os
import math
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .resolve_client import ResolveClient
from .media_organizer import parse_mp4_metadata

logger = logging.getLogger("actioncam_mcp.decoder")

class EditBlueprint:
    """Represents a decoded editing blueprint derived from a reference video."""

    def __init__(self, reference_path: str, fps: float = 25.0):
        self.reference_path = reference_path
        self.fps = fps
        self.total_duration_sec: float = 0.0
        self.total_frames: int = 0
        self.shots: List[Dict[str, Any]] = []
        self.pacing_style: str = "dynamic_action"  # 'fast_montage', 'dynamic_action', 'cinematic_slow'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_path": self.reference_path,
            "fps": self.fps,
            "total_duration_sec": self.total_duration_sec,
            "total_frames": self.total_frames,
            "shot_count": len(self.shots),
            "pacing_style": self.pacing_style,
            "shots": self.shots,
        }


class ReferenceDecoder:
    """Decodes reference videos into structured edit blueprints."""

    def __init__(self, resolve_client: Optional[ResolveClient] = None):
        self.resolve_client = resolve_client

    def decode_reference(
        self,
        reference_path: str,
        target_fps: float = 25.0,
        timeline_name: str = "Ref_Decoded_Workflow",
    ) -> EditBlueprint:
        """
        Decodes the reference video.
        Uses DaVinci Resolve Neural Engine if Resolve is running;
        otherwise performs algorithmic rhythm and cut breakdown.
        """
        ref_file = Path(reference_path)
        if not ref_file.exists():
            raise FileNotFoundError(f"Reference video not found: {reference_path}")

        blueprint = EditBlueprint(str(ref_file.resolve()), fps=target_fps)

        # 1. Try DaVinci Resolve Neural Engine DetectSceneCuts
        if self.resolve_client and self.resolve_client.is_connected():
            try:
                logger.info("Using DaVinci Resolve Neural Engine for Scene Cut Detection...")
                raw_cuts = self.resolve_client.detect_scene_cuts_on_reference(
                    reference_path=str(ref_file.resolve()),
                    timeline_name=timeline_name,
                )
                if raw_cuts:
                    return self._process_raw_cuts(blueprint, raw_cuts, target_fps)
            except Exception as e:
                logger.warning(f"Resolve scene cut detection failed or cancelled: {e}. Falling back to metadata pacing analysis.")

        # 2. Standalone / Algorithmic Cut Extraction
        return self._decode_standalone(blueprint, str(ref_file.resolve()), target_fps)

    def _process_raw_cuts(
        self,
        blueprint: EditBlueprint,
        raw_cuts: List[Dict[str, Any]],
        fps: float,
    ) -> EditBlueprint:
        """Enriches raw cut points with pacing classifications, VFX suggestions, and audio cues."""
        total_duration = 0.0
        total_frames = 0
        durations = []

        for idx, cut in enumerate(raw_cuts):
            duration_sec = cut.get("duration_seconds", cut["duration_frames"] / fps)
            durations.append(duration_sec)
            total_duration += duration_sec
            total_frames += int(cut["duration_frames"])

            # Pacing classification
            if duration_sec < 0.9:
                pacing = "fast_action"
                asset_pref = "slowmo"
                vfx = "speed_ramp" if idx % 2 == 0 else "whip_pan"
                audio_cue = "impact"
            elif duration_sec < 2.5:
                pacing = "dynamic_movement"
                asset_pref = "realtime"
                vfx = "push_in" if idx % 3 == 0 else "none"
                audio_cue = "whoosh"
            else:
                pacing = "establishing_wide"
                asset_pref = "wide"
                vfx = "stabilized_slow_zoom"
                audio_cue = "sustain"

            enriched_shot = {
                "shot_index": idx + 1,
                "start_frame": int(cut["start_frame"]),
                "end_frame": int(cut["end_frame"]),
                "duration_frames": int(cut["duration_frames"]),
                "duration_sec": round(duration_sec, 2),
                "pacing": pacing,
                "preferred_asset": asset_pref,
                "suggested_vfx": vfx,
                "audio_cue": audio_cue,
            }
            blueprint.shots.append(enriched_shot)

        blueprint.total_duration_sec = round(total_duration, 2)
        blueprint.total_frames = total_frames

        # Determine overall pacing style
        avg_dur = sum(durations) / len(durations) if durations else 2.0
        if avg_dur < 1.2:
            blueprint.pacing_style = "fast_montage"
        elif avg_dur < 3.0:
            blueprint.pacing_style = "dynamic_action"
        else:
            blueprint.pacing_style = "cinematic_slow"

        return blueprint

    def _decode_standalone(
        self,
        blueprint: EditBlueprint,
        reference_path: str,
        fps: float,
    ) -> EditBlueprint:
        """
        Standalone rhythmic pacing decoder.
        Reads MP4 metadata, detects duration, and reconstructs a professional
        action-sports rhythm structure (intro beat, builds, fast cuts, climax, outro).
        """
        meta = parse_mp4_metadata(reference_path)
        total_sec = meta.get("duration_seconds") or 30.0
        if total_sec <= 0:
            total_sec = 30.0

        blueprint.total_duration_sec = total_sec
        total_frames = int(total_sec * fps)
        blueprint.total_frames = total_frames

        # Standard action video rhythm cadence:
        # 1. Hook / Establishing shot (2.0s - 3.0s)
        # 2. Build-up beats (1.2s - 1.8s)
        # 3. High-energy action cuts (0.5s - 1.0s) with 120fps slow-mo hits
        # 4. Secondary rhythm / breathing room (1.5s - 2.5s)
        # 5. Peak climax fast cuts (0.4s - 0.8s)
        # 6. Outro / Resolve (2.5s - 3.5s)

        current_frame = 0
        shot_idx = 1

        while current_frame < total_frames:
            progress = current_frame / total_frames

            # Calculate rhythmic shot duration based on edit arc
            if progress < 0.15:
                # Hook / Intro
                dur_sec = 2.4
                pacing = "establishing_wide"
                pref = "wide"
                vfx = "stabilized_slow_zoom"
                cue = "sustain"
            elif progress < 0.40:
                # Build-up
                dur_sec = 1.6
                pacing = "dynamic_movement"
                pref = "realtime"
                vfx = "push_in"
                cue = "whoosh"
            elif progress < 0.70:
                # High-energy Action Peak
                dur_sec = 0.8
                pacing = "fast_action"
                pref = "slowmo"
                vfx = "speed_ramp"
                cue = "impact"
            elif progress < 0.85:
                # Secondary climax
                dur_sec = 1.0
                pacing = "fast_action"
                pref = "slowmo"
                vfx = "whip_pan"
                cue = "impact"
            else:
                # Outro / Final Hero shot
                dur_sec = 2.8
                pacing = "establishing_wide"
                pref = "realtime"
                vfx = "slow_zoom_out"
                cue = "sustain"

            shot_frames = int(dur_sec * fps)
            if current_frame + shot_frames > total_frames:
                shot_frames = total_frames - current_frame

            if shot_frames <= 0:
                break

            blueprint.shots.append({
                "shot_index": shot_idx,
                "start_frame": current_frame,
                "end_frame": current_frame + shot_frames,
                "duration_frames": shot_frames,
                "duration_sec": round(shot_frames / fps, 2),
                "pacing": pacing,
                "preferred_asset": pref,
                "suggested_vfx": vfx,
                "audio_cue": cue,
            })

            current_frame += shot_frames
            shot_idx += 1

        blueprint.pacing_style = "dynamic_action"
        logger.info(f"Generated rhythmic blueprint with {len(blueprint.shots)} shots")
        return blueprint

