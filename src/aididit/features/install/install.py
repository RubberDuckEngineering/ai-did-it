"""Install (or upgrade in place) the A·I·DID·IT pack into a project.

Steps, each stopping the run on failure:
1. `specify init` when the folder is not yet a Spec Kit project (skippable with --no-init).
2. `specify extension add --dev <pack> --force` — Spec Kit validates the manifest, renders every
   command for the project's agent, and keeps an existing `aididit-config.yml` on reinstall.
3. Seed the project's Kanban board from the template, never overwriting an existing one.
4. Register the single-lane workflow (best effort: a warning, not a failure).
5. Warn when the constitution is still Spec Kit's unfilled template: the panel judges scope by it.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from aididit._exit import EXIT_OK, EXIT_PRECONDITION, EXIT_STEP_FAILED
from aididit._pack import (
    BOARD_TEMPLATE,
    CONSTITUTION,
    CONSTITUTION_TEMPLATE_MARK,
    LANE_WORKFLOW_FILE,
    PROJECT_STATE_DIR,
    SPECKIT_DIR,
)
from aididit._process import Runner

Say = Callable[[str], None]


@dataclass(frozen=True)
class InstallRequest:
    project: Path
    integration: str = "claude"
    init_missing: bool = True


class _StepFailed(Exception):
    pass


def install(request: InstallRequest, *, specify: list[str], run: Runner, pack_dir: Path, say: Say) -> int:
    project = request.project
    if not project.is_dir():
        say(f"error: {project} does not exist.")
        return EXIT_PRECONDITION
    needs_init = not (project / SPECKIT_DIR).is_dir()
    if needs_init and not request.init_missing:
        say(f"error: {project} is not a Spec Kit project (no {SPECKIT_DIR}/). Drop --no-init to create one.")
        return EXIT_PRECONDITION

    def step(label: str, *args: str) -> bool:
        say(f"-> {label}")
        return run([*specify, *args], project).ok

    try:
        if needs_init:
            _require(
                step(
                    "specify init",
                    "init",
                    "--here",
                    "--force",
                    "--non-interactive",
                    "--ignore-agent-tools",
                    "--integration",
                    request.integration,
                ),
                "specify init",
            )
        _require(
            step(
                "specify extension add (AI Did It pack)",
                "extension",
                "add",
                "--dev",
                str(pack_dir),
                "--force",
            ),
            "specify extension add",
        )
    except _StepFailed as failure:
        say(f"error: `{failure}` failed; nothing after it was run.")
        return EXIT_STEP_FAILED

    _seed_state(project, pack_dir, say)
    if not step(
        "specify workflow add (single-lane workflow)", "workflow", "add", str(pack_dir / LANE_WORKFLOW_FILE)
    ):
        say("warning: the lane workflow was not registered; every stage command still works.")
    _check_constitution(project, say)

    say(
        "AI Did It is installed. Put a story in .specify/aididit/board.md under Ready, then tell your "
        'agent "Agents Assemble".'
    )
    return EXIT_OK


def _require(succeeded: bool, label: str) -> None:
    if not succeeded:
        raise _StepFailed(label)


def _check_constitution(project: Path, say: Say) -> None:
    if not _still_the_template(project / CONSTITUTION):
        return
    say(
        f"warning: {CONSTITUTION.as_posix()} is still Spec Kit's unfilled template. The panel judges "
        "scope against it, so write it first with the /speckit.constitution command."
    )


def _still_the_template(constitution: Path) -> bool:
    return constitution.is_file() and CONSTITUTION_TEMPLATE_MARK in constitution.read_text(encoding="utf-8")


def _seed_state(project: Path, pack_dir: Path, say: Say) -> None:
    _seed_board(project, pack_dir, say)
    ignore = project / PROJECT_STATE_DIR / ".gitignore"
    if not ignore.exists():
        # Lane handoff notes and logs are working state, not history; the board and retros stay tracked.
        ignore.write_text("lanes/\n", encoding="utf-8")


def _seed_board(project: Path, pack_dir: Path, say: Say) -> None:
    board = project / PROJECT_STATE_DIR / "board.md"
    if board.exists():
        say(f"-> keeping your existing board at {board.relative_to(project).as_posix()}")
        return
    board.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pack_dir / BOARD_TEMPLATE, board)
    say(f"-> seeded a starter board at {board.relative_to(project).as_posix()}")
