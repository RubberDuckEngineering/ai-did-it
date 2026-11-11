"""Feature: CI runs only the action code a reviewer saw.

A tag such as `@v4` can be moved to new code after review; a commit SHA cannot. Pinning every
`uses:` to a full SHA, with the release named in a comment, means a workflow change is the only way
the code CI runs can change, and the comment tells the next reader which release to compare against.

Acceptance criteria
- Given any step in any workflow that uses an action, when it is read, then it names a full
  40-character commit SHA followed by a `# vX.Y.Z` release comment.
- Given an action used in several places, when the workflows are read, then every use names the
  same commit, so no job is left behind on an old release.
- Given the identity job, when it is read, then it asks `tools.commit_range` for the commits the
  event brought before it runs either check, so a push is judged on what it pushed, not all history.
- Given the test job, when it is read, then exactly one leg of its matrix measures every diagram in
  a browser, with the measurement required, so a missing browser fails the build instead of
  skipping the width check.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
USES = re.compile(r"^\s*-?\s*uses:\s*(?P<ref>\S+)(?P<rest>.*)$")
PINNED = re.compile(r"^(?P<action>[\w.-]+/[\w./-]+)@(?P<sha>[0-9a-f]{40})$")
RELEASE_COMMENT = re.compile(r"^\s+# v\d+\.\d+\.\d+$")


def _uses() -> list[tuple[str, str, str]]:
    found = []
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        for number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
            if match := USES.match(line):
                found.append((f"{workflow.name}:{number}", match["ref"], match["rest"]))
    return found


ALL_USES = _uses()


def test_the_workflows_use_actions_at_all():
    assert {where.split(":")[0] for where, _, _ in ALL_USES} == {"ci.yml", "release.yml", "security.yml"}


@pytest.mark.parametrize(("where", "ref", "rest"), ALL_USES, ids=[u[0] for u in ALL_USES])
def test_every_action_is_pinned_to_a_commit_with_its_release_named(where, ref, rest):
    assert PINNED.match(ref), f"{where}: {ref} is not pinned to a full commit SHA"
    assert RELEASE_COMMENT.match(rest), f"{where}: no `# vX.Y.Z` comment names the release"


def test_one_action_runs_the_same_commit_everywhere():
    commits = defaultdict(set)
    for _, ref, _ in ALL_USES:
        action, _, version = ref.partition("@")
        commits[action].add(version)

    assert {action: refs for action, refs in commits.items() if len(refs) > 1} == {}


def test_the_identity_job_checks_only_the_commits_the_event_brought():
    ci = yaml.safe_load((WORKFLOWS / "ci.yml").read_text(encoding="utf-8"))
    identity = ci["jobs"]["identity"]
    runs = [step.get("run", "") for step in identity["steps"]]
    reads_range = [i for i, run in enumerate(runs) if "python -m tools.commit_range" in run]
    checks = [i for i, run in enumerate(runs) if '--range "$RANGE"' in run]

    assert "RANGE" not in identity.get("env", {}), "the job still sets its own range"
    assert len(reads_range) == 1, "no step asks tools.commit_range for the range"
    assert len(checks) == 2, "both checks read the range"
    assert all(reads_range[0] < check for check in checks), "the range is read after a check ran"


def test_one_test_leg_measures_every_diagram_and_cannot_skip():
    ci = yaml.safe_load((WORKFLOWS / "ci.yml").read_text(encoding="utf-8"))
    test = ci["jobs"]["test"]
    measuring = [step for step in test["steps"] if "-m diagrams" in step.get("run", "")]

    assert len(measuring) == 1, "no step, or more than one, measures the diagrams"
    step = measuring[0]
    assert "--group diagrams" in step["run"], "the step runs without Playwright installed"
    assert step.get("env", {}).get("AIDIDIT_REQUIRE_DIAGRAMS") == "1", "a missing browser would skip"
    assert step["if"] == "matrix.os == 'windows-latest' && matrix.python == '3.13'"
    assert "windows-latest" in test["strategy"]["matrix"]["os"], "the measuring leg left the matrix"
    assert "3.13" in test["strategy"]["matrix"]["python"], "the measuring leg left the matrix"
