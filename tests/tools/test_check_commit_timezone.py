"""Feature: a commit made as the project is dated in UTC.

Every git date carries the committer's UTC offset, and an offset narrows down where someone lives.
Commits made under the project's address are dated `+0000`, so the history says when, never where.
A contributor committing as themselves keeps their own offset: it is theirs to share.

Acceptance criteria
- Given project commits dated `+0000`, when the check runs, then it passes.
- Given a project author or committer whose date carries another offset, when the check runs, then
  it fails and names the commit and which date.
- Given a commit whose author and committer are someone else, when the check runs, then their
  offsets are left alone.
- Given a hit, when it is reported, then the offset itself is not printed.
- Given a revision range, when the check runs, then only commits in that range are read.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.tools.git_history import CLEAN, commit, git
from tools.check_commit_timezone import PROJECT_EMAIL, find_local_times, main, read_dates

PROJECT = ("Rubber Duck Engineering", PROJECT_EMAIL)
EASTERN = "2026-11-10T07:00:00-0500"
INDIA = "2026-11-10T17:30:00+0530"


@pytest.fixture
def repo(tmp_path) -> Path:
    git(tmp_path, "init", "-q")
    return tmp_path


def test_project_commits_dated_in_utc_pass(repo):
    commit(repo, "feat: one", author=PROJECT, committer=PROJECT)
    commit(repo, "fix: two", author=PROJECT, committer=PROJECT)

    assert find_local_times(read_dates(repo, "HEAD")) == []


@pytest.mark.parametrize(
    ("which", "dates"),
    [
        ("author date", {"author_date": EASTERN}),
        ("committer date", {"committer_date": INDIA}),
    ],
)
def test_a_project_date_with_a_local_offset_is_a_leak(repo, which, dates):
    commit(repo, "feat: clean", author=PROJECT, committer=PROJECT)
    sha = commit(repo, "fix: local", author=PROJECT, committer=PROJECT, **dates)

    assert find_local_times(read_dates(repo, "HEAD")) == [f"{sha[:12]} {which}: not +0000"]


def test_only_the_project_side_of_a_commit_is_held_to_utc(repo):
    commit(repo, "fix: theirs, ours", author=CLEAN, committer=PROJECT, author_date=EASTERN)
    sha = commit(repo, "fix: ours, theirs", author=PROJECT, committer=CLEAN, author_date=EASTERN)

    assert find_local_times(read_dates(repo, "HEAD")) == [f"{sha[:12]} author date: not +0000"]


def test_a_contributor_keeps_their_own_time_zone(repo):
    commit(repo, "feat: theirs", author_date=EASTERN, committer_date=INDIA)

    assert find_local_times(read_dates(repo, "HEAD")) == []


def test_the_project_address_matches_in_any_letter_case(repo):
    shouting = (PROJECT[0], PROJECT_EMAIL.upper())
    commit(repo, "fix: local", author=shouting, committer=shouting, author_date=EASTERN)

    assert len(find_local_times(read_dates(repo, "HEAD"))) == 1


def test_a_hit_fails_without_printing_the_offset(repo, capsys):
    commit(repo, "fix: local", author=PROJECT, committer=PROJECT, committer_date=EASTERN)

    code = main(["--repo", str(repo), "--range", "HEAD"])
    printed = capsys.readouterr()
    output = printed.out + printed.err

    assert code == 1
    assert "committer date" in output
    assert "0500" not in output


def test_a_clean_history_passes_through_main(repo, capsys):
    commit(repo, "feat: clean", author=PROJECT, committer=PROJECT)

    assert main(["--repo", str(repo), "--range", "HEAD"]) == 0
    assert "checked 1 commit: 0 local time zone(s)" in capsys.readouterr().out


def test_only_commits_in_the_range_are_read(repo):
    commit(repo, "fix: local, before the range", author=PROJECT, author_date=EASTERN)
    base = commit(repo, "feat: base", author=PROJECT, committer=PROJECT)
    head = commit(repo, "feat: inside the range", author=PROJECT, committer=PROJECT)

    dates = read_dates(repo, f"{base}..{head}")

    assert [d.sha for d in dates] == [head]
    assert find_local_times(dates) == []
