"""Find the `specify` executable, preferring the copy bundled with this tool."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path

OVERRIDE_VARIABLE = "AIDIDIT_SPECIFY"
_EXECUTABLE_NAMES = ("specify.exe", "specify")


def locate_specify(
    *, env: Mapping[str, str], python: Path, which: Callable[[str], str | None]
) -> list[str] | None:
    override = env.get(OVERRIDE_VARIABLE)
    if override:
        return [override]
    bundled = _bundled_next_to(python)
    if bundled:
        return [str(bundled)]
    on_path = which("specify")
    return [on_path] if on_path else None


def _bundled_next_to(python: Path) -> Path | None:
    for name in _EXECUTABLE_NAMES:
        candidate = python.parent / name
        if candidate.is_file():
            return candidate
    return None
