"""`aididit` — install and check the A·I·DID·IT expansion pack for GitHub Spec Kit."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from aididit import __version__
from aididit._exit import EXIT_PRECONDITION
from aididit._pack import PACK_DIR, SPECKIT_INSTALL_HINT
from aididit._process import Runner, subprocess_runner
from aididit._specify import locate_specify
from aididit.features.doctor.doctor import run_doctor
from aididit.features.install.install import InstallRequest, install
from aididit.features.uninstall.uninstall import UninstallRequest, uninstall


@dataclass(frozen=True)
class Deps:
    run: Runner
    specify: list[str] | None
    which: Callable[[str], str | None]
    say: Callable[[str], None]
    python_version: tuple[int, int]


def default_deps() -> Deps:
    return Deps(
        run=subprocess_runner,
        specify=locate_specify(env=os.environ, python=Path(sys.executable), which=shutil.which),
        which=shutil.which,
        say=print,
        python_version=(sys.version_info.major, sys.version_info.minor),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aididit",
        description="AI Did It: Assemble, Ideate, Draft, Iterate, Deliver, Investigate, Tidy - "
        "an agile expansion pack for GitHub Spec Kit.",
    )
    parser.add_argument("--version", action="version", version=f"aididit {__version__}")
    verbs = parser.add_subparsers(dest="verb", metavar="{install,uninstall,doctor}")

    install_cmd = verbs.add_parser(
        "install", help="add the pack to a project (runs `specify init` if needed)"
    )
    install_cmd.add_argument(
        "project", nargs="?", default=".", help="project folder (default: current folder)"
    )
    install_cmd.add_argument(
        "--integration", default="claude", help="agent to set up when initialising Spec Kit (default: claude)"
    )
    install_cmd.add_argument(
        "--no-init",
        action="store_true",
        help="fail instead of running `specify init` in a non-Spec Kit folder",
    )

    uninstall_cmd = verbs.add_parser("uninstall", help="remove the pack, keeping your board and retros")
    uninstall_cmd.add_argument("project", nargs="?", default=".")
    uninstall_cmd.add_argument("--keep-config", action="store_true", help="keep aididit-config.yml")

    verbs.add_parser("doctor", help="check this machine has what the full loop needs")
    return parser


def main(argv: Sequence[str] | None = None, *, deps: Deps | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.verb is None:
        parser.print_help()
        return EXIT_PRECONDITION
    deps = deps or default_deps()

    if args.verb == "doctor":
        return run_doctor(
            which=deps.which, specify=deps.specify, python_version=deps.python_version, say=deps.say
        )
    if deps.specify is None:
        deps.say(
            f"error: Spec Kit's `specify` command was not found. Install it with: {SPECKIT_INSTALL_HINT}"
        )
        return EXIT_PRECONDITION
    project = Path(args.project).resolve()
    if args.verb == "install":
        request = InstallRequest(project=project, integration=args.integration, init_missing=not args.no_init)
        return install(request, specify=deps.specify, run=deps.run, pack_dir=PACK_DIR, say=deps.say)
    return uninstall(
        UninstallRequest(project=project, keep_config=args.keep_config),
        specify=deps.specify,
        run=deps.run,
        say=deps.say,
    )
