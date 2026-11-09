"""Feature: the README's Quick Start states what the package itself requires.

Acceptance criteria
- Given the Python floor in pyproject.toml, when a reader follows the Quick Start, then the README
  names that same floor before the install command.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
README = (REPO / "README.md").read_text(encoding="utf-8")
PYPROJECT = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))


def _quick_start() -> str:
    start = README.index("## 🚀 Quick Start")
    return README[start : README.index("\n## ", start + 1)]


def test_the_quick_start_names_the_python_floor_before_the_install_command():
    floor = PYPROJECT["project"]["requires-python"].removeprefix(">=")
    section = _quick_start()
    before_install = section[: section.index("uv tool install")]

    assert re.search(rf"Python {re.escape(floor)}\b", before_install), f"name Python {floor} first"
