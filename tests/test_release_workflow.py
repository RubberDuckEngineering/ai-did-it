"""Feature: anyone can prove a release zip was built by this repository's release workflow.

The Spec Kit catalog pins the zip's sha256, and immutable releases stop a published asset from being
swapped. Neither says where the zip came from. A build-provenance attestation, signed with the
workflow's own identity, does: `gh attestation verify <zip> --repo RubberDuckEngineering/ai-did-it`
checks it.

Acceptance criteria
- Given a version tag, when the release workflow builds the zip, then it attests that zip's build
  provenance before it publishes the release, so a release never goes out unattested.
- Given the release workflow, when it runs, then its token can write only the contents, the
  attestation and the signing identity it needs, and nothing by default.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "release.yml"
ZIP = "dist/aididit-${{ github.ref_name }}.zip"
ATTEST = "actions/attest-build-provenance@"


def _workflow() -> dict:
    assert WORKFLOW.is_file(), ".github/workflows/release.yml does not exist"
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps() -> list[dict]:
    jobs = _workflow()["jobs"]
    assert "pack-zip" in jobs, "no `pack-zip` job in release.yml"
    return jobs["pack-zip"]["steps"]


def _index(steps: list[dict], found: str, what: str) -> int:
    hits = [i for i, step in enumerate(steps) if found in step.get("run", "") + step.get("uses", "")]
    assert len(hits) == 1, f"expected one step that {what}, found {len(hits)}"
    return hits[0]


def test_the_zip_is_attested_after_it_is_built_and_before_it_is_published():
    steps = _steps()
    built = _index(steps, "tools.build_pack_zip", "builds the zip")
    attested = _index(steps, ATTEST, "attests the build")
    published = _index(steps, "gh release create", "publishes the release")

    assert steps[attested].get("with", {}).get("subject-path") == ZIP, "the attestation names another file"
    assert built < attested < published, "the zip is attested out of order"


def test_the_token_writes_only_what_the_release_needs():
    workflow = _workflow()
    job = workflow["jobs"]["pack-zip"]

    assert workflow.get("permissions") == {}, "the workflow's default token can write"
    assert job.get("permissions") == {
        "contents": "write",
        "id-token": "write",
        "attestations": "write",
    }
