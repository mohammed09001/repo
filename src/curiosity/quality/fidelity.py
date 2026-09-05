"""Deterministic fidelity anchors for translation/rewrite safety.

These lexical checks run before any model-assisted judgment. They catch the
most dangerous rewrite failure modes without spending tokens: invented numbers,
reversed negation, changed comparison direction, and added causes or certainty.
"""

from __future__ import annotations

import re

_NUMBER = re.compile(r"\d+(?:\.\d+)?(?:%|th|rd|st|nd)?")
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_NEGATION = re.compile(
    r"\b(?:not|no|never|without|none|neither|nor|non-|doesn't|isn't|aren't|"
    r"didn't|won't|can't|cannot|hasn't|haven't)\b",
    re.I,
)
_COMPARE = re.compile(
    r"\b(?:more|less|greater|smaller|larger|faster|slower|higher|lower|"
    r"earlier|later|exceeds|below|above)\b",
    re.I,
)
_HEDGE = re.compile(
    r"\b(?:can|could|may|might|must|should|would|will|suggests?|appears?|seems?|"
    r"indicates?|implies?|possibly|perhaps)\b",
    re.I,
)
_CERTAIN = re.compile(
    r"\b(?:proves?|confirms?|demonstrates?|establishes?|guarantees?|definitely|certainly)\b",
    re.I,
)
_CAUSAL = re.compile(r"\b(?:because|causes|caused|therefore|hence|leads? to|results? in|thus)\b", re.I)
_SUPERLATIVE = re.compile(r"\b(?:best|worst|greatest|most|least|biggest|smallest|largest)\b", re.I)
_DIRECTION = re.compile(
    r"\b(?:increases?|decreases?|rises?|falls?|raises?|lowers?|gains?|loses?|"
    r"speeds?|slows?|expands?|shrinks?)\b",
    re.I,
)

_NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "100",
    "thousand": "1000",
    "million": "1000000",
}


def _numbers(text: str) -> set[str]:
    """Digits, years, and spelled-out small numbers, so ``2`` and ``two`` are
    the same numeric anchor."""
    numbers = set(_NUMBER.findall(text)) | set(_YEAR.findall(text))
    lowered = text.casefold()
    for word, value in _NUMBER_WORDS.items():
        if re.search(rf"\b{word}\b", lowered):
            numbers.add(value)
    return numbers


def anchor_violations(original: str, rewritten: str, *, translated: bool = False) -> tuple[str, ...]:
    """Return every anchor class the rewrite broke, or an empty tuple if safe.

    ``translated=True`` relaxes lexical negation/comparison/modality checks
    because those words differ across languages; numbers, dates, and added
    cause/certainty language remain strictly checked.
    """
    violations: list[str] = []
    if _numbers(rewritten) - _numbers(original):
        violations.append("numbers")
    if not translated:
        if bool(_NEGATION.search(original)) != bool(_NEGATION.search(rewritten)):
            violations.append("negation")
        if _COMPARE.search(rewritten) and not _COMPARE.search(original):
            violations.append("comparison_direction")
        if bool(_HEDGE.search(original)) != bool(_HEDGE.search(rewritten)):
            violations.append("modality")
        if _CERTAIN.search(rewritten) and not _CERTAIN.search(original):
            violations.append("certainty_added")
    if _CAUSAL.search(rewritten) and not _CAUSAL.search(original):
        violations.append("causality_added")
    if _SUPERLATIVE.search(rewritten) and not _SUPERLATIVE.search(original):
        violations.append("superlative_added")
    return tuple(violations)


def anchor_conflict(a: str, b: str) -> bool:
    """True when two facts disagree on a hard anchor (numbers, negation polarity,
    or comparison direction). Such facts are different claims and must never be
    merged by the Near-Duplicate Firewall."""
    if _numbers(a) != _numbers(b):
        return True
    if bool(_NEGATION.search(a)) != bool(_NEGATION.search(b)):
        return True
    if set(_DIRECTION.findall(a.casefold())) != set(_DIRECTION.findall(b.casefold())):
        return True
    return False