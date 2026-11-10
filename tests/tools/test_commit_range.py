"""Feature: CI judges each commit once, when it arrives.

The identity and time-zone checks read the commits a CI run is about. A pull request is about the
commits between its base and its head. A push is about the commits it pushed, not all of history:
a commit already on `main` was judged when it landed, and a maintainer who accepted it should not
see every later push turn red for it.

Acceptance criteria
- Given a pull request event, when the range is read, then it runs from the base to the head.
- Given a push event, when the range is read, then it runs from the commit before the push to the
  commit after it.
- Given a push that created the branch (no commit before it), when the range is read, then it is
  everything reachable from the pushed commit.
- Given a commit already on the branch, when a later push is checked, then that commit is not read.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.tools.git_history import commit, git
from tools import check_commit_timezone
from tools.check_commit_timezone import PROJECT_EMAIL
from tools.commit_range import NO_COMMIT, main, range_for

BEFORE = "a" * 40
AFTER = "b" * 40
PROJECT = ("Rubber Duck Engineering", PROJECT_EMAIL)
EASTERN = "2026-11-10T07:00:00-0500"


def test_a_pull_request_runs_from_its_base_to_its_head():
    event = {"pull_request": {"base": {"sha": BEFORE}, "head": {"sha": AFTER}}}

    assert range_for("pull_request", event) == f"{BEFORE}..{AFTER}"


def test_a_push_runs_from_before_it_to_after_it():
    assert range_for("push", {"before": BEFORE, "after": AFTER}) == f"{BEFORE}..{AFTER}"


def test_a_push_that_creates_the_branch_runs_over_everything_it_reaches():
    assert range_for("push", {"before": NO_COMMIT, "after": AFTER}) == AFTER


def test_main_prints_the_range_of_the_event_file(tmp_path, capsys):
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps({"before": BEFORE, "after": AFTER}), encoding="utf-8")

    assert main(["--event-name", "push", "--event-path", str(event_path)]) == 0
    assert capsys.readouterr().out == f"{BEFORE}..{AFTER}\n"


@pytest.fixture
def repo(tmp_path) -> Path:
    git(tmp_path, "init", "-q")
    return tmp_path


def test_a_commit_already_on_the_branch_is_not_judged_again(repo):
    accepted = commit(repo, "fix: accepted", author=PROJECT, committer=PROJECT, author_date=EASTERN)
    pushed = commit(repo, "fix: pushed", author=PROJECT, committer=PROJECT)
    pushed_range = range_for("push", {"before": accepted, "after": pushed})

    assert check_commit_timezone.main(["--range", "HEAD", "--repo", str(repo)]) == 1
    assert check_commit_timezone.main(["--range", pushed_range, "--repo", str(repo)]) == 0
