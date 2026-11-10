"""Feature: no commit carries a name or address from the maintainers' private denylist.

A commit's author and committer travel with it forever, outside every file a content scan reads. The
check compares those four fields against a private term list held outside the repo (in CI, an
Actions secret), and it reports a hit by commit and field only: the log of a public repo must not
print the very term it is protecting.

Acceptance criteria
- Given commits whose identities hold no denylist term, when the check runs, then it passes.
- Given a denylist term in any of author name, author email, committer name or committer email, in
  any letter case, when the check runs, then it fails and names the commit and the field.
- Given a hit, when it is reported, then neither the term nor the identity appears in the output.
- Given an empty denylist, when the check runs, then it refuses to pass.
- Given a revision range, when the check runs, then only commits in that range are read.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.tools.git_history import CLEAN, commit, git
from tools.check_commit_identity import Identity, find_leaks, main, read_identities

TERMS = ["zanzibar quokka", "wombat-77"]  # made up; never a real person


@pytest.fixture
def repo(tmp_path) -> Path:
    git(tmp_path, "init", "-q")
    return tmp_path


@pytest.fixture
def denylist(tmp_path) -> Path:
    path = tmp_path.parent / f"{tmp_path.name}-denylist.txt"
    path.write_text("\n".join(TERMS) + "\n\n", encoding="utf-8")
    return path


def test_identities_without_a_denylist_term_pass(repo):
    commit(repo, "feat: one")
    commit(repo, "fix: two")

    assert find_leaks(read_identities(repo, "HEAD"), TERMS) == []


@pytest.mark.parametrize(
    ("field", "author", "committer"),
    [
        ("author name", ("Zanzibar Quokka", CLEAN[1]), CLEAN),
        ("author email", (CLEAN[0], "ZANZIBAR QUOKKA@example.com"), CLEAN),
        ("committer name", CLEAN, ("dev Wombat-77", CLEAN[1])),
        ("committer email", CLEAN, (CLEAN[0], "wombat-77@users.noreply.example.com")),
    ],
)
def test_a_denylist_term_in_any_identity_field_is_a_leak(repo, field, author, committer):
    commit(repo, "feat: clean")
    sha = commit(repo, "fix: leaky", author=author, committer=committer)

    leaks = find_leaks(read_identities(repo, "HEAD"), TERMS)

    assert len(leaks) == 1
    assert leaks[0].startswith(f"{sha[:12]} {field}: denylist line ")


def test_a_leak_names_the_denylist_line_without_echoing_the_term(repo, denylist, capsys):
    commit(repo, "fix: leaky", author=("Wombat-77", CLEAN[1]))

    code = main(["--repo", str(repo), "--denylist", str(denylist), "--range", "HEAD"])
    printed = capsys.readouterr()
    output = (printed.out + printed.err).lower()

    assert code == 1
    assert "denylist line 2" in output
    assert not [term for term in TERMS if term in output]


def test_a_clean_history_passes_through_main(repo, denylist, capsys):
    commit(repo, "feat: clean")

    assert main(["--repo", str(repo), "--denylist", str(denylist), "--range", "HEAD"]) == 0
    assert "1 commit" in capsys.readouterr().out


def test_an_empty_denylist_refuses_to_pass(repo, tmp_path, capsys):
    commit(repo, "feat: clean")
    empty = tmp_path.parent / f"{tmp_path.name}-empty.txt"
    empty.write_text("\n  \n", encoding="utf-8")

    assert main(["--repo", str(repo), "--denylist", str(empty), "--range", "HEAD"]) == 2
    assert "empty" in capsys.readouterr().err


def test_only_commits_in_the_range_are_read(repo):
    commit(repo, "fix: leaky, before the range", author=("Zanzibar Quokka", CLEAN[1]))
    base = commit(repo, "feat: base")
    head = commit(repo, "feat: inside the range")

    identities = read_identities(repo, f"{base}..{head}")

    assert [i.sha for i in identities] == [head]
    assert find_leaks(identities, TERMS) == []


def test_an_identity_holds_all_four_fields(repo):
    commit(repo, "feat: one", author=("A Name", "a@example.com"), committer=("C Name", "c@example.com"))

    (identity,) = read_identities(repo, "HEAD")

    assert identity == Identity(identity.sha, "A Name", "a@example.com", "C Name", "c@example.com")
