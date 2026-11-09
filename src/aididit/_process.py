"""The single port to the outside world: running an external command."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class Runner(Protocol):
    def __call__(self, argv: Sequence[str], cwd: Path, capture: bool = False) -> CommandResult: ...


def subprocess_runner(argv: Sequence[str], cwd: Path, capture: bool = False) -> CommandResult:
    """Run argv (never through a shell). Output streams to the terminal unless captured."""
    completed = subprocess.run(list(argv), cwd=cwd, capture_output=capture, text=True, check=False)
    return CommandResult(completed.returncode, completed.stdout or "", completed.stderr or "")
