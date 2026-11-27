"""
Sound Notifier for ActionCam MCP Studio.
Plays non-blocking audio cues from actioncam_mcp/assets/sounds/ for:
- export_done, task_done, error, tool_step
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("actioncam_mcp.sound_notifier")

SOUNDS_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"

SOUND_FILES = {
    "export_done": "export_done.ogg",
    "task_done": "task_done.ogg",
    "error": "error.ogg",
    "tool_step": "tool_step.ogg",
}


class SoundNotifier:
    """Plays non-blocking notification sounds for MCP tool events."""

    def __init__(self, assets_dir: Optional[Path] = None, enabled: Optional[bool] = None):
        self.assets_dir = Path(assets_dir) if assets_dir else SOUNDS_ASSETS_DIR
        if enabled is None:
            self.enabled = os.getenv("ACTIONCAM_ENABLE_SOUNDS", "1") != "0"
        else:
            self.enabled = enabled

    def get_sound_path(self, event: str) -> Optional[Path]:
        fname = SOUND_FILES.get(event)
        if not fname:
            return None
        path = self.assets_dir / fname
        return path if path.exists() else None

    def notify(self, event: str, block: bool = False) -> bool:
        """
        Triggers a notification sound for `event` ('export_done', 'task_done', 'error', 'tool_step').
        Never raises if audio hardware or players are unavailable.
        """
        if not self.enabled:
            return False
        sound_path = self.get_sound_path(event)
        if not sound_path:
            return False
        try:
            if os.name == "nt":
                ps_cmd = (
                    f"Add-Type -AssemblyName PresentationCore; "
                    f"$p = New-Object System.Windows.Media.MediaPlayer; "
                    f"$p.Open([uri]'{sound_path.as_uri()}'); $p.Play(); Start-Sleep -Milliseconds 1500"
                )
                proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if block:
                    proc.wait(timeout=3)
                return True
        except Exception as e:
            logger.debug(f"Sound notification skipped ({event}): {e}")
        return False
