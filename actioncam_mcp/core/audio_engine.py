"""
Audio and Sound Design Engine.
Manages background music alignment, cut-point SFX placement (impacts, risers, whooshes),
and Fairlight track assignment for DaVinci Resolve.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..config import DEFAULT_SOUNDS_DIR

logger = logging.getLogger("actioncam_mcp.audio")

AUDIO_EXTENSIONS = {".wav", ".mp3", ".aac", ".m4a", ".flac", ".ogg"}


class AudioEngine:
    """Handles sound design, BGM placement, and transition SFX matching."""

    def __init__(self, sfx_library_dir: Optional[str] = None):
        self.sfx_library_dir = Path(sfx_library_dir) if sfx_library_dir else DEFAULT_SOUNDS_DIR

    def scan_sounds_library(self) -> Dict[str, List[str]]:
        """Scans the default audio mixin source (e.g. ) and categorizes audio files."""
        categories: Dict[str, List[str]] = {
            "ambience": [],
            "whoosh": [],
            "impact": [],
            "chime": [],
            "bgm": [],
            "all": [],
        }
        if not self.sfx_library_dir.exists():
            logger.warning(f"Audio library directory not found: {self.sfx_library_dir}")
            return categories

        for entry in sorted(self.sfx_library_dir.iterdir()):
            if not entry.is_file() or entry.suffix.lower() not in AUDIO_EXTENSIONS:
                continue
            path_str = str(entry.resolve())
            name = entry.name.lower()
            categories["all"].append(path_str)
            if any(k in name for k in ("ambience", "cricket", "wind", "nature", "rain", "forest")):
                categories["ambience"].append(path_str)
            elif any(k in name for k in ("whoosh", "woosh", "swoosh", "sweep")):
                categories["whoosh"].append(path_str)
            elif any(k in name for k in ("impact", "hit", "boom", "heartbeat", "drop")):
                categories["impact"].append(path_str)
            elif any(k in name for k in ("notification", "chime", "retro", "bell")):
                categories["chime"].append(path_str)
            elif any(k in name for k in ("waiting", "music", "bgm", "track", "suspense")):
                categories["bgm"].append(path_str)
        return categories

    def plan_sound_design(
        self,
        matched_shots: List[Dict[str, Any]],
        bgm_path: Optional[str] = None,
        available_sfx_files: Optional[List[str]] = None,
        fps: float = 25.0,
    ) -> Dict[str, Any]:
        """
        Creates an audio assembly plan:
        - Audio Track 1: Master BGM / Music
        - Audio Track 2: Impact / Beat Hits (aligned with fast action cuts)
        - Audio Track 3: Whooshes / Swishes (aligned 4-8 frames before transition)
        """
        plan = {
            "bgm": None,
            "sfx_cues": [],
        }

        if bgm_path and os.path.exists(bgm_path):
            plan["bgm"] = {
                "path": str(Path(bgm_path).resolve()),
                "track_index": 1,
                "start_frame": 0,
                "record_frame": 0,
            }

        sfx_files = available_sfx_files or []
        impact_sfx = [f for f in sfx_files if any(k in os.path.basename(f).lower() for k in ("impact", "hit", "boom", "drop"))]
        whoosh_sfx = [f for f in sfx_files if any(k in os.path.basename(f).lower() for k in ("whoosh", "transition", "swish"))]

        for shot in matched_shots:
            cue = shot.get("audio_cue")
            rec_frame = shot.get("record_frame", 0)

            if cue == "impact":
                # Place impact sound right at cut frame
                sfx_file = impact_sfx[0] if impact_sfx else None
                plan["sfx_cues"].append({
                    "type": "impact",
                    "path": sfx_file,
                    "record_frame": rec_frame,
                    "track_index": 2,
                    "volume_db": -2.0,
                    "description": f"Cut hit at frame {rec_frame}",
                })
            elif cue == "whoosh":
                # Lead in whoosh 6 frames before cut
                lead_frame = max(0, rec_frame - 6)
                sfx_file = whoosh_sfx[0] if whoosh_sfx else None
                plan["sfx_cues"].append({
                    "type": "whoosh",
                    "path": sfx_file,
                    "record_frame": lead_frame,
                    "track_index": 3,
                    "volume_db": -6.0,
                    "description": f"Transition whoosh leading into frame {rec_frame}",
                })

        logger.info(f"Generated audio plan: BGM={'Yes' if plan['bgm'] else 'No'}, SFX Cues={len(plan['sfx_cues'])}")
        return plan

