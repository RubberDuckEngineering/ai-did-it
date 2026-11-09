"""The lane spawn scripts (bash and PowerShell) honour one shared interface.

Contract: validate inputs (exit 2) → dry-run prints exactly one `DRY-RUN:` line and creates
nothing → a real spawn needs the claude binary (exit 3 when absent) → on success prints
`SPAWNED lane=… link=… pid=… log=…` and starts the process detached with the prompt as one argv
element.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from aididit._pack import PACK_DIR

BASH_SCRIPT = PACK_DIR / "scripts" / "bash" / "spawn-lane.sh"
PWSH_SCRIPT = PACK_DIR / "scripts" / "powershell" / "spawn-lane.ps1"
BASH = shutil.which("bash")
PWSH = shutil.which("pwsh")
TRICKY_PROMPT = 'Handoff: lane "a" said \\"hi\\" & $(rm -rf /) ; `echo pwned`'


def _bash(*args: str) -> list[str]:
    return [BASH, BASH_SCRIPT.as_posix(), *args]


def _pwsh(*args: str) -> list[str]:
    return [PWSH, "-NoProfile", "-NonInteractive", "-File", str(PWSH_SCRIPT), *args]


SHELLS = [
    pytest.param(
        _bash,
        {"lane": "--lane", "link": "--link", "prompt": "--prompt-file", "mode": "--mode", "dry": "--dry-run"},
        marks=pytest.mark.skipif(BASH is None, reason="bash not installed"),
        id="bash",
    ),
    pytest.param(
        _pwsh,
        {"lane": "-Lane", "link": "-Link", "prompt": "-PromptFile", "mode": "-Mode", "dry": "-DryRun"},
        marks=pytest.mark.skipif(PWSH is None, reason="pwsh not installed"),
        id="pwsh",
    ),
]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "prompt.md").write_text(TRICKY_PROMPT, encoding="utf-8")
    return tmp_path


def _run(command: list[str], cwd: Path, **env: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, env={**os.environ, **env}, timeout=60
    )


def _args(
    flags: dict[str, str], lane="lane-aid-3", link="draft", prompt="prompt.md", *extra: str
) -> list[str]:
    return [flags["lane"], lane, flags["link"], link, flags["prompt"], prompt, *extra]


@pytest.mark.parametrize(("shell", "flags"), SHELLS)
def test_dry_run_prints_one_line_and_creates_nothing(shell, flags, project):
    result = _run(shell(*_args(flags), flags["dry"]), project, AIDIDIT_CLAUDE_BIN="claude")

    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("DRY-RUN: claude")
    assert "-p" in lines[0]
    assert not (project / ".specify").exists()


@pytest.mark.parametrize(("shell", "flags"), SHELLS)
def test_remote_mode_dry_run_names_the_session(shell, flags, project):
    result = _run(shell(*_args(flags), flags["mode"], "claude-remote", flags["dry"]), project)

    assert result.returncode == 0, result.stderr
    assert "--remote-control" in result.stdout
    assert "lane-aid-3-draft" in result.stdout


@pytest.mark.parametrize(("shell", "flags"), SHELLS)
@pytest.mark.parametrize(
    ("lane", "link", "prompt"),
    [
        ("Lane-Upper", "draft", "prompt.md"),
        ("lane;rm", "draft", "prompt.md"),
        ("x" * 64, "draft", "prompt.md"),
        ("lane-ok", "assemble", "prompt.md"),
        ("lane-ok", "draft", "missing.md"),
    ],
    ids=[
        "uppercase-lane",
        "shell-metachar-lane",
        "lane-too-long",
        "assemble-is-not-a-link",
        "missing-prompt",
    ],
)
def test_invalid_input_exits_2(shell, flags, project, lane, link, prompt):
    result = _run(shell(*_args(flags, lane, link, prompt), flags["dry"]), project)

    assert result.returncode == 2
    assert result.stderr.strip()


@pytest.mark.parametrize(("shell", "flags"), SHELLS)
def test_unknown_mode_exits_2(shell, flags, project):
    result = _run(shell(*_args(flags), flags["mode"], "yolo", flags["dry"]), project)

    assert result.returncode == 2


@pytest.mark.parametrize(("shell", "flags"), SHELLS)
def test_missing_claude_binary_exits_3(shell, flags, project):
    result = _run(shell(*_args(flags)), project, AIDIDIT_CLAUDE_BIN=str(project / "no-such-claude"))

    assert result.returncode == 3


@pytest.mark.skipif(BASH is None or sys.platform == "win32", reason="POSIX detached spawn")
def test_bash_spawn_passes_the_prompt_as_one_untouched_argument(project):
    capture = project / "argv.txt"
    fake = project / "fake-claude"
    fake.write_text(f'#!/usr/bin/env bash\nprintf "%s\\0" "$@" > "{capture.as_posix()}"\n', encoding="utf-8")
    fake.chmod(0o755)
    flags = SHELLS[0].values[1]

    result = _run(_bash(*_args(flags)), project, AIDIDIT_CLAUDE_BIN=str(fake))

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("SPAWNED lane=lane-aid-3 link=draft pid=")
    assert (project / ".specify" / "aididit" / "lanes" / "lane-aid-3" / "draft.log").exists()
    deadline = time.monotonic() + 10
    while not capture.exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    assert capture.read_text(encoding="utf-8").split("\0")[:2] == ["-p", TRICKY_PROMPT]
