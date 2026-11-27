"""CLI hook entrypoint for playing ActionCam MCP notification sounds."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core.sound_notifier import SoundNotifier


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "task_done"
    SoundNotifier().notify(event, block=True)


if __name__ == "__main__":
    main()
