"""Feature: every link into the organisation names a repository that exists under that name.

The repository was renamed. GitHub redirects the old name, but only until someone creates a repo
with it, and the redirect hides the stale link from anyone clicking it. The package metadata, the
extension manifest the Spec Kit catalog reads, the README badges and the issue template all carry
the URL, so the check reads every tracked file rather than a list that would miss the next one.

Acceptance criteria
- Given any tracked file, when it links to a repository in the organisation, then that
  repository is one this project knows by its current name.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ORG_REPO_LINK = re.compile(r"github\.com/RubberDuckEngineering/([A-Za-z0-9_.-]+)")
CURRENT_REPOS = {"ai-did-it"}


def _tracked_files() -> list[Path]:
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, text=True, check=True)
    return [REPO / name for name in listed.stdout.split("\0") if name]


def test_every_organisation_link_names_a_current_repository():
    stale = [
        f"{path.relative_to(REPO).as_posix()}:{line_no}: {name}"
        for path in _tracked_files()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        for name in ORG_REPO_LINK.findall(line)
        if name not in CURRENT_REPOS
    ]

    assert stale == []
