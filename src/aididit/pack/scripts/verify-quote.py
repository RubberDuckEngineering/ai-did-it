"""Verify that quoted strings appear on a cited page. Standard library only, any OS.

Usage:
    python verify-quote.py --source <url-or-file> --control "<byline phrase>" --quote "<text>" [--quote ...]

The page is reduced to visible text (tags, scripts and styles removed), then case, whitespace,
curly quotes and dashes are normalised before a substring check. Every run checks a positive
control (a phrase known to be on the page, such as the byline) and a negative control (fresh
nonsense that cannot be on it). The positive control may also match the raw page, so a JSON-LD
byline counts. A missing quote is only reported as MISSING when the control was found in the
visible text and every byte of the page decoded; otherwise the controls cannot vouch for the text
the quote was looked for in.

Exit codes:
    0  FOUND               every quote is on the page
    3  MISSING             at least one quote is not on the page, and the controls vouch for its text
    4  INSTRUMENT-FAILURE  a control failed, the source could not be read, the verifier crashed, or
                           a quote is missing from text the controls cannot vouch for

Anything other than 0 or 3 is an instrument failure, never a missing quote.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
import uuid
from collections.abc import Sequence
from html.parser import HTMLParser
from pathlib import Path
from typing import NamedTuple

FOUND = 0
MISSING = 3
INSTRUMENT_FAILURE = 4
VERDICT_NAMES = {FOUND: "FOUND", MISSING: "MISSING", INSTRUMENT_FAILURE: "INSTRUMENT-FAILURE"}

FETCH_TIMEOUT_SECONDS = 30
USER_AGENT = "aididit-verify-quote/1.0"
PDF_MAGIC = b"%PDF-"
DEFAULT_CHARSET = "utf-8"
REPLACEMENT_CHARACTER = "�"
# Browsers read a charset declared in the page's first 1024 bytes when the server sends none.
CHARSET_SNIFF_BYTES = 1024
META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?([\w.:-]+)""", re.IGNORECASE)
# The labels browsers decode as windows-1252, from https://encoding.spec.whatwg.org/encodings.json.
# Python's latin-1 would turn the curly quotes these pages carry (bytes 0x91-0x94) into controls.
WINDOWS_1252_LABELS = frozenset(
    {
        "ansi_x3.4-1968", "ascii", "cp1252", "cp819", "csisolatin1", "ibm819", "iso-8859-1",
        "iso-ir-100", "iso8859-1", "iso88591", "iso_8859-1", "iso_8859-1:1987", "l1", "latin1",
        "us-ascii", "windows-1252", "x-cp1252",
    }
)  # fmt: skip
CHARACTER_FOLDS = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u2032": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u2033": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2212": "-",
        "\u00ad": None,
    }
)
WHITESPACE = re.compile(r"\s+")
HIDDEN_TAGS = frozenset({"script", "style"})
BLOCK_TAGS = frozenset(
    {
        "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt", "figcaption",
        "figure", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav",
        "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul",
    }
)  # fmt: skip


class InstrumentFailure(Exception):
    """The page could not be read in a form the matcher can trust."""


class Report(NamedTuple):
    verdict: int
    reason: str
    control: tuple[str, bool]
    negative: tuple[str, bool]
    quotes: list[tuple[str, bool]]


def normalise(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text.translate(CHARACTER_FOLDS))
    return WHITESPACE.sub(" ", folded).strip().casefold()


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in HIDDEN_TAGS:
            self.hidden_depth += 1
        elif tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in HIDDEN_TAGS:
            self.hidden_depth = max(0, self.hidden_depth - 1)
        elif tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.parts.append(data)


def visible_text(page: str) -> str:
    parser = _VisibleText()
    parser.feed(page)
    parser.close()
    return "".join(parser.parts)


def negative_control() -> str:
    return f"qzxv {uuid.uuid4().hex} wombat"


