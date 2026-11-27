"""
Comprehensive Unit & API Test Suite for ActionCam MCP Studio.
Covers ResolveClient helpers, ExportManager classification, AudioEngine,
MCP JSON-RPC 2.0 server, and Desktop HTTP API endpoints.
"""

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core.resolve_client import ResolveClient
from actioncam_mcp.core.export_manager import ExportManager
from actioncam_mcp.core.audio_engine import AudioEngine
from actioncam_mcp.core.sound_notifier import SoundNotifier
from actioncam_mcp.server.mcp_server import ActionCamMCPServer
from actioncam_mcp.server.http_api import DesktopAPIHandler


class TestActionCamCore(unittest.TestCase):
    def test_normalize_lut_path(self):
        abs_win = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\DJI\DJI OSMO Action 4 D-Log M to Rec.709 V1.cube"
        self.assertEqual(
            ResolveClient.normalize_lut_path(abs_win),
            "DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube",
        )
        rel = "DJI/DJI OSMO Action 4 Nature Pro.cube"
        self.assertEqual(ResolveClient.normalize_lut_path(rel), rel)

    def test_export_classification(self):
        self.assertEqual(ExportManager.classify_export_folder(profile_key="youtube_4k"), "YouTube")
        self.assertEqual(ExportManager.classify_export_folder(profile_key="youtube_1080p"), "YouTube")
        self.assertEqual(ExportManager.classify_export_folder(profile_key="reels_shorts_9_16"), "Reels_Shorts")
        self.assertEqual(ExportManager.classify_export_folder(profile_key="master_dnxhr"), "Master")
        self.assertEqual(ExportManager.classify_export_folder(profile_key="web_1080p_fast"), "Web_Preview")
        self.assertEqual(ExportManager.classify_export_folder(filename="Illumen_Dev_Journey.mp4"), "YouTube")

        with tempfile.TemporaryDirectory() as tmp:
            yt_dir = ExportManager.classify_export_dir(tmp, profile_key="youtube_1080p")
            self.assertTrue(yt_dir.exists())
            self.assertEqual(yt_dir.name, "YouTube")

    def test_audio_engine_scan_and_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            for fname in (
                "wild-ambience.wav",
                "fast-whoosh.wav",
                "impact-hit.wav",
                "retro-notification.wav",
                "suspense-waiting-bgm.wav",
            ):
                (Path(tmp) / fname).write_bytes(b"\x00" * 64)

            engine = AudioEngine(sfx_library_dir=tmp)
            cats = engine.scan_sounds_library()
            self.assertEqual(len(cats["all"]), 5)
            self.assertEqual(len(cats["ambience"]), 1)
            self.assertEqual(len(cats["whoosh"]), 1)
            self.assertEqual(len(cats["impact"]), 1)
            self.assertEqual(len(cats["chime"]), 1)
            self.assertEqual(len(cats["bgm"]), 1)

            plan = engine.plan_sound_design(
                [{"audio_cue": "impact", "record_frame": 100}, {"audio_cue": "whoosh", "record_frame": 200}],
                bgm_path=cats["bgm"][0],
                available_sfx_files=cats["all"],
            )
            self.assertIsNotNone(plan["bgm"])
            self.assertEqual(len(plan["sfx_cues"]), 2)


class TestMCPAndHTTPAPI(unittest.TestCase):
    def test_mcp_server_handshake_session_and_sounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["ACTIONCAM_ENABLE_SOUNDS"] = "0"
            srv = ActionCamMCPServer()
            srv.session_mgr.memory_file = Path(tmp) / "mem.json"

            init_resp = srv.process_request({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test-llm", "version": "1.0"}},
            })
            self.assertIn("sessionId", init_resp["result"]["serverInfo"])
            self.assertFalse(srv.session_mgr.initialized)

            notif = srv.process_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
            self.assertIsNone(notif)
            self.assertTrue(srv.session_mgr.initialized)

            mem_res = srv.handle_call_tool("actioncam_memory_update", {"key": "active_timeline", "value": "Journey_Edit"})
            self.assertEqual(mem_res["memory"]["active_timeline"], "Journey_Edit")

            notifier = SoundNotifier(enabled=False)
            for ev in ("export_done", "task_done", "error", "tool_step"):
                self.assertIsNotNone(notifier.get_sound_path(ev), f"Missing sound asset for {ev}")

    def test_mcp_server_tools_and_status(self):
        srv = ActionCamMCPServer()
        names = [t["name"] for t in srv.tools]
        self.assertIn("actioncam_check_status", names)
        self.assertIn("actioncam_assemble_timeline", names)
        self.assertIn("actioncam_queue_export", names)
        res = srv.handle_call_tool("actioncam_check_status", {})
        self.assertIn("connected", res)

    def test_http_api_and_ui_pages(self):
        ui_dir = str(ROOT / "actioncam_mcp" / "desktop_ui")

        class _TestServer(ThreadingHTTPServer):
            def __init__(self, *args, **kwargs):
                self.resolve_client = ResolveClient()
                self.decoder = None
                self.export_mgr = ExportManager(self.resolve_client)
                super().__init__(*args, **kwargs)

        httpd = _TestServer(("127.0.0.1", 0), partial(DesktopAPIHandler, directory=ui_dir))
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(f"http://127.0.0.1:{port}/api/status", timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertIn("connected", data)

            with opener.open(f"http://127.0.0.1:{port}/api/presets", timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                presets = json.loads(resp.read().decode("utf-8"))
                self.assertIn("youtube_1080p", presets["export_profiles"])

            for page in ("/index.html", "/guide.html", "/docs/assets/davinci-resolve-edit-page.jpg"):
                with opener.open(f"http://127.0.0.1:{port}{page}", timeout=5) as resp:
                    self.assertEqual(resp.status, 200)
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
