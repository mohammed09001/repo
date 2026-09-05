from dataclasses import dataclass

from curiosity.runtime import Playback, TerminalPlayback, TtySurface, render, render_fact, safe_text


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


@dataclass
class Pulse:
    display_fact: str


class Queue:
    def __init__(self):
        self.pulses = [Pulse("One fact\x1b]8;;https://bad\x07."), Pulse("Two facts.")]
        self.acknowledged = []
        self.refills = 0

    def current_playback_pulse(self):
        return self.pulses[0] if self.pulses else None

    def acknowledge_playback_pulse(self, pulse):
        assert pulse is self.pulses[0]
        self.acknowledged.append(self.pulses.pop(0))
        return True

    def refill_playback(self):
        self.refills += 1
        return True


def test_terminal_loop_uses_exact_default_dwell_and_fact_only_output():
    queue = Queue()
    output, sleeps = [], []
    shown = TerminalPlayback(queue, sleeps.append, output.append).run()
    assert shown == 2
    assert sleeps == [10, 10]
    assert "\x1b" not in output[0]
    assert "Source" not in "\n".join(output)
    assert render_fact("Fact.") == "Fact."


def test_tty_surface_replaces_only_its_owned_region():
    output: list[str] = []
    surface = TtySurface(output.append)
    surface.show("First fact.")
    surface.show("Second fact that wraps\nonto two lines.")
    surface.close()
    joined = "".join(output)
    # Each update first clears the previously owned lines, never the history.
    assert "First fact." in joined
    assert "\x1b[2K" in joined
    assert joined.endswith("\r\n")


def test_tty_surface_clears_exactly_the_wrapped_lines():
    output: list[str] = []
    surface = TtySurface(output.append)
    surface.show("one\ntwo\nthree")
    surface.show("short")
    joined = "".join(output)
    # Three owned lines -> two upward moves plus three clears.
    assert joined.count("\x1b[1A") == 2
    assert joined.count("\x1b[2K") == 3
    surface.close()


def test_tty_surface_multi_line_region_uses_upward_clears():
    output: list[str] = []
    surface = TtySurface(output.append)
    surface.show("first wraps\nonto a second line")
    surface.show("next fact")
    joined = "".join(output)
    assert joined.count("\x1b[1A") == 1
    assert joined.count("\x1b[2K") == 2
    surface.close()


def test_terminal_loop_with_surface_shows_one_region_and_closes_on_exit():
    queue = Queue()
    output, sleeps = [], []
    surface = TtySurface(output.append)
    shown = TerminalPlayback(queue, sleeps.append, output.append, surface=surface).run()
    assert shown == 2
    assert sleeps == [10, 10]
    assert "".join(output).endswith("\r\n")


def test_terminal_loop_ambient_continue_and_refill_gates():
    queue = Queue()
    output, sleeps = [], []
    calls = {"continue": 0, "refill": 0}

    def should_continue():
        calls["continue"] += 1
        # Allow the first fact, then quiet at the next boundary.
        return calls["continue"] <= 1

    def should_refill():
        calls["refill"] += 1
        return False

    shown = TerminalPlayback(
        queue, sleeps.append, output.append, should_continue=should_continue, should_refill=should_refill
    ).run()
    assert shown == 1
    assert sleeps == [10]
    assert calls["continue"] == 2
    assert calls["refill"] == 1
    assert queue.refills == 0
    assert output == ["One fact]8;;https://bad."]


def test_ambient_quiet_at_start_shows_nothing():
    queue = Queue()
    shown = TerminalPlayback(queue, lambda _: None, lambda _: None, should_continue=lambda: False).run()
    assert shown == 0
    assert queue.acknowledged == []


def test_malicious_osc_ansi_input_is_neutralized():
    text = "Fact \x1b]8;;https://evil\x07 escaped."
    cleaned = safe_text(text)
    assert "\x1b" not in cleaned
    assert "\x07" not in cleaned
    assert render_fact(text) == render_fact(cleaned)
    output: list[str] = []
    TtySurface(output.append).show(text)
    assert "\x1b]8" not in "".join(output)


def test_terminal_loop_closes_surface_on_keyboard_interrupt():
    import pytest

    queue = Queue()
    output, sleeps = [], []
    surface = TtySurface(output.append)

    def sleeper(seconds):
        sleeps.append(seconds)
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        TerminalPlayback(queue, sleeper, output.append, surface=surface).run()
    assert sleeps == [10]
    assert "".join(output).endswith("\r\n")
