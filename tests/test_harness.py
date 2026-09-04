import json

import pytest

from curiosity.harness import (
    CAPABILITIES,
    claude_event,
    install_claude,
    opencode_event,
    uninstall_claude,
)


def test_unknown_harness_events_degrade_safely():
    from curiosity.harness import normalize

    assert normalize("manual", "unknown") is None
    assert normalize("manual", "idle") is None


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


def test_disabled_claude_and_opencode_status_are_conservative(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"disableAllHooks": true}')
    with pytest.raises(ValueError, match="disabled"):
        install_claude(path)
    assert opencode_event({"type": "session.status", "properties": {"status": "busy"}}).event_type == "working"
    assert opencode_event({"type": "session.status", "properties": {"status": "unknown"}}) is None
    assert CAPABILITIES["codex_notify"] == {"start": False, "busy": False, "idle": False, "complete": True}
    from curiosity.harness import normalize

    assert normalize("codex_notify", "idle") is None
