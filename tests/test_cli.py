"""The CLI routes verbs to feature slices and turns their results into exit codes."""

from __future__ import annotations

from contextlib import nullcontext as _no_exit

import pytest

from aididit import __version__
from aididit._exit import EXIT_OK, EXIT_PRECONDITION
from aididit._pack import PACK_DIR
from aididit.cli import Deps, main
from tests.conftest import RecordingRunner


def _deps(runner: RecordingRunner, messages: list[str], specify=("specify",), tools=None) -> Deps:
    found = dict(tools or {"git": "/bin/git"})
    return Deps(
        run=runner,
        specify=list(specify) if specify else None,
        which=found.get,
        say=messages.append,
        python_version=(3, 12),
    )


def test_version_flag_prints_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_verb_prints_help_and_fails(capsys):
    assert main([]) == EXIT_PRECONDITION
    assert "install" in capsys.readouterr().out


def test_install_routes_to_feature_with_bundled_pack(speckit_project, runner, messages):
    code = main(["install", str(speckit_project), "--integration", "copilot"], deps=_deps(runner, messages))

    assert code == EXIT_OK
    assert ("specify", "extension", "add", "--dev", str(PACK_DIR), "--force") in runner.argvs


def test_install_defaults_to_current_directory(speckit_project, runner, messages, monkeypatch):
    monkeypatch.chdir(speckit_project)

    main(["install"], deps=_deps(runner, messages))

    assert runner.calls[0][1] == speckit_project.resolve()


def test_install_no_init_flag_is_honoured(project, runner, messages):
    code = main(["install", str(project), "--no-init"], deps=_deps(runner, messages))

    assert code == EXIT_PRECONDITION


def test_install_without_specify_explains_how_to_get_it(project, runner, messages):
    code = main(["install", str(project)], deps=_deps(runner, messages, specify=None))

    assert code == EXIT_PRECONDITION
    assert runner.calls == []
    assert any("uv tool install specify-cli" in m for m in messages)


def test_uninstall_routes_to_feature(speckit_project, runner, messages):
    code = main(["uninstall", str(speckit_project), "--keep-config"], deps=_deps(runner, messages))

    assert code == EXIT_OK
    assert runner.argvs[-1][-1] == "--keep-config"


def test_uninstall_without_specify_fails(speckit_project, runner, messages):
    assert (
        main(["uninstall", str(speckit_project)], deps=_deps(runner, messages, specify=None))
        == EXIT_PRECONDITION
    )


def test_doctor_routes_to_feature(runner, messages):
    assert main(["doctor"], deps=_deps(runner, messages)) == EXIT_OK
    assert any("specify" in m for m in messages)


def test_default_deps_are_real(monkeypatch):
    from aididit import cli

    deps = cli.default_deps()

    assert deps.run is cli.subprocess_runner
    assert deps.python_version >= (3, 11)


@pytest.mark.parametrize("verb", ["install", "uninstall", "doctor", "--help", "install --help"])
def test_everything_the_cli_prints_is_ascii(verb, speckit_project, runner, messages, capsys):
    """A Windows console decodes output with its own code page, so a middle dot printed as
    "A·I·DID·IT" showed up as a replacement character (dogfood run). ASCII reads the same on all."""
    argv = verb.split() + ([str(speckit_project)] if verb in {"install", "uninstall"} else [])

    with pytest.raises(SystemExit) if "--help" in argv else _no_exit():
        main(argv, deps=_deps(runner, messages))

    printed = "\n".join(messages) + capsys.readouterr().out
    assert printed.strip()
    assert [line for line in printed.splitlines() if not line.isascii()] == []
