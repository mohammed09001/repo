from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from html.parser import HTMLParser
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from curiosity.contracts.models import (
    Chunk,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    deterministic_id,
)
from curiosity.store import LocalStore


class IngestError(RuntimeError):
    pass


@dataclass(frozen=True)
class FetchResponse:
    status: int
    body: bytes
    mime_type: str
    etag: str | None = None
    last_modified: str | None = None


class Fetcher(Protocol):
    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse: ...


class UrllibFetcher:
    """Bounded default fetcher for the explicit CLI path; tests inject fixtures instead."""

    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        request = Request(url, headers={"User-Agent": "curiosity-engine/0.1 ingest", **headers})
        try:
            with urlopen(request, timeout=10) as response:  # noqa: S310 - explicit user source URL
                body = response.read(max_bytes + 1)
                mime = response.headers.get_content_type()
                return FetchResponse(
                    response.status,
                    body,
                    mime,
                    response.headers.get("ETag"),
                    response.headers.get("Last-Modified"),
                )
        except HTTPError as error:
            return FetchResponse(error.code, b"", error.headers.get_content_type())
        except URLError as error:
            raise IngestError(f"network error: {error.reason}") from error


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
    parser = _MainText()
    try:
        parser.feed(body.decode("utf-8", errors="strict"))
    except UnicodeDecodeError as exc:
        raise IngestError("HTML is not UTF-8 text") from exc
    text = normalize_text(" ".join(parser.parts))
    if not text:
        raise IngestError("HTML parser found no usable text")
    return text


def parse_document(body: bytes, mime_type: str) -> tuple[str, str]:
    if mime_type in {"text/html", "application/xhtml+xml"}:
        return parse_html(body), "html-fallback-1"
    if mime_type == "text/plain":
        return normalize_text(body.decode("utf-8", errors="strict")), "plain-1"
    if mime_type == "application/pdf":
        try:
            import docling  # type: ignore[import-not-found]  # isolated optional boundary
        except ImportError as exc:
            raise IngestError("PDF requires optional Docling parser") from exc
        raise IngestError(f"Docling integration is not enabled for {docling.__name__}")
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
    ):
        self.store, self.fetcher, self.max_bytes, self.chunk_ceiling = (
            store,
            fetcher,
            max_bytes,
            chunk_ceiling,
        )

    def ingest(self, source: SourceRecord) -> tuple[SourceDocument, list[Chunk], bool]:
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
        response = self.fetcher.fetch(
            source.canonical_locator, headers=headers, max_bytes=self.max_bytes
        )
        if response.status == 304:
            if not cached:
                raise IngestError("304 response without local cache metadata")
            row = self.store.connection.execute(
                "SELECT payload_json FROM documents WHERE content_sha256=?",
                (cached["content_sha256"],),
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
            )
        if response.status != 200:
            raise IngestError(f"fetch failed with HTTP {response.status}")
        if len(response.body) > self.max_bytes:
            raise IngestError("response exceeds byte limit")
        text, parser_version = parse_document(response.body, response.mime_type)
        raw_hash = sha256(response.body).hexdigest()
        normalized_hash = sha256(text.encode()).hexdigest()
        document = SourceDocument(
            id=deterministic_id("document", source.id, normalized_hash),
            source_id=source.id,
            content_sha256=raw_hash,
            raw_text=text,
            captured_at=datetime.now(UTC),
            provenance=ProvenanceClass.SOURCE,
        )
        existing_id = self.store.put_document(document)
        if existing_id != document.id:
            row = self.store.connection.execute(
                "SELECT payload_json FROM documents WHERE id=?", (existing_id,)
            ).fetchone()
            document = SourceDocument.model_validate_json(row["payload_json"])
        chunks = chunk_text(
            document, text, ceiling=self.chunk_ceiling, parser_version=parser_version
        )
        for chunk in chunks:
            self.store.put_chunk(chunk)
        self.store.put_cache(
            cache_key=cache_key,
            content_sha256=document.content_sha256,
            fetched_at=datetime.now(UTC),
            parser_version=parser_version,
            etag=response.etag,
            last_modified=response.last_modified,
            metadata={"raw_sha256": raw_hash, "normalized_sha256": normalized_hash},
        )
        return document, chunks, False
