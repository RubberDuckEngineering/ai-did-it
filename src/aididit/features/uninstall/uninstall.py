"""Remove the pack from a project while keeping the team's own data.

The board, retros and lane ledgers live under .specify/aididit/ — they belong to the project,
not to the pack, so uninstall leaves them in place.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from aididit._exit import EXIT_OK, EXIT_PRECONDITION, EXIT_STEP_FAILED
from aididit._pack import EXTENSION_ID, LANE_WORKFLOW_ID, PROJECT_STATE_DIR, SPECKIT_DIR
from aididit._process import Runner


@dataclass(frozen=True)
class UninstallRequest:
    project: Path
    keep_config: bool = False


def uninstall(
    request: UninstallRequest, *, specify: list[str], run: Runner, say: Callable[[str], None]
) -> int:
    project = request.project
    if not (project / SPECKIT_DIR).is_dir():
        say(f"error: {project} is not a Spec Kit project; nothing to remove.")
        return EXIT_PRECONDITION

    if not run([*specify, "workflow", "remove", LANE_WORKFLOW_ID], project).ok:
        say("warning: the lane workflow was not registered or could not be removed; continuing.")

    remove = [*specify, "extension", "remove", EXTENSION_ID, "--force"]
    if request.keep_config:
        remove.append("--keep-config")
    if not run(remove, project).ok:
        say("error: `specify extension remove` failed.")
        return EXIT_STEP_FAILED

    kept = PROJECT_STATE_DIR.as_posix()
    say(f"AI Did It removed. Your board, retros and lane ledgers in {kept}/ were kept.")
    return EXIT_OK
