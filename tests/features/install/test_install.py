"""Feature: install the A·I·DID·IT pack into a project.

Acceptance criteria
- Given a folder that is not yet a Spec Kit project, when I install, then Spec Kit is
  initialised for my agent and the pack is added.
- Given an existing Spec Kit project, when I install again, then init is skipped and the pack
  is reinstalled in place (idempotent upgrade).
- Given any step fails, when I install, then later steps do not run and the exit code is non-zero.
- Given I already have a board, when I install, then my board is left untouched.
"""

from __future__ import annotations

from pathlib import Path

from aididit._exit import EXIT_OK, EXIT_PRECONDITION, EXIT_STEP_FAILED
from aididit.features.install.install import InstallRequest, install
from tests.conftest import SPECIFY, RecordingRunner


def _install(project: Path, runner: RecordingRunner, pack_dir: Path, say, **kwargs) -> int:
    request = InstallRequest(project=project, **kwargs)
    return install(request, specify=SPECIFY, run=runner, pack_dir=pack_dir, say=say)


def test_given_plain_folder_when_install_then_initialises_speckit_for_the_agent(
    project, runner, pack_dir, say
):
    code = _install(project, runner, pack_dir, say)

    assert code == EXIT_OK
    assert runner.argvs[0] == (
        "specify",
        "init",
        "--here",
        "--force",
        "--non-interactive",
        "--ignore-agent-tools",
        "--integration",
        "claude",
    )
    assert all(cwd == project for _, cwd in runner.calls)


def test_given_agent_cli_absent_when_install_then_init_does_not_require_it(project, runner, pack_dir, say):
    """Spec Kit refuses to init when the agent's CLI is missing unless told not to check. Many agents
    (an IDE assistant, a CI runner) have no CLI on PATH, so the installer must never depend on one."""
    _install(project, runner, pack_dir, say)

    assert "--ignore-agent-tools" in runner.argvs[0]


def test_given_plain_folder_when_install_then_adds_pack_after_init(project, runner, pack_dir, say):
    _install(project, runner, pack_dir, say)

    assert runner.argvs[1] == ("specify", "extension", "add", "--dev", str(pack_dir), "--force")


def test_given_plain_folder_when_install_then_registers_the_lane_workflow(project, runner, pack_dir, say):
    _install(project, runner, pack_dir, say)

    workflow = pack_dir / "workflows" / "aididit-lane.yml"
    assert runner.argvs[2] == ("specify", "workflow", "add", str(workflow))
    assert len(runner.argvs) == 3


def test_given_another_agent_when_install_then_passes_that_integration(project, runner, pack_dir, say):
    _install(project, runner, pack_dir, say, integration="copilot")

    assert runner.argvs[0][-2:] == ("--integration", "copilot")


def test_given_existing_speckit_project_when_install_then_skips_init(speckit_project, runner, pack_dir, say):
    code = _install(speckit_project, runner, pack_dir, say)

    assert code == EXIT_OK
    assert all(argv[1] != "init" for argv in runner.argvs)
    assert runner.argvs[0][:3] == ("specify", "extension", "add")


def test_given_no_init_flag_and_no_speckit_when_install_then_refuses_without_running_anything(
    project, runner, pack_dir, say, messages
):
    code = _install(project, runner, pack_dir, say, init_missing=False)

    assert code == EXIT_PRECONDITION
    assert runner.calls == []
    assert any("not a Spec Kit project" in m for m in messages)


def test_given_missing_folder_when_install_then_refuses(tmp_path, runner, pack_dir, say, messages):
    code = _install(tmp_path / "nope", runner, pack_dir, say)

    assert code == EXIT_PRECONDITION
    assert runner.calls == []
    assert any("does not exist" in m for m in messages)


def test_given_init_fails_when_install_then_stops_before_adding_pack(
    project, runner, pack_dir, say, messages
):
    runner.fail_on("specify", "init")

    code = _install(project, runner, pack_dir, say)

    assert code == EXIT_STEP_FAILED
    assert len(runner.argvs) == 1
    assert any("specify init" in m for m in messages)


def test_given_pack_add_fails_when_install_then_exits_non_zero_and_skips_board(
    speckit_project, runner, pack_dir, say
):
    runner.fail_on("specify", "extension", "add")

    code = _install(speckit_project, runner, pack_dir, say)

    assert code == EXIT_STEP_FAILED
    assert not (speckit_project / ".specify" / "aididit" / "board.md").exists()


def test_given_workflow_add_fails_when_install_then_warns_but_succeeds(
    speckit_project, runner, pack_dir, say, messages
):
    runner.fail_on("specify", "workflow", "add")

    code = _install(speckit_project, runner, pack_dir, say)

    assert code == EXIT_OK
    assert any(m.startswith("warning:") and "workflow" in m for m in messages)


def test_given_no_board_when_install_then_seeds_board_from_template(speckit_project, runner, pack_dir, say):
    _install(speckit_project, runner, pack_dir, say)

    board = speckit_project / ".specify" / "aididit" / "board.md"
    assert board.read_text(encoding="utf-8") == "# Board\n\n## Backlog\n"


def test_given_existing_board_when_install_then_leaves_it_untouched(speckit_project, runner, pack_dir, say):
    board = speckit_project / ".specify" / "aididit" / "board.md"
    board.parent.mkdir(parents=True)
    board.write_text("my work", encoding="utf-8")

    _install(speckit_project, runner, pack_dir, say)

    assert board.read_text(encoding="utf-8") == "my work"


def test_given_success_when_install_then_tells_the_user_how_to_start(
    speckit_project, runner, pack_dir, say, messages
):
    _install(speckit_project, runner, pack_dir, say)

    assert any("Agents Assemble" in m for m in messages)


def test_given_install_when_done_then_lane_ledgers_are_git_ignored(speckit_project, runner, pack_dir, say):
    _install(speckit_project, runner, pack_dir, say)

    ignore = speckit_project / ".specify" / "aididit" / ".gitignore"
    assert "lanes/" in ignore.read_text(encoding="utf-8").splitlines()


def test_given_existing_state_ignore_when_install_then_it_is_kept(speckit_project, runner, pack_dir, say):
    ignore = speckit_project / ".specify" / "aididit" / ".gitignore"
    ignore.parent.mkdir(parents=True)
    ignore.write_text("custom/\n", encoding="utf-8")

    _install(speckit_project, runner, pack_dir, say)

    assert ignore.read_text(encoding="utf-8") == "custom/\n"


def _write_constitution(project: Path, first_line: str) -> None:
    memory = project / ".specify" / "memory"
    memory.mkdir()
    (memory / "constitution.md").write_text(first_line + "\n", encoding="utf-8")


def test_given_the_constitution_is_still_the_template_when_install_then_warns_to_write_it(
    speckit_project, runner, pack_dir, say, messages
):
    """The panel judges scope against the constitution; an unfilled template makes every such check
    empty (dogfood finding F-03). The line below is Spec Kit 1.3's template's first line, verbatim."""
    _write_constitution(speckit_project, "# [PROJECT_NAME] Constitution")

    assert _install(speckit_project, runner, pack_dir, say) == EXIT_OK
    assert any(m.startswith("warning:") and "/speckit.constitution" in m for m in messages)


def test_given_a_written_constitution_when_install_then_no_constitution_warning(
    speckit_project, runner, pack_dir, say, messages
):
    _write_constitution(speckit_project, "# Tally Constitution")

    _install(speckit_project, runner, pack_dir, say)

    assert not any("constitution" in m for m in messages)
