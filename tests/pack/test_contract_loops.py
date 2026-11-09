"""Feature: the lane contract closes its loops.

The dogfood lane found five rules that left a loop open. Tidy filed fifteen pack fixes that no
lane was allowed to make (F-39). A human's "merged" could start Investigate on an open PR (F-36).
Nobody owned committing the markdown board, so a lane committed it (F-26), which widened the lane's
allowed paths with no rule for doing so (F-22). With no branch protection, "every required check"
held for an empty set (F-08). Each rule is now defined once in the lane contract under a named term,
and every passage that relies on it points there.

Acceptance criteria
- Given the lane contract, when a stage points at one of its terms, then the term is defined in the
  section the pointer names.
- Given a learning that would change the installed pack, when Tidy files it, then it is drafted for
  the pack's own repository instead of the project's board.
- Given a human says "merged", when the orchestrator reads it, then it checks the host before starting
  Investigate, and never reads `merge_commit_sha` as proof.
- Given any clean-tree gate, when the board or the lane ledger has changes, then the gate ignores
  them, and lanes never commit the board.
- Given Draft's tasks need a path outside the kickoff's allowed paths, when Draft hands off, then
  the widening is checked against sibling lanes and recorded.
- Given a repository with no required checks, when a stage asks whether the required checks are
  green, then every check that ran on the PR head counts.
"""

from __future__ import annotations

import re

import pytest
import yaml

from aididit._pack import PACK_DIR

CONTRACT = "shared/lane-contract.md"
MERGED_MESSAGE = '"merged <item-ref>"'
PACK_MARKDOWN = sorted(PACK_DIR.rglob("*.md"))

# Each term the contract defines, and the section that defines it.
TERMS = {
    "merge check": 1,
    "runtime state": 2,
    "upstream route": 6,
    "widening allowed paths": 6,
    "required checks": 7,
}
POINTER = re.compile(r"(?i)(" + "|".join(TERMS) + r") \(`lane-contract\.md` §(\d)\)")

# Each place a dogfood finding was traced to, and the terms it must now point at.
CITATIONS = {
    "personas/pr-prep/speckit.aididit.pr-prep.md": {"required checks"},
    "shared/lifecycle.md": {"merge check"},
    "shared/retro.md": {"upstream route"},
    "stages/assemble/speckit.aididit.assemble.md": {"merge check", "required checks", "upstream route"},
    "stages/deliver/speckit.aididit.deliver.md": {"merge check", "required checks"},
    "stages/draft/speckit.aididit.draft.md": {"widening allowed paths"},
    "stages/investigate/speckit.aididit.investigate.md": {"merge check"},
    "stages/tidy/speckit.aididit.tidy.md": {"merge check", "upstream route"},
}

# Every clean-tree gate in the pack, by the words that open it.
CLEAN_TREE_GATES = [
    (CONTRACT, "**Clean tree.**"),
    ("shared/pipeline-guide.md", "**Clean tree before every handoff.**"),
    ("shared/lifecycle.md", "**Commit before handoff.**"),
    ("shared/board-adapters.md", "**The adapter does not commit.**"),
    ("stages/assemble/speckit.aididit.assemble.md", "`git status --short` is clean in the primary checkout"),
    ("stages/draft/speckit.aididit.draft.md", "**0.1 Clean tree.**"),
    ("stages/draft/speckit.aididit.draft.md", "**Clean tree gate.**"),
    ("stages/iterate/speckit.aididit.iterate.md", "**Clean tree gate.**"),
    ("stages/deliver/speckit.aididit.deliver.md", "**Clean-tree rule.**"),
    ("stages/deliver/speckit.aididit.deliver.md", "**Clean tree gate.**"),
    ("stages/investigate/speckit.aididit.investigate.md", "**Pre-handoff gate:**"),
    ("stages/tidy/speckit.aididit.tidy.md", "**Pre-completion gate:**"),
]


def _text(rel: str) -> str:
    return (PACK_DIR / rel).read_text(encoding="utf-8")


