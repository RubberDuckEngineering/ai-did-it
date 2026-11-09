"""Build the release zip: the pack at the archive root, so `specify extension add --from <url>` finds it.

Usage: python -m tools.build_pack_zip --out dist/aididit.zip [--expect-version v0.2.0]
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from collections.abc import Iterable, Sequence
from pathlib import Path

import yaml

from aididit._pack import PACK_DIR

REPO = Path(__file__).resolve().parents[1]
EXTRAS = (REPO / "README.md", REPO / "LICENSE")
EXIT_OK = 0
EXIT_VERSION_MISMATCH = 1


def build_pack_zip(out: Path, pack_dir: Path = PACK_DIR, extras: Iterable[Path] = EXTRAS) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(pack_dir.rglob("*")):
            if path.is_file() and not _is_bytecode(path):
                archive.write(path, path.relative_to(pack_dir).as_posix())
        for extra in extras:
            archive.write(extra, extra.name)
    return out


def pack_version(pack_dir: Path = PACK_DIR) -> str:
    manifest = yaml.safe_load((pack_dir / "extension.yml").read_text(encoding="utf-8"))
    return manifest["extension"]["version"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expect-version", help="the release tag; must name the pack version")
    args = parser.parse_args(argv)

    version = pack_version()
    if args.expect_version is not None and args.expect_version.removeprefix("v") != version:
        print(f"tag {args.expect_version} does not match the pack version {version}", file=sys.stderr)
        return EXIT_VERSION_MISMATCH
    print(f"built {build_pack_zip(args.out)} for version {version}")
    return EXIT_OK


def _is_bytecode(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix == ".pyc"


if __name__ == "__main__":
    raise SystemExit(main())
