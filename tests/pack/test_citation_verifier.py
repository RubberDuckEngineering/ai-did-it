"""Feature: the panel verifies a quote with one shipped instrument, not an improvised grep.

The dogfood lane found (F-13) that on Windows Git Bash `grep` aborts with exit 134 on minified HTML
and even on plain markdown. The panel's citation check read every non-zero exit as "no match", so
an abort recorded every quote as MISSING. The pack now ships `scripts/verify-quote.py`, and the
panel's citation rules point at it.

Acceptance criteria
- Given a citation to verify, when the orchestrator checks its quotes, then the panel contract names
  the shipped verifier and how to call it.
- Given the verifier's exit code, when it is anything other than found or missing, then the contract
  calls it an instrument failure, never a missing quote.
- Given the exit codes the contract documents, when they are compared with the script, then they
  agree.
- Given a quote missing from a page whose controls passed, when the contract classifies it, then it
  is a finding about the citation, not an instrument failure, however many quotes are missing.
"""

from __future__ import annotations

import importlib.util
import re

from aididit._pack import PACK_DIR

PANEL = "shared/practitioner-panel.md"
PANEL_GUIDE = "shared/panel-guide.md"
VERIFIER = "scripts/verify-quote.py"
INVOCATION = re.compile(
    r"python \.specify/extensions/aididit/scripts/verify-quote\.py --source \S+ --control \S.* --quote "
)
NON_VERDICT_RULE = "any exit other than `0` or `3` is an instrument failure"
MISSING_IS_A_VERDICT = "a missing quote on a page whose controls passed is a finding about the citation"
# The rule the verifier replaced: with grep as the matcher, every quote missing at once meant the
# matcher had failed. With controls that vouch for the text, it more likely means a fabricated quote.
RETIRED_RULE = "every quote missing"


def _section(rel: str, heading: str) -> str:
    """The heading's own section: up to the next heading of the same level."""
    lines = (PACK_DIR / rel).read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(n for n, line in enumerate(lines) if line.rstrip() == heading)
    same_level = heading.split(" ", 1)[0] + " "
    end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith(same_level)), len(lines))
    return "".join(lines[start:end])


def _verifier():
    spec = importlib.util.spec_from_file_location("aididit.pack.scripts.verify_quote", PACK_DIR / VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_panel_verifies_quotes_with_the_shipped_verifier():
    section = _section(PANEL, "## 3. Verifying Citations")

    assert INVOCATION.search(section), "section 3 must show how to call the shipped verifier"


def test_a_non_verdict_exit_is_an_instrument_failure_wherever_the_panel_says_so():
    verifying = _section(PANEL, "## 3. Verifying Citations")
    failure_modes = _section(PANEL, "## 7. Failure Modes")

    assert NON_VERDICT_RULE in verifying.casefold()
    assert re.search(r"verifier exits other than `0` or `3`.*\| instrument failure", failure_modes.casefold())


def test_the_documented_exit_codes_match_the_script():
    section = _section(PANEL, "## 3. Verifying Citations")
    verifier = _verifier()

    for code, name in verifier.VERDICT_NAMES.items():
        assert f"`{code}` is {name}" in section, f"section 3 must document exit {code} as {name}"


def test_the_panel_guide_points_at_the_verifier_instead_of_restating_it():
    step = _section(PANEL_GUIDE, "### Step 6: Verify every citation")

    assert "`verify-quote.py`" in step
    assert "section 3" in step


def test_a_missing_quote_under_passing_controls_is_a_verdict_however_many_are_missing():
    verifying = _section(PANEL, "## 3. Verifying Citations").casefold()
    failure_modes = _section(PANEL, "## 7. Failure Modes").casefold()

    assert MISSING_IS_A_VERDICT in verifying
    assert RETIRED_RULE not in verifying, f"section 3 keeps the retired rule: {RETIRED_RULE}"
    assert RETIRED_RULE not in failure_modes, f"section 7 keeps the retired rule: {RETIRED_RULE}"
