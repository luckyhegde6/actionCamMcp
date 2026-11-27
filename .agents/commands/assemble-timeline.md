# Command: /assemble-timeline

1. Run `actioncam_check_status` to confirm DaVinci Resolve Studio 21 is connected.
2. Call `actioncam_memory_update` with `active_project` and `active_timeline`.
3. Clear all video and audio tracks (`ResolveClient.clear_timeline_tracks()`).
4. Append curated clips using source-clip FPS frame ranges.
5. Apply normalized D-Log M LUT + CDL color grade + Speed Warp on 100fps segments.
6. Mix audio from `$ACTIONCAM_SOUNDS_DIR` (or `actioncam_mcp/assets/sounds`).
