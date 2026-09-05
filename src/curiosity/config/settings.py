"""Deterministic layered configuration with secret-safe capability reporting."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir, user_data_dir


@dataclass(frozen=True)
class FeatureFlags:
    youtube: bool = False
    embeddings: bool = False
    sqlite_vec: bool = False
    harness: bool = False


@dataclass(frozen=True)
class AppConfig:
    config_path: Path
    data_path: Path
    provider_api_key: str | None = field(default=None, repr=False)
    provider_model: str | None = None
    provider_base_url: str | None = None
    provider_cheap_model: str | None = None
    provider_strong_model: str | None = None
    provider_max_calls: int | None = None
    provider_max_cost: float | None = None
    provider_cache: bool = True
    provider_prices: dict[str, float] = field(default_factory=dict)
    github_token: str | None = field(default=None, repr=False)
    semantic_scholar_api_key: str | None = field(default=None, repr=False)
    youtube_api_key: str | None = field(default=None, repr=False)
    features: FeatureFlags = field(default_factory=FeatureFlags)


def user_config_path() -> Path:
    return Path(user_config_dir("curiosity-engine", appauthor=False)) / "config.toml"


def default_data_path() -> Path:
    return Path(user_data_dir("curiosity-engine", appauthor=False))


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"1", "true", "yes", "on"}:
        return True
    if isinstance(value, str) and value.lower() in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"expected boolean, received {value!r}")


def _file_values(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as config_file:
        values = tomllib.load(config_file)
    if not isinstance(values, dict):
        raise ValueError("config TOML must be a table")
    return values


def load_config(
    *,
    cli: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
    config_path: Path | None = None,
) -> AppConfig:
    """Merge defaults < file < environment < explicit non-None CLI values."""
    cli = cli or {}
    env = env or os.environ
    chosen_config = Path(
        cli.get("config_path") or config_path or env.get("CURIOSITY_CONFIG") or user_config_path()
    )
    file_values = _file_values(chosen_config)
    file_features = file_values.get("features", {})
    if not isinstance(file_features, dict):
        raise ValueError("[features] must be a table")
    data_value = (
        cli.get("data_path")
        or env.get("CURIOSITY_DATA_PATH")
        or file_values.get("data_path")
        or default_data_path()
    )
    feature_values: dict[str, bool] = {}
    for name in ("youtube", "embeddings", "sqlite_vec", "harness"):
        env_value = env.get(f"CURIOSITY_FEATURE_{name.upper()}")
        cli_value = cli.get(f"feature_{name}")
        raw = (
            cli_value
            if cli_value is not None
            else env_value
            if env_value is not None
            else file_features.get(name, False)
        )
        feature_values[name] = _bool(raw)
    key = (
        cli.get("provider_api_key")
        or env.get("CURIOSITY_PROVIDER_API_KEY")
        or file_values.get("provider_api_key")
    )
    provider_model = (
        cli.get("provider_model")
        or env.get("CURIOSITY_PROVIDER_MODEL")
        or file_values.get("provider_model")
    )
    provider_base_url = (
        cli.get("provider_base_url")
        or env.get("CURIOSITY_PROVIDER_BASE_URL")
        or file_values.get("provider_base_url")
    )
    provider_cheap_model = (
        cli.get("provider_cheap_model")
        or env.get("CURIOSITY_PROVIDER_CHEAP_MODEL")
        or file_values.get("provider_cheap_model")
    )
    provider_strong_model = (
        cli.get("provider_strong_model")
        or env.get("CURIOSITY_PROVIDER_STRONG_MODEL")
        or file_values.get("provider_strong_model")
    )
    provider_max_calls_raw = (
        cli.get("provider_max_calls")
        or env.get("CURIOSITY_PROVIDER_MAX_CALLS")
        or file_values.get("provider_max_calls")
    )
    provider_max_cost_raw = (
        cli.get("provider_max_cost")
        or env.get("CURIOSITY_PROVIDER_MAX_COST")
        or file_values.get("provider_max_cost")
    )
    prices_raw = file_values.get("provider_prices", {})
    if not isinstance(prices_raw, dict):
        raise ValueError("[provider_prices] must be a table of per-million-token prices")
    github_token = (
        cli.get("github_token")
        or env.get("CURIOSITY_GITHUB_TOKEN")
        or file_values.get("github_token")
    )
    semantic_scholar_api_key = (
        cli.get("semantic_scholar_api_key")
        or env.get("CURIOSITY_SEMANTIC_SCHOLAR_API_KEY")
        or env.get("CURIOSITY_S2_API_KEY")
        or file_values.get("semantic_scholar_api_key")
    )
    youtube_api_key = (
        cli.get("youtube_api_key")
        or env.get("CURIOSITY_YOUTUBE_API_KEY")
        or file_values.get("youtube_api_key")
    )
    prices = {
        key.lower(): float(value)
        for key, value in prices_raw.items()
        if key.lower() in {"input", "output"}
    }
    return AppConfig(
        chosen_config,
        Path(data_value),
        key,
        provider_model,
        provider_base_url,
        provider_cheap_model,
        provider_strong_model,
        int(provider_max_calls_raw) if provider_max_calls_raw is not None else None,
        float(provider_max_cost_raw) if provider_max_cost_raw is not None else None,
        _bool(
            cli.get("provider_cache")
            if cli.get("provider_cache") is not None
            else env.get("CURIOSITY_PROVIDER_CACHE", "true")
            if "CURIOSITY_PROVIDER_CACHE" in env
            else file_values.get("provider_cache", True)
        ),
        prices,
        github_token,
        semantic_scholar_api_key,
        youtube_api_key,
        FeatureFlags(**feature_values),
    )


def provider_readiness(config: AppConfig) -> tuple[bool, str]:
    """True only when a real provider endpoint can actually be constructed.

    Mirrors the registry's constructibility rule so `doctor` never claims a
    capability that cannot be built. No network probe is performed here.
    """
    if not config.provider_api_key:
        return False, "no provider API key"
    model = config.provider_model or config.provider_cheap_model
    if not model:
        return False, "no provider model configured"
    return True, "configured"


def capability_state(config: AppConfig) -> dict[str, str]:
    ready, reason = provider_readiness(config)
    return {
        "model_generation": "configured" if ready else f"offline fallback ({reason})",
        "youtube": "enabled" if config.features.youtube else "disabled",
        "embeddings": "enabled" if config.features.embeddings else "disabled",
        "sqlite_vec": "enabled" if config.features.sqlite_vec else "disabled",
        "harness": "enabled" if config.features.harness else "disabled",
        "discovery_github": "configured" if config.github_token else "unauthenticated public limits",
        "discovery_papers": "configured"
        if config.semantic_scholar_api_key
        else "unauthenticated shared pool",
        "discovery_youtube": "configured" if config.youtube_api_key else "unconfigured",
    }
