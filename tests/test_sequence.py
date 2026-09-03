from curiosity.sequence import QueueItem, plan_queue


def test_queue_is_seeded_bounded_and_excludes_stale_items():
    values = [
        QueueItem("a", "science", 2, True, "ranked"),
        QueueItem("b", "science", 1, True, "ranked"),
        QueueItem("c", "science", 0, True, "ranked"),
        QueueItem("d", "art", 1, False, "stale"),
    ]
    queue = plan_queue(values, size=3, max_topic_streak=2)
    assert [item.card_id for item in queue] == ["a", "b"]