def check(page: str, control: str, quotes: Sequence[str], negative: str | None = None) -> Report:
    text = normalise(visible_text(page))
    raw = normalise(page)
    negative = negative or negative_control()
    controls = (control, _on_page(control, text, raw)), (negative, _on_page(negative, text, raw))
    failures = []
    if not controls[0][1]:
        failures.append("positive control missed")
    if controls[1][1]:
        failures.append("negative control matched")
    if failures:
        return Report(INSTRUMENT_FAILURE, "; ".join(failures), *controls, [])
    results = [(quote, normalise(quote) in text) for quote in quotes]
    if all(found for _, found in results):
        return Report(FOUND, "every quote is on the page", *controls, results)
    blind_spot = _blind_spot(control, text)
    if blind_spot:
        return Report(INSTRUMENT_FAILURE, blind_spot, *controls, results)
    return Report(MISSING, "at least one quote is not on the page", *controls, results)


def _on_page(phrase: str, text: str, raw: str) -> bool:
    needle = normalise(phrase)
    return needle in text or needle in raw


def _blind_spot(control: str, text: str) -> str:
    """Why the controls cannot vouch for the text a quote was missing from, or "" when they can."""
    if normalise(control) not in text:
        return "positive control found only in the markup: the page text may be rendered by script"
    if REPLACEMENT_CHARACTER in text:
        return "the page has bytes its declared charset could not decode"
    return ""


def _decode(body: bytes, charset: str | None, source: str) -> str:
    if body.startswith(PDF_MAGIC):
        raise InstrumentFailure(f"{source} is a PDF: extract its text to a file and verify that file")
    label = (charset or _declared_charset(body) or DEFAULT_CHARSET).strip().lower()
    return body.decode("cp1252" if label in WINDOWS_1252_LABELS else label, errors="replace")


def _declared_charset(body: bytes) -> str | None:
    declared = META_CHARSET.search(body[:CHARSET_SNIFF_BYTES])
    return declared.group(1).decode("ascii") if declared else None


def load(source: str) -> str:
    try:
        if source.startswith(("http://", "https://")):
            request = urllib.request.Request(source, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
                return _decode(response.read(), response.headers.get_content_charset(), source)
        return _decode(Path(source).read_bytes(), None, source)
    except OSError as error:  # URLError and HTTPError are both OSError
        raise InstrumentFailure(f"could not read {source}: {error}") from error


def _phrase(value: str) -> str:
    if not normalise(value):
        raise argparse.ArgumentTypeError("a blank phrase matches every page, so it proves nothing")
    return value


def _parse(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify quoted strings against a cited page.")
    parser.add_argument("--source", required=True, help="URL or file path of the cited page")
    parser.add_argument(
        "--control", required=True, type=_phrase, help="a phrase known to be on the page, e.g. the byline"
    )
    parser.add_argument(
        "--quote", required=True, type=_phrase, action="append", help="a quoted string; repeat for more"
    )
    return parser.parse_args(argv)


def _print_report(report: Report) -> None:
    (control, control_found), (negative, negative_found) = report.control, report.negative
    print(f"CONTROL+ {'FOUND' if control_found else 'MISSED'} {json.dumps(control)}")
    print(f"CONTROL- {'MATCHED' if negative_found else 'ABSENT'} {json.dumps(negative)}")
    for quote, found in report.quotes:
        print(f"QUOTE {'FOUND' if found else 'MISSING'} {json.dumps(quote)}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse(argv)
    try:
        report = check(load(args.source), args.control, args.quote)
    except Exception as error:  # an instrument that crashed has measured nothing
        print(f"VERDICT INSTRUMENT-FAILURE {json.dumps(f'{type(error).__name__}: {error}')}")
        return INSTRUMENT_FAILURE
    _print_report(report)
    print(f"VERDICT {VERDICT_NAMES[report.verdict]} {json.dumps(report.reason)}")
    return report.verdict


if __name__ == "__main__":
    sys.exit(main())
