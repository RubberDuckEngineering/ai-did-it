"""Contract tests for the bundled Spec Kit extension.

The pack is prose that an agent executes, so its failure modes are broken references: a command
file missing from the manifest, a path to a shared file that does not exist, a command token
Spec Kit cannot resolve, or a config key nobody defined. Each test below fails on exactly one
of those.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest
import yaml

from aididit import __version__
from aididit._pack import PACK_DIR

REPO = Path(__file__).resolve().parents[2]
MANIFEST = yaml.safe_load((PACK_DIR / "extension.yml").read_text(encoding="utf-8"))
COMMANDS = MANIFEST["provides"]["commands"]
CORE_COMMANDS = {
    "analyze",
    "checklist",
    "clarify",
    "constitution",
    "implement",
    "plan",
    "specify",
    "tasks",
    "taskstoissues",
}
COMMAND_NAME = re.compile(r"^speckit\.aididit\.[a-z0-9-]+$")
RUNTIME_PATH = re.compile(r"\.specify/extensions/aididit/([A-Za-z0-9_./-]+)")
TOKEN = re.compile(r"__SPECKIT_COMMAND_([A-Z0-9_-]+)__")
CONFIG_KEY = re.compile(r"`(board|lanes|panel|loops|delivery|retro)\.([a-z_]+)")
FILE_SUFFIXES = {"md", "yml", "yaml", "sh", "ps1"}  # `retro.md` is a file, not a config key
CANONICAL_COMMAND = re.compile(r"/speckit\.((?:aididit\.)?[a-z0-9-]+)")
PACK_MARKDOWN = sorted(PACK_DIR.rglob("*.md"))
COMMAND_FILES = {PACK_DIR / c["file"] for c in COMMANDS}
REFERENCE_MARKDOWN = [doc for doc in PACK_MARKDOWN if doc not in COMMAND_FILES]
CREATED_AT_INSTALL = {"aididit-config.yml"}  # Spec Kit copies it from aididit-config.template.yml


def _token_for(command_name: str) -> str:
    return command_name.removeprefix("speckit.").upper().replace(".", "_")


def _rel(path: Path) -> str:
    return path.relative_to(PACK_DIR).as_posix()


def test_versions_agree_across_package_manifest_and_pyproject():
    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))

    assert MANIFEST["extension"]["version"] == __version__ == pyproject["project"]["version"]


def test_manifest_targets_speckit_1_3_or_later():
    assert MANIFEST["schema_version"] == "1.0"
    assert MANIFEST["extension"]["id"] == "aididit"
    assert MANIFEST["requires"]["speckit_version"].startswith(">=1.3.0")


@pytest.mark.parametrize("command", COMMANDS, ids=lambda c: c["name"])
def test_each_command_is_well_formed(command):
    path = PACK_DIR / command["file"]
    text = path.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text.split("---", 2)[1])

    assert COMMAND_NAME.match(command["name"])
    assert path.name == f"{command['name']}.md"
    assert text.startswith("---\n")
    assert set(frontmatter) == {"description"}
    assert "$ARGUMENTS" in text


def test_no_command_claims_a_name_outside_the_packs_namespace():
    """Aliases such as `speckit.assemble` doubled the skill list, sat in Spec Kit core's own
    unprefixed namespace, and collided with other `speckit.*` workflows (dogfood finding F-02)."""
    aliased = {c["name"]: c["aliases"] for c in COMMANDS if c.get("aliases")}

    assert aliased == {}


def test_every_command_file_in_the_pack_is_registered():
    on_disk = {_rel(p) for p in PACK_DIR.rglob("speckit.aididit.*.md")}

    assert on_disk == {c["file"] for c in COMMANDS}


def test_the_seven_stages_and_seven_personas_are_all_present():
    names = {c["name"].removeprefix("speckit.aididit.") for c in COMMANDS}

    assert names == {
        "assemble",
        "ideate",
        "draft",
        "iterate",
        "deliver",
        "investigate",
        "tidy",
        "po",
        "architect",
        "qa",
        "devsec",
        "devops",
        "pr-prep",
        "pr-review",
    }


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_runtime_path_points_at_a_file_in_the_pack(doc):
    text = doc.read_text(encoding="utf-8")
    missing = {
        ref.rstrip(".")
        for ref in RUNTIME_PATH.findall(text)
        if ref.rstrip(".") not in CREATED_AT_INSTALL and not (PACK_DIR / ref.rstrip(".")).exists()
    }

    assert missing == set()


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_command_token_resolves(doc):
    known = {_token_for(c["name"]) for c in COMMANDS} | {c.upper() for c in CORE_COMMANDS}

    unknown = set(TOKEN.findall(doc.read_text(encoding="utf-8"))) - known

    assert unknown == set()


@pytest.mark.parametrize("doc", REFERENCE_MARKDOWN, ids=_rel)
def test_reference_files_name_commands_without_tokens(doc):
    """Spec Kit renders command tokens only in registered command files; the shared guides are
    copied verbatim, so a token there reaches the agent raw (dogfood finding F-01)."""
    assert TOKEN.findall(doc.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_canonical_command_name_is_a_real_command(doc):
    known = {c["name"].removeprefix("speckit.") for c in COMMANDS} | CORE_COMMANDS

    unknown = set(CANONICAL_COMMAND.findall(doc.read_text(encoding="utf-8"))) - known

    assert unknown == set()


@pytest.mark.parametrize("doc", PACK_MARKDOWN, ids=_rel)
def test_every_config_key_mentioned_exists_in_the_template(doc):
    template = yaml.safe_load((PACK_DIR / "aididit-config.template.yml").read_text(encoding="utf-8"))

    undefined = {
        f"{section}.{key}"
        for section, key in CONFIG_KEY.findall(doc.read_text(encoding="utf-8"))
        if key not in FILE_SUFFIXES and key not in template[section]
    }

    assert undefined == set()


def test_config_template_is_declared_with_the_preserved_name():
    config = MANIFEST["provides"]["config"][0]

    assert config["name"].endswith("-config.yml")
    assert (PACK_DIR / config["template"]).is_file()


def test_lane_workflow_runs_the_six_links_with_a_merge_gate():
    workflow = yaml.safe_load((PACK_DIR / "workflows" / "aididit-lane.yml").read_text(encoding="utf-8"))
    sequence = [s.get("command", s["id"]).removeprefix("speckit.aididit.") for s in workflow["steps"]]

    assert sequence == ["ideate", "accept", "draft", "iterate", "deliver", "merge", "investigate", "tidy"]
    assert workflow["workflow"]["version"] == __version__


def test_lane_workflow_asks_for_the_same_spec_kit_range_as_the_pack():
    workflow = yaml.safe_load((PACK_DIR / "workflows" / "aididit-lane.yml").read_text(encoding="utf-8"))

    assert workflow["requires"]["speckit_version"] == MANIFEST["requires"]["speckit_version"]


def test_lane_workflow_invokes_stages_as_direct_runs_so_they_never_self_chain():
    workflow = yaml.safe_load((PACK_DIR / "workflows" / "aididit-lane.yml").read_text(encoding="utf-8"))
    args = {s["id"]: s["input"]["args"] for s in workflow["steps"] if "command" in s}

    assert args["ideate"] == "mode:B item:{{ inputs.item }}"
    assert all(a == "item:{{ inputs.item }}" for step, a in args.items() if step != "ideate")
    assert "lane" not in workflow["inputs"]


def test_board_template_has_the_five_columns_in_order():
    headings = re.findall(
        r"^## (.+)$", (PACK_DIR / "templates" / "board.md").read_text(encoding="utf-8"), re.M
    )

    assert headings == ["Backlog", "Ready", "In Progress", "In Review", "Done"]


@pytest.mark.parametrize("separator", [".", "-"], ids=["markdown-agents", "skills-agents"])
def test_spec_kit_renders_every_token_as_a_registered_command(separator):
    """Dogfood finding F-14 proposed renaming `PR-PREP` to `PR_PREP`. Spec Kit keeps a hyphen inside
    its segment, so the rename would have rendered `/speckit.aididit.pr.prep` for markdown agents.
    This renders each token with Spec Kit's own resolver, so its rule is the oracle."""
    from specify_cli.integrations.base import IntegrationBase

    known = {f"/{name.replace('.', separator)}" for name in {c["name"] for c in COMMANDS}}
    known |= {f"/speckit{separator}{core}" for core in CORE_COMMANDS}
    names = {name for doc in PACK_MARKDOWN for name in TOKEN.findall(doc.read_text(encoding="utf-8"))}
    tokens = {f"__SPECKIT_COMMAND_{name}__" for name in names}

    rendered = {IntegrationBase.resolve_command_refs(token, separator) for token in tokens}

    assert tokens
    assert rendered - known == set()
