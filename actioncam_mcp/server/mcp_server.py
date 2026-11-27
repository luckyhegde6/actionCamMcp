"""
ActionCam MCP Server (Model Context Protocol).
Implements standard JSON-RPC 2.0 over STDIO to expose DaVinci Resolve Studio
video editing, scene detection, clip matching, and export automation to AI agents.
"""

import sys
import json
import logging
import traceback
from typing import Dict, Any, List

from ..core import (
    ResolveClient,
    MediaOrganizer,
    ReferenceDecoder,
    CutMatcher,
    AudioEngine,
    ExportManager,
    generate_fcpxml,
)
from ..core.sound_notifier import SoundNotifier
from ..config import CAMERA_PRESETS, EXPORT_PROFILES
from .session_manager import SessionManager

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="[ActionCam MCP] %(levelname)s: %(message)s")
logger = logging.getLogger("actioncam_mcp.server")

class ActionCamMCPServer:
    """Model Context Protocol server for ActionCam video production."""

    def __init__(self):
        self.resolve_client = ResolveClient()
        self.decoder = ReferenceDecoder(self.resolve_client)
        self.export_mgr = ExportManager(self.resolve_client)
        self.session_mgr = SessionManager()
        self.notifier = SoundNotifier()
        self.tools = self._register_tools()

    def _register_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "actioncam_check_status",
                "description": "Check whether DaVinci Resolve Studio is running and connected via its Scripting API, along with active project info.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "actioncam_session_status",
                "description": "Return current MCP session ID, handshake state, and persistent LLM memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "actioncam_memory_update",
                "description": "Persist key/value context (active_project, active_timeline, or custom notes) into session memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Memory key to update"},
                        "value": {"type": "string", "description": "Value to store"},
                    },
                    "required": ["key", "value"],
                },
            },
            {
                "name": "actioncam_scan_and_organize",
                "description": "Scans chosen camera directories (e.g. DJI Action 4 SD card or local folders), categorizes clips into Realtime vs Slow-Mo (60/120fps), and creates organized project folders.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_dir": {"type": "string", "description": "Path to folder containing raw camera clips"},
                        "project_dir": {"type": "string", "description": "Target project folder where files will be structured"},
                        "mode": {"type": "string", "enum": ["copy", "move", "symlink"], "default": "copy"},
                    },
                    "required": ["source_dir", "project_dir"],
                },
            },
            {
                "name": "actioncam_decode_reference_video",
                "description": "Decodes an edit from a reference video. Uses DaVinci Resolve Neural Engine DetectSceneCuts() to find every shot duration, pacing, and cut transition rhythm.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "reference_path": {"type": "string", "description": "Absolute path to reference video file (MP4/MOV)"},
                        "fps": {"type": "number", "default": 25.0, "description": "Target timeline frame rate"},
                    },
                    "required": ["reference_path"],
                },
            },
            {
                "name": "actioncam_assemble_timeline",
                "description": "Matches raw clips from chosen folders to the decoded reference cuts and assembles a ready-to-edit timeline in DaVinci Resolve Studio (with LUTs, trimming, and slow-mo retiming).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "timeline_name": {"type": "string", "description": "Name for the new timeline in DaVinci Resolve"},
                        "reference_path": {"type": "string", "description": "Path to the reference video file"},
                        "source_dir": {"type": "string", "description": "Directory containing source clips to match into the edit"},
                        "camera_preset": {"type": "string", "enum": list(CAMERA_PRESETS.keys()), "default": "dji_action4_dlog_m"},
                        "custom_lut_path": {"type": "string", "description": "Optional path to custom .cube LUT file"},
                        "bgm_path": {"type": "string", "description": "Optional background music audio file path"},
                        "export_fcpxml": {"type": "boolean", "default": True, "description": "Also write an FCPXML 1.9 file to disk"},
                    },
                    "required": ["timeline_name", "reference_path", "source_dir"],
                },
            },
            {
                "name": "actioncam_queue_export",
                "description": "Configures Deliver page render settings and queues/starts rendering in DaVinci Resolve (YouTube 4K, 9:16 Reels/Shorts, Master ProRes/DNxHR, Web 1080p).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "output_dir": {"type": "string", "description": "Directory where exported video will be saved"},
                        "filename_prefix": {"type": "string", "description": "Base filename for exported video (without extension)"},
                        "profile": {"type": "string", "enum": list(EXPORT_PROFILES.keys()), "default": "youtube_4k"},
                        "start_render_now": {"type": "boolean", "default": False, "description": "Immediately trigger rendering or just queue it"},
                    },
                    "required": ["output_dir", "filename_prefix"],
                },
            },
            {
                "name": "actioncam_apply_studio_effects",
                "description": "Applies DaVinci Resolve Studio Neural Engine features to timeline clips: Super Scale (2x/3x/4x), Speed Warp motion retiming, 3D Depth Map, or Track Locking.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "effect_type": {
                            "type": "string",
                            "enum": ["super_scale", "speed_warp", "depth_map", "lock_track"],
                            "description": "Studio Neural feature to apply"
                        },
                        "track_index": {"type": "integer", "default": 1, "description": "Target track index"},
                        "clip_index": {"type": "integer", "default": 1, "description": "Clip index on track (1-based)"},
                        "super_scale_multiplier": {"type": "integer", "enum": [2, 3, 4], "default": 2},
                        "lock_track": {"type": "boolean", "default": True}
                    },
                    "required": ["effect_type"]
                }
            },
            {
                "name": "actioncam_run_full_workflow",
                "description": "Executes the entire end-to-end video workflow: organizes raw clips, decodes reference edit, matches cuts, builds DaVinci Resolve timeline, adds sound cues, applies LUT, and queues export.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "DaVinci Resolve project name"},
                        "project_dir": {"type": "string", "description": "Local workspace folder for the project"},
                        "source_dir": {"type": "string", "description": "Folder with raw camera clips"},
                        "reference_path": {"type": "string", "description": "Reference video to decode"},
                        "bgm_path": {"type": "string", "description": "Optional background music file"},
                        "camera_preset": {"type": "string", "default": "dji_action4_dlog_m"},
                        "export_profile": {"type": "string", "default": "youtube_4k"},
                    },
                    "required": ["project_name", "project_dir", "source_dir", "reference_path"],
                },
            },
        ]

    def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches tool execution."""
        try:
            if tool_name == "actioncam_check_status":
                connected = self.resolve_client.is_connected()
                proj = self.resolve_client.get_current_project()
                version = self.resolve_client.get_version()
                return {
                    "connected": connected,
                    "resolve_version": version,
                    "active_project": proj.GetName() if proj else None,
                    "message": "Connected to DaVinci Resolve Studio" if connected else "DaVinci Resolve Studio is not running or external scripting is disabled",
                }

            elif tool_name == "actioncam_scan_and_organize":
                source_dir = arguments["source_dir"]
                proj_dir = arguments["project_dir"]
                mode = arguments.get("mode", "copy")

                organizer = MediaOrganizer(proj_dir)
                assets = organizer.scan_directory(source_dir)
                organized = organizer.organize_assets(assets, mode=mode)
                return {
                    "total_scanned": len(assets),
                    "organized_summary": {k: len(v) for k, v in organized.items()},
                    "project_dir": proj_dir,
                }

            elif tool_name == "actioncam_decode_reference_video":
                ref_path = arguments["reference_path"]
                fps = arguments.get("fps", 25.0)
                blueprint = self.decoder.decode_reference(ref_path, target_fps=fps)
                return blueprint.to_dict()

            elif tool_name == "actioncam_assemble_timeline":
                tl_name = arguments["timeline_name"]
                ref_path = arguments["reference_path"]
                source_dir = arguments["source_dir"]
                cam_preset = arguments.get("camera_preset", "dji_action4_dlog_m")
                lut_path = arguments.get("custom_lut_path")
                bgm_path = arguments.get("bgm_path")
                do_fcpxml = arguments.get("export_fcpxml", True)

                # 1. Decode reference
                blueprint = self.decoder.decode_reference(ref_path)

                # 2. Scan source clips
                organizer = MediaOrganizer(source_dir)
                clips = organizer.scan_directory(source_dir)
                video_clips = [c for c in clips if c["type"] == "video"]

                if not video_clips:
                    raise ValueError(f"No video clips found in source directory: {source_dir}")

                # 3. Match cuts
                matcher = CutMatcher(camera_preset_key=cam_preset, custom_lut_path=lut_path)
                matched_shots = matcher.match_clips_to_blueprint(blueprint, video_clips)

                # 4. Plan Audio
                audio_engine = AudioEngine()
                audio_plan = audio_engine.plan_sound_design(matched_shots, bgm_path=bgm_path)

                result: Dict[str, Any] = {
                    "timeline_name": tl_name,
                    "shot_count": len(matched_shots),
                    "total_duration_sec": blueprint.total_duration_sec,
                    "resolve_timeline_created": False,
                    "fcpxml_path": None,
                }

                # 5. Assemble in Resolve if connected
                if self.resolve_client.is_connected():
                    try:
                        self.resolve_client.create_bin_structure()
                        # Import source media
                        clip_paths = list(set(s["clip_path"] for s in matched_shots))
                        self.resolve_client.import_media(clip_paths, "01 Raw Footage/Realtime")

                        # Assemble
                        timeline = self.resolve_client.assemble_matched_timeline(
                            timeline_name=tl_name,
                            shot_mappings=matched_shots,
                            bgm_path=bgm_path,
                            sfx_entries=audio_plan.get("sfx_cues"),
                        )
                        result["resolve_timeline_created"] = bool(timeline)
                    except Exception as e:
                        logger.warning(f"Live Resolve assembly failed: {e}")

                # 6. Generate FCPXML
                if do_fcpxml:
                    xml_path = f"{source_dir}/{tl_name}.fcpxml"
                    generated = generate_fcpxml(tl_name, matched_shots, xml_path, fps=blueprint.fps, bgm_path=bgm_path)
                    result["fcpxml_path"] = generated

                return result

            elif tool_name == "actioncam_apply_studio_effects":
                effect_type = arguments["effect_type"]
                track_idx = arguments.get("track_index", 1)
                clip_idx = arguments.get("clip_index", 1)

                if not self.resolve_client.is_connected():
                    return {"success": False, "message": "DaVinci Resolve Studio is not connected."}

                proj = self.resolve_client.get_current_project()
                if not proj:
                    return {"success": False, "message": "No active project in Resolve."}

                tl = proj.GetCurrentTimeline()
                if not tl:
                    return {"success": False, "message": "No active timeline in Resolve."}

                if effect_type == "lock_track":
                    locked = arguments.get("lock_track", True)
                    ok = self.resolve_client.set_track_locking(tl, "video", track_idx, locked)
                    return {"success": ok, "message": f"Track Video {track_idx} locked: {locked}"}

                items = tl.GetItemListInTrack("video", track_idx) or []
                if clip_idx > len(items) or clip_idx < 1:
                    return {"success": False, "message": f"Clip index {clip_idx} out of range (track has {len(items)} clips)."}

                target_item = items[clip_idx - 1]
                if effect_type == "super_scale":
                    mult = arguments.get("super_scale_multiplier", 2)
                    ok = self.resolve_client.apply_studio_super_scale(target_item, multiplier=mult)
                    return {"success": ok, "message": f"Applied Neural Super Scale {mult}x to clip #{clip_idx}"}
                elif effect_type == "speed_warp":
                    ok = self.resolve_client.apply_studio_speed_warp(target_item)
                    return {"success": ok, "message": f"Applied Neural Speed Warp retiming to clip #{clip_idx}"}
                elif effect_type == "depth_map":
                    ok = self.resolve_client.apply_studio_depth_map(target_item)
                    return {"success": ok, "message": f"Added 3D Depth Map ResolveFX node to clip #{clip_idx}"}
                else:
                    return {"success": False, "message": f"Unknown effect type: {effect_type}"}

            elif tool_name == "actioncam_queue_export":
                out_dir = arguments["output_dir"]
                prefix = arguments["filename_prefix"]
                profile = arguments.get("profile", "youtube_4k")
                start_now = arguments.get("start_render_now", False)

                render_info = self.export_mgr.queue_render(out_dir, prefix, profile_key=profile)
                if start_now and render_info.get("job_id") and self.resolve_client.is_connected():
                    self.resolve_client.start_rendering([render_info["job_id"]])
                    render_info["status"] = "Rendering Started"

                return render_info

            elif tool_name == "actioncam_run_full_workflow":
                p_name = arguments["project_name"]
                p_dir = arguments["project_dir"]
                s_dir = arguments["source_dir"]
                ref_path = arguments["reference_path"]
                bgm_path = arguments.get("bgm_path")
                cam_preset = arguments.get("camera_preset", "dji_action4_dlog_m")
                export_profile = arguments.get("export_profile", "youtube_4k")

                # Step A: Organize
                org = MediaOrganizer(p_dir)
                assets = org.scan_directory(s_dir)
                organized = org.organize_assets(assets, mode="copy")

                # Step B: Project in Resolve
                if self.resolve_client.is_connected():
                    self.resolve_client.create_project(p_name)
                    self.resolve_client.create_bin_structure()

                # Step C: Decode reference
                blueprint = self.decoder.decode_reference(ref_path)

                # Step D: Match cuts
                video_clips = [c for c in assets if c["type"] == "video"]
                matcher = CutMatcher(camera_preset_key=cam_preset)
                matched_shots = matcher.match_clips_to_blueprint(blueprint, video_clips)

                # Step E: Assemble
                audio_plan = AudioEngine().plan_sound_design(matched_shots, bgm_path=bgm_path)
                xml_out = f"{p_dir}/{p_name}.fcpxml"
                fcpxml_path = generate_fcpxml(p_name, matched_shots, xml_out, fps=blueprint.fps, bgm_path=bgm_path)

                resolve_success = False
                if self.resolve_client.is_connected():
                    try:
                        self.resolve_client.assemble_matched_timeline(
                            timeline_name=f"{p_name}_Main",
                            shot_mappings=matched_shots,
                            bgm_path=bgm_path,
                            sfx_entries=audio_plan.get("sfx_cues"),
                        )
                        resolve_success = True
                    except Exception as e:
                        logger.error(f"Live Resolve assembly error: {e}")

                # Step F: Queue export
                export_res = self.export_mgr.queue_render(
                    output_dir=f"{p_dir}/05_Exports",
                    filename_prefix=f"{p_name}_Final",
                    profile_key=export_profile,
                )

                return {
                    "project_name": p_name,
                    "shots_assembled": len(matched_shots),
                    "duration_sec": blueprint.total_duration_sec,
                    "resolve_connected": self.resolve_client.is_connected(),
                    "resolve_timeline_assembled": resolve_success,
                    "fcpxml_path": fcpxml_path,
                    "export_status": export_res,
                }

            elif tool_name == "actioncam_session_status":
                return self.session_mgr.get_status()

            elif tool_name == "actioncam_memory_update":
                return self.session_mgr.update_memory(arguments["key"], arguments["value"])

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}\n{traceback.format_exc()}")
            self.session_mgr.record_tool_call(tool_name, status="error", summary=str(e))
            self.notifier.notify("error")
            return {"error": str(e), "traceback": traceback.format_exc()}

    def process_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes a single JSON-RPC 2.0 request (testable without stdio)."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            hs = self.session_mgr.begin_handshake(params)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": hs["protocol_version"],
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": "actioncam-mcp-server",
                        "version": "1.1.0",
                        "sessionId": hs["session_id"],
                    },
                },
            }
        if method == "notifications/initialized":
            self.session_mgr.complete_handshake()
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.tools}}
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            self.notifier.notify("tool_step")
            tool_res = self.handle_call_tool(tool_name, arguments)
            if "error" not in tool_res:
                self.session_mgr.record_tool_call(tool_name, status="ok")
                if tool_name == "actioncam_queue_export":
                    self.notifier.notify("export_done")
                elif tool_name == "actioncam_run_full_workflow":
                    self.notifier.notify("task_done")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(tool_res, indent=2)}]},
            }
        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method {method} not found"},
        }

    def run_stdio(self):
        """Standard JSON-RPC 2.0 loop over stdin and stdout."""
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                response = self.process_request(request)
                if response is None:
                    continue
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    server = ActionCamMCPServer()
    server.run_stdio()

