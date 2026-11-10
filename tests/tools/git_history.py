"""Build throwaway git histories for the maintainer-tool tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

CLEAN = ("Rubber Duck Engineering", "maintainers@example.com")
UTC_NOON = "2026-11-10T12:00:00+0000"


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
    ).stdout.strip()


def commit(
    repo: Path,
    message: str,
    author: tuple[str, str] = CLEAN,
    committer: tuple[str, str] = CLEAN,
    author_date: str = UTC_NOON,
    committer_date: str = UTC_NOON,
) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": author[0],
        "GIT_AUTHOR_EMAIL": author[1],
        "GIT_AUTHOR_DATE": author_date,
        "GIT_COMMITTER_NAME": committer[0],
        "GIT_COMMITTER_EMAIL": committer[1],
        "GIT_COMMITTER_DATE": committer_date,
    }
    git(repo, "commit", "--allow-empty", "--no-gpg-sign", "-q", "-m", message, env=env)
    return git(repo, "rev-parse", "HEAD")
