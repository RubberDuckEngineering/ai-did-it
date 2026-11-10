"""Fail when a commit made as the project carries a UTC offset other than +0000.

Usage: python -m tools.check_commit_timezone [--range REV] [--repo DIR]

A git date keeps the committer's offset, and an offset narrows down where someone lives. Only the
project's own address is held to UTC: a contributor committing as themselves keeps their offset.
A hit names the commit and which date, never the offset.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

PROJECT_EMAIL = "admin@rubberduckengineering.com"
UTC = "+0000"
EXIT_CLEAN = 0
EXIT_LOCAL_TIME = 1
FIELD_SEPARATOR = "\x1f"
LOG_FORMAT = FIELD_SEPARATOR.join(["%H", "%ae", "%ad", "%ce", "%cd"])
SHORT_SHA = 12


class Dated(NamedTuple):
    sha: str
    author_email: str
    author_date: str
    committer_email: str
    committer_date: str


SIDES = {
    "author date": ("author_email", "author_date"),
    "committer date": ("committer_email", "committer_date"),
}


def read_dates(repo: Path, rev_range: str) -> list[Dated]:
    log = subprocess.run(
        ["git", "log", "--date=raw", f"--format={LOG_FORMAT}", rev_range, "--"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    return [Dated(*line.split(FIELD_SEPARATOR)) for line in log.splitlines() if line]


def find_local_times(commits: Sequence[Dated]) -> list[str]:
    hits = []
    for dated in commits:
        for label, (email, date) in SIDES.items():
            if _is_project(getattr(dated, email)) and _offset(getattr(dated, date)) != UTC:
                hits.append(f"{dated.sha[:SHORT_SHA]} {label}: not {UTC}")
    return hits


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--range", default="HEAD", help="a git revision range (default: all of HEAD)")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    commits = read_dates(args.repo, args.range)
    hits = find_local_times(commits)
    for hit in hits:
        print(hit, file=sys.stderr)
    noun = "commit" if len(commits) == 1 else "commits"
    print(f"checked {len(commits)} {noun}: {len(hits)} local time zone(s)")
    return EXIT_LOCAL_TIME if hits else EXIT_CLEAN


def _is_project(email: str) -> bool:
    return email.casefold() == PROJECT_EMAIL


def _offset(raw_date: str) -> str:
    return raw_date.split()[-1]


if __name__ == "__main__":
    raise SystemExit(main())
