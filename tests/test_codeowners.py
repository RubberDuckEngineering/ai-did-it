"""Feature: every change needs an approval from the maintainers team.

The `protect main` ruleset requires a code owner's approval, and CODEOWNERS says who that is. An
owner is always an organization team, never a person or an address: a team keeps the approvers out
of the repository's files, and changing who approves is a team change, not a commit.

Acceptance criteria
- Given CODEOWNERS, when it is read, then a rule for every file (`*`) names the maintainers team.
- Given any rule, when its owners are read, then each is a team of this organization.
"""

from __future__ import annotations

from pathlib import Path

import pytest

CODEOWNERS = Path(__file__).resolve().parents[1] / ".github" / "CODEOWNERS"
ORG = "RubberDuckEngineering"
MAINTAINERS = f"@{ORG}/maintainers"


def _rules() -> list[tuple[str, list[str]]]:
    if not CODEOWNERS.exists():
        return []
    rules = []
    for line in CODEOWNERS.read_text(encoding="utf-8").splitlines():
        fields = line.split("#", 1)[0].split()
        if fields:
            rules.append((fields[0], fields[1:]))
    return rules


def test_every_file_is_owned_by_the_maintainers_team():
    assert ("*", [MAINTAINERS]) in _rules()


@pytest.mark.parametrize(("pattern", "owners"), _rules(), ids=[r[0] for r in _rules()])
def test_every_owner_is_a_team_of_the_organization(pattern, owners):
    assert owners, f"{pattern}: no owner"
    assert [o for o in owners if not o.startswith(f"@{ORG}/")] == [], f"{pattern}: not a team"
