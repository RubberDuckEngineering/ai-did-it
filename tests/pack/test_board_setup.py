"""Feature: the markdown board is ready however the pack was installed.

`aididit install` seeds the starter board, but `specify extension add` (the route the Spec Kit
catalog uses) does not. Every stage reads the board through the adapter, so the adapter's markdown
provider creates a missing board from the starter template the way the github provider creates its
missing labels. The starter board's demo item sits outside the ids a user's items will take.

Acceptance criteria
- Given each board provider, when its section is read, then it states its own Step 0 exactly once.
- Given the markdown provider's Step 0, when it is read, then it copies the starter board from a
  pack path that exists, only when no board is there yet.
- Given the starter board, when a user creates their first item, then it gets `AID-1` and no item
  on the board already has that id.
"""

from __future__ import annotations

import re

import pytest

from aididit._pack import PACK_DIR

ADAPTERS = PACK_DIR / "shared" / "board-adapters.md"
STARTER_BOARD = PACK_DIR / "templates" / "board.md"
STEP_0 = "**Step 0 for this provider:**"
PROVIDERS = ["markdown", "github", "jira"]
RUNTIME_PATH = re.compile(r"\.specify/extensions/aididit/([A-Za-z0-9_./-]+)")
ITEM_ID = re.compile(r"^### AID-(\d+) ", re.M)


def _provider_section(provider: str) -> str:
    text = ADAPTERS.read_text(encoding="utf-8")
    sections = re.split(r"^## (?=\d+\. )", text, flags=re.M)
    matches = [s for s in sections if re.match(rf"\d+\. Provider: {provider}\b", s)]
    assert len(matches) == 1, f"no single section for provider {provider}"
    return matches[0]


@pytest.mark.parametrize("provider", PROVIDERS)
def test_every_board_provider_states_its_step_0(provider):
    assert _provider_section(provider).count(STEP_0) == 1


def test_the_markdown_step_0_seeds_a_missing_board_from_the_starter_template():
    section = _provider_section("markdown")
    assert STEP_0 in section, "the markdown provider has no Step 0"
    step_0 = section[section.index(STEP_0) :].split("\n\n", 1)[0]
    sources = [PACK_DIR / rel for rel in RUNTIME_PATH.findall(step_0)]

    assert STARTER_BOARD in sources, "Step 0 does not copy the starter board"
    assert "never overwrite" in step_0.lower(), "Step 0 may replace an existing board"


def test_a_users_first_item_on_the_starter_board_is_aid_1():
    taken = [int(n) for n in ITEM_ID.findall(STARTER_BOARD.read_text(encoding="utf-8"))]
    next_id = 1 + max(taken, default=0)

    assert next_id == 1
    assert 1 not in taken
