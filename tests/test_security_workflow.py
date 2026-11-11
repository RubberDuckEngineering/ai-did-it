"""Feature: every change, and every week, is scanned for leaked secrets and vulnerable dependencies.

The PII checks read commit metadata. They do not look for keys or tokens in the code, or for a
dependency with a published CVE. Gitleaks reads the whole history for secrets and Trivy reads
`uv.lock` for vulnerable packages. Both run on each pull request and push to `main`, and weekly,
because a new CVE can land on a lockfile nobody touched. Dependabot proposes the updates.

Acceptance criteria
- Given a commit anywhere in the history, when the secrets job runs, then gitleaks reads every
  commit, prints no secret it finds and fails the run on a finding.
- Given a dependency with a HIGH or CRITICAL CVE, when the dependency job runs, then the run fails.
- Given a scanner downloaded at run time, when it is installed, then its version is pinned and its
  checksum is verified before it runs.
- Given no code change, when a week passes, then both scans run again.
- Given the workflow, when it runs, then it can only read the repository, except where it uploads
  results to the Security tab.
- Given the repository's package managers, when Dependabot reads its config, then each one is
  covered.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "security.yml"
DEPENDABOT = REPO / ".github" / "dependabot.yml"
DOWNLOAD = re.compile(r"(?:wget|curl)\b[^\n]*https://github\.com/[\w.-]+/[\w.-]+/releases/download/")
PINNED_VERSION = re.compile(r'^\s*[A-Z_]+_VERSION="\d+\.\d+\.\d+"$', re.M)
CHECKSUM = re.compile(r'^\s*EXPECTED_SHA256="[0-9a-f]{64}"$', re.M)


def _read(path: Path) -> dict:
    assert path.is_file(), f"{path.relative_to(REPO).as_posix()} does not exist"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _workflow() -> dict:
    return _read(WORKFLOW)


def _job(name: str) -> dict:
    jobs = _workflow()["jobs"]
    assert name in jobs, f"no `{name}` job in security.yml"
    return jobs[name]


def _script(job: dict) -> str:
    """The job's shell, with each backslash-continued command joined onto one line."""
    return "\n".join(step.get("run", "") for step in job["steps"]).replace("\\\n", " ")


def _triggers() -> dict:
    workflow = _workflow()
    # PyYAML reads the bare key `on` as the boolean True.
    return workflow.get("on", workflow.get(True))


def test_the_secrets_job_reads_the_whole_history_and_fails_on_a_finding():
    job = _job("secrets")
    checkout = next(s for s in job["steps"] if str(s.get("uses", "")).startswith("actions/checkout@"))
    command = next(line for line in _script(job).splitlines() if line.strip().startswith("gitleaks git"))

    assert checkout.get("with", {}).get("fetch-depth") == 0, "a shallow clone hides older commits"
    assert "--redact" in command, "a finding would print the secret into a public log"
    assert "--exit-code 1" in command


def test_the_dependency_job_fails_on_a_high_or_critical_cve():
    command = next(
        line for line in _script(_job("dependencies")).splitlines() if line.strip().startswith("trivy fs")
    )

    assert "--scanners vuln" in command
    assert "--exit-code 1" in command
    assert set(re.search(r"--severity (\S+)", command).group(1).split(",")) >= {"HIGH", "CRITICAL"}


def test_every_downloaded_scanner_is_pinned_and_checksum_verified():
    for name in ("secrets", "dependencies"):
        script = _script(_job(name))
        assert DOWNLOAD.search(script), f"`{name}` downloads no scanner"
        assert PINNED_VERSION.search(script), f"`{name}` does not pin its scanner's version"
        assert CHECKSUM.search(script), f"`{name}` has no expected checksum"
        verify = script.find("sha256sum -c")
        assert 0 <= verify < script.find("tar -x"), f"`{name}` unpacks before it verifies"


def test_the_scans_run_on_each_change_and_every_week():
    triggers = _triggers()

    assert "pull_request" in triggers
    assert triggers["push"]["branches"] == ["main"]
    assert triggers.get("schedule"), "no weekly run, so a new CVE waits for the next change"


def test_the_workflow_reads_only_except_where_it_uploads_results():
    workflow = _workflow()

    assert workflow["permissions"] == {"contents": "read"}
    for name, job in workflow["jobs"].items():
        uploads = any("upload-sarif" in str(s.get("uses", "")) for s in job["steps"])
        granted = job.get("permissions", {})
        assert granted == ({"contents": "read", "security-events": "write"} if uploads else {}), name


def test_dependabot_covers_every_package_manager_the_repository_uses():
    assert (REPO / "uv.lock").is_file() and any(WORKFLOW.parent.glob("*.yml"))
    config = _read(DEPENDABOT)
    covered = {u["package-ecosystem"] for u in config["updates"] if u["directory"] == "/"}

    assert covered >= {"github-actions", "uv"}
