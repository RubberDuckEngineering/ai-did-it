"""Every Mermaid diagram wears the house style, and the house style reads on every GitHub theme.

The house style is defined once: the first diagram in docs/brand.md. Its init line and its
classDefs are the canonical header. Every other diagram must copy the init line exactly and may only
use classDefs from that set, so a colour change happens in one place and these tests re-measure it.

"Light and dark safe" is a measured claim, not a vibe. Contrast is computed with the WCAG 2.2
relative-luminance formula against each GitHub page background:
- text on its own fill needs 4.5:1 (SC 1.4.3, contrast minimum);
- a node, line or group needs 3:1 against the page (SC 1.4.11, non-text contrast), from its fill or
  from its stroke, because a dark fill with a bright outline is visible on both themes.

"Fits on GitHub" is measured too. GitHub draws each diagram in a frame as wide as the page column
and shrinks a wider one to fit, text and all. On 2026-11-11 that drew 21 of 34 diagrams small on a
1280 px screen, the README's at 39% of its size, too small to read. The width test renders every
diagram with the Mermaid build and settings GitHub's viewer uses and checks its natural width
against the column. It needs a browser, so it is skipped without one unless
AIDIDIT_REQUIRE_DIAGRAMS=1, which CI sets on the one leg that runs it.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BRAND_DOC = REPO / "docs" / "brand.md"
STAGE_GUIDE = REPO / "docs" / "stages.md"
STAGES_DIR = REPO / "src" / "aididit" / "pack" / "stages"
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "build", "htmlcov"}

# Page backgrounds from GitHub's Primer design tokens (bgColor.default): light is white, dark is
# dark neutral.1, dark dimmed is neutral.3. Pure black bounds the high-contrast dark themes.
PAGES = {
    "GitHub light": "#FFFFFF",
    "GitHub dark": "#0D1117",
    "GitHub dark dimmed": "#212830",
    "pure black": "#000000",
}
TEXT_MIN = 4.5
GRAPHIC_MIN = 3.0

# GitHub's diagram viewer (viewscreen.githubusercontent.com, read 2026-11-11) bundles Mermaid 12.2.0
# and calls mermaid.initialize with these settings. The integrity hash pins the exact file.
MERMAID_JS = "https://cdn.jsdelivr.net/npm/mermaid@12.2.0/dist/mermaid.min.js"
MERMAID_SRI = "sha256-qKam+AWwdKgmGiglyG+ZyAVKyzs19Qu34kpPnyw8O58="
GITHUB_MERMAID_CONFIG = {
    "startOnLoad": False,
    "securityLevel": "antiscript",
    "flowchart": {"diagramPadding": 48},
    "theme": "default",
}
# The narrowest desktop column a diagram appears in: the README on the repository's home page, which
# GitHub draws 838 px wide at every window from 1280 px up. A docs page's column is 861 px or wider.
GITHUB_COLUMN = 838

FENCE = re.compile(r"^```mermaid\n(.*?)^```", re.M | re.S)
INIT = re.compile(r"^%%\{init: (.*)\}%%$")
CLASSDEF = re.compile(r"^\s*classDef (\S+) (\S+)\s*$")
USED_CLASS = re.compile(r":::([A-Za-z]\w*)|^\s*class \S+ ([A-Za-z]\w*)\s*$", re.M)
AD_HOC_STYLE = re.compile(r"^\s*(style|linkStyle)\s", re.M)


def _markdown_files() -> list[Path]:
    return sorted(
        p for p in REPO.rglob("*.md") if not any(part in SKIP_DIRS for part in p.relative_to(REPO).parts)
    )


def _diagrams(path: Path) -> list[str]:
    return FENCE.findall(path.read_text(encoding="utf-8"))


DIAGRAMS = [
    (f"{path.relative_to(REPO).as_posix()}#{n}", body)
    for path in _markdown_files()
    for n, body in enumerate(_diagrams(path), 1)
]
IDS = [ident for ident, _ in DIAGRAMS]


def _house() -> tuple[str, dict, dict[str, str]]:
    first = _diagrams(BRAND_DOC)[0]
    init_line = first.splitlines()[0]
    theme = json.loads(INIT.match(init_line).group(1))["themeVariables"]
    class_defs = {m.group(1): m.group(2) for m in map(CLASSDEF.match, first.splitlines()) if m}
    return init_line, theme, class_defs


def _style(spec: str) -> dict[str, str]:
    return dict(part.split(":", 1) for part in spec.split(","))


def _luminance(hex_colour: str) -> float:
    channels = [int(hex_colour.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_contrast_matches_the_wcag_reference_values():
    assert round(contrast("#000000", "#FFFFFF"), 2) == 21.0
    assert round(contrast("#777777", "#FFFFFF"), 2) == 4.48


def test_the_brand_doc_defines_the_house_style():
    init_line, theme, class_defs = _house()

    assert init_line.startswith('%%{init: {"theme": "base"')
    assert theme["edgeLabelBackground"]
    assert {"duck", "link", "gate", "human", "panel", "stop", "ok", "note", "persona"} <= set(class_defs)


@pytest.mark.parametrize(("ident", "body"), DIAGRAMS, ids=IDS)
def test_every_diagram_starts_with_the_house_init_line(ident, body):
    init_line, _, _ = _house()

    assert body.splitlines()[0] == init_line


@pytest.mark.parametrize(("ident", "body"), DIAGRAMS, ids=IDS)
def test_every_diagram_is_a_flowchart(ident, body):
    """Contrast is proven for flowchart nodes, edges, labels and groups. Other diagram types float
    text straight on the page (sequence messages, state transitions), which no single colour can
    make readable on both themes."""
    assert body.splitlines()[1].startswith("flowchart ")


@pytest.mark.parametrize(("ident", "body"), DIAGRAMS, ids=IDS)
def test_every_class_def_comes_from_the_house_palette(ident, body):
    _, _, house = _house()
    defined = {m.group(1): m.group(2) for m in map(CLASSDEF.match, body.splitlines()) if m}

    off_palette = {name: spec for name, spec in defined.items() if house.get(name) != spec}

    assert off_palette == {}


@pytest.mark.parametrize(("ident", "body"), DIAGRAMS, ids=IDS)
def test_every_class_a_diagram_uses_is_defined_in_it(ident, body):
    defined = {m.group(1) for m in map(CLASSDEF.match, body.splitlines()) if m}
    used = {a or b for a, b in USED_CLASS.findall(body)}

    assert used - defined == set()


@pytest.mark.parametrize(("ident", "body"), DIAGRAMS, ids=IDS)
def test_no_diagram_paints_with_ad_hoc_styles(ident, body):
    assert AD_HOC_STYLE.findall(body) == []


def test_house_text_is_readable_on_every_class():
    _, _, house = _house()

    weak = {
        name: round(contrast(style["fill"], style["color"]), 2)
        for name, style in ((n, _style(s)) for n, s in house.items())
        if contrast(style["fill"], style["color"]) < TEXT_MIN
    }

    assert weak == {}


@pytest.mark.parametrize("page", PAGES)
def test_house_nodes_stand_out_on_every_github_theme(page):
    _, _, house = _house()
    background = PAGES[page]

    invisible = [
        name
        for name, style in ((n, _style(s)) for n, s in house.items())
        if max(contrast(style["fill"], background), contrast(style["stroke"], background)) < GRAPHIC_MIN
    ]

    assert invisible == []


@pytest.mark.parametrize("page", PAGES)
def test_house_lines_labels_and_groups_read_on_every_github_theme(page):
    _, theme, _ = _house()
    background = PAGES[page]

    assert contrast(theme["lineColor"], background) >= GRAPHIC_MIN
    assert contrast(theme["edgeLabelBackground"], theme["textColor"]) >= TEXT_MIN
    assert contrast(theme["primaryColor"], theme["primaryTextColor"]) >= TEXT_MIN
    assert contrast(theme["clusterBkg"], theme["titleColor"]) >= TEXT_MIN
    assert max(contrast(theme["clusterBkg"], background), contrast(theme["clusterBorder"], background)) >= (
        GRAPHIC_MIN
    )


def _unavailable(reason: str):
    if os.environ.get("AIDIDIT_REQUIRE_DIAGRAMS") == "1":
        pytest.fail(f"AIDIDIT_REQUIRE_DIAGRAMS=1 but {reason}")
    pytest.skip(reason)


@pytest.fixture(scope="module")
def mermaid():
    """A browser page holding GitHub's Mermaid build, initialised the way GitHub initialises it.

    Edge is the browser because Windows ships it and the fonts GitHub's diagrams ask for, so the text
    is measured in the font a reader sees rather than a fallback."""
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError:
        _unavailable("Playwright is not installed: run `uv run --group diagrams pytest -m diagrams`")
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="msedge")
        except Error as error:
            _unavailable(f"Microsoft Edge could not start: {error.message.splitlines()[0]}")
        page = browser.new_page()
        script = f'<script src="{MERMAID_JS}" integrity="{MERMAID_SRI}" crossorigin="anonymous"></script>'
        page.set_content(f'<div id="drawing"></div>{script}', wait_until="load")
        page.evaluate("config => mermaid.initialize(config)", GITHUB_MERMAID_CONFIG)
        yield page
        browser.close()


def _natural_width(page, ident: str, body: str) -> float:
    return page.evaluate(
        """async ([id, source]) => {
            const drawing = document.getElementById("drawing");
            drawing.innerHTML = (await mermaid.render(id, source)).svg;
            return drawing.querySelector("svg").viewBox.baseVal.width;
        }""",
        [re.sub(r"\W", "-", ident), body],
    )


@pytest.mark.diagrams
@pytest.mark.parametrize(("ident", "body"), DIAGRAMS, ids=IDS)
def test_every_diagram_fits_the_github_column_without_shrinking(mermaid, ident, body):
    width = _natural_width(mermaid, ident, body)

    assert width <= GITHUB_COLUMN, f"{ident} is {width:.0f} px wide; GitHub shrinks it, text and all"


@pytest.mark.parametrize("stage", sorted(p.name for p in STAGES_DIR.iterdir() if p.is_dir()))
def test_every_stage_has_a_flow_in_the_stage_guide(stage):
    sections = STAGE_GUIDE.read_text(encoding="utf-8").split("\n## ")[1:]
    section = next((s for s in sections if stage in s.splitlines()[0].lower()), "")

    assert "```mermaid" in section
