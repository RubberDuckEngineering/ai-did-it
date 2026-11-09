"""The installer finds the Spec Kit that ships with it before any other copy.

Order: explicit override (AIDIDIT_SPECIFY) → the `specify` entry point installed next to this
tool's own Python (the bundled dependency) → `specify` on PATH → not found.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aididit._specify import locate_specify


@pytest.fixture
def venv(tmp_path: Path) -> Path:
    scripts = tmp_path / "venv" / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "python.exe").write_text("")
    return scripts


def test_given_override_when_locate_then_uses_it(venv):
    found = locate_specify(
        env={"AIDIDIT_SPECIFY": "/opt/specify"}, python=venv / "python.exe", which=lambda _: None
    )

    assert found == ["/opt/specify"]


@pytest.mark.parametrize("name", ["specify.exe", "specify"])
def test_given_bundled_specify_next_to_python_when_locate_then_prefers_it(venv, name):
    (venv / name).write_text("")

    found = locate_specify(env={}, python=venv / "python.exe", which=lambda _: "/usr/bin/specify")

    assert found == [str(venv / name)]


def test_given_only_path_specify_when_locate_then_uses_path(venv):
    found = locate_specify(env={}, python=venv / "python.exe", which=lambda _: "/usr/bin/specify")

    assert found == ["/usr/bin/specify"]


def test_given_no_specify_anywhere_when_locate_then_none(venv):
    assert locate_specify(env={}, python=venv / "python.exe", which=lambda _: None) is None
