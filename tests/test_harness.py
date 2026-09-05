import json

import pytest

from curiosity.harness import (
    CAPABILITIES,
    claude_event,
    claude_status,
    codex_event,
    install_claude,
    install_opencode,
    opencode_event,
    opencode_plugin,
    uninstall_claude,
    uninstall_opencode,
)


def test_unknown_harness_events_degrade_safely():
    from curiosity.harness import normalize

    assert normalize("manual", "unknown") is None
    assert normalize("manual", "idle") is None
    assert normalize("codex_notify", "idle") is None


def test_claude_round_trip_preserves_unrelated_settings_and_discards_private_hook_fields(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"permissions": {"allow": ["Read"]}, "hooks": {"Stop": []}}))
    install_claude(path)
    saved = json.loads(path.read_text())
    assert saved["permissions"] == {"allow": ["Read"]}
    assert uninstall_claude(path)
    assert json.loads(path.read_text())["permissions"] == {"allow": ["Read"]}
    event = claude_event({"hook_event_name": "Stop", "prompt": "private", "transcript_path": "private"})
    assert event is not None and event.details == {"adapter": "claude"}


def test_claude_status_diagnostics_are_setting_derived_and_not_scraped(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "permissions": {"allow": ["Read"]},
                "statusLine": {"type": "command", "command": "user status line"},
                "hooks": {"Stop": [], "PreToolUse": [{"matcher": "Bash", "hooks": []}]},
            }
        )
    )
    diagnostic = claude_status(path)
    assert diagnostic["disable_all_hooks"] is False
    assert diagnostic["owned_stop_hook"] is False
    assert diagnostic["other_stop_hooks"] is False
    assert diagnostic["status_line_present"] is True
    assert diagnostic["status_line_unused"] is True
    install_claude(path)
    assert claude_status(path)["owned_stop_hook"] is True


def test_disabled_claude_and_opencode_status_are_conservative(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"disableAllHooks": true}')
    with pytest.raises(ValueError, match="disabled"):
        install_claude(path)
    assert claude_status(path)["disable_all_hooks"] is True
    assert opencode_event({"type": "session.status", "properties": {"status": "busy"}}).event_type == "working"
    assert opencode_event({"type": "session.status", "properties": {"status": "unknown"}}) is None
    assert CAPABILITIES["codex_notify"] == {"start": False, "busy": False, "idle": False, "complete": True}
    from curiosity.harness import normalize

    assert normalize("codex_notify", "idle") is None


def test_opencode_session_error_is_terminal_quiet():
    event = opencode_event({"type": "session.error", "properties": {"error": "private"}})
    assert event is not None and event.event_type == "session_end"
    assert event.details == {"adapter": "opencode"}
    # Unknown session events are never guessed.
    assert opencode_event({"type": "session.deleted"}) is None
    assert opencode_event({"type": "session.updated"}) is None


def test_codex_completion_payload_maps_and_ignores_prompt_fields():
    event = codex_event({"type": "agent-turn-complete", "turn-id": "12345", "prompt": "private"})
    assert event is not None and event.event_type == "turn_complete"
    assert event.details == {"adapter": "codex_notify"}
    assert codex_event({"type": "agent-turn-start"}) is None
    assert codex_event({}) is None


def test_opencode_plugin_is_ownership_marked_debounced_and_reversible(tmp_path):
    plugin = opencode_plugin()
    assert "curiosity-harness-plugin" in plugin
    assert "session.error" in plugin
    # The plugin debounces repeated kinds within 1s before spawning a process.
    assert "Date.now()" in plugin
    path = tmp_path / "curiosity.js"
    install_opencode(path)
    assert path.exists()
    assert "curiosity-harness-plugin" in path.read_text(encoding="utf-8")
    # Reinstall over an owned plugin refreshes it instead of clobbering.
    install_opencode(path)
    # Refusing to overwrite an unrelated plugin preserves it.
    other = tmp_path / "other.js"
    other.write_text("export const Other = async () => ({})")
    with pytest.raises(ValueError, match="refusing"):
        install_opencode(other)
    assert other.read_text(encoding="utf-8") == "export const Other = async () => ({})"
    assert uninstall_opencode(path)
    assert not path.exists()
    assert not uninstall_opencode(path)
    assert not uninstall_opencode(other)