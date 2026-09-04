from collections import deque

import pytest

from curiosity.sources.adapters import (
    GitHubAdapter,
    SemanticScholarAdapter,
    WebAdapter,
    YouTubeAdapter,
    canonicalize_url,
)
from curiosity.sources.http import (
    BudgetExceeded,
    DiscoveryBudget,
    DiscoveryError,
    HttpClient,
    HttpResponse,
)


def fixture_client(*responses: HttpResponse, budget: int = 20) -> HttpClient:
    queue = deque(responses)

    def transport(url, headers, timeout):
        return queue.popleft()

    return HttpClient(transport=transport, budget=DiscoveryBudget(budget), retries=0)


def test_github_fixture_maps_metadata_and_rate_headers():
    body = b'{"items":[{"html_url":"https://github.com/acme/widget","full_name":"acme/widget","description":"demo"}]}'
    record = GitHubAdapter(
        fixture_client(HttpResponse(200, {"ETag": "tag", "X-RateLimit-Resource": "search"}, body))
    ).search("widget")[0]
    assert record.canonical_locator == "https://github.com/acme/widget"
    assert record.metadata["etag"] == "tag" and record.metadata["rate_resource"] == "search"


def test_semantic_scholar_fixture_never_claims_absent_abstract():
    body = b'{"data":[{"paperId":"p1","title":"Paper","url":"https://example.org/p1","year":2026}]}'
    record = SemanticScholarAdapter(fixture_client(HttpResponse(200, {}, body))).search("paper")[0]
    assert record.metadata["abstract_available"] == "false"


def test_semantic_scholar_batch_uses_one_post_request():
    calls = []

    def post(url, headers, body, timeout):
        calls.append((url, body))
        return HttpResponse(
            200,
            {},
            b'[{"paperId":"p1","title":"One"},{"paperId":"p2","title":"Two"}]',
        )

    adapter = SemanticScholarAdapter(HttpClient(post_transport=post, retries=0))
    assert [record.metadata["paper_id"] for record in adapter.batch_metadata(["p1", "p2"])] == [
        "p1",
        "p2",
    ]
    assert len(calls) == 1 and calls[0][1] == b'["p1","p2"]'


def test_http_budget_rate_timeout_and_malformed_policies():
    client = fixture_client(HttpResponse(429, {"Retry-After": "60"}, b"{}"), budget=1)
    with pytest.raises(DiscoveryError) as limited:
        client.get_json("https://example.test")
    assert limited.value.transient and limited.value.retry_after is not None
    with pytest.raises(BudgetExceeded):
        client.get_json("https://example.test")
    with pytest.raises(DiscoveryError, match="malformed JSON"):
        fixture_client(HttpResponse(200, {}, b"not-json")).get_json("https://example.test")


def test_url_feed_and_youtube_policy_boundaries():
    assert (
        canonicalize_url("HTTPS://Example.test/a?utm_source=x&edition=2#part")
        == "https://example.test/a?edition=2"
    )
    feed = b"<rss><channel><item><title>One</title><link>https://example.test/a?utm_x=1&amp;id=2</link></item><item><link>not-a-url</link></item></channel></rss>"
    records = WebAdapter().feed(feed, feed_url="https://example.test/feed")
    assert len(records) == 1 and records[0].metadata["content_fetched"] == "false"
    with pytest.raises(DiscoveryError, match="no API key"):
        YouTubeAdapter(fixture_client()).search("music")
    video = YouTubeAdapter(
        fixture_client(
            HttpResponse(200, {}, b'{"items":[{"id":"abc","snippet":{"title":"Video"}}]}')
        ),
        "key",
    ).search("music")[0]
    assert video.metadata["transcript_downloaded"] == "false"


def test_malformed_feed_and_size_bound_are_rejected():
    with pytest.raises(DiscoveryError):
        WebAdapter().feed(b"<rss>", feed_url="https://example.test/feed")
    with pytest.raises(DiscoveryError, match="size bound"):
        HttpClient(
            transport=lambda *_: HttpResponse(200, {}, b"x" * 4), max_response_bytes=3
        ).get_json("https://example.test")
