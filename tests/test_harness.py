from curiosity.harness import normalize


def test_unknown_harness_events_degrade_safely():
    assert normalize("manual", "unknown") is None
    assert normalize("manual", "idle").details == {"adapter": "manual"}
