from curiosity.ranking import Candidate, ProfilePreferences, rank


def test_explainable_verified_ranking_and_repetition():
    profile = ProfilePreferences({"science": 3, "art": 1}, unexpected_discovery_weight=0)
    items = [
        Candidate("a", "science", "s", True, 1, 1, 1, 1),
        Candidate("b", "art", "s", True, 1, 1, 1, 1),
        Candidate("c", "science", "s", False, 1, 1, 1, 1),
    ]
    ranked = rank(items, profile, recent_ids=frozenset({"a"}))
    assert [item.candidate.id for item in ranked] == ["b", "a"]
    assert ranked[1].reasons["repetition_penalty"] == -1
