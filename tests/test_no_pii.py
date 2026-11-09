"""Nothing in this repository may identify a person or a private system.

Two layers:
1. Generic patterns that hold for every contributor: email addresses, home-directory paths,
   hosted-tracker URLs and real-looking ticket keys.
2. An optional private denylist. Point AIDIDIT_PII_DENYLIST at a file outside the repo with one
   term per line (names, handles, private project names). The terms never enter the repo; the
   test reads them at run time. Without the variable the second layer is skipped.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()  # holds the patterns themselves; reviewed by hand
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build", "htmlcov"}
SKIP_FILES = {"uv.lock", ".coverage"}
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".toml", ".sh", ".ps1", ".json", ".txt", ".cfg", ".svg", ""}

ALLOWED_EMAIL_DOMAINS = ("example.com", "example.org")
PROJECT_CONTACTS = {"admin@rubberduckengineering.com"}  # the project's published contact, not a person
ALLOWED_KEY_PREFIXES = {
    "AID",
    "PROJ",
    "AC",  # this pack's own example ids and acceptance-criterion ids
    "SHA",
    "UTF",
    "ISO",
    "CVE",
    "CWE",
    "RFC",
    "TLS",
    "ASVS",
    "OWASP",
    "ADR",
    "UTC",
    "GMT",
    "PEP",
    "PDF",  # a PDF file header, e.g. %PDF-1.7
}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
HOME_PATH = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z]|/(?:Users|home)/[a-z][a-z0-9_-]+/", re.I)
TRACKER_URL = re.compile(r"[a-z0-9-]+\.atlassian\.net", re.I)
TICKET_KEY = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-\d+\b")


def _repo_files() -> list[Path]:
    files = []
    for path in REPO.rglob("*"):
        rel = path.relative_to(REPO)
        if any(part in SKIP_DIRS for part in rel.parts) or not path.is_file():
            continue
        if path.name in SKIP_FILES or path.suffix not in TEXT_SUFFIXES or path == SELF:
            continue
        files.append(path)
    return files


FILES = _repo_files()


def _email_allowed(address: str) -> bool:
    address = address.lower()
    return address in PROJECT_CONTACTS or address.endswith(ALLOWED_EMAIL_DOMAINS)


def _hits(pattern: re.Pattern[str], allowed) -> list[str]:
    found = []
    for path in FILES:
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for match in pattern.finditer(line):
                if not allowed(match):
                    found.append(f"{path.relative_to(REPO).as_posix()}:{number}: {match.group(0)}")
    return found


def test_scan_covers_the_pack_and_the_code():
    names = {p.relative_to(REPO).as_posix() for p in FILES}

    assert "src/aididit/pack/extension.yml" in names
    assert "src/aididit/cli.py" in names
    assert "docs/assets/banner.svg" in names


def test_no_email_addresses():
    assert _hits(EMAIL, lambda m: _email_allowed(m.group(0))) == []


@pytest.mark.parametrize(
    ("address", "allowed"),
    [
        ("someone@example.com", True),
        ("ADMIN@RubberDuckEngineering.com", True),
        ("someone.else@rubberduckengineering.com", False),
        ("admin@rubberduckengineering.com.evil.net", False),
    ],
)
def test_only_example_domains_and_the_project_contact_are_allowed(address, allowed):
    assert _email_allowed(address) is allowed


def test_no_home_directory_paths():
    assert _hits(HOME_PATH, lambda m: False) == []


def test_no_hosted_tracker_urls():
    assert _hits(TRACKER_URL, lambda m: False) == []


def test_no_real_looking_ticket_keys():
    assert _hits(TICKET_KEY, lambda m: m.group(1) in ALLOWED_KEY_PREFIXES) == []


def test_private_denylist_terms_are_absent():
    denylist = os.environ.get("AIDIDIT_PII_DENYLIST")
    if not denylist:
        pytest.skip("set AIDIDIT_PII_DENYLIST to a private term list to run this check")
    terms = [t.strip().lower() for t in Path(denylist).read_text(encoding="utf-8").splitlines() if t.strip()]
    pattern = re.compile("|".join(re.escape(t) for t in terms), re.I)

    assert _hits(pattern, lambda m: False) == []
