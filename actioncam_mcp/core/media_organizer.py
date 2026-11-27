"""
Media Organizer and Metadata Scanner for Action Cam footage.
Parses MP4/MOV metadata directly using pure Python ISO BMFF parsing,
classifies clips (frame rates, slow-motion, resolutions), and organizes
files into standardized project directories and DaVinci Resolve bins.
"""

import os
import shutil
import struct
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from ..config import PROJECT_DIR_STRUCTURE

logger = logging.getLogger("actioncam_mcp.organizer")

def parse_mp4_metadata(file_path: str) -> Dict[str, Any]:
    """
    Fast pure-Python parser for MP4/MOV files.
    Extracts duration, timescale, width, height, and calculated FPS.
    """
    metadata = {
        "duration_seconds": 0.0,
        "width": 0,
        "height": 0,
        "fps": 25.0,
        "is_slowmo": False,
        "file_size_mb": 0.0,
    }

    try:
        size_bytes = os.path.getsize(file_path)
        metadata["file_size_mb"] = round(size_bytes / (1024 * 1024), 2)

        with open(file_path, "rb") as f:
            while f.tell() < size_bytes:
                header = f.read(8)
                if len(header) < 8:
                    break
                atom_size, atom_type = struct.unpack(">I4s", header)
                atom_type = atom_type.decode("latin1", errors="ignore")

                if atom_size == 1:
                    # 64-bit size
                    ext_header = f.read(8)
                    atom_size = struct.unpack(">Q", ext_header)[0]
                    body_size = atom_size - 16
                else:
                    body_size = atom_size - 8

                if body_size < 0:
                    break

                if atom_type == "moov":
                    # Read inside moov container
                    moov_data = f.read(body_size)
                    _parse_moov_payload(moov_data, metadata)
                    break
                else:
                    f.seek(body_size, os.SEEK_CUR)

    except Exception as e:
        logger.debug(f"Could not fully parse MP4 {file_path}: {e}")

    # Fallback heuristic if FPS couldn't be parsed
    if metadata["fps"] >= 59.0:
        metadata["is_slowmo"] = True

    return metadata

def _parse_moov_payload(data: bytes, metadata: Dict[str, Any]):
    """Walks atoms inside moov to extract mvhd, tkhd, and mdhd."""
    offset = 0
    total_len = len(data)

    while offset + 8 <= total_len:
        atom_size, atom_type = struct.unpack_from(">I4s", data, offset)
        atom_type = atom_type.decode("latin1", errors="ignore")

        if atom_size == 1:
            atom_size = struct.unpack_from(">Q", data, offset + 8)[0]
            header_size = 16
        else:
            header_size = 8

        if atom_size <= 0 or offset + atom_size > total_len:
            break

        body_offset = offset + header_size
        body_len = atom_size - header_size

        if atom_type == "mvhd":
            # Movie header: version (1 byte), flags (3 bytes)
            version = data[body_offset]
            if version == 0 and body_len >= 20:
                # v0: creation (4), mod (4), timescale (4), duration (4)
                timescale, duration = struct.unpack_from(">II", data, body_offset + 12)
                if timescale > 0:
                    metadata["duration_seconds"] = round(duration / timescale, 2)
            elif version == 1 and body_len >= 28:
                # v1: creation (8), mod (8), timescale (4), duration (8)
                timescale, duration = struct.unpack_from(">IQ", data, body_offset + 20)
                if timescale > 0:
                    metadata["duration_seconds"] = round(duration / timescale, 2)

        elif atom_type == "trak":
            # Traverse trak to find tkhd and mdhd
            _parse_trak_payload(data[body_offset : body_offset + body_len], metadata)

        offset += atom_size

def _parse_trak_payload(data: bytes, metadata: Dict[str, Any]):
    """Extracts resolution and sample rate from trak."""
    offset = 0
    total_len = len(data)

    while offset + 8 <= total_len:
        atom_size, atom_type = struct.unpack_from(">I4s", data, offset)
        atom_type = atom_type.decode("latin1", errors="ignore")

        if atom_size == 1:
            atom_size = struct.unpack_from(">Q", data, offset + 8)[0]
            header_size = 16
        else:
            header_size = 8

        if atom_size <= 0 or offset + atom_size > total_len:
            break

        body_offset = offset + header_size
        body_len = atom_size - header_size

        if atom_type == "tkhd":
            version = data[body_offset]
            # Width and height are at the end of tkhd in fixed point 16.16
            if version == 0 and body_len >= 84:
                w_fixed, h_fixed = struct.unpack_from(">II", data, body_offset + 76)
                w, h = w_fixed >> 16, h_fixed >> 16
                if w > 0 and h > 0 and metadata["width"] == 0:
                    metadata["width"] = w
                    metadata["height"] = h
            elif version == 1 and body_len >= 96:
                w_fixed, h_fixed = struct.unpack_from(">II", data, body_offset + 88)
                w, h = w_fixed >> 16, h_fixed >> 16
                if w > 0 and h > 0 and metadata["width"] == 0:
                    metadata["width"] = w
                    metadata["height"] = h

        elif atom_type == "mdia":
            # Inside mdia -> mdhd or minf -> stbl -> stts for FPS
            _parse_mdia_payload(data[body_offset : body_offset + body_len], metadata)

        offset += atom_size

