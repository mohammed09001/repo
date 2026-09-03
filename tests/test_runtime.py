from curiosity.runtime import Playback, render


def test_safe_local_playback_controls_and_rendering():
    runtime = Playback((("Hook\x1b", "Body text", "Local source"),))
    runtime.pause()
    assert runtime.next() is None
    runtime.resume()
    card = runtime.next()
    assert card is not None
    assert "\x1b" not in render(card, width=20)
    runtime.stop()
    assert runtime.next() is None
