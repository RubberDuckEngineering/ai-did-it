"""Feature: check that this machine can run the full A·I·DID·IT loop.

- Given every required tool is present, when I run doctor, then it exits 0.
- Given a required tool is missing, when I run doctor, then it exits 1 and names the fix.
- Given only optional tools are missing, when I run doctor, then it still exits 0 and explains
  which capability is unavailable.
"""

from __future__ import annotations

from aididit._exit import EXIT_OK, EXIT_STEP_FAILED
from aididit.features.doctor.doctor import run_doctor

ALL_TOOLS = {"git": "/bin/git", "gh": "/bin/gh", "claude": "/bin/claude"}


def _which(available: dict[str, str]):
    return available.get


def test_given_everything_present_when_doctor_then_ok(say, messages):
    code = run_doctor(which=_which(ALL_TOOLS), specify=["specify"], python_version=(3, 12), say=say)

    assert code == EXIT_OK
    assert sum(m.startswith("ok") for m in messages) == 5


def test_given_old_python_when_doctor_then_fails(say, messages):
    code = run_doctor(which=_which(ALL_TOOLS), specify=["specify"], python_version=(3, 10), say=say)

    assert code == EXIT_STEP_FAILED
    assert any(m.startswith("MISSING") and "python" in m for m in messages)


def test_given_no_specify_when_doctor_then_fails_and_names_the_fix(say, messages):
    code = run_doctor(which=_which(ALL_TOOLS), specify=None, python_version=(3, 12), say=say)

    assert code == EXIT_STEP_FAILED
    assert any("specify" in m and "uv tool install" in m for m in messages)


def test_given_no_git_when_doctor_then_fails(say, messages):
    tools = {k: v for k, v in ALL_TOOLS.items() if k != "git"}

    code = run_doctor(which=_which(tools), specify=["specify"], python_version=(3, 12), say=say)

    assert code == EXIT_STEP_FAILED


def test_given_only_optional_tools_missing_when_doctor_then_ok_with_notes(say, messages):
    code = run_doctor(which=_which({"git": "/bin/git"}), specify=["specify"], python_version=(3, 11), say=say)

    assert code == EXIT_OK
    optional = [m for m in messages if m.startswith("optional")]
    assert len(optional) == 2
    assert any("gh" in m and "GitHub" in m for m in optional)
    assert any("claude" in m and "lane" in m for m in optional)
