"""
Configuration module for ActionCam MCP.
Contains Resolve Scripting paths, project templates, presets, and export profiles.
"""

import os
import sys
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE_ROOT = Path("F:/Edits/actionCamMcp/projects")
DEFAULT_SOUNDS_DIR = Path(os.getenv("ACTIONCAM_SOUNDS_DIR", "F:/Edits/Sounds"))

# DaVinci Resolve Scripting Paths (Windows)
RESOLVE_SCRIPT_API_DEFAULT = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
RESOLVE_SCRIPT_LIB_DEFAULT = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
RESOLVE_MODULES_PATH_DEFAULT = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
RESOLVE_EXE_DEFAULT = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"

# Standard Project Directory Structure
PROJECT_DIR_STRUCTURE = [
    "01_Original_Camera_Files",
    "01_Original_Camera_Files/Realtime_25_30fps",
    "01_Original_Camera_Files/SlowMo_60_120fps",
    "02_Reference_Videos",
    "03_Audio_Music_SFX",
    "03_Audio_Music_SFX/Music",
    "03_Audio_Music_SFX/SFX_Impacts",
    "03_Audio_Music_SFX/SFX_Whooshes",
    "04_LUTs_Presets",
    "05_Exports",
    "05_Exports/YouTube",
    "05_Exports/Reels_Shorts",
    "05_Exports/Master",
    "05_Exports/Web_Preview",
    "06_VFX_Assets",
]

# Standard Media Pool Bins in DaVinci Resolve
MEDIA_POOL_BINS = [
    "01 Raw Footage",
    "01 Raw Footage/Realtime",
    "01 Raw Footage/Slow Motion",
    "02 Reference Edits",
    "03 Audio & SFX",
    "03 Audio & SFX/Music",
    "03 Audio & SFX/SFX",
    "04 Timelines",
    "05 VFX & Titles",
]

# Export Profiles for Deliver Page
EXPORT_PROFILES = {
    "youtube_4k": {
        "name": "YouTube 4K UHD",
        "category_folder": "YouTube",
        "format": "mp4",
        "codec": "H265",
        "width": 3840,
        "height": 2160,
        "frame_rate": 25.0,
        "quality_bitrate": 45000,
        "audio_codec": "aac",
        "description": "High quality 4K 25fps export optimized for YouTube compression",
    },
    "youtube_1080p": {
        "name": "YouTube 1080p HD",
        "category_folder": "YouTube",
        "format": "mp4",
        "codec": "H264",
        "width": 1920,
        "height": 1080,
        "frame_rate": 100.0,
        "quality_bitrate": 25000,
        "audio_codec": "aac",
        "description": "1080p HD export optimized for YouTube upload",
    },
    "reels_shorts_9_16": {
        "name": "Instagram Reels / TikTok / YouTube Shorts (9:16)",
        "category_folder": "Reels_Shorts",
        "format": "mp4",
        "codec": "H264",
        "width": 1080,
        "height": 1920,
        "frame_rate": 30.0,
        "quality_bitrate": 20000,
        "audio_codec": "aac",
        "description": "Vertical 1080x1920 9:16 format with high bitrate for social feeds",
    },
    "master_dnxhr": {
        "name": "Master Archive (DNxHR HQX)",
        "category_folder": "Master",
        "format": "mov",
        "codec": "DNxHR",
        "width": 3840,
        "height": 2160,
        "frame_rate": 25.0,
        "quality_bitrate": 0,  # Uncompressed/Master
        "audio_codec": "lpcm",
        "description": "Lossless 10-bit master delivery archive for grading & storage",
    },
    "web_1080p_fast": {
        "name": "Web Preview 1080p Fast",
        "category_folder": "Web_Preview",
        "format": "mp4",
        "codec": "H264",
        "width": 1920,
        "height": 1080,
        "frame_rate": 25.0,
        "quality_bitrate": 10000,
        "audio_codec": "aac",
        "description": "Quick lightweight preview export for client review and sharing",
    },
}

# Color & Camera Presets
CAMERA_PRESETS = {
    "dji_action4_dlog_m": {
        "name": "DJI Action 4 D-Log M (10-Bit)",
        "color_space": "Rec.709",
        "gamma": "Rec.709",
        "recommended_lut": "DJI_Action4_DLogM_to_Rec709.cube",
        "description": "Flat color profile with maximum dynamic range, mapped to Rec.709 contrast",
    },
    "dji_action4_normal": {
        "name": "DJI Action 4 Normal (Standard Rec.709)",
        "color_space": "Rec.709",
        "gamma": "Rec.709",
        "recommended_lut": None,
        "description": "Ready-to-use color profile with punchy contrast and vibrant saturation",
    },
}

# Server Settings
DEFAULT_API_HOST = "127.0.0.1"
DEFAULT_API_PORT = 8765

