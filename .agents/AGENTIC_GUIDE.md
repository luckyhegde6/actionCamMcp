# ActionCam MCP — Agentic Guide (LLM & MCP-Agent Playbook)

This guide defines how LLM clients (Claude Desktop, Antigravity, Cursor, Codex) interact with **ActionCam MCP Studio** safely, deterministically, and with persistent session memory.

---

## 1. MCP Handshake & Session Lifecycle

Every MCP client **must** perform the standard JSON-RPC 2.0 handshake before dispatching editing tools:

1. **`initialize`**: Client sends `protocolVersion` and `clientInfo`. `SessionManager.begin_handshake()` generates a `sessionId` and returns server capabilities.
2. **`notifications/initialized`**: Client confirms readiness; `SessionManager.complete_handshake()` marks `initialized: true`.
3. **Session & Memory Tools**:
   - `actioncam_session_status`: Inspect `session_id`, `initialized` state, `active_project`, `active_timeline`, and `recent_tools`.
   - `actioncam_memory_update`: Persist `active_project`, `active_timeline`, or custom `notes` across turns in `.agents/memory/session_memory.json`.

---

## 2. Sound Feedback Hooks (`actioncam_mcp/assets/sounds/`)

`SoundNotifier` (`actioncam_mcp/core/sound_notifier.py`) and `.agents/hooks/sound_hook.py` play non-blocking audio cues:
- `tool_step.ogg` — Intermediate MCP tool invocation
- `task_done.ogg` — Full workflow completion
- `export_done.ogg` — Deliver render queue completion
- `error.ogg` — Tool or Resolve scripting error

Disable sounds in headless CI by setting `ACTIONCAM_ENABLE_SOUNDS=0`.

---

## 3. Directory Layout

```text
.agents/
├── AGENTIC_GUIDE.md
├── TODO.md
├── rules/
│   └── resolve-and-mcp-rules.md
├── commands/
│   ├── assemble-timeline.md
│   ├── export-youtube.md
│   └── verify-ui.md
├── hooks/
│   ├── hooks.json
│   └── sound_hook.py
└── memory/
    └── session_memory.json   (runtime, gitignored)
```
