"""Deterministic fidelity anchors for translation/rewrite safety."""

from curiosity.quality.fidelity import anchor_violations


def test_safe_rewrite_has_no_violations():
    original = "Mars has 2 small moons that orbit the planet."
    rewritten = "Mars has 2 small moons orbiting it."
    assert anchor_violations(original, rewritten) == ()


def test_invented_number_is_rejected():
    original = "Mars has 2 small moons."
    assert "numbers" in anchor_violations(original, "Mars has 99 small moons.")


def test_reversed_negation_is_rejected():
    original = "Titan does not have a dense oxygen atmosphere."
    assert "negation" in anchor_violations(original, "Titan has a dense oxygen atmosphere.")


def test_added_comparison_direction_is_rejected():
    original = "The lake stores water."
    assert "comparison_direction" in anchor_violations(original, "The lake stores more water.")


def test_modality_and_causality_and_superlative_changes_are_rejected():
    original = "The experiment suggests an effect."
    assert "modality" in anchor_violations(original, "The experiment proves an effect.")
    original2 = "The plant grew in the chamber."
    assert "causality_added" in anchor_violations(original2, "Because of light the plant grew in the chamber.")
    original3 = "The engine performed well in tests."
    assert "superlative_added" in anchor_violations(original3, "The engine is the best in tests.")


def test_translated_mode_relaxes_lexical_negation_but_keeps_numbers():
    original = "火星有2顆小衛星。"
    good = "Mars has 2 small moons."
    assert anchor_violations(original, good, translated=True) == ()
    assert "numbers" in anchor_violations(original, "Mars has 9 small moons.", translated=True)