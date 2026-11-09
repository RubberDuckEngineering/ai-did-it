"""The citation verifier (`scripts/verify-quote.py`) is an instrument, so it is tested as one.

Contract: read a page from a URL or a file, reduce it to visible text, normalise case, whitespace,
quotes and dashes, then look for each quote. Every run checks a positive control (a phrase known to
be on the page) and a negative control (a phrase that cannot be). Exit 0 means every quote was
found, exit 3 means at least one is missing, and exit 4 means the instrument failed: a control
missed, the fetch failed, or the verifier itself crashed. A crash is never reported as "missing".
"""

from __future__ import annotations

import importlib.util
import string
import subprocess
import sys
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import ClassVar

import pytest

from aididit._pack import PACK_DIR

SCRIPT = PACK_DIR / "scripts" / "verify-quote.py"
BYLINE = "Kent Beck"
PAGE = """<!doctype html>
<html><head>
<title>Notes</title>
<style>p { color: red; } .hidden-style-phrase { }</style>
<script type="application/ld+json">{"@type": "Article", "author": {"name": "Kent Beck"}}</script>
<script>var hiddenScriptPhrase = "only in a script";</script>
</head><body>
<p class="byline">Posted by <a rel="author" href="/about">Kent Beck</a></p>
<p>Make it work, make it right,
   make it <em>fast</em>.</p>
<p>It\u2019s the \u201csimplest thing\u201d that could possibly work \u2014 nothing more.</p>
<p>Tom&nbsp;&amp;&nbsp;Jerry</p><p>Start of the next paragraph</p>
</body></html>
"""
JSON_LD_ONLY_PAGE = """<html><head>
<script type="application/ld+json">{"author": {"name": "Kent Beck"}}</script>
</head><body><p>Optimism is an occupational hazard of programming.</p></body></html>
"""
# The byline and the article live only in a script's data, as on a page whose text is rendered by
# JavaScript: the visible text is empty, so a quote the verifier misses may still be on the page.
SCRIPT_RENDERED_PAGE = """<html><head><script id="__NEXT_DATA__" type="application/json">
{"props": {"author": "Kent Beck", "body": "Make it work, make it right, make it fast."}}
</script></head><body><div id="root"></div></body></html>
"""
# A curly apostrophe in windows-1252 is the single byte 0x92, which is not valid UTF-8.
LEGACY_APOSTROPHE_PAGE = b"<body><p>Kent Beck: it\x92s the simplest thing</p></body>"
LEGACY_QUOTE = "it's the simplest thing"


def _load() -> ModuleType:
    """Load the hyphenated script under the package's namespace: coverage matches `aididit` by module name."""
    spec = importlib.util.spec_from_file_location("aididit.pack.scripts.verify_quote", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def vq() -> ModuleType:
    return _load()


@pytest.fixture
def page_file(tmp_path: Path) -> Path:
    path = tmp_path / "page.html"
    path.write_text(PAGE, encoding="utf-8")
    return path


def _main(vq: ModuleType, source: Path | str, *quotes: str, control: str = BYLINE) -> int:
    argv = ["--source", str(source), "--control", control]
    for quote in quotes:
        argv += ["--quote", quote]
    return vq.main(argv)


# ── Verdicts ──────────────────────────────────────────────────────────────────────────────────


def test_every_quote_on_the_page_is_found(vq, page_file, capsys):
    code = _main(vq, page_file, "make it work, make it right", "could possibly work")

    assert code == vq.FOUND == 0
    out = capsys.readouterr().out
    assert out.count("QUOTE FOUND") == 2
    assert "VERDICT FOUND" in out


def test_a_quote_that_is_not_on_the_page_is_missing(vq, page_file, capsys):
    code = _main(vq, page_file, "make it work", "make it cheap")

    assert code == vq.MISSING == 3
    out = capsys.readouterr().out
    assert 'QUOTE MISSING "make it cheap"' in out
    assert 'QUOTE FOUND "make it work"' in out
    assert "VERDICT MISSING" in out


def test_a_missed_positive_control_is_an_instrument_failure_even_when_quotes_match(vq, page_file, capsys):
    code = _main(vq, page_file, "make it work", control="Martin Fowler")

    assert code == vq.INSTRUMENT_FAILURE == 4
    out = capsys.readouterr().out
    assert "CONTROL+ MISSED" in out
    assert "VERDICT INSTRUMENT-FAILURE" in out
    assert "QUOTE" not in out


def test_a_matched_negative_control_is_an_instrument_failure(vq):
    nonsense = "zebra quantum marmalade"
    report = vq.check(PAGE + f"<p>{nonsense}</p>", BYLINE, ["make it work"], negative=nonsense)

    assert report.verdict == vq.INSTRUMENT_FAILURE
    assert "negative control" in report.reason


def test_the_negative_control_is_fresh_nonsense_on_every_run(vq):
    first, second = vq.negative_control(), vq.negative_control()

    assert first != second


def test_the_exit_codes_are_distinct_and_none_is_a_crash_code(vq):
    codes = {vq.FOUND, vq.MISSING, vq.INSTRUMENT_FAILURE}

    assert len(codes) == 3
    assert codes.isdisjoint({1, 2}), "1 is Python's uncaught-exception code and 2 is argparse's"


# ── Normalisation ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "quote",
    [
        'It\'s the "simplest thing" that could possibly work - nothing more',
        "it\u2019s the \u201csimplest thing\u201d",
        "IT\u2018S THE \u201cSIMPLEST THING\u201d",
        "possibly work \u2013 nothing more",
    ],
    ids=["straight-quote-curly-page", "curly-quote-curly-page", "single-curly-and-case", "en-dash"],
)
def test_quotes_dashes_and_case_are_normalised(vq, quote):
    assert vq.check(PAGE, BYLINE, [quote]).verdict == vq.FOUND


