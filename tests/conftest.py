"""Shared test doubles.

The only external dependency the CLI talks to is the `specify` executable, through the
`Runner` port. `RecordingRunner` mirrors the real runner's contract exactly: it receives an
argv list and a working directory and returns an exit code plus captured text. It never
invents behaviour the real `specify` cannot have; scripted exit codes come from the test.
The real contract is exercised end to end in tests/e2e.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from aididit._process import CommandResult

SPECIFY = ["specify"]


@dataclass
class RecordingRunner:
    """Records every invocation; returns a scripted result keyed by the argv prefix."""

    scripted: dict[tuple[str, ...], CommandResult] = field(default_factory=dict)
    calls: list[tuple[tuple[str, ...], Path]] = field(default_factory=list)

    def __call__(self, argv: Sequence[str], cwd: Path, capture: bool = False) -> CommandResult:
        key = tuple(argv)
        self.calls.append((key, cwd))
        for prefix, result in self.scripted.items():
            if key[: len(prefix)] == prefix:
                return result
        return CommandResult(returncode=0)

    def fail_on(self, *prefix: str, returncode: int = 1, stdout: str = "") -> None:
        self.scripted[tuple(prefix)] = CommandResult(returncode=returncode, stdout=stdout)

    @property
    def argvs(self) -> list[tuple[str, ...]]:
        return [argv for argv, _ in self.calls]


@pytest.fixture
def runner() -> RecordingRunner:
    return RecordingRunner()


@pytest.fixture
def messages() -> list[str]:
    return []


@pytest.fixture
def say(messages: list[str]):
    return messages.append


@pytest.fixture
def pack_dir(tmp_path: Path) -> Path:
    """A minimal stand-in pack with the one file the installer reads itself."""
    pack = tmp_path / "pack"
    (pack / "templates").mkdir(parents=True)
    (pack / "templates" / "board.md").write_text("# Board\n\n## Backlog\n", encoding="utf-8")
    (pack / "workflows").mkdir()
    (pack / "workflows" / "aididit-lane.yml").write_text("schema_version: '1.0'\n", encoding="utf-8")
    return pack


@pytest.fixture
def project(tmp_path: Path) -> Path:
    proj = tmp_path / "project"
    proj.mkdir()
    return proj


@pytest.fixture
def speckit_project(project: Path) -> Path:
    (project / ".specify").mkdir()
    return project
