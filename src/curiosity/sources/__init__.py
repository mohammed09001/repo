"""Bounded, policy-safe metadata discovery adapters."""

from .adapters import GitHubAdapter, SemanticScholarAdapter, WebAdapter, YouTubeAdapter
from .http import DiscoveryBudget, DiscoveryError, HttpClient

__all__ = [
    "DiscoveryBudget",
    "DiscoveryError",
    "GitHubAdapter",
    "HttpClient",
    "SemanticScholarAdapter",
    "WebAdapter",
    "YouTubeAdapter",
]
