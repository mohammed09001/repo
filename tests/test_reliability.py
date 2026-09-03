import pytest

from curiosity.reliability import Budget, retry_delay


def test_budget_and_backoff_are_bounded_and_deterministic():
    budget = Budget(max_requests=1, max_bytes=3)
    budget.consume(byte_count=3)
    assert budget.summary() == {"requests": 1, "bytes": 3}
    with pytest.raises(RuntimeError):
        budget.consume()
    assert retry_delay(2) == 1.0
