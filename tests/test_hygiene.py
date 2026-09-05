"""Repository hygiene: runtime verification artifacts must never be committed."""

from pathlib import Path
from subprocess import check_output

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_gitignore_covers_runtime_database_artifacts():
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    for required in (".cli-verification/", "*.db-wal", "*.db-shm"):
        assert required in gitignore, f".gitignore must contain {required!r}"


def test_no_personal_runtime_database_is_tracked():
    if not (REPO / ".git").exists():
        pytest.skip("repository metadata is absent")
    tracked = check_output(["git", "ls-files"], cwd=REPO, text=True).splitlines()
    offenders = [
        path
        for path in tracked
        if path.endswith("curiosity.db")
        or (path.startswith(".cli-verification/") and path.endswith((".db", ".db-wal", ".db-shm")))
    ]
    assert not offenders, f"runtime databases are tracked: {offenders}"