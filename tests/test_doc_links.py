"""Every relative link in the human-facing docs resolves: the file exists, and so does the anchor.

Citations point at `docs/sources.md#<id>`, so an anchor check is what keeps a citation honest: a
misspelt or deleted source id fails here instead of rendering as a link to the top of the page.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DOCS = [
    REPO / "README.md",
    REPO / "CONTRIBUTING.md",
    REPO / "SECURITY.md",
    *sorted((REPO / "docs").glob("*.md")),
]
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
ANCHORED_LINK = re.compile(r"\]\(([^)#\s]*\.md)?#([^)\s]+)\)")
EXPLICIT_ANCHOR = re.compile(r"<a id=\"([^\"]+)\"></a>")
HEADING = re.compile(r"^#{1,6} (.+)$", re.M)
FENCED = re.compile(r"^```.*?^```", re.M | re.S)


def _local_targets(doc: Path) -> list[str]:
    return [
        t
        for t in LINK.findall(doc.read_text(encoding="utf-8"))
        if "://" not in t and not t.startswith("mailto:")
    ]


def github_slug(heading: str) -> str:
    """GitHub's heading anchor: lower-case, punctuation and emoji dropped, spaces become hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors_in(doc: Path) -> set[str]:
    text = FENCED.sub("", doc.read_text(encoding="utf-8"))
    return set(EXPLICIT_ANCHOR.findall(text)) | {github_slug(h) for h in HEADING.findall(text)}


@pytest.mark.parametrize("doc", DOCS, ids=lambda d: d.relative_to(REPO).as_posix())
def test_relative_links_resolve(doc):
    broken = [t for t in _local_targets(doc) if not (doc.parent / t).exists()]

    assert broken == []


@pytest.mark.parametrize("doc", DOCS, ids=lambda d: d.relative_to(REPO).as_posix())
def test_anchors_resolve(doc):
    text = FENCED.sub("", doc.read_text(encoding="utf-8"))
    links = [(target or doc.name, fragment) for target, fragment in ANCHORED_LINK.findall(text)]

    broken = [
        f"{target}#{fragment}"
        for target, fragment in links
        if (doc.parent / target).exists() and fragment not in anchors_in(doc.parent / target)
    ]

    assert broken == []


def test_github_slug_matches_githubs_rules():
    assert github_slug("🦆 Ducks in a Row: the Brand Book") == "-ducks-in-a-row-the-brand-book"
    assert github_slug("Assemble — Air Traffic for Agents") == "assemble--air-traffic-for-agents"
