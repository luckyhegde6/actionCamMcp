"""
Installer script for ActionCam MCP Studio Workflow Integration Plugin.
Copies or symlinks the plugin into DaVinci Resolve Studio's Workflow Integration Plugins folder.
"""

import os
import sys
import shutil
from pathlib import Path

PLUGIN_SRC = Path(__file__).resolve().parent / "workflow_plugin" / "com.actioncam.resolve.studio"
RESOLVE_PLUGINS_ROOT = Path(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Workflow Integration Plugins")
TARGET_DIR = RESOLVE_PLUGINS_ROOT / "com.actioncam.resolve.studio"

def install():
    print(f"Installing ActionCam MCP Studio Workflow Plugin into DaVinci Resolve...")
    print(f"Source: {PLUGIN_SRC}")
    print(f"Target: {TARGET_DIR}")

    if not PLUGIN_SRC.exists():
        print(f"Error: Plugin source directory not found at {PLUGIN_SRC}")
        return False

    try:
        RESOLVE_PLUGINS_ROOT.mkdir(parents=True, exist_ok=True)

        if TARGET_DIR.exists():
            print(f"Existing plugin directory found. Updating...")
            shutil.rmtree(TARGET_DIR)

        shutil.copytree(PLUGIN_SRC, TARGET_DIR)
        print(f"\n[SUCCESS] ActionCam MCP Studio Plugin successfully installed!")
        print(f"You can now launch DaVinci Resolve Studio and access it under:")
        print(f"  Workspace > Workflow Integrations > ActionCam MCP Studio Workflow\n")
        return True
    except PermissionError:
        print("\n[NOTE] Administrator permissions required to write into %PROGRAMDATA%.")
        print("To install into DaVinci Resolve Studio:")
        print("  1. Open an Administrator PowerShell or Command Prompt.")
        print(f"  2. Run: python \"{Path(__file__).resolve()}\"")
        print("  OR manually copy:")
        print(f"     \"{PLUGIN_SRC}\"")
        print("     to:")
        print(f"     \"{TARGET_DIR}\"\n")
        return False

if __name__ == "__main__":
    install()
