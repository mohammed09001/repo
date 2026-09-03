"""Official-API and explicit-seed discovery adapters; no document parsing or LLM use."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.etree import ElementTree

from curiosity.contracts.models import (
    ProvenanceClass,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)

from .http import DiscoveryError, HttpClient


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("only absolute http(s) URLs are valid source seeds")
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith(("utm_", "fbclid", "gclid"))
    ]
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", urlencode(query), "")
    )


def _source(
    *,
    kind: SourceType,
    locator: str,
    title: str,
    metadata: dict[str, str],
    trust: TrustClass = TrustClass.REMOTE_UNTRUSTED,
) -> SourceRecord:
    return SourceRecord(
        id=deterministic_id("source", locator),
        source_type=kind,
        canonical_locator=locator,
        title=title or locator,
        trust=trust,
        provenance=ProvenanceClass.SOURCE,
        retrieved_at=datetime.now(UTC),
        metadata=metadata,
    )


class SourceAdapter(Protocol):
    def search(self, query: str, *, limit: int = 10) -> list[SourceRecord]: ...

    def metadata(self, locator: str) -> SourceRecord: ...


class GitHubAdapter:
    base_url = "https://api.github.com"

    def __init__(self, client: HttpClient, token: str | None = None):
        self.client, self.token = client, token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def search(self, query: str, *, limit: int = 10) -> list[SourceRecord]:
        payload, response_headers = self.client.get_json(
            f"{self.base_url}/search/repositories?q={query}&per_page={min(limit, 100)}",
            headers=self._headers(),
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise DiscoveryError("GitHub search payload lacks items", transient=False)
        return [
            self._repository(item, response_headers)
            for item in payload["items"]
            if isinstance(item, dict)
        ]

    def metadata(self, locator: str) -> SourceRecord:
        canonical = canonicalize_url(locator)
        path = urlsplit(canonical).path.strip("/")
        payload, headers = self.client.get_json(
            f"{self.base_url}/repos/{path}", headers=self._headers()
        )
        if not isinstance(payload, dict):
            raise DiscoveryError("GitHub metadata payload is not an object", transient=False)
        return self._repository(payload, headers)

    def _repository(
        self, item: dict[str, Any], headers: dict[str, str] | None = None
    ) -> SourceRecord:
        locator = canonicalize_url(str(item.get("html_url", "")))
        headers = headers or {}
        metadata = {
            "adapter": "github",
            "full_name": str(item.get("full_name", "")),
            "description": str(item.get("description") or ""),
            "default_branch": str(item.get("default_branch") or ""),
            "etag": str(headers.get("ETag", "")),
            "last_modified": str(headers.get("Last-Modified", "")),
            "rate_remaining": str(headers.get("X-RateLimit-Remaining", "")),
            "rate_resource": str(headers.get("X-RateLimit-Resource", "")),
        }
        return _source(
            kind=SourceType.WEB,
            locator=locator,
            title=metadata["full_name"] or locator,
            metadata=metadata,
        )


class SemanticScholarAdapter:
    base_url = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, client: HttpClient):
        self.client = client

    def search(self, query: str, *, limit: int = 10) -> list[SourceRecord]:
        fields = "paperId,title,abstract,url,year,venue"
        payload, _ = self.client.get_json(
            f"{self.base_url}/paper/search?query={query}&limit={min(limit, 100)}&fields={fields}"
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise DiscoveryError("Semantic Scholar search payload lacks data", transient=False)
        return [self._paper(item) for item in payload["data"] if isinstance(item, dict)]

    def metadata(self, locator: str) -> SourceRecord:
        paper_id = locator.rsplit("/", 1)[-1]
        payload, _ = self.client.get_json(
            f"{self.base_url}/paper/{paper_id}?fields=paperId,title,abstract,url,year,venue"
        )
        if not isinstance(payload, dict):
            raise DiscoveryError("Semantic Scholar paper payload is not an object", transient=False)
        return self._paper(payload)

    def _paper(self, item: dict[str, Any]) -> SourceRecord:
        paper_id = str(item.get("paperId", ""))
        if not paper_id:
            raise DiscoveryError("Semantic Scholar paper lacks paperId", transient=False)
        locator = str(item.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}")
        abstract = item.get("abstract")
        return _source(
            kind=SourceType.ARTICLE,
            locator=canonicalize_url(locator),
            title=str(item.get("title") or paper_id),
            metadata={
                "adapter": "semantic_scholar",
                "paper_id": paper_id,
                "year": str(item.get("year") or ""),
                "venue": str(item.get("venue") or ""),
                "abstract_available": "true" if isinstance(abstract, str) and abstract else "false",
            },
        )

    def batch_metadata(self, paper_ids: list[str]) -> list[SourceRecord]:
        if not paper_ids or len(paper_ids) > 100:
            raise ValueError("batch must contain 1..100 paper IDs")
        # The official batch endpoint is POST; callers can inject a matching transport when enabled.
        return [self.metadata(paper_id) for paper_id in paper_ids]


class WebAdapter:
    def explicit_url(self, url: str, *, title: str | None = None) -> SourceRecord:
        locator = canonicalize_url(url)
        return _source(
            kind=SourceType.WEB,
            locator=locator,
            title=title or locator,
            metadata={"adapter": "explicit_url", "content_fetched": "false"},
        )

    def feed(self, xml: bytes, *, feed_url: str) -> list[SourceRecord]:
        try:
            root = ElementTree.fromstring(xml)
        except ElementTree.ParseError as exc:
            raise DiscoveryError("malformed RSS/Atom feed", transient=False) from exc
        records: list[SourceRecord] = []
        for entry in root.findall(".//item") + root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        ):
            link = entry.findtext("link") or ""
            atom_link = entry.find("{http://www.w3.org/2005/Atom}link")
            if atom_link is not None:
                link = atom_link.attrib.get("href", link)
            if not link:
                continue
            try:
                locator = canonicalize_url(link)
            except ValueError:
                continue
            title = (
                entry.findtext("title")
                or entry.findtext("{http://www.w3.org/2005/Atom}title")
                or locator
            )
            records.append(
                _source(
                    kind=SourceType.WEB,
                    locator=locator,
                    title=title,
                    metadata={
                        "adapter": "feed",
                        "feed_url": canonicalize_url(feed_url),
                        "content_fetched": "false",
                    },
                )
            )
        return records


class YouTubeAdapter:
    base_url = "https://www.googleapis.com/youtube/v3"

    def __init__(self, client: HttpClient, api_key: str | None = None):
        self.client, self.api_key = client, api_key

    def _key(self) -> str:
        if not self.api_key:
            raise DiscoveryError(
                "YouTube metadata capability is unavailable: no API key", transient=False
            )
        return self.api_key

    def search(self, query: str, *, limit: int = 10) -> list[SourceRecord]:
        payload, _ = self.client.get_json(
            f"{self.base_url}/search?part=snippet&type=video&q={query}&maxResults={min(limit, 50)}&key={self._key()}"
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise DiscoveryError("YouTube search payload lacks items", transient=False)
        return [self._video(item) for item in payload["items"] if isinstance(item, dict)]

    def metadata(self, locator: str) -> SourceRecord:
        video_id = urlsplit(locator).query.removeprefix("v=") or locator.rsplit("/", 1)[-1]
        payload, _ = self.client.get_json(
            f"{self.base_url}/videos?part=snippet&id={video_id}&key={self._key()}"
        )
        if not isinstance(payload, dict) or not payload.get("items"):
            raise DiscoveryError("YouTube video metadata is unavailable", transient=False)
        return self._video(payload["items"][0])

    def _video(self, item: dict[str, Any]) -> SourceRecord:
        video_id = str(
            item.get("id")
            if isinstance(item.get("id"), str)
            else item.get("id", {}).get("videoId", "")
        )
        if not video_id:
            raise DiscoveryError("YouTube result lacks video ID", transient=False)
        snippet = item.get("snippet", {}) if isinstance(item.get("snippet"), dict) else {}
        return _source(
            kind=SourceType.VIDEO,
            locator=f"https://www.youtube.com/watch?v={video_id}",
            title=str(snippet.get("title") or video_id),
            metadata={
                "adapter": "youtube",
                "video_id": video_id,
                "channel_id": str(snippet.get("channelId") or ""),
                "caption_capability": "authorization_required",
                "transcript_downloaded": "false",
            },
        )
