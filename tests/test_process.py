"""The real Runner adapter and the `python -m aididit` entry point, exercised for real."""

from __future__ import annotations

import runpy
import sys

import pytest

from aididit import __version__
from aididit._process import subprocess_runner


def test_real_runner_captures_output_and_exit_code(tmp_path):
    result = subprocess_runner(
        [sys.executable, "-c", "import sys; print('hi'); sys.exit(3)"], tmp_path, capture=True
    )

    assert result.returncode == 3
    assert not result.ok
    assert result.stdout.strip() == "hi"


def test_real_runner_runs_in_the_requested_folder(tmp_path):
    result = subprocess_runner(
        [sys.executable, "-c", "import os; print(os.getcwd())"], tmp_path, capture=True
    )

    assert result.ok
    assert result.stdout.strip().lower() == str(tmp_path).lower()


def test_module_entry_point_reports_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["aididit", "--version"])

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("aididit", run_name="__main__")

    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out
