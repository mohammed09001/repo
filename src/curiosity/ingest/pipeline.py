from __future__ import annotations

import io
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from html.parser import HTMLParser
from typing import Protocol

import httpx

from curiosity.contracts.models import (
    Chunk,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    deterministic_id,
)
from curiosity.store import LocalStore


class IngestError(RuntimeError):
    def __init__(self, message: str, *, transient: bool = False) -> None:
        super().__init__(message)
        self.transient = transient


@dataclass(frozen=True)
class FetchResponse:
    status: int
    body: bytes
    mime_type: str
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True)
class IngestOutcome:
    document: SourceDocument
    chunks: list[Chunk]
    reused: bool
    reparsed: bool
    parser_version: str
    parser_mode: str = ""
    parser_elapsed_ms: float = 0.0


class Fetcher(Protocol):
    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse: ...


def _read_bounded(response: httpx.Response, max_bytes: int) -> bytes:
    parts: list[bytes] = []
    total = 0
    for chunk in response.iter_bytes():
        total += len(chunk)
        if total > max_bytes:
            break
        parts.append(chunk)
    return b"".join(parts)


class HttpxFetcher:
    """Pooled bounded fetcher for the explicit CLI path; tests inject fixtures instead."""

    def __init__(self, client: httpx.Client):
        self.client = client

    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        request_headers = {"User-Agent": "curiosity-engine/1.0 ingest", **headers}
        try:
            with self.client.stream(
                "GET",
                url,
                headers=request_headers,
                follow_redirects=True,
                timeout=10.0,
            ) as response:
                if response.status_code not in {200, 304}:
                    from curiosity.reliability import classify_http_status

                    raise IngestError(
                        f"fetch failed with HTTP {response.status_code}",
                        transient=classify_http_status(response.status_code) == "transient",
                    )
                body = _read_bounded(response, max_bytes)
                mime = response.headers.get("content-type", "").split(";")[0].strip()
                return FetchResponse(
                    response.status_code,
                    body,
                    mime,
                    response.headers.get("etag"),
                    response.headers.get("last-modified"),
                )
        except IngestError:
            raise
        except httpx.HTTPError as error:
            raise IngestError(f"network error: {error}", transient=True) from error


