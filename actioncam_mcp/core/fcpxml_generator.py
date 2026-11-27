"""
FCPXML 1.9 Timeline Generator for DaVinci Resolve.
Enables offline project interchange and direct import into DaVinci Resolve Studio
via File > Import > Timeline (XML/EDL).
"""

import os
from xml.etree import ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional, Any
from pathlib import Path

def generate_fcpxml(
    timeline_name: str,
    matched_shots: List[Dict[str, Any]],
    output_xml_path: str,
    fps: float = 25.0,
    width: int = 1920,
    height: int = 1080,
    bgm_path: Optional[str] = None,
) -> str:
    """
    Constructs a standard FCPXML document for DaVinci Resolve.
    """
    root = ET.Element("fcpxml", version="1.9")
    resources = ET.SubElement(root, "resources")

    # Format definition
    frame_dur = f"100/{int(fps * 100)}s" if fps in (25.0, 50.0) else f"1001/{int(fps * 1000)}s"
    fmt = ET.SubElement(
        resources,
        "format",
        id="r1",
        frameDuration=frame_dur,
        width=str(width),
        height=str(height),
    )

    # Asset definitions
    asset_id_map = {}
    asset_counter = 2

    all_media = [s["clip_path"] for s in matched_shots if "clip_path" in s]
    if bgm_path:
        all_media.append(bgm_path)

    unique_media = sorted(list(set(all_media)))
    for media_file in unique_media:
        r_id = f"r{asset_counter}"
        asset_id_map[media_file] = r_id
        asset_counter += 1

        file_url = Path(media_file).as_uri()
        ET.SubElement(
            resources,
            "asset",
            id=r_id,
            name=Path(media_file).name,
            src=file_url,
            format="r1",
        )

    # Library and Event
    library = ET.SubElement(root, "library")
    event = ET.SubElement(library, "event", name="ActionCam_AI_Project")
    project = ET.SubElement(event, "project", name=timeline_name)

    # Sequence
    total_frames = sum(s.get("timeline_duration", 50) for s in matched_shots)
    total_duration_str = f"{total_frames * 100}/{int(fps * 100)}s"

    sequence = ET.SubElement(
        project,
        "sequence",
        format="r1",
        duration=total_duration_str,
        tcStart="0s",
    )

    spine = ET.SubElement(sequence, "spine")

    # Video Clips on Spine
    curr_frame = 0
    for shot in matched_shots:
        clip_path = shot.get("clip_path")
        asset_id = asset_id_map.get(clip_path, "r2")
        dur_frames = shot.get("timeline_duration", 50)
        start_frame = shot.get("source_start_frame", 0)

        offset_str = f"{curr_frame * 100}/{int(fps * 100)}s"
        dur_str = f"{dur_frames * 100}/{int(fps * 100)}s"
        start_str = f"{start_frame * 100}/{int(fps * 100)}s"

        clip_elem = ET.SubElement(
            spine,
            "asset-clip",
            ref=asset_id,
            name=shot.get("clip_name", "Shot"),
            offset=offset_str,
            duration=dur_str,
            start=start_str,
        )

        # Markers for VFX suggestions
        vfx = shot.get("suggested_vfx")
        if vfx and vfx != "none":
            ET.SubElement(
                clip_elem,
                "marker",
                start=offset_str,
                duration="1/25s",
                value=f"VFX: {vfx}",
                note=f"ActionCam AI suggested effect: {vfx}",
            )

        curr_frame += dur_frames

    # Pretty format XML
    rough_string = ET.tostring(root, "utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    out_file = Path(output_xml_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    return str(out_file.resolve())

