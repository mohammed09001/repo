from datetime import UTC, datetime
from pathlib import Path

import pytest

from curiosity.contracts.models import (
    ProvenanceClass,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.ingest.pipeline import FetchResponse, IngestError, IngestionPipeline
from curiosity.store import LocalStore


class FakeFetcher:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.headers = []

    def fetch(self, url, *, headers, max_bytes):
        self.headers.append(headers)
        return self.responses.pop(0)


def source():
    return SourceRecord(
        id=deterministic_id("source", "ingest"),
        source_type=SourceType.WEB,
        canonical_locator="https://example.test/article",
        title="Article",
        trust=TrustClass.REMOTE_UNTRUSTED,
        provenance=ProvenanceClass.SOURCE,
        retrieved_at=datetime(2026, 9, 3, tzinfo=UTC),
    )


def test_200_then_304_reuses_document_and_chunks(tmp_path: Path):
    fetcher = FakeFetcher(
        FetchResponse(
            200,
            b"<html><nav>noise</nav><article><h1>Title</h1><p>Useful durable content.</p></article><script>bad()</script></html>",
            "text/html",
            "tag",
            "yesterday",
        ),
        FetchResponse(304, b"", "text/html"),
    )
    with LocalStore(tmp_path / "store.db") as store:
        pipeline = IngestionPipeline(store, fetcher)
        document, chunks, reused = pipeline.ingest(source())
        again, again_chunks, reused_again = pipeline.ingest(source())
        assert not reused and reused_again and again.id == document.id and again_chunks == chunks
        assert fetcher.headers[1]["If-None-Match"] == "tag"
        assert "noise" not in document.raw_text and "bad" not in document.raw_text


def test_bounded_failures_and_deterministic_chunks(tmp_path: Path):
    with LocalStore(tmp_path / "store.db") as store:
        pipeline = IngestionPipeline(
            store, FakeFetcher(FetchResponse(200, b"x" * 20, "image/png")), max_bytes=10
        )
        with pytest.raises(IngestError, match="byte limit"):
            pipeline.ingest(source())
    with LocalStore(tmp_path / "store2.db") as store:
        html = b"<p>One sentence. Two sentence. Three sentence.</p>"
        first = IngestionPipeline(
            store, FakeFetcher(FetchResponse(200, html, "text/html")), chunk_ceiling=100
        ).ingest(source())[1]
        second = IngestionPipeline(
            store, FakeFetcher(FetchResponse(200, html, "text/html")), chunk_ceiling=100
        ).ingest(source())[1]
        assert [chunk.id for chunk in first] == [chunk.id for chunk in second]


def test_pdf_isolated_and_does_not_mutate_existing_document(tmp_path: Path):
    with LocalStore(tmp_path / "store.db") as store:
        pipeline = IngestionPipeline(
            store, FakeFetcher(FetchResponse(200, b"%PDF", "application/pdf"))
        )
        with pytest.raises(IngestError, match="Docling"):
            pipeline.ingest(source())
        assert store.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
