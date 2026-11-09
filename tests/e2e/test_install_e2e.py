"""End to end: the real `specify` (the copy bundled with this package) installs, upgrades and
removes the pack in a throwaway project. This is the test that keeps the unit tests' fake
runner honest about what Spec Kit actually does.

Skipped when `specify` cannot be found, unless AIDIDIT_REQUIRE_E2E=1 (CI sets it), in which case a
missing `specify` is a failure rather than a silent skip.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from aididit._exit import EXIT_OK
from aididit._pack import PACK_DIR
from aididit._process import subprocess_runner
from aididit._specify import locate_specify
from aididit.cli import Deps, main

pytestmark = pytest.mark.e2e

SPECIFY = locate_specify(env=os.environ, python=Path(sys.executable), which=shutil.which)
if SPECIFY is None:
    if os.environ.get("AIDIDIT_REQUIRE_E2E") == "1":
        raise RuntimeError("AIDIDIT_REQUIRE_E2E=1 but `specify` was not found")
    pytest.skip("`specify` not available", allow_module_level=True)

MANIFEST = yaml.safe_load((PACK_DIR / "extension.yml").read_text(encoding="utf-8"))
SKILL_NAMES = [c["name"].replace(".", "-") for c in MANIFEST["provides"]["commands"]]
INSTALL_LOG: list[str] = []
SPECKIT_TOKEN = re.compile(r"__SPECKIT_COMMAND_[A-Z][A-Z0-9_-]*__")  # Spec Kit 1.3's own token shape


def _cli(*args: str, log: list[str]) -> int:
    deps = Deps(
        run=subprocess_runner, specify=SPECIFY, which=shutil.which, say=log.append, python_version=(3, 11)
    )
    return main(list(args), deps=deps)


@pytest.fixture(scope="module")
def installed(tmp_path_factory) -> Path:
    project = tmp_path_factory.mktemp("e2e") / "demo"
    project.mkdir()

    assert _cli("install", str(project), "--integration", "claude", log=INSTALL_LOG) == EXIT_OK, INSTALL_LOG
    return project


def test_pack_is_copied_into_the_project(installed):
    ext = installed / ".specify" / "extensions" / "aididit"

    assert (ext / "extension.yml").is_file()
    assert (ext / "shared" / "lifecycle.md").is_file()
    assert (ext / "scripts" / "bash" / "spawn-lane.sh").is_file()


def test_the_installed_citation_verifier_runs_where_the_panel_says_it_is(installed, tmp_path):
    verifier = installed / ".specify" / "extensions" / "aididit" / "scripts" / "verify-quote.py"
    page = tmp_path / "page.html"
    page.write_text('<p>Posted by <a rel="author">Kent Beck</a></p><p>Make it work.</p>', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(verifier),
            "--source",
            str(page),
            "--control",
            "Kent Beck",
            "--quote",
            "make it work",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "VERDICT FOUND" in result.stdout


def test_config_is_deployed_from_the_template(installed):
    config = installed / ".specify" / "extensions" / "aididit" / "aididit-config.yml"

    assert yaml.safe_load(config.read_text(encoding="utf-8"))["board"]["provider"] == "markdown"


@pytest.mark.parametrize("skill", SKILL_NAMES)
def test_every_command_becomes_a_claude_skill(installed, skill):
    assert (installed / ".claude" / "skills" / skill / "SKILL.md").is_file()


def test_no_skill_is_created_outside_the_packs_namespace(installed):
    ours = {p.name for p in (installed / ".claude" / "skills").iterdir() if "aididit" not in p.name}
    stages = {"speckit-assemble", "speckit-ideate", "speckit-draft", "speckit-iterate", "speckit-deliver"}

    assert ours & (stages | {"speckit-investigate", "speckit-tidy"}) == set()


def test_installed_guides_carry_no_raw_command_tokens(installed):
    shared = installed / ".specify" / "extensions" / "aididit" / "shared"
    raw = [p.name for p in shared.rglob("*.md") if SPECKIT_TOKEN.search(p.read_text(encoding="utf-8"))]

    assert list(shared.rglob("*.md"))
    assert raw == []


def test_a_fresh_project_is_told_its_constitution_is_unwritten(installed):
    """Keeps the installer's template mark honest against the constitution Spec Kit really writes."""
    assert any(m.startswith("warning:") and "constitution" in m for m in INSTALL_LOG), INSTALL_LOG


@pytest.mark.parametrize("skill", SKILL_NAMES)
def test_command_tokens_are_rendered_for_the_agent(installed, skill):
    text = (installed / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")

    assert SPECKIT_TOKEN.findall(text) == []


def test_board_and_ignore_file_are_seeded(installed):
    state = installed / ".specify" / "aididit"

    assert "## Ready" in (state / "board.md").read_text(encoding="utf-8")
    assert "lanes/" in (state / ".gitignore").read_text(encoding="utf-8")


def test_reinstall_keeps_the_teams_config_and_board(installed):
    config = installed / ".specify" / "extensions" / "aididit" / "aididit-config.yml"
    board = installed / ".specify" / "aididit" / "board.md"
    config.write_text(
        config.read_text(encoding="utf-8").replace("runner: inline", "runner: claude"), encoding="utf-8"
    )
    board.write_text("# my board\n", encoding="utf-8")
    log: list[str] = []

    assert _cli("install", str(installed), log=log) == EXIT_OK, log
    assert "runner: claude" in config.read_text(encoding="utf-8")
    assert board.read_text(encoding="utf-8") == "# my board\n"


def test_lane_workflow_is_registered(installed):
    listing = subprocess_runner([*SPECIFY, "workflow", "list"], installed, capture=True)

    assert "aididit-lane" in listing.stdout + listing.stderr


def test_uninstall_removes_the_pack_and_keeps_the_board(installed):
    log: list[str] = []

    assert _cli("uninstall", str(installed), log=log) == EXIT_OK, log
    assert not (installed / ".specify" / "extensions" / "aididit" / "extension.yml").exists()
    assert not (installed / ".claude" / "skills" / "speckit-aididit-assemble").exists()
    assert (installed / ".specify" / "aididit" / "board.md").exists()


def test_spec_kit_installs_the_release_zip(tmp_path):
    from specify_cli._assets import get_speckit_version
    from specify_cli.extensions import ExtensionManager

    from tools.build_pack_zip import build_pack_zip

    project = tmp_path / "from-zip"
    project.mkdir()
    log: list[str] = []
    assert _cli("install", str(project), "--integration", "claude", log=log) == EXIT_OK, log
    archive = build_pack_zip(tmp_path / "aididit.zip")

    manifest = ExtensionManager(project).install_from_archive(archive, get_speckit_version(), force=True)

    ext = project / ".specify" / "extensions" / "aididit"
    assert manifest.id == "aididit"
    assert (ext / "README.md").is_file()  # only the zip carries it: the archive, not the folder, installed
    assert (ext / "scripts" / "verify-quote.py").is_file()
