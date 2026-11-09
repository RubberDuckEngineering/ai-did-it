"""Fail when a commit's author or committer holds a term from the private denylist.

Usage: python -m tools.check_commit_identity --denylist PATH [--range REV] [--repo DIR]

A hit is reported by commit and field only. The output never repeats the term or the identity,
because in a public repository the CI log is as public as the commit.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

EXIT_CLEAN = 0
EXIT_LEAK = 1
EXIT_EMPTY_DENYLIST = 2
FIELD_SEPARATOR = "\x1f"
LOG_FORMAT = FIELD_SEPARATOR.join(["%H", "%an", "%ae", "%cn", "%ce"])
SHORT_SHA = 12


class Identity(NamedTuple):
    sha: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str


FIELDS = {
    "author name": "author_name",
    "author email": "author_email",
    "committer name": "committer_name",
    "committer email": "committer_email",
}


def read_identities(repo: Path, rev_range: str) -> list[Identity]:
    log = subprocess.run(
        ["git", "log", f"--format={LOG_FORMAT}", rev_range, "--"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    return [Identity(*line.split(FIELD_SEPARATOR)) for line in log.splitlines() if line]


def find_leaks(identities: Sequence[Identity], terms: Sequence[str]) -> list[str]:
    leaks = []
    for identity in identities:
        for label, attribute in FIELDS.items():
            value = getattr(identity, attribute).casefold()
            for line, term in enumerate(terms, 1):
                if term and term.casefold() in value:
                    leaks.append(f"{identity.sha[:SHORT_SHA]} {label}: denylist line {line}")
    return leaks


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--denylist", type=Path, required=True, help="one private term per line")
    parser.add_argument("--range", default="HEAD", help="a git revision range (default: all of HEAD)")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    terms = [line.strip() for line in args.denylist.read_text(encoding="utf-8").splitlines()]
    if not any(terms):
        print("the denylist is empty: refusing to pass a check that compared nothing", file=sys.stderr)
        return EXIT_EMPTY_DENYLIST
    identities = read_identities(args.repo, args.range)
    leaks = find_leaks(identities, terms)
    for leak in leaks:
        print(leak, file=sys.stderr)
    noun = "commit" if len(identities) == 1 else "commits"
    print(f"checked {len(identities)} {noun}: {len(leaks)} identity leak(s)")
    return EXIT_LEAK if leaks else EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main())
