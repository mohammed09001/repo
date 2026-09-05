"""Conservative source identity. Canonical URL first; provider-scoped stable IDs
when directly provided; never merge solely on similar display titles."""

from __future__ import annotations

from curiosity.contracts.models import SourceRecord


def source_identity_key(record: SourceRecord) -> str:
    """Return a namespaced stable identity. Provider IDs are scoped so two
    providers cannot accidentally collapse distinct works."""
    metadata = record.metadata
    if metadata.get("paper_id"):
        return f"paper:{metadata['paper_id']}"
    if metadata.get("full_name"):
        return f"repo:{metadata['full_name']}"
    if metadata.get("video_id"):
        return f"video:{metadata['video_id']}"
    if metadata.get("doi"):
        return f"doi:{metadata['doi']}"
    return f"url:{record.canonical_locator}"