def _parse_mdia_payload(data: bytes, metadata: Dict[str, Any]):
    """Recursively search for mdhd or stbl in mdia."""
    offset = 0
    total_len = len(data)

    while offset + 8 <= total_len:
        atom_size, atom_type = struct.unpack_from(">I4s", data, offset)
        atom_type = atom_type.decode("latin1", errors="ignore")
        if atom_size <= 0 or offset + atom_size > total_len:
            break

        body = data[offset + 8 : offset + atom_size]
        if atom_type == "mdhd" and len(body) >= 20:
            version = body[0]
            if version == 0:
                timescale, duration = struct.unpack_from(">II", body, 12)
            else:
                timescale, duration = struct.unpack_from(">IQ", body, 20)
            if timescale > 0 and metadata["duration_seconds"] == 0:
                metadata["duration_seconds"] = round(duration / timescale, 2)
        elif atom_type in ("minf", "stbl"):
            _parse_mdia_payload(body, metadata)
        elif atom_type == "stts" and len(body) >= 16:
            # Time-to-sample atom: entry count, sample count, sample delta
            entry_count = struct.unpack_from(">I", body, 4)[0]
            if entry_count > 0:
                sample_count, sample_delta = struct.unpack_from(">II", body, 8)
                # If timescale known from mdhd or default 24000/25000/30000/60000/120000
                if sample_delta > 0:
                    # Common action camera timebases
                    if sample_delta in (1000, 2000, 500, 250):
                        fps_calc = 120000 / sample_delta if sample_delta <= 1000 else 60.0
                    else:
                        fps_calc = 25.0
                    # Check for 120fps, 60fps, 50fps, 25fps
                    if sample_delta <= 500:
                        metadata["fps"] = 120.0
                        metadata["is_slowmo"] = True
                    elif sample_delta <= 1000:
                        metadata["fps"] = 60.0
                    else:
                        metadata["fps"] = 25.0

        offset += atom_size


class MediaOrganizer:
    """Scans and organizes media directories for video editing."""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)

    def scan_directory(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Scans a directory for video, audio, and reference files.
        Extracts format, duration, resolution, and slow-mo flags.
        """
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        video_exts = {".mp4", ".mov", ".m4v", ".mkv", ".braw", ".avi"}
        audio_exts = {".wav", ".mp3", ".aac", ".m4a", ".flac", ".aif"}
        ref_names = {"ref", "reference", "sample", "guide", "edit"}

        scanned = []
        for file in src.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower()
                if ext in video_exts:
                    meta = parse_mp4_metadata(str(file))
                    is_ref = any(ref in file.stem.lower() for ref in ref_names)
                    scanned.append({
                        "name": file.name,
                        "path": str(file.resolve()),
                        "type": "reference" if is_ref else "video",
                        "size_mb": meta["file_size_mb"],
                        "duration_sec": meta["duration_seconds"],
                        "width": meta["width"],
                        "height": meta["height"],
                        "fps": meta["fps"],
                        "is_slowmo": meta["is_slowmo"],
                    })
                elif ext in audio_exts:
                    scanned.append({
                        "name": file.name,
                        "path": str(file.resolve()),
                        "type": "audio",
                        "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                        "duration_sec": 0.0,
                        "width": 0,
                        "height": 0,
                        "fps": 0,
                        "is_slowmo": False,
                    })

        logger.info(f"Scanned {len(scanned)} assets in {source_path}")
        return scanned

    def setup_project_folders(self) -> Dict[str, Path]:
        """Creates standard project folders on disk."""
        created = {}
        for sub in PROJECT_DIR_STRUCTURE:
            target = self.project_dir / sub
            target.mkdir(parents=True, exist_ok=True)
            created[sub] = target
        return created

    def organize_assets(
        self,
        source_assets: List[Dict[str, Any]],
        mode: str = "copy",  # 'copy', 'move', or 'symlink'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organizes scanned assets into project folders.
        Groups into Realtime vs SlowMo, Reference Videos, and Audio.
        """
        folders = self.setup_project_folders()
        organized: Dict[str, List[Dict[str, Any]]] = {
            "realtime": [],
            "slowmo": [],
            "reference": [],
            "audio": [],
        }

        for asset in source_assets:
            src_file = Path(asset["path"])
            dest_dir = None

            if asset["type"] == "reference":
                dest_dir = folders["02_Reference_Videos"]
                category = "reference"
            elif asset["type"] == "audio":
                dest_dir = folders["03_Audio_Music_SFX/Music"]
                category = "audio"
            elif asset["is_slowmo"] or asset["fps"] >= 59.0:
                dest_dir = folders["01_Original_Camera_Files/SlowMo_60_120fps"]
                category = "slowmo"
            else:
                dest_dir = folders["01_Original_Camera_Files/Realtime_25_30fps"]
                category = "realtime"

            dest_path = dest_dir / src_file.name

            # Avoid re-copying if already in destination
            if src_file.resolve() != dest_path.resolve():
                if mode == "copy":
                    shutil.copy2(src_file, dest_path)
                elif mode == "move":
                    shutil.move(src_file, dest_path)
                elif mode == "symlink":
                    try:
                        dest_path.symlink_to(src_file)
                    except OSError:
                        shutil.copy2(src_file, dest_path)

            organized_item = dict(asset)
            organized_item["organized_path"] = str(dest_path.resolve())
            organized[category].append(organized_item)

        return organized

