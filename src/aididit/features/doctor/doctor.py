"""Check that this machine can run the full A·I·DID·IT loop, and say what is missing."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from aididit._exit import EXIT_OK, EXIT_STEP_FAILED
from aididit._pack import SPECKIT_INSTALL_HINT

MINIMUM_PYTHON = (3, 11)


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    required: bool
    detail: str

    def line(self) -> str:
        status = "ok" if self.ok else ("MISSING" if self.required else "optional")
        return f"{status:<8} {self.name:<8} {self.detail}"


def run_doctor(
    *,
    which: Callable[[str], str | None],
    specify: list[str] | None,
    python_version: tuple[int, int],
    say: Callable[[str], None],
) -> int:
    checks = [
        Check(
            "python",
            python_version >= MINIMUM_PYTHON,
            True,
            f"{python_version[0]}.{python_version[1]} (need >= {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]})",
        ),
        Check(
            "specify",
            specify is not None,
            True,
            specify[0] if specify else f"Spec Kit not found - {SPECKIT_INSTALL_HINT}",
        ),
        _tool(which, "git", True, "branches, commits and lanes need git"),
        _tool(which, "gh", False, "needed for the GitHub board provider and for opening and reviewing PRs"),
        _tool(which, "claude", False, "needed only for the claude / claude-remote lane runners"),
    ]
    for check in checks:
        say(check.line())
    return EXIT_OK if all(c.ok for c in checks if c.required) else EXIT_STEP_FAILED


def _tool(which: Callable[[str], str | None], name: str, required: bool, purpose: str) -> Check:
    location = which(name)
    return Check(name, location is not None, required, location or purpose)
