"""
Desktop Application Launcher for ActionCam MCP.
Starts the local API server and opens the UI in native desktop application mode
(using Edge or Chrome app window, or system default browser).
"""

import os
import sys
import time
import shutil
import webbrowser
import subprocess
import threading
from pathlib import Path

from ..server.http_api import start_server
from ..config import DEFAULT_API_HOST, DEFAULT_API_PORT

def find_browser_app_executable():
    """Finds Chrome or Edge to run UI in clean standalone window mode."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def open_desktop_window(url: str):
    """Opens URL in app window mode if supported, or system browser."""
    browser_exe = find_browser_app_executable()
    if browser_exe:
        try:
            subprocess.Popen([browser_exe, f"--app={url}", "--window-size=1280,850"])
            return
        except Exception:
            pass
    webbrowser.open(url)

def main():
    host = DEFAULT_API_HOST
    port = DEFAULT_API_PORT
    url = f"http://{host}:{port}/index.html"

    ui_dir = str(Path(__file__).resolve().parent)

    # Start server in thread
    server_thread = threading.Thread(
        target=start_server,
        kwargs={"host": host, "port": port, "ui_dir": ui_dir},
        daemon=True,
    )
    server_thread.start()

    # Wait for server to bind
    time.sleep(1.0)

    print(f"Launching ActionCam MCP Desktop Window...")
    open_desktop_window(url)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting ActionCam MCP Desktop...")

if __name__ == "__main__":
    main()

