"""Optional, privacy-minimized coding-agent lifecycle adapters."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from curiosity.contracts.models import HarnessEvent, JobStatus, ProvenanceClass, deterministic_id

SUPPORTED = {"session_start", "working", "idle", "turn_complete", "session_end"}


def normalize(adapter: str, event_type: str, *, at: datetime | None = None) -> HarnessEvent | None:
    required_capability = {
        "session_start": "start",
        "working": "busy",
        "idle": "idle",
        "turn_complete": "complete",
        "session_end": "complete",
    }.get(event_type)
    if (
        adapter not in CAPABILITIES
        or event_type not in SUPPORTED
        or not CAPABILITIES[adapter].get(required_capability or "", False)
    ):
        return None
    moment = (at or datetime.now(UTC)).astimezone(UTC)
    return HarnessEvent(
        id=deterministic_id("event", adapter, event_type, moment.isoformat()),
        job_status=JobStatus.RUNNING if event_type == "working" else JobStatus.SUCCEEDED,
        event_type=event_type,
        occurred_at=moment,
        details={"adapter": adapter},
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )


CAPABILITIES = {
    "manual": {"start": False, "busy": False, "idle": False, "complete": False},
    "claude": {"start": False, "busy": False, "idle": False, "complete": True},
    "opencode": {"start": True, "busy": True, "idle": True, "complete": True},
    "codex_notify": {"start": False, "busy": False, "idle": False, "complete": True},
}


def claude_event(payload: dict[str, Any]) -> HarnessEvent | None:
    """Map documented Stop hook input, retaining no input field values."""
    return normalize("claude", "turn_complete") if payload.get("hook_event_name") == "Stop" else None


def opencode_event(payload: dict[str, Any]) -> HarnessEvent | None:
    kind = payload.get("type")
    if kind == "session.created":
        return normalize("opencode", "session_start")
    if kind == "session.idle":
        return normalize("opencode", "idle")
    if kind == "session.error":
        # A session error is a terminal/quiet transition; it is never guessed
        # as busy or as successful completion.
        return normalize("opencode", "session_end")
    if kind == "session.status":
        status = payload.get("properties", {}).get("status")
        if status in {"busy", "idle"}:
            return normalize("opencode", "working" if status == "busy" else "idle")
    return None


def codex_event(payload: dict[str, Any]) -> HarnessEvent | None:
    """Map the current Codex 'notify' completion payload only.

    Codex spawns the configured command after each completed turn with a JSON
    payload whose type is ``agent-turn-complete``; it exposes no busy/idle
    signal, so only the completion is mapped. Any prompt/input fields in the
    payload are never read.
    """
    if payload.get("type") != "agent-turn-complete":
        return None
    return normalize("codex_notify", "turn_complete")


def codex_notification() -> HarnessEvent:
    """Codex completion notification has no implied busy/idle state."""
    event = codex_event({"type": "agent-turn-complete"})
    assert event is not None
    return event


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return parsed


def install_claude(settings_path: Path, *, command: str = "curiosity harness emit claude turn_complete") -> None:
    """Add one owned Stop hook; never replace user hook groups or settings."""
    settings = _read_json(settings_path)
    if settings.get("disableAllHooks") is True:
        raise ValueError("Claude hooks are disabled by disableAllHooks")
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("existing Claude hooks configuration is not an object")
    owned = {"matcher": "", "hooks": [{"type": "command", "command": command}]}
    stop = hooks.setdefault("Stop", [])
    if not isinstance(stop, list):
        raise ValueError("existing Claude Stop hooks configuration is not a list")
    if owned not in stop:
        stop.append(owned)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def uninstall_claude(settings_path: Path, *, command: str = "curiosity harness emit claude turn_complete") -> bool:
    settings = _read_json(settings_path)
    stop = settings.get("hooks", {}).get("Stop", [])
    owned = {"matcher": "", "hooks": [{"type": "command", "command": command}]}
    if owned not in stop:
        return False
    stop.remove(owned)
    if not stop:
        settings["hooks"].pop("Stop")
    if not settings.get("hooks"):
        settings.pop("hooks", None)
    settings_path.write_text(json.dumps(settings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return True


def claude_status(
    settings_path: Path, *, command: str = "curiosity harness emit claude turn_complete"
) -> dict[str, bool]:
    """Compatibility diagnostics read from the settings file; never scraped."""
    settings = _read_json(settings_path)
    owned = {"matcher": "", "hooks": [{"type": "command", "command": command}]}
    stop = settings.get("hooks", {}).get("Stop", [])
    return {
        "disable_all_hooks": settings.get("disableAllHooks") is True,
        "owned_stop_hook": owned in stop if isinstance(stop, list) else False,
        "other_stop_hooks": (
            any(hook != owned for hook in stop) if isinstance(stop, list) else False
        ),
        "status_line_present": "statusLine" in settings,
        # Explicit rejection: driving orchestration from the status line would
        # spawn a Curiosity process at status-line frequency and replace the
        # user's own statusLine; completion hooks already cover the lifecycle.
        "status_line_unused": True,
    }


def opencode_plugin(command: str = "curiosity harness emit opencode") -> str:
    """Native plugin using only documented session lifecycle event names.

    ``session.status`` busy/idle, ``session.idle``, ``session.created``, and
    ``session.error`` are all currently documented OpenCode session events.
    A per-kind 1s debounce absorbs event storms before any process is spawned.
    """
    quoted = json.dumps(command)
    return (
        "// Managed by Curiosity Engine. Marker: curiosity-harness-plugin.\n"
        "// Remove with: curiosity harness uninstall opencode --path <this file>\n"
        f"export const Curiosity = async () => {{\n"
        f"  let lastKind = null\n"
        f"  let lastAt = 0\n"
        f"  return {{\n"
        f"    event: async ({{ event }}) => {{\n"
        f'      if (!["session.created", "session.idle", "session.status", "session.error"].includes(event.type)) return\n'
        f"      const status = event.properties?.status\n"
        f'      if (event.type === "session.status" && !["busy", "idle"].includes(status)) return\n'
        f"      const kind =\n"
        f'        event.type === "session.created" ? "session_start"\n'
        f'        : event.type === "session.error" ? "session_end"\n'
        f'        : event.type === "session.idle" ? "idle"\n'
        f'        : status === "busy" ? "working"\n'
        f'        : "idle"\n'
        f"      const now = Date.now()\n"
        f"      if (kind === lastKind && now - lastAt < 1000) return\n"
        f"      lastKind = kind\n"
        f"      lastAt = now\n"
        f"      Bun.spawn({{ cmd: [\"sh\", \"-lc\", {quoted} + \" \" + kind] }})\n"
        f"    }},\n"
        f"  }}\n"
        f"}}\n"
    )


_OPCODE_OWNERSHIP_MARKER = "curiosity-harness-plugin"


def install_opencode(plugin_path: Path, *, command: str = "curiosity harness emit opencode") -> None:
    if plugin_path.exists():
        existing = plugin_path.read_text(encoding="utf-8")
        if _OPCODE_OWNERSHIP_MARKER not in existing:
            raise ValueError(f"refusing to overwrite existing plugin: {plugin_path}")
    plugin_path.parent.mkdir(parents=True, exist_ok=True)
    plugin_path.write_text(opencode_plugin(command), encoding="utf-8")


def uninstall_opencode(plugin_path: Path) -> bool:
    if not plugin_path.exists() or _OPCODE_OWNERSHIP_MARKER not in plugin_path.read_text(
        encoding="utf-8"
    ):
        return False
    plugin_path.unlink()
    return True
