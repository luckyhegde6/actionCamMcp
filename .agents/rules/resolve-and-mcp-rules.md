# Resolve & MCP Agent Rules & Guardrails

## Guardrails (Mandatory)
1. **No Hardcoded Local Paths or PII**: Never commit drive-specific paths (`F:\Edits\...`, `C:\Users\...`), API keys, or personal identifiers. Always use relative paths or environment variables (`ACTIONCAM_SOUNDS_DIR`, `ACTIONCAM_PROJECTS_DIR`).
2. **Clear Both Video & Audio Tracks**: Always call `ResolveClient.clear_timeline_tracks(tl)` before rebuilding a timeline so orphan audio clips cannot push new video downstream.
3. **Relative LUT Paths**: `TimelineItem.SetLUT()` requires paths relative to Resolve's `Support/LUT/` directory (use `ResolveClient.normalize_lut_path()`).
4. **Speed Warp Integer Enums**: Use `RetimeProcess=3` (Optical Flow) and `MotionEstimation=4` (Speed Warp).
5. **Hardware Guardrails (4GB VRAM)**: Edit in `1920x1080` and avoid heavy 3D Fusion particle trees during unattended runs.
6. **Verify Before Reporting**: Run `python tests/test_suite.py` and `python tests/test_workflow.py` after every code change.