@pytest.mark.parametrize(
    "quote",
    ["make it work,   make it right, make it fast", "make it work,\nmake it right", "tom & jerry"],
    ids=["runs-of-spaces", "newline", "non-breaking-space-and-entity"],
)
def test_whitespace_is_normalised(vq, quote):
    assert vq.check(PAGE, BYLINE, [quote]).verdict == vq.FOUND


@pytest.mark.parametrize(
    ("variant", "plain"),
    [
        *[(char, "'") for char in "\u2018\u2019\u201a\u201b\u2032"],
        *[(char, '"') for char in "\u201c\u201d\u201e\u201f\u2033"],
        *[(char, "-") for char in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"],
        ("\u00ad", ""),
        ("\ufb01", "fi"),
        ("\u2026", "..."),
    ],
)
def test_each_typographic_variant_folds_to_its_plain_form(vq, variant, plain):
    assert vq.normalise(f"a{variant}b") == f"a{plain}b"


def test_normalise_folds_every_variant_to_one_form(vq):
    assert vq.normalise("  \u201cA\u00a0\u00a0B\u201d\n\u2014\u00adC ") == '"a b" -c'


# ── Tag stripping ─────────────────────────────────────────────────────────────────────────────


def test_inline_markup_does_not_split_a_quote(vq):
    assert vq.check(PAGE, BYLINE, ["make it right, make it fast."]).verdict == vq.FOUND


def test_block_tags_separate_words(vq):
    text = vq.visible_text("<p>Jerry</p><p>Start</p><div>a<br>b</div>")

    assert vq.normalise(text) == "jerry start a b"


BLOCK_TAGS = (
    "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt", "figcaption",
    "figure", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav",
    "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul",
)  # fmt: skip


@pytest.mark.parametrize("tag", BLOCK_TAGS)
def test_every_block_tag_separates_the_words_either_side(vq, tag):
    assert vq.normalise(vq.visible_text(f"end<{tag}>start")) == "end start"
    assert vq.normalise(vq.visible_text(f"end</{tag}>start")) == "end start"


@pytest.mark.parametrize("tag", ["a", "abbr", "b", "code", "em", "i", "mark", "q", "span", "strong"])
def test_an_inline_tag_joins_the_text_either_side(vq, tag):
    assert vq.normalise(vq.visible_text(f"un<{tag}>broken</{tag}>.")) == "unbroken."


def test_a_stray_closing_script_tag_does_not_hide_the_rest_of_the_page(vq):
    assert vq.normalise(vq.visible_text("<p>before</script> after</p>")) == "before after"


def test_script_and_style_are_not_page_text(vq):
    report = vq.check(PAGE, BYLINE, ["only in a script", "hidden-style-phrase"])

    assert report.verdict == vq.MISSING
    assert [found for _, found in report.quotes] == [False, False]


def test_a_json_ld_byline_counts_as_the_positive_control(vq):
    report = vq.check(JSON_LD_ONLY_PAGE, BYLINE, ["occupational hazard"])

    assert report.verdict == vq.FOUND


def test_a_control_found_only_in_markup_cannot_vouch_for_a_missing_quote(vq):
    report = vq.check(SCRIPT_RENDERED_PAGE, BYLINE, ["make it right"])

    assert report.verdict == vq.INSTRUMENT_FAILURE
    assert "only in the markup" in report.reason


# ── Sources ───────────────────────────────────────────────────────────────────────────────────


class _Handler(BaseHTTPRequestHandler):
    routes: ClassVar[dict[str, tuple[int, str, bytes]]] = {
        "/page": (200, "text/html; charset=utf-8", PAGE.encode("utf-8")),
        "/latin": (
            200,
            "text/html; charset=iso-8859-1",
            "<p>Kent Beck: caf\u00e9 cr\u00e8me</p>".encode("latin-1"),
        ),
        "/latin-apostrophe": (200, "text/html; charset=iso-8859-1", LEGACY_APOSTROPHE_PAGE),
        "/paper.pdf": (200, "application/pdf", b"%PDF-1.7\n%binary"),
    }

    def do_GET(self) -> None:
        status, content_type, body = self.routes.get(self.path, (404, "text/plain", b"not found"))
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        """Keep the test output quiet."""


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def test_a_fetched_page_is_verified(vq, server):
    assert _main(vq, f"{server}/page", "simplest thing") == vq.FOUND


def test_the_served_charset_decodes_the_page(vq, server):
    assert _main(vq, f"{server}/latin", "caf\u00e9 cr\u00e8me") == vq.FOUND


def test_a_latin_1_label_decodes_as_windows_1252_the_way_browsers_read_it(vq, server):
    assert _main(vq, f"{server}/latin-apostrophe", LEGACY_QUOTE) == vq.FOUND


@pytest.mark.parametrize(
    "declaration",
    [
        b'<meta charset="windows-1252">',
        b'<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">',
    ],
    ids=["meta-charset", "http-equiv"],
)
def test_a_charset_declared_in_the_page_decodes_a_file(vq, tmp_path, declaration):
    page = tmp_path / "legacy.html"
    page.write_bytes(b"<html><head>" + declaration + b"</head>" + LEGACY_APOSTROPHE_PAGE + b"</html>")

    assert _main(vq, page, LEGACY_QUOTE) == vq.FOUND


def test_undecodable_bytes_cannot_vouch_for_a_missing_quote(vq, tmp_path):
    page = tmp_path / "undeclared.html"
    page.write_bytes(LEGACY_APOSTROPHE_PAGE)

    assert _main(vq, page, LEGACY_QUOTE) == vq.INSTRUMENT_FAILURE
    assert _main(vq, page, "the simplest thing") == vq.FOUND


def test_a_failed_fetch_is_an_instrument_failure_not_a_missing_quote(vq, server, capsys):
    code = _main(vq, f"{server}/gone", "simplest thing")

    assert code == vq.INSTRUMENT_FAILURE
    assert "VERDICT INSTRUMENT-FAILURE" in capsys.readouterr().out


def test_a_refused_connection_is_an_instrument_failure(vq):
    assert _main(vq, "http://127.0.0.1:9/page", "simplest thing") == vq.INSTRUMENT_FAILURE


def test_an_unreadable_file_is_an_instrument_failure(vq, tmp_path):
    assert _main(vq, tmp_path / "absent.html", "simplest thing") == vq.INSTRUMENT_FAILURE


@pytest.mark.parametrize("where", ["file", "url"])
def test_a_pdf_is_an_instrument_failure_because_the_matcher_cannot_read_it(
    vq, server, tmp_path, capsys, where
):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.7\n%binary")
    source = pdf if where == "file" else f"{server}/paper.pdf"

    assert _main(vq, source, "anything") == vq.INSTRUMENT_FAILURE
    assert "PDF" in capsys.readouterr().out


# ── Crash discipline ──────────────────────────────────────────────────────────────────────────


def test_an_unexpected_crash_is_an_instrument_failure_never_missing(vq, page_file, monkeypatch, capsys):
    def explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError("matcher blew up")

    monkeypatch.setattr(vq, "check", explode)

    assert _main(vq, page_file, "make it work") == vq.INSTRUMENT_FAILURE
    assert "matcher blew up" in capsys.readouterr().out


def test_a_quote_is_required(vq, page_file):
    with pytest.raises(SystemExit) as exit_info:
        vq.main(["--source", str(page_file), "--control", BYLINE])

    assert exit_info.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [["--control", "   ", "--quote", "make it work"], ["--control", BYLINE, "--quote", string.whitespace]],
    ids=["blank-control", "blank-quote"],
)
def test_a_blank_phrase_is_a_usage_error_because_it_matches_every_page(vq, page_file, argv):
    with pytest.raises(SystemExit) as exit_info:
        vq.main(["--source", str(page_file), *argv])

    assert exit_info.value.code == 2


def test_a_control_written_with_an_entity_matches_the_decoded_text(vq):
    assert vq.check(PAGE, "Tom & Jerry", ["make it work"]).verdict == vq.FOUND


@pytest.mark.parametrize(
    ("quote", "control", "expected"),
    [
        ("it\u2019s the \u201csimplest thing\u201d", BYLINE, 0),
        ("make it cheap", BYLINE, 3),
        ("make it work", "Martin Fowler", 4),
    ],
    ids=["found", "missing", "instrument-failure"],
)
def test_a_real_process_returns_the_documented_exit_code(page_file, quote, control, expected):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--source", str(page_file), "--control", control, "--quote", quote],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == expected, result.stdout + result.stderr
    assert result.stdout.isascii(), "output must survive a legacy Windows console code page"
