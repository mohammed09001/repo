from dataclasses import dataclass

from curiosity.runtime import Playback, TerminalPlayback, render, render_fact


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

    def current_playback_pulse(self):
        return self.pulses[0] if self.pulses else None

    def acknowledge_playback_pulse(self, pulse):
        assert pulse is self.pulses[0]
        self.acknowledged.append(self.pulses.pop(0))
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
