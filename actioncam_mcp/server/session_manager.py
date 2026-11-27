"""
Session & Memory Manager for ActionCam MCP Server.
Handles proper MCP initialize -> notifications/initialized handshake state
and persists cross-turn LLM memory in .agents/memory/session_memory.json.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MEMORY_FILE = REPO_ROOT / ".agents" / "memory" / "session_memory.json"


class SessionManager:
    """Manages MCP handshake state, active session metadata, and persistent LLM memory."""

    def __init__(self, memory_file: Optional[Path] = None):
        self.memory_file = Path(memory_file) if memory_file else DEFAULT_MEMORY_FILE
        self.session_id: str = str(uuid.uuid4())
        self.handshake_started: bool = False
        self.initialized: bool = False
        self.protocol_version: str = "2024-11-05"
        self.client_info: Dict[str, Any] = {}
        self.state: Dict[str, Any] = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if self.memory_file.exists():
            try:
                return json.loads(self.memory_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "active_project": None,
            "active_timeline": None,
            "notes": {},
            "recent_tools": [],
        }

    def save_memory(self) -> None:
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def begin_handshake(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self.session_id = str(uuid.uuid4())
        self.handshake_started = True
        self.initialized = False
        self.protocol_version = params.get("protocolVersion", "2024-11-05")
        self.client_info = params.get("clientInfo", {})
        self.state["last_session_id"] = self.session_id
        self.state["last_handshake_at"] = datetime.now(timezone.utc).isoformat()
        self.save_memory()
        return {
            "session_id": self.session_id,
            "protocol_version": self.protocol_version,
            "client_info": self.client_info,
        }

    def complete_handshake(self) -> None:
        if self.handshake_started:
            self.initialized = True
            self.state["initialized"] = True
            self.save_memory()

    def record_tool_call(self, tool_name: str, status: str = "ok", summary: Optional[str] = None) -> None:
        history: List[Dict[str, Any]] = self.state.setdefault("recent_tools", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "tool": tool_name,
            "status": status,
            "summary": summary,
        })
        self.state["recent_tools"] = history[-20:]
        self.save_memory()

    def update_memory(self, key: str, value: Any) -> Dict[str, Any]:
        if key in ("active_project", "active_timeline"):
            self.state[key] = value
        else:
            self.state.setdefault("notes", {})[key] = value
        self.save_memory()
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "handshake_started": self.handshake_started,
            "initialized": self.initialized,
            "protocol_version": self.protocol_version,
            "client_info": self.client_info,
            "memory": self.state,
        }
