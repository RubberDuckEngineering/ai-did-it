"""Feature: the practitioner panel is spent where a judgement is real.

The dogfood lane measured each panel sub-agent at about 59k to 75k tokens, set by its preloaded
context rather than its task. Intent panels ran in four stages and never changed the plan; retro
wording vets cost five sub-agents per link; twenty mostly mechanical review findings took ten
member runs. The rules that fix this live in one place, `panel-guide.md` Part 0, and every stage
that convenes a panel points at the rule it obeys.

Acceptance criteria
- Given the panel guide, when a stage reads it, then it finds each proportionality rule once,
  under a stable id (P1 to P5).
- Given any pointer to a rule in the pack, when it is followed, then the rule exists.
- Given a stage that convenes a panel for intent, leftover findings, retro vets or grooming, when
  it reaches that step, then it cites the rule that decides whether the panel convenes.
- Given the inline runner, when a link hands off, then its prompt references the lane contract by
  path instead of copying it into a session that already has it on disk.
"""

from __future__ import annotations

import re

import pytest

from aididit._pack import PACK_DIR

PANEL_GUIDE = PACK_DIR / "shared" / "panel-guide.md"
RULE_DEFINITION = re.compile(r"^### (P\d+)\. ", re.M)
RULE_POINTER = re.compile(r"`panel-guide\.md` (P\d+)")
RULES = {"P1", "P2", "P3", "P4", "P5"}
PACK_MARKDOWN = sorted(PACK_DIR.rglob("*.md"))

# Each place the dogfood lane spent a panel, and the rule that now decides whether it convenes.
CITATIONS = {
    "stages/draft/speckit.aididit.draft.md": {"P1", "P2", "P4"},
    "stages/iterate/speckit.aididit.iterate.md": {"P1", "P2", "P4"},
    "stages/deliver/speckit.aididit.deliver.md": {"P1", "P2", "P4"},
    "stages/tidy/speckit.aididit.tidy.md": {"P2", "P5"},
    "shared/retro.md": {"P3"},
}


def _text(rel: str) -> str:
    return (PACK_DIR / rel).read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    following = text.find("\n## ", start + len(heading))
    return text[start : following if following != -1 else len(text)]


def test_the_panel_guide_defines_each_proportionality_rule_exactly_once():
    defined = RULE_DEFINITION.findall(PANEL_GUIDE.read_text(encoding="utf-8"))

    assert sorted(defined) == sorted(RULES)


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=lambda p: p.relative_to(PACK_DIR).as_posix())
def test_every_pointer_to_a_rule_resolves(doc):
    pointed = set(RULE_POINTER.findall(doc.read_text(encoding="utf-8")))

    assert pointed - RULES == set()


@pytest.mark.parametrize(("rel", "rules"), sorted(CITATIONS.items()), ids=sorted(CITATIONS))
def test_every_panel_step_cites_the_rule_that_decides_it(rel, rules):
    cited = set(RULE_POINTER.findall(_text(rel)))

    assert rules - cited == set()


def test_the_inline_runner_hands_off_the_contract_by_path():
    inline = _section(_text("shared/lane-runner.md"), "## Mode: `inline`")

    assert "by path" in inline
    assert "lane contract inline" not in inline
