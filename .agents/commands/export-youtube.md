# Command: /export-youtube

1. Resolve target directory via `ExportManager.classify_export_dir("./exports", profile_key="youtube_1080p")` -> `./exports/YouTube/`.
2. Save project (`ResolveClient.save_project()`).
3. Load `YouTube - 1080p` Deliver preset and call `ResolveClient.render_timeline(..., wait=True)`.
4. Trigger `export_done` sound hook on completion or `error` sound hook on failure.