def _rel(path) -> str:
    return path.relative_to(PACK_DIR).as_posix()


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    following = text.find("\n## ", start + len(heading))
    return text[start : following if following != -1 else len(text)]


def _contract_section(number: int) -> str:
    return _section(_text(CONTRACT), f"\n## {number}. ")


def _item(text: str, opening: str) -> str:
    """The paragraph or list item that starts with `opening`, with its nested items, up to the next
    blank line or the next item at the same depth or shallower."""
    start = text.index(opening)
    prefix = text[text.rfind("\n", 0, start) + 1 : start]
    depth = len(prefix) - len(prefix.lstrip(" "))
    item_end = re.compile(rf"\n(?:[ \t]*\n| {{0,{depth}}}(?:[-*]|\d+\.) )")
    following = item_end.search(text, start + len(opening))
    return text[start : following.start() if following else len(text)]


def _definition(term: str) -> str:
    return _item(_contract_section(TERMS[term]), f"**{term.capitalize()}.**")


@pytest.mark.parametrize("term", sorted(TERMS))
def test_the_contract_defines_each_term_in_the_section_its_pointers_name(term):
    assert f"**{term.capitalize()}.**" in _contract_section(TERMS[term])


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_pointer_to_a_contract_term_names_its_section(doc):
    wrong = [(term, int(section)) for term, section in POINTER.findall(doc.read_text(encoding="utf-8"))]

    assert [(t, s) for t, s in wrong if TERMS[t.lower()] != s] == []


@pytest.mark.parametrize(("rel", "terms"), sorted(CITATIONS.items()), ids=sorted(CITATIONS))
def test_every_traced_passage_points_at_the_term_that_closes_its_loop(rel, terms):
    cited = {term.lower() for term, _ in POINTER.findall(_text(rel))}

    assert terms - cited == set()


def test_pack_changes_go_upstream_and_project_files_go_to_a_claimed_lane():
    route = _definition("upstream route")
    manifest = yaml.safe_load(_text("extension.yml"))

    assert ".specify/aididit/lanes/<lane-id>/upstream.md" in route
    assert "`repository`" in route and manifest["extension"]["repository"].startswith("https://")
    assert "allowed paths" in route


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_no_rule_leaves_a_pack_change_to_a_later_lane(doc):
    assert "a later lane applies it" not in doc.read_text(encoding="utf-8")


def test_the_merge_check_reads_the_host_not_the_message():
    check = _definition("merge check")

    assert "gh pr view <n> --json state,mergedAt" in check
    assert "`merge_commit_sha`" in check


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_merged_message_goes_through_the_merge_check(doc):
    lines = doc.read_text(encoding="utf-8").splitlines()

    unchecked = [line for line in lines if MERGED_MESSAGE in line and "merge check" not in line.lower()]

    assert unchecked == []


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_merge_commit_sha_is_never_read_as_proof(doc):
    lines = doc.read_text(encoding="utf-8").splitlines()

    assert [line for line in lines if "merge_commit_sha" in line and "never" not in line.lower()] == []


@pytest.mark.parametrize(("rel", "opening"), CLEAN_TREE_GATES, ids=[f"{r}:{o}" for r, o in CLEAN_TREE_GATES])
def test_every_clean_tree_gate_ignores_runtime_state(rel, opening):
    assert "runtime state" in _item(_text(rel), opening)


def test_lanes_never_commit_the_board_and_one_owner_does():
    state = _definition("runtime state")

    assert "Lanes never commit" in state
    assert "human" in state


def test_a_widening_is_checked_against_sibling_lanes_before_handoff():
    rule = _definition("widening allowed paths")
    handoff = _section(_text("stages/draft/speckit.aididit.draft.md"), "## Step N+1")
    resume = _section(_text("stages/assemble/speckit.aididit.assemble.md"), "## Orchestrator resume file")

    assert "`tasks.md`" in rule and "ORCHESTRATOR-RESUME.md" in rule
    assert "`tasks.md`" in handoff
    assert "allowed paths" in _item(resume, "2. **Lane table:**")


def test_required_checks_are_never_an_empty_set():
    assert "every check that ran on the PR head" in _definition("required checks")
