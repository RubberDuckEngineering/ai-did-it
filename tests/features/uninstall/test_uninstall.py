"""Feature: remove the pack from a project.

- Given an installed project, when I uninstall, then the extension and lane workflow are removed
  and my board, retros and lane ledgers under .specify/aididit/ are kept.
- Given I ask to keep config, when I uninstall, then Spec Kit is told to keep it.
- Given the folder is not a Spec Kit project, when I uninstall, then nothing runs.
"""

from __future__ import annotations

from aididit._exit import EXIT_OK, EXIT_PRECONDITION, EXIT_STEP_FAILED
from aididit.features.uninstall.uninstall import UninstallRequest, uninstall
from tests.conftest import SPECIFY


def test_given_installed_project_when_uninstall_then_removes_extension_and_workflow(
    speckit_project, runner, say
):
    code = uninstall(UninstallRequest(project=speckit_project), specify=SPECIFY, run=runner, say=say)

    assert code == EXIT_OK
    assert runner.argvs == [
        ("specify", "workflow", "remove", "aididit-lane"),
        ("specify", "extension", "remove", "aididit", "--force"),
    ]


def test_given_keep_config_when_uninstall_then_passes_keep_config(speckit_project, runner, say):
    uninstall(
        UninstallRequest(project=speckit_project, keep_config=True), specify=SPECIFY, run=runner, say=say
    )

    assert runner.argvs[-1] == ("specify", "extension", "remove", "aididit", "--force", "--keep-config")


def test_given_project_data_when_uninstall_then_says_it_was_kept(speckit_project, runner, say, messages):
    uninstall(UninstallRequest(project=speckit_project), specify=SPECIFY, run=runner, say=say)

    assert any(".specify/aididit" in m and "kept" in m for m in messages)


def test_given_workflow_remove_fails_when_uninstall_then_still_removes_extension(
    speckit_project, runner, say
):
    runner.fail_on("specify", "workflow", "remove")

    code = uninstall(UninstallRequest(project=speckit_project), specify=SPECIFY, run=runner, say=say)

    assert code == EXIT_OK
    assert runner.argvs[-1][:3] == ("specify", "extension", "remove")


def test_given_extension_remove_fails_when_uninstall_then_exits_non_zero(speckit_project, runner, say):
    runner.fail_on("specify", "extension", "remove")

    code = uninstall(UninstallRequest(project=speckit_project), specify=SPECIFY, run=runner, say=say)

    assert code == EXIT_STEP_FAILED


def test_given_not_a_speckit_project_when_uninstall_then_runs_nothing(project, runner, say):
    code = uninstall(UninstallRequest(project=project), specify=SPECIFY, run=runner, say=say)

    assert code == EXIT_PRECONDITION
    assert runner.calls == []
