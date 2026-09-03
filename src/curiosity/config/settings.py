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
    return AppConfig(chosen_config, Path(data_value), key, FeatureFlags(**feature_values))


def capability_state(config: AppConfig) -> dict[str, str]:
    return {
        "model_generation": "configured"
        if config.provider_api_key
        else "offline fallback (NoLLMProvider)",
        "youtube": "enabled" if config.features.youtube else "disabled",
        "embeddings": "enabled" if config.features.embeddings else "disabled",
        "sqlite_vec": "enabled" if config.features.sqlite_vec else "disabled",
        "harness": "enabled" if config.features.harness else "disabled",
    }