class _MainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "header", "footer"}:
            self.ignored += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "header", "footer"} and self.ignored:
            self.ignored -= 1
        if tag in {"p", "div", "article", "section", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored:
            self.parts.append(data)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_html(body: bytes) -> str:
    """Fallback for malformed pages when the primary extractor yields no content."""
    parser = _MainText()
    try:
        parser.feed(body.decode("utf-8", errors="strict"))
    except UnicodeDecodeError as exc:
        raise IngestError("HTML is not UTF-8 text") from exc
    text = normalize_text(" ".join(parser.parts))
    if not text:
        raise IngestError("HTML parser found no usable text")
    return text


def _sentence_count(text: str) -> int:
    # ASCII plus CJK sentence terminators so non-English text still qualifies
    # for the fast lane and can be escalated to the translation quality lane.
    return len(re.findall(r"[.!?\u3002\uff01\uff1f](?:\s|$)", text))


def html_quality(text: str) -> bool:
    """Cheap extraction-quality heuristic; never model scoring.

    A qualified main text is long enough and not boilerplate-dominated: almost
    all real text carries at least one sentence per 1000 characters, while
    navigation-heavy extraction is far sparser. The gate is deliberately
    permissive so genuine single-sentence pages are never rejected.
    """
    length = len(text)
    if length < 20:
        return False
    sentences = _sentence_count(text)
    if sentences < 1:
        return False
    return length / sentences <= 1000


def _extract_with(body: bytes, *, fast: bool) -> str:
    from trafilatura import extract

    kwargs = {"fast": True} if fast else {"favor_precision": True}
    try:
        extracted = extract(
            body.decode("utf-8", errors="strict"),
            output_format="txt",
            include_comments=False,
            include_tables=False,
            **kwargs,
        )
    except UnicodeDecodeError as exc:
        raise IngestError("HTML is not UTF-8 text") from exc
    return normalize_text(extracted or "")


def extract_html(body: bytes) -> tuple[str, str]:
    """Precision-first HTML extraction with a quality-gated fallback.

    Trafilatura's ``fast`` mode was benchmarked on the golden corpus and
    rejected for HTML: on clean small pages it can return empty text, and on
    noisy pages it leaks navigation boilerplate that cheap quality heuristics
    cannot reliably detect. The precision path is therefore the cheapest mode
    that meets quality; only its own quality-gated failure escalates to the
    conservative HTML fallback.
    """
    try:
        import trafilatura  # noqa: F401
    except ImportError as exc:  # pragma: no cover - declared runtime dependency
        raise IngestError("Trafilatura is not installed") from exc
    text = _extract_with(body, fast=False)
    if html_quality(text):
        return text, HTML_PRECISION_VERSION
    fallback = parse_html(body)
    if html_quality(fallback):
        return fallback, HTML_FALLBACK_VERSION
    raise IngestError("HTML extraction found no usable main content")


def parse_pdf(
    body: bytes,
    *,
    max_pages: int = 50,
    max_file_size: int = 10_000_000,
    document_timeout_seconds: float = 60.0,
    threads: int = 1,
) -> tuple[str, str, float]:
    """Convert a bounded, engine-fetched PDF through Docling.

    Uses an in-memory ``DocumentStream`` (never an uncontrolled remote source)
    and Docling's own ``max_num_pages``/``max_file_size`` bounds plus a
    ``document_timeout`` and a single CPU thread. OCR and table structure are
    disabled by default for born-digital text PDFs. Only a full ``SUCCESS``
    status is qualified; partial/failed conversion never becomes a canonical
    successful document.
    """
    started = time.perf_counter()
    if not body.startswith(b"%PDF"):
        raise IngestError("PDF signature is invalid")
    if len(body) > max_file_size:
        raise IngestError("PDF exceeds configured file size limit")
    if body.count(b"/Type /Page") > max_pages:
        raise IngestError("PDF exceeds configured page limit")
    try:
        from docling.datamodel.base_models import DocumentStream, InputFormat
        from docling.datamodel.pipeline_options import (
            AcceleratorDevice,
            AcceleratorOptions,
            PdfPipelineOptions,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as exc:
        raise IngestError("Docling requires the optional curiosity-engine[pdf] dependency") from exc
    pipeline_options = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=False,
        document_timeout=document_timeout_seconds,
        accelerator_options=AcceleratorOptions(num_threads=threads, device=AcceleratorDevice.CPU),
    )
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
    try:
        result = converter.convert(
            DocumentStream(name="document.pdf", stream=io.BytesIO(body)),
            raises_on_error=False,
            max_num_pages=max_pages,
            max_file_size=max_file_size,
        )
    except Exception as exc:  # Docling raises several provider-specific exceptions.
        raise IngestError("Docling conversion failed") from exc
    from docling.datamodel.document import ConversionStatus

    if result.status != ConversionStatus.SUCCESS:
        raise IngestError(f"Docling conversion did not succeed ({result.status.value})")
    text = normalize_text(result.document.export_to_markdown())
    if len(text) < 20:
        raise IngestError("Docling produced no usable text")
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    return text, PDF_PARSER_VERSION, elapsed_ms


HTML_FAST_VERSION = "trafilatura-2.2-fast-1"
HTML_PRECISION_VERSION = "trafilatura-2.2-precision-1"
HTML_FALLBACK_VERSION = "trafilatura-2.2-fallback-1"
PLAIN_PARSER_VERSION = "plain-1"
PDF_PARSER_VERSION = "docling-2-bounded-1"

def current_parser_versions(mime_type: str) -> frozenset[str]:
    """Current parser contract versions for a MIME type.

    Computed from the live version constants so a contract bump (including the
    parser-mode contract) intentionally invalidates cached parses. Fast mode is
    deliberately absent: it was rejected by the parser benchmark, so a
    fast-parsed cached document is re-parsed on reuse.
    """
    if mime_type in {"text/html", "application/xhtml+xml"}:
        return frozenset({HTML_PRECISION_VERSION, HTML_FALLBACK_VERSION})
    if mime_type == "text/plain":
        return frozenset({PLAIN_PARSER_VERSION})
    if mime_type == "application/pdf":
        return frozenset({PDF_PARSER_VERSION})
    return frozenset()


def parse_document(
    body: bytes,
    mime_type: str,
    *,
    pdf_max_pages: int = 50,
    pdf_max_file_size: int = 10_000_000,
    pdf_timeout_seconds: float = 60.0,
    parser_threads: int = 1,
) -> tuple[str, str, str, float]:
    """Return ``(text, parser_version, parser_mode, elapsed_ms)`` for one body."""
    if mime_type in {"text/html", "application/xhtml+xml"}:
        started = time.perf_counter()
        text, version = extract_html(body)
        mode = version
        return text, version, mode, round((time.perf_counter() - started) * 1000, 1)
    if mime_type == "text/plain":
        return (
            normalize_text(body.decode("utf-8", errors="strict")),
            PLAIN_PARSER_VERSION,
            PLAIN_PARSER_VERSION,
            0.0,
        )
    if mime_type == "application/pdf":
        text, version, elapsed = parse_pdf(
            body,
            max_pages=pdf_max_pages,
            max_file_size=pdf_max_file_size,
            document_timeout_seconds=pdf_timeout_seconds,
            threads=parser_threads,
        )
        return text, version, version, elapsed
    raise IngestError(f"MIME type is not allowed: {mime_type}")


def chunk_text(
    document: SourceDocument, text: str, *, ceiling: int = 1_200, parser_version: str = "plain-1"
) -> list[Chunk]:
    if ceiling < 100:
        raise ValueError("chunk ceiling must be at least 100 characters")
    units = [unit.strip() for unit in re.split(r"(?<=[.!?])\s+|\n{2,}", text) if unit.strip()]
    chunks: list[Chunk] = []
    current = ""
    start = 0
    for unit in units:
        candidate = f"{current} {unit}".strip()
        if current and len(candidate) > ceiling:
            ordinal = len(chunks)
            normalized = normalize_text(current)
            chunks.append(
                Chunk(
                    id=deterministic_id(
                        "chunk",
                        document.id,
                        parser_version,
                        str(ordinal),
                        sha256(normalized.encode()).hexdigest(),
                    ),
                    document_id=document.id,
                    ordinal=ordinal,
                    text=normalized,
                    char_start=start,
                    char_end=start + len(current),
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                )
            )
            start += len(current) + 1
            current = unit
        else:
            current = candidate
    if current:
        ordinal = len(chunks)
        normalized = normalize_text(current)
        chunks.append(
            Chunk(
                id=deterministic_id(
                    "chunk",
                    document.id,
                    parser_version,
                    str(ordinal),
                    sha256(normalized.encode()).hexdigest(),
                ),
                document_id=document.id,
                ordinal=ordinal,
                text=normalized,
                char_start=start,
                char_end=start + len(current),
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
        )
    return chunks


class IngestionPipeline:
    def __init__(
        self,
        store: LocalStore,
        fetcher: Fetcher,
        *,
        max_bytes: int = 2_000_000,
        chunk_ceiling: int = 1_200,
        pdf_max_pages: int = 50,
        pdf_max_file_size: int = 10_000_000,
        pdf_timeout_seconds: float = 60.0,
        parser_threads: int = 1,
    ):
        self.store, self.fetcher, self.max_bytes, self.chunk_ceiling = (
            store,
            fetcher,
            max_bytes,
            chunk_ceiling,
        )
        self.pdf_max_pages = pdf_max_pages
        self.pdf_max_file_size = pdf_max_file_size
        self.pdf_timeout_seconds = pdf_timeout_seconds
        self.parser_threads = parser_threads
        self.counters: dict[str, int | float] = {
            "http_fetches": 0,
            "http_cache_hits": 0,
            "bytes_downloaded": 0,
            "retries": 0,
            "failures": 0,
            "parser_elapsed_ms": 0.0,
        }

    def _fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        from curiosity.reliability import bounded_retry

        def attempt() -> FetchResponse:
            return self.fetcher.fetch(url, headers=headers, max_bytes=max_bytes)

        def count_retry(_attempt: int) -> None:
            self.counters["retries"] = int(self.counters["retries"]) + 1

        try:
            return bounded_retry(attempt, attempts=3, base_seconds=0.0, on_retry=count_retry)
        except IngestError:
            self.counters["failures"] = int(self.counters["failures"]) + 1
            raise

    def ingest(self, source: SourceRecord) -> IngestOutcome:
        """Fetch or reuse one source branch.

        ``reused`` is True only when the exact document and chunk branch was
        already built with a current parser contract, so downstream stages can
        be skipped entirely. ``reparsed`` is True when unchanged bytes were
        intentionally re-parsed because the parser contract moved.
        """
        self.store.put_source(source)
        cache_key = f"source:{source.canonical_locator}"
        cached = self.store.get_cache(cache_key)
        headers = {
            key: value
            for key, value in (
                ("If-None-Match", cached.get("etag") if cached else None),
                ("If-Modified-Since", cached.get("last_modified") if cached else None),
            )
            if value
        }
        response = self._fetch(
            source.canonical_locator, headers=headers, max_bytes=self.max_bytes
        )
        if response.status == 304:
            self.counters["http_cache_hits"] = int(self.counters["http_cache_hits"]) + 1
            if not cached:
                raise IngestError("304 response without local cache metadata")
            mime_type = cached["metadata"].get("mime_type", "")
            expected_versions = current_parser_versions(mime_type) if mime_type else frozenset()
            if cached["parser_version"] in expected_versions and cached.get("document_id"):
                document, chunks, _, parser_version = self._reuse(cached)
                return IngestOutcome(document, chunks, True, False, parser_version)
            raw_bytes = cached.get("raw_bytes")
            if not raw_bytes:
                raise IngestError("304 cache has no stored bytes to re-parse; re-add the source")
            # Same bytes but the parser contract moved: intentionally re-parse.
            document, chunks, parser_mode, elapsed = self._parse_and_chunk(source, raw_bytes, mime_type)
            self.counters["parser_elapsed_ms"] = float(self.counters["parser_elapsed_ms"]) + elapsed
            self.store.put_cache(
                cache_key=cache_key,
                content_sha256=document.content_sha256,
                fetched_at=datetime.now(UTC),
                parser_version=parser_mode,
                etag=cached.get("etag"),
                last_modified=cached.get("last_modified"),
                metadata={"raw_sha256": cached["content_sha256"], "mime_type": mime_type},
                document_id=document.id,
                raw_bytes=raw_bytes,
            )
            return IngestOutcome(
                document, chunks, False, True, parser_mode, parser_mode, elapsed
            )
        if response.status != 200:
            raise IngestError(f"fetch failed with HTTP {response.status}")
        if len(response.body) > self.max_bytes:
            raise IngestError("response exceeds byte limit")
        self.counters["http_fetches"] = int(self.counters["http_fetches"]) + 1
        self.counters["bytes_downloaded"] = int(self.counters["bytes_downloaded"]) + len(
            response.body
        )
        document, chunks, parser_mode, elapsed = self._parse_and_chunk(
            source, response.body, response.mime_type
        )
        self.counters["parser_elapsed_ms"] = float(self.counters["parser_elapsed_ms"]) + elapsed
        self.store.put_cache(
            cache_key=cache_key,
            content_sha256=document.content_sha256,
            fetched_at=datetime.now(UTC),
            parser_version=parser_mode,
            etag=response.etag,
            last_modified=response.last_modified,
            metadata={
                "raw_sha256": sha256(response.body).hexdigest(),
                "mime_type": response.mime_type,
            },
            document_id=document.id,
            raw_bytes=response.body,
        )
        return IngestOutcome(
            document, chunks, False, False, parser_mode, parser_mode, elapsed
        )

    def _reuse(self, cached: dict[str, object]) -> tuple[SourceDocument, list[Chunk], bool, str]:
        document_id = cached.get("document_id")
        if not document_id:
            row = self.store.connection.execute(
                "SELECT id FROM documents WHERE content_sha256=? ORDER BY captured_at DESC LIMIT 1",
                (cached["content_sha256"],),
            ).fetchone()
            if not row:
                raise IngestError("304 cache metadata has no local document")
            document_id = row["id"]
        row = self.store.connection.execute(
            "SELECT payload_json FROM documents WHERE id=?", (document_id,)
        ).fetchone()
        if not row:
            raise IngestError("304 cache metadata has no local document")
        document = SourceDocument.model_validate_json(row["payload_json"])
        rows = self.store.connection.execute(
            "SELECT payload_json FROM chunks WHERE document_id=? ORDER BY ordinal",
            (document.id,),
        )
        return (
            document,
            [Chunk.model_validate_json(item["payload_json"]) for item in rows],
            True,
            str(cached["parser_version"]),
        )

    def _parse_and_chunk(
        self, source: SourceRecord, body: bytes, mime_type: str
    ) -> tuple[SourceDocument, list[Chunk], str, float]:
        text, parser_version, parser_mode, elapsed = parse_document(
            body,
            mime_type,
            pdf_max_pages=self.pdf_max_pages,
            pdf_max_file_size=self.pdf_max_file_size,
            pdf_timeout_seconds=self.pdf_timeout_seconds,
            parser_threads=self.parser_threads,
        )
        raw_hash = sha256(body).hexdigest()
        document = SourceDocument(
            id=deterministic_id("document", source.id, raw_hash, parser_version),
            source_id=source.id,
            content_sha256=raw_hash,
            raw_text=text,
            captured_at=datetime.now(UTC),
            provenance=ProvenanceClass.SOURCE,
        )
        self.store.put_document(document)
        chunks = chunk_text(
            document, text, ceiling=self.chunk_ceiling, parser_version=parser_version
        )
        for chunk in chunks:
            self.store.put_chunk(chunk)
        return document, chunks, parser_mode, elapsed
