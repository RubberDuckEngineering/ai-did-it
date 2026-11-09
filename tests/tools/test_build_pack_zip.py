"""Feature: a release ships the pack as a zip that Spec Kit can install by URL.

Spec Kit installs an extension archive only when `extension.yml` sits at the archive root or inside
exactly one top-level folder (`ExtensionManager.install_from_archive`, specify-cli 1.3.0). A GitHub
tag archive of this repo buries it three folders deep, so a release attaches its own zip.

Acceptance criteria
- Given the pack, when the zip is built, then `extension.yml` and every pack file sit at its root,
  with the repo's README and LICENSE beside them and no Python bytecode.
- Given a release tag, when its version differs from the pack's, then no zip is built.
- Given a release tag that matches, when the zip is built, then it lands where the release asks.
"""

from __future__ import annotations

import zipfile

import pytest

from aididit._pack import PACK_DIR
from tools.build_pack_zip import EXTRAS, build_pack_zip, main, pack_version

PACK_VERSION = pack_version()


def _pack_files() -> set[str]:
    return {
        p.relative_to(PACK_DIR).as_posix()
        for p in PACK_DIR.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def test_the_manifest_and_every_pack_file_sit_at_the_zip_root(tmp_path):
    out = build_pack_zip(tmp_path / "pack.zip")
    names = set(zipfile.ZipFile(out).namelist())

    assert "extension.yml" in names
    assert _pack_files() <= names


def test_the_readme_and_licence_travel_with_the_pack(tmp_path):
    names = set(zipfile.ZipFile(build_pack_zip(tmp_path / "pack.zip")).namelist())

    assert {extra.name for extra in EXTRAS} == {"README.md", "LICENSE"}
    assert {"README.md", "LICENSE"} <= names


def test_python_bytecode_never_ships(tmp_path):
    pack = tmp_path / "pack"
    (pack / "scripts" / "__pycache__").mkdir(parents=True)
    (pack / "extension.yml").write_text("schema_version: '1.0'\n", encoding="utf-8")
    (pack / "scripts" / "tool.py").write_text("print('hi')\n", encoding="utf-8")
    (pack / "scripts" / "__pycache__" / "tool.cpython-311.pyc").write_bytes(b"bytecode")
    (pack / "scripts" / "stray.pyc").write_bytes(b"bytecode")

    names = zipfile.ZipFile(build_pack_zip(tmp_path / "pack.zip", pack_dir=pack)).namelist()

    assert "scripts/tool.py" in names
    assert not [n for n in names if "__pycache__" in n or n.endswith(".pyc")]


def test_a_tag_that_disagrees_with_the_pack_version_builds_nothing(tmp_path, capsys):
    out = tmp_path / "pack.zip"

    code = main(["--out", str(out), "--expect-version", "v9.9.9"])

    assert code == 1
    assert not out.exists()
    assert PACK_VERSION in capsys.readouterr().err


@pytest.mark.parametrize("tag", [PACK_VERSION, f"v{PACK_VERSION}"])
def test_a_matching_tag_builds_the_zip_where_asked(tmp_path, tag):
    out = tmp_path / "dist" / "pack.zip"

    assert main(["--out", str(out), "--expect-version", tag]) == 0
    assert zipfile.is_zipfile(out)


def test_without_a_tag_the_zip_is_built_for_a_dry_run(tmp_path):
    out = tmp_path / "pack.zip"

    assert main(["--out", str(out)]) == 0
    assert zipfile.is_zipfile(out)
