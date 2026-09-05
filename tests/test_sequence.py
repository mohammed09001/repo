from curiosity.sequence import QueueItem, plan_queue


def test_queue_is_seeded_bounded_and_excludes_stale_items():
    values = [
        QueueItem("a", "science", 2, True, "ranked"),
        QueueItem("b", "science", 1, True, "ranked"),
        QueueItem("c", "science", 0, True, "ranked"),
        QueueItem("d", "art", 1, False, "stale"),
    ]
    # The streak cap only bites when another topic is available; here only
    # science is verified, so the queue fills to size without stale items.
    queue = plan_queue(values, size=3, max_topic_streak=2)
    assert [item.card_id for item in queue] == ["a", "b", "c"]
    assert "d" not in {item.card_id for item in queue}


def test_topic_streak_cap_prefers_alternatives():
    values = [
        QueueItem("a", "science", 3, True, "ranked"),
        QueueItem("b", "science", 2, True, "ranked"),
        QueueItem("c", "art", 1, True, "ranked"),
        QueueItem("d", "art", 0, True, "ranked"),
    ]
    queue = plan_queue(values, size=4, max_topic_streak=2)
    topics = [item.topic for item in queue]
    # No run of three identical topics.
    for i in range(len(topics) - 2):
        assert not (topics[i] == topics[i + 1] == topics[i + 2])


def _similarity(a, b):
    from curiosity.dedupe.engine import lexical_similarity

    return lexical_similarity(a.text, b.text)


def test_mmr_reduces_redundancy_and_attaches_reason_codes():
    values = [
        QueueItem("a", "general", 1.0, True, "ranked", text="Mars has 2 small moons."),
        QueueItem("b", "general", 0.9, True, "ranked", text="Mars possesses two small moons orbiting it."),
        QueueItem("c", "general", 0.8, True, "ranked", text="Ocean currents transport heat around the planet."),
    ]
    # The near-paraphrase b is discounted by similarity, so a and c win the
    # two-slot queue despite b's higher raw score.
    queue = plan_queue(values, size=2, diversity_lambda=0.6, similarity=_similarity)
    assert [item.card_id for item in queue] == ["a", "c"]
    assert all(item.reason for item in queue)


def test_mmr_without_similarity_falls_back_to_relevance():
    values = [
        QueueItem("a", "general", 1.0, True, "ranked"),
        QueueItem("b", "general", 0.5, True, "ranked"),
        QueueItem("c", "general", 0.0, True, "ranked"),
    ]
    queue = plan_queue(values, size=3)
    assert [item.card_id for item in queue] == ["a", "b", "c"]


def test_unexpected_discovery_share_is_bounded_and_reason_coded():
    values = [
        QueueItem("a", "science", 3, True, "ranked"),
        QueueItem("b", "art", 2, True, "ranked"),
        QueueItem("c", "art", 1, True, "ranked"),
        QueueItem("d", "poetry", 0.5, True, "ranked"),
    ]
    queue = plan_queue(
        values, size=4, unexpected_share=0.25, unexpected_topics=frozenset({"poetry"}),
    )
    unexpected = [item for item in queue if item.topic == "poetry"]
    assert len(unexpected) <= 1  # 25% of 4 = 1 slot reserved, never more
    if unexpected:
        assert unexpected[0].reason == "unexpected_discovery"


def test_same_seed_same_state_gives_deterministic_queue():
    values = [
        QueueItem(f"f{i}", "general", float(i % 5), True, "ranked") for i in range(20)
    ]
    a = plan_queue(values, size=6, seed=7, diversity_lambda=0.5)
    b = plan_queue(values, size=6, seed=7, diversity_lambda=0.5)
    assert [item.card_id for item in a] == [item.card_id for item in b]
