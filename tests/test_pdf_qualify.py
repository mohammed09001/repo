"""Real Docling PDF qualification with hard resource bounds.

Skipped cleanly when the optional ``curiosity-engine[pdf]`` extra is absent so
the core offline suite never depends on Docling. The PDF CI job installs the
extra and runs these tests for real.
"""

import importlib.util
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

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("docling") is None,
    reason="requires the optional curiosity-engine[pdf] extra",
)

FIXTURES = Path(__file__).parent / "fixtures"
PDF_BYTES = (FIXTURES / "sample.pdf").read_bytes()

NOW = datetime(2026, 9, 5, tzinfo=UTC)


class FakeFetcher:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.headers = []

    def fetch(self, url, *, headers, max_bytes):
        self.headers.append(headers)
        return self.responses.pop(0)


def source(locator: str = "https://example.test/paper") -> SourceRecord:
    return SourceRecord(
        id=deterministic_id("source", "pdf-qualify"),
        source_type=SourceType.WEB,
        canonical_locator=locator,
        title="Qualified PDF",
        trust=TrustClass.REMOTE_UNTRUSTED,
        provenance=ProvenanceClass.SOURCE,
        retrieved_at=NOW,
    )


def test_real_pdf_succeeds_through_full_application(tmp_path):
    from curiosity.application import CuriosityApplication

    class AppFetcher:
        def fetch(self, url, *, headers, max_bytes):
            return FetchResponse(200, PDF_BYTES, "application/pdf", "etag-v1")

    database = tmp_path / "data" / "curiosity.db"
    with LocalStore(database) as store:
        pipeline = IngestionPipeline(store, FakeFetcher(FetchResponse(200, PDF_BYTES, "application/pdf", "etag-v1")))
        outcome = pipeline.ingest(source())
        assert not outcome.reused
        assert outcome.parser_version.startswith("docling-")
        assert outcome.parser_elapsed_ms >= 0
        assert "periodic table organizes chemical elements" in outcome.document.raw_text
        assert outcome.chunks
        app = CuriosityApplication(store, fetcher=AppFetcher(), now=lambda: NOW)
        app.initialize()
        report = app.refresh_build()
        assert report.pulses_built == 1
        pulses = store.list_eligible_pulses()
        assert "periodic table" in pulses[0].display_fact
        assert store.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
    with LocalStore(database) as reopened:
        assert len(reopened.list_pulses()) == 1


def test_oversized_pdf_rejected_before_conversion(tmp_path):
    with LocalStore(tmp_path / "store.db") as store:
        big = b"%PDF-1.4\n" + b"x" * 2000
        pipeline = IngestionPipeline(store, FakeFetcher(FetchResponse(200, big, "application/pdf")), pdf_max_file_size=1000)
        with pytest.raises(IngestError, match="file size"):
            pipeline.ingest(source())
        assert store.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0


def test_page_limit_rejected_before_conversion(tmp_path):
    with LocalStore(tmp_path / "store.db") as store:
        many_pages = b"%PDF-1.4\n" + b"/Type /Page" * 60
        pipeline = IngestionPipeline(store, FakeFetcher(FetchResponse(200, many_pages, "application/pdf")), pdf_max_pages=10)
        with pytest.raises(IngestError, match="page limit"):
            pipeline.ingest(source())
        assert store.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0


def test_malformed_pdf_leaves_no_eligible_document(tmp_path):
    with LocalStore(tmp_path / "store.db") as store:
        malformed = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF"
        pipeline = IngestionPipeline(store, FakeFetcher(FetchResponse(200, malformed, "application/pdf")), pdf_timeout_seconds=15)
        with pytest.raises(IngestError, match="did not succeed"):
            pipeline.ingest(source())
        assert store.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0


def test_second_unchanged_pdf_refresh_performs_no_reconversion(tmp_path):
    fetcher = FakeFetcher(
        FetchResponse(200, PDF_BYTES, "application/pdf", "etag-v1"),
        FetchResponse(304, b"", "application/pdf"),
    )
    with LocalStore(tmp_path / "store.db") as store:
        pipeline = IngestionPipeline(store, fetcher)
        first = pipeline.ingest(source())
        second = pipeline.ingest(source())
        assert not first.reused and second.reused
        assert second.document.id == first.document.id
        assert second.chunks == first.chunks
        assert fetcher.headers[1]["If-None-Match"] == "etag-v1"