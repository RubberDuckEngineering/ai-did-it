"""Feature: a rule the pack repeats lives in one place.

The dogfood lane found rules stated more than once, with the copies disagreeing. Secret
handling said "refuse", "redact" and "reference by context" in three files (F-04). Decision records
had three shapes, one with a date where Draft demanded a timestamp (F-12), and Ideate pointed at the
wrong file for the format (F-07). The retro commit subject named the item in one file and the feature
in another (F-30). Deliver refreshed the PR body after every commit while pr-prep said at most once
(F-31). Each rule now has one home, and every other mention points there.

Acceptance criteria
- Given text a stage is about to write, when it is scanned for secrets, then one rule decides: one
  list of credential shapes, one redaction marker, refuse only when redaction fails.
- Given a decision to record, when a stage records it, then it uses the one format, with a UTC
  timestamp rather than a date.
- Given a retro commit, when any stage names its subject, then the subject has one shape.
- Given a commit on the PR branch, when Deliver refreshes the body, then it follows pr-prep's rule for
  body edits.
"""

from __future__ import annotations

import re

import pytest

from aididit._pack import PACK_DIR

SECRET_RULE = "shared/disciplines/prompt-crafting.md"
SECRET_POINTER = re.compile(r"(?i)secret scan \(`disciplines/prompt-crafting\.md`\)")
SECRET_SCANS = [
    "shared/board-adapters.md",
    "shared/lane-contract.md",
    "shared/lane-runner.md",
    "shared/retro.md",
    "stages/assemble/speckit.aididit.assemble.md",
    "stages/ideate/speckit.aididit.ideate.md",
    "stages/investigate/speckit.aididit.investigate.md",
]
# The stages and shared guides write text. The code-review personas audit code for secrets, which is
# a different job, so they keep their own patterns.
WRITING_MARKDOWN = sorted([*PACK_DIR.glob("shared/**/*.md"), *PACK_DIR.glob("stages/**/*.md")])

DECISION_FORMAT = "shared/practitioner-panel.md"
DECISION_POINTER = re.compile(r"decision-record format \(`practitioner-panel\.md` section 8\)")
DECISION_RECORDERS = [
    "shared/panel-guide.md",
    "shared/pipeline-guide.md",
    "stages/deliver/speckit.aididit.deliver.md",
    "stages/draft/speckit.aididit.draft.md",
    "stages/ideate/speckit.aididit.ideate.md",
]

RETRO_SUBJECT = re.compile(r"chore\(retro\):[^`\"\n]*")
RETRO_STAGES = "<stage>|ideate|draft|iterate|deliver"
CANONICAL_RETRO_SUBJECT = re.compile(rf"chore\(retro\): ({RETRO_STAGES})-stage retro for <item-ref>")

PACK_MARKDOWN = sorted(PACK_DIR.rglob("*.md"))


def _text(rel: str) -> str:
    return (PACK_DIR / rel).read_text(encoding="utf-8")


def _rel(path) -> str:
    return path.relative_to(PACK_DIR).as_posix()


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    following = text.find("\n## ", start + len(heading))
    return text[start : following if following != -1 else len(text)]


def _fenced_after(text: str, heading: str) -> str:
    """The first fenced block after `heading`; a template's own `##` lines stay inside it."""
    opening = text.index("```", text.index(heading))
    return text[opening : text.index("\n```", opening + 3)]


def test_credential_shapes_are_listed_once():
    listing = [_rel(doc) for doc in WRITING_MARKDOWN if "AKIA" in doc.read_text(encoding="utf-8")]

    assert listing == [SECRET_RULE]


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_one_redaction_marker(doc):
    assert "REDACTED" not in doc.read_text(encoding="utf-8")


def test_the_secret_rule_redacts_first_and_refuses_only_when_that_fails():
    rule = _section(_text(SECRET_RULE), "## Secret scan")

    assert "<redacted:{kind}>" in rule
    assert "refuse to write" in rule.lower()


@pytest.mark.parametrize("rel", SECRET_SCANS)
def test_every_secret_scan_points_at_the_one_rule(rel):
    assert SECRET_POINTER.search(_text(rel))


def test_the_decision_record_carries_a_timestamp_not_a_date():
    record = _fenced_after(_text(DECISION_FORMAT), "### Decision record")

    assert "**Recorded:**" in record and "date -u" in record
    assert "**Date:**" not in record


@pytest.mark.parametrize("rel", DECISION_RECORDERS)
def test_every_decision_recorder_points_at_the_one_format(rel):
    assert DECISION_POINTER.search(_text(rel))


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_retro_commit_subject_has_the_one_shape(doc):
    subjects = RETRO_SUBJECT.findall(doc.read_text(encoding="utf-8"))
    named = [s for s in subjects if s.strip() != "chore(retro):"]

    assert [s for s in named if not CANONICAL_RETRO_SUBJECT.fullmatch(s.strip())] == []


def test_deliver_refreshes_the_body_by_pr_preps_rule():
    rule = _section(_text("stages/deliver/speckit.aididit.deliver.md"), "## Standing Rule")

    assert "**PR body edits**" in rule
    assert "**PR body edits.**" in _text("personas/pr-prep/speckit.aididit.pr-prep.md")
    assert "after every commit" not in rule.lower()
