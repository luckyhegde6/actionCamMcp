"""
Lightweight REST & Static Web Server for the Desktop UI.
Uses standard library ThreadingHTTPServer for zero-dependency reliability.
"""

import os
import sys
import json
import logging
import subprocess
import mimetypes
import functools
from pathlib import Path
from typing import Any, Optional
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from ..core import (
    ResolveClient,
    MediaOrganizer,
    ReferenceDecoder,
    CutMatcher,
    AudioEngine,
    ExportManager,
    generate_fcpxml,
)
from ..core.youtube_publisher import YouTubePublisher
from ..config import CAMERA_PRESETS, EXPORT_PROFILES, RESOLVE_EXE_DEFAULT

logger = logging.getLogger("actioncam_mcp.api")

class DesktopAPIHandler(SimpleHTTPRequestHandler):
    """Handles API requests and serves desktop UI assets."""
    protocol_version = "HTTP/1.1"

    @property
    def resolve_client(self):
        return self.server.resolve_client

    @property
    def decoder(self):
        return self.server.decoder

    @property
    def export_mgr(self):
        return self.server.export_mgr

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/status":
            connected = self.resolve_client.is_connected()
            proj = self.resolve_client.get_current_project()
            version = self.resolve_client.get_version()
            self._send_json({
                "connected": connected,
                "version": version,
                "project": proj.GetName() if proj else None,
                "resolve_exe_exists": os.path.exists(RESOLVE_EXE_DEFAULT),
            })

        elif parsed.path == "/api/presets":
            self._send_json({
                "camera_presets": CAMERA_PRESETS,
                "export_profiles": EXPORT_PROFILES,
            })

        elif parsed.path.startswith("/docs/assets/"):
            rel = parsed.path.lstrip("/")
            docs_file = (Path(__file__).resolve().parent.parent.parent / rel).resolve()
            assets_root = (Path(__file__).resolve().parent.parent.parent / "docs" / "assets").resolve()
            if docs_file.is_file() and str(docs_file).startswith(str(assets_root)):
                ctype, _ = mimetypes.guess_type(str(docs_file))
                data = docs_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", ctype or "application/octet-stream")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(data)
                self.close_connection = True
            else:
                self.send_error(404, "Asset not found")

        else:
            # Serve Desktop UI files
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        try:
            if parsed.path == "/api/launch-resolve":
                if os.path.exists(RESOLVE_EXE_DEFAULT):
                    subprocess.Popen([RESOLVE_EXE_DEFAULT])
                    self._send_json({"status": "Launching DaVinci Resolve Studio..."})
                else:
                    self._send_json({"error": f"DaVinci Resolve not found at {RESOLVE_EXE_DEFAULT}"}, 404)

            elif parsed.path == "/api/scan":
                source_dir = payload.get("source_dir", "")
                organizer = MediaOrganizer(source_dir)
                assets = organizer.scan_directory(source_dir)
                self._send_json({"assets": assets, "count": len(assets)})

            elif parsed.path == "/api/organize":
                source_dir = payload.get("source_dir", "")
                proj_dir = payload.get("project_dir", "")
                mode = payload.get("mode", "copy")

                organizer = MediaOrganizer(proj_dir)
                assets = organizer.scan_directory(source_dir)
                organized = organizer.organize_assets(assets, mode=mode)
                self._send_json({"organized": {k: len(v) for k, v in organized.items()}, "details": organized})

            elif parsed.path == "/api/decode-reference":
                ref_path = payload.get("reference_path", "")
                fps = float(payload.get("fps", 25.0))
                blueprint = self.decoder.decode_reference(ref_path, target_fps=fps)
                self._send_json(blueprint.to_dict())

            elif parsed.path == "/api/match-cuts":
                ref_path = payload.get("reference_path", "")
                source_dir = payload.get("source_dir", "")
                cam_preset = payload.get("camera_preset", "dji_action4_dlog_m")
                lut_path = payload.get("custom_lut_path")

                blueprint = self.decoder.decode_reference(ref_path)
                organizer = MediaOrganizer(source_dir)
                assets = organizer.scan_directory(source_dir)
                video_clips = [c for c in assets if c["type"] == "video"]

                matcher = CutMatcher(camera_preset_key=cam_preset, custom_lut_path=lut_path)
                matched_shots = matcher.match_clips_to_blueprint(blueprint, video_clips)
                self._send_json({"matched_shots": matched_shots, "blueprint": blueprint.to_dict()})

            elif parsed.path == "/api/assemble":
                tl_name = payload.get("timeline_name", "ActionCam_Edit")
                ref_path = payload.get("reference_path", "")
                source_dir = payload.get("source_dir", "")
                cam_preset = payload.get("camera_preset", "dji_action4_dlog_m")
                lut_path = payload.get("custom_lut_path")
                bgm_path = payload.get("bgm_path")

                # Match
                blueprint = self.decoder.decode_reference(ref_path)
                organizer = MediaOrganizer(source_dir)
                assets = organizer.scan_directory(source_dir)
                video_clips = [c for c in assets if c["type"] == "video"]

                matcher = CutMatcher(camera_preset_key=cam_preset, custom_lut_path=lut_path)
                matched_shots = matcher.match_clips_to_blueprint(blueprint, video_clips)

                audio_engine = AudioEngine()
                audio_plan = audio_engine.plan_sound_design(matched_shots, bgm_path=bgm_path)

                resolve_success = False
                if self.resolve_client.is_connected():
                    try:
                        self.resolve_client.create_bin_structure()
                        clip_paths = list(set(s["clip_path"] for s in matched_shots))
                        self.resolve_client.import_media(clip_paths, "01 Raw Footage/Realtime")

                        timeline = self.resolve_client.assemble_matched_timeline(
                            timeline_name=tl_name,
                            shot_mappings=matched_shots,
                            bgm_path=bgm_path,
                            sfx_entries=audio_plan.get("sfx_cues"),
                        )
                        resolve_success = bool(timeline)
                    except Exception as e:
                        logger.error(f"Live assembly error: {e}")

                xml_out = os.path.join(source_dir, f"{tl_name}.fcpxml")
                fcpxml_path = generate_fcpxml(tl_name, matched_shots, xml_out, fps=blueprint.fps, bgm_path=bgm_path)

                self._send_json({
                    "timeline_name": tl_name,
                    "shots_assembled": len(matched_shots),
                    "resolve_assembled": resolve_success,
                    "fcpxml_path": fcpxml_path,
                })

            elif parsed.path == "/api/export":
                out_dir = payload.get("output_dir", "")
                prefix = payload.get("filename_prefix", "ActionCam_Export")
                profile = payload.get("profile", "youtube_4k")
                start_now = payload.get("start_render_now", False)

                render_info = self.export_mgr.queue_render(out_dir, prefix, profile_key=profile)
                if start_now and render_info.get("job_id") and self.resolve_client.is_connected():
                    self.resolve_client.start_rendering([render_info["job_id"]])
                    render_info["status"] = "Rendering Started"

                self._send_json(render_info)

            elif parsed.path == "/api/youtube/prepare":
                pub = YouTubePublisher()
                meta = pub.generate_youtube_metadata(
                    title=payload.get("title", "Illumen dev Showcase"),
                    description=payload.get("description", ""),
                    tags=payload.get("tags"),
                    privacy_status=payload.get("privacy_status", "private"),
                )
                res = pub.upload_video_resumable(
                    video_path=payload.get("video_path", ""),
                    metadata=meta,
                    execute_upload=bool(payload.get("execute_upload", False)),
                )
                self._send_json(res)

            else:
                self._send_json({"error": f"Unknown endpoint: {parsed.path}"}, 404)

        except Exception as e:
            logger.error(f"API Error at {parsed.path}: {e}")
            self._send_json({"error": str(e)}, 500)


def start_server(host: str = "127.0.0.1", port: int = 8765, ui_dir: Optional[str] = None):
    """Launches the HTTP server."""
    if not ui_dir:
        ui_dir = str(Path(__file__).resolve().parent.parent / "desktop_ui")

    server_address = (host, port)
    
    class AppServer(ThreadingHTTPServer):
        def __init__(self, *args, **kwargs):
            self.resolve_client = ResolveClient()
            self.decoder = ReferenceDecoder(self.resolve_client)
            self.export_mgr = ExportManager(self.resolve_client)
            super().__init__(*args, **kwargs)

    handler_factory = functools.partial(DesktopAPIHandler, directory=ui_dir)
    httpd = AppServer(server_address, handler_factory)
    logger.info(f"ActionCam MCP Desktop Server running at http://{host}:{port}/")
    print(f"\n=======================================================")
    print(f"  ActionCam MCP Desktop Workflow Server")
    print(f"  URL: http://{host}:{port}/")
    print(f"  DaVinci Resolve Connection: Initializing...")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
