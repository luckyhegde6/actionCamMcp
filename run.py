"""
ActionCam MCP - Unified CLI and Application Entrypoint.

Usage:
  python run.py desktop        # Launches Desktop UI in native app window
  python run.py server         # Runs the local REST API server
  python run.py mcp            # Runs the stdio MCP server for AI agents
  python run.py status         # Tests connection to DaVinci Resolve Studio
  python run.py full [args]    # Runs headless end-to-end workflow
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from actioncam_mcp.core import ResolveClient, MediaOrganizer, ReferenceDecoder, CutMatcher, AudioEngine, ExportManager, generate_fcpxml
from actioncam_mcp.server.http_api import start_server
from actioncam_mcp.server.mcp_server import ActionCamMCPServer

def cmd_status():
    print("\n--- DaVinci Resolve Connection Status ---")
    client = ResolveClient()
    connected = client.is_connected()
    if connected:
        version = client.get_version()
        proj = client.get_current_project()
        proj_name = proj.GetName() if proj else "No project open"
        print(f"Status:   CONNECTED")
        print(f"Version:  DaVinci Resolve {version}")
        print(f"Project:  {proj_name}")
    else:
        print("Status:   NOT CONNECTED")
        print("Note:     Make sure DaVinci Resolve Studio is open, and:")
        print("          Preferences > System > General > External Scripting is set to 'Local'.")
    print("-----------------------------------------\n")

def cmd_mcp():
    server = ActionCamMCPServer()
    server.run_stdio()

def cmd_server(host, port):
    start_server(host=host, port=port)

def cmd_desktop():
    from actioncam_mcp.desktop_ui.launch_desktop import main as launch_main
    launch_main()

def cmd_full(args):
    print(f"\n[ActionCam Full Workflow] Project: {args.project}")
    client = ResolveClient()
    connected = client.is_connected()
    print(f"Resolve Studio: {'Connected' if connected else 'Offline (generating FCPXML fallback)'}")

    # 1. Scan and Organize
    org = MediaOrganizer(args.project_dir)
    print(f"Scanning source directory: {args.source_dir}...")
    assets = org.scan_directory(args.source_dir)
    organized = org.organize_assets(assets, mode="copy")
    print(f"Organized: {len(organized['realtime'])} realtime, {len(organized['slowmo'])} slow-mo clips.")

    # 2. Decode Reference
    decoder = ReferenceDecoder(client)
    print(f"Decoding reference: {args.ref}...")
    blueprint = decoder.decode_reference(args.ref, target_fps=args.fps)
    print(f"Decoded {len(blueprint.shots)} shots, total duration: {blueprint.total_duration_sec}s.")

    # 3. Match Clips
    matcher = CutMatcher(camera_preset_key=args.preset, custom_lut_path=args.lut)
    video_clips = [c for c in assets if c["type"] == "video"]
    if not video_clips:
        print("No video clips found in source directory.")
        return

    matched = matcher.match_clips_to_blueprint(blueprint, video_clips)
    print(f"Matched {len(matched)} cuts.")

    # 4. Assemble
    xml_path = f"{args.project_dir}/{args.project}.fcpxml"
    fcpxml_out = generate_fcpxml(args.project, matched, xml_path, fps=args.fps, bgm_path=args.bgm)
    print(f"Generated FCPXML: {fcpxml_out}")

    if connected:
        try:
            client.create_project(args.project)
            client.create_bin_structure()
            timeline = client.assemble_matched_timeline(f"{args.project}_Main", matched, bgm_path=args.bgm)
            print("Successfully assembled live timeline in DaVinci Resolve Studio!")
        except Exception as e:
            print(f"Live Resolve assembly error: {e}")

    print("\nWorkflow Complete!\n")

def main():
    parser = argparse.ArgumentParser(description="ActionCam MCP - AI Video Production Workflow")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("desktop", help="Launch the Desktop UI app window")
    subparsers.add_parser("ui", help="Alias for desktop")
    subparsers.add_parser("mcp", help="Run the stdio MCP server for AI agents")
    subparsers.add_parser("status", help="Check DaVinci Resolve Studio connection")

    server_parser = subparsers.add_parser("server", help="Run local REST API server")
    server_parser.add_argument("--host", default="127.0.0.1")
    server_parser.add_argument("--port", type=int, default=8765)

    full_parser = subparsers.add_parser("full", help="Run full automated pipeline")
    full_parser.add_argument("--project", default="Action4_Edit_01")
    full_parser.add_argument("--project-dir", default="F:/Edits/actionCamMcp/projects/Action4_Edit_01")
    full_parser.add_argument("--source-dir", required=True)
    full_parser.add_argument("--ref", required=True)
    full_parser.add_argument("--bgm", default=None)
    full_parser.add_argument("--preset", default="dji_action4_dlog_m")
    full_parser.add_argument("--lut", default=None)
    full_parser.add_argument("--fps", type=float, default=25.0)

    args = parser.parse_args()

    if args.command in ("desktop", "ui"):
        cmd_desktop()
    elif args.command == "mcp":
        cmd_mcp()
    elif args.command == "server":
        cmd_server(args.host, args.port)
    elif args.command == "status":
        cmd_status()
    elif args.command == "full":
        cmd_full(args)
    else:
        # Default action: run status check and show help
        cmd_status()
        parser.print_help()

if __name__ == "__main__":
    main()

