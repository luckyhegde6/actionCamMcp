---
name: davinci-resolve
description: "Professional automation, scripting, color science, and MCP integration for DaVinci Resolve Studio (19.x, 20.x, 21.x)."
tags: [video, davinci-resolve, blackmagic, editing, color-grading, fusion, fairlight, mcp, studio-automation]
author: "ActionCam MCP / MAS Video Lab"
version: "2.1.0"
---

# DaVinci Resolve Studio — AI Agent & Automation Skill

This skill playbook provides AI coding agents (Claude Code, Antigravity, Cursor, Codex, Gemini) with exact rules, API references, failure modes, and code recipes for programmatic control of **Blackmagic Design DaVinci Resolve Studio**.

---

## 1. System & Engine Architecture

### 1.1 Supported Versions & License Gating
- **DaVinci Resolve Studio (19.1+ / 21.x)**: Full external scripting enabled via Python 3.6 - 3.14+ 64-bit and Lua 5.1.
- **Critical License Gate**: External process scripting (`dvr.scriptapp("Resolve")` invoked from external CLI/MCP processes) requires **DaVinci Resolve Studio**. In the free version, external scripts return `None` (free edition only allows internal Console / Scripts menu execution).
- **Resolve 21.1+ Native MCP**: DaVinci Resolve Studio 21.1+ includes official native AI Assistant MCP integration (`File > Setup AI Assistants` running `resolve.mcp.exe` / `ResolveMCP`).

### 1.2 Environment Variables (Windows)
Always ensure the following paths are loaded before importing `DaVinciResolveScript`:
```powershell
$env:RESOLVE_SCRIPT_API = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
$env:RESOLVE_SCRIPT_LIB = "C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
$env:PYTHONPATH = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules;$env:PYTHONPATH"
```

In Python:
```python
import os, sys
os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
modules_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
```

---

## 2. When to Use & When NOT to Use

### ✅ When to Use:
1. **Automated Batch Ingest & Media Pool Organization**: Creating structured bin hierarchies, importing camera memory cards, tagging metadata.
2. **Programmatic Timeline Assembly & Rough Cutting**: Placing clips with precise frame-accurate `startFrame`, `endFrame`, and `recordFrame`.
3. **Reference Video Decoding & Scene Cut Detection**: Running Neural Engine `timeline.DetectSceneCuts()` to reverse-engineer viral reference edits.
4. **Color Grading & LUT Application**: Applying `.cube` LUTs and CDL grades to individual clip nodes or timeline node graphs.
5. **Render Queue Dispatch**: Configuring Deliver page presets (YouTube 4K, 9:16 Vertical Reels, Master DNxHR/ProRes) and polling render job statuses.

### ❌ When NOT to Use:
1. **Attempting external scripting on Free (non-Studio) Resolve**: Will fail silently (`scriptapp` returns `None`). Use FCPXML 1.9 file interchange instead.
2. **Heavy Fusion compositions or 3D particle trees on 4GB VRAM GPUs**: Causes GPU Out of Memory crashes. Use half-resolution timeline proxies.
3. **Assuming `StartRendering()` finishes immediately**: Rendering is an asynchronous background job; always poll `GetRenderJobStatus(jobId)` until `Complete`.

---

## 3. Mandatory Agent Directives

1. **Verify Connection First**: Call `client.is_connected()` before dispatching timeline commands. If offline, gracefully fall back to FCPXML 1.9 generation.
2. **Lock Frame Rates Early**: Resolve locks the project timeline frame rate once media has been added to the Media Pool. Set `timelineFrameRate` before importing clips!
3. **Color Space Alignment**: Always align timeline color science with the deliver codec. When applying LUTs (e.g. DJI D-Log M to Rec.709), ensure input gamma matches source.
4. **Hardware-Aware Memory Rules (4GB VRAM / GTX 1650)**:
   - Timeline resolution: Edit in **1920x1080 HD**.
   - Playback proxy: Set `Playback > Timeline Proxy Resolution > Half`.
   - Deliver page: Can safely render to **4K UHD (3840x2160)** without timeline re-cutting.

---

## 4. Failure Taxonomy & Safe Workarounds

| Failure Scenario | Root Cause | Safe Agent Action |
| :--- | :--- | :--- |
| `scriptapp("Resolve") returns None` | Resolve Studio not running or Preferences set to None | Check if process running; instruct user to set `Preferences > System > General > External scripting: Local`. |
| `Import error: No module named DaVinciResolveScript` | `PYTHONPATH` was overwritten or sandbox python path took precedence | Explicitly `sys.path.insert(0, modules_path)` pointing directly to `%PROGRAMDATA%.../Modules`. |
| Legal Range Clipping in H.264/H.265 | LUT placed after Rec.709 CST without tone mapping | Place camera normalization LUTs in Node 1 before secondary color curves. |
| Render queue hangs or times out | Drive space exhausted or codec license missing | Validate target path exists, check disk free space, poll `GetRenderJobStatus()`. |

