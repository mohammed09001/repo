from pathlib import Path

from curiosity.cli import main
from curiosity.config.capabilities import NoLLMProvider
from curiosity.config.settings import load_config


def test_config_precedence_file_then_env_then_cli(tmp_path: Path):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        'data_path = "file-data"\n[features]\nyoutube = false\nembeddings = true\n'
    )
    env = {"CURIOSITY_DATA_PATH": str(tmp_path / "env-data"), "CURIOSITY_FEATURE_YOUTUBE": "true"}
    config = load_config(
        config_path=config_file,
        env=env,
        cli={"data_path": tmp_path / "cli-data", "feature_youtube": False},
    )
    assert config.data_path == tmp_path / "cli-data"
    assert config.features.youtube is False
    assert config.features.embeddings is True


def test_paths_are_injectable_not_hard_coded_to_user_or_os(tmp_path: Path):
    config = load_config(
        config_path=tmp_path / "settings.toml",
        env={},
        cli={"data_path": tmp_path / "portable-data"},
    )
    assert config.config_path == tmp_path / "settings.toml"
    assert config.data_path == tmp_path / "portable-data"


def test_no_llm_is_deterministic_and_offline():
    provider = NoLLMProvider()
    assert provider.generate("First thought. Second thought.") == "Consider: First thought."


def test_doctor_reports_no_secret_and_starts_without_provider(tmp_path: Path, capsys):
    assert (
        main(
            [
                "doctor",
                "--config",
                str(tmp_path / "config.toml"),
                "--data-path",
                str(tmp_path / "data"),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "offline fallback" in output
    assert "API_KEY" not in output


def test_doctor_cli_flags_override_file_features(tmp_path: Path, capsys):
    config_file = tmp_path / "config.toml"
    config_file.write_text("[features]\nyoutube = false\n")
    assert main(["doctor", "--config", str(config_file), "--youtube"]) == 0
    assert "capability.youtube enabled" in capsys.readouterr().out
