"""
Export Manager for Deliver Page presets and render queue jobs.
Provides presets for YouTube 4K, 9:16 Reels/Shorts, Master ProRes/DNxHR, and Web 1080p.
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..config import EXPORT_PROFILES
from .resolve_client import ResolveClient

logger = logging.getLogger("actioncam_mcp.export")

class ExportManager:
    """Manages Deliver page render settings, export classification, and queue dispatch."""

    def __init__(self, resolve_client: Optional[ResolveClient] = None):
        self.resolve_client = resolve_client

    def get_available_profiles(self) -> Dict[str, Any]:
        """Returns the dictionary of configured export profiles."""
        return EXPORT_PROFILES

    @staticmethod
    def classify_export_folder(
        profile_key: Optional[str] = None,
        preset_name: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> str:
        """
        Determines the destination subfolder (e.g. 'YouTube', 'Reels_Shorts', 'Master', 'Web_Preview')
        based on the export profile, Resolve preset name, or filename.
        """
        if profile_key and profile_key in EXPORT_PROFILES:
            folder = EXPORT_PROFILES[profile_key].get("category_folder")
            if folder:
                return folder

        hint = f"{profile_key or ''} {preset_name or ''} {filename or ''}".lower()
        if any(k in hint for k in ("short", "reel", "tiktok", "9_16", "vertical")):
            return "Reels_Shorts"
        if any(k in hint for k in ("youtube", "yt", "illumen")):
            return "YouTube"
        if any(k in hint for k in ("master", "dnxhr", "prores", "archive")):
            return "Master"
        if any(k in hint for k in ("web", "preview")):
            return "Web_Preview"
        return "YouTube"

    @classmethod
    def classify_export_dir(
        cls,
        base_output_dir: str,
        profile_key: Optional[str] = None,
        preset_name: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """Resolves and creates the classified export subdirectory (e.g. exports/YouTube)."""
        base = Path(base_output_dir)
        category = cls.classify_export_folder(profile_key=profile_key, preset_name=preset_name, filename=filename)
        if base.name.lower() == category.lower():
            target = base
        else:
            target = base / category
        target.mkdir(parents=True, exist_ok=True)
        return target

    @classmethod
    def organize_existing_exports(cls, base_output_dir: str) -> List[Dict[str, str]]:
        """Moves root-level exported media files into their classified subfolders (e.g. YouTube/)."""
        base = Path(base_output_dir)
        if not base.exists():
            return []
        moved = []
        for entry in base.iterdir():
            if entry.is_file() and entry.suffix.lower() in (".mp4", ".mov", ".mkv"):
                target_dir = cls.classify_export_dir(str(base), filename=entry.name)
                dest = target_dir / entry.name
                if dest != entry:
                    shutil.move(str(entry), str(dest))
                    moved.append({"source": str(entry), "destination": str(dest), "category": target_dir.name})
        return moved

    def queue_render(
        self,
        output_dir: str,
        filename_prefix: str,
        profile_key: str = "youtube_4k",
        custom_overrides: Optional[Dict[str, Any]] = None,
        classify: bool = True,
    ) -> Dict[str, Any]:
        """
        Configures the render job in DaVinci Resolve, automatically classifying into
        platform folders (e.g. YouTube/) when classify=True.
        """
        profile = EXPORT_PROFILES.get(profile_key, EXPORT_PROFILES["youtube_4k"])
        out_dir = (
            self.classify_export_dir(output_dir, profile_key=profile_key, filename=filename_prefix)
            if classify
            else Path(output_dir)
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        render_info = {
            "profile_key": profile_key,
            "profile_name": profile["name"],
            "category_folder": out_dir.name,
            "target_dir": str(out_dir.resolve()),
            "filename": f"{filename_prefix}.{profile['format']}",
            "resolution": f"{profile['width']}x{profile['height']}",
            "codec": profile["codec"],
            "fps": profile["frame_rate"],
        }

        if self.resolve_client and self.resolve_client.is_connected():
            job_id = self.resolve_client.setup_render_job(
                target_dir=str(out_dir.resolve()),
                custom_name=filename_prefix,
                profile_key=profile_key,
                custom_settings=custom_overrides,
            )
            render_info["job_id"] = job_id
            render_info["status"] = "Queued in DaVinci Resolve"
        else:
            render_info["job_id"] = None
            render_info["status"] = "Prepared (Resolve offline)"

        return render_info

