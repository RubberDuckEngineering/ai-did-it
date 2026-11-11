# Contributing

Thanks for helping. This project eats its own cooking: every change follows the same rules the
pack asks of your agent.

## How changes get in

- **Anyone can open an issue.** Use the bug report or the pack improvement template. A lesson from
  running the pack in your own repository is the most useful thing you can send.
- **Pull requests are open to collaborators only.** The repository is set so that only people the
  maintainers have added can open one. If you'd like to become a collaborator, say so in an issue.
- **Every change to `main` goes through a pull request** with every CI check green, every review
  thread resolved and an approval from the maintainers team, the code owner of every file,
  given after its latest push. Nothing else can push
  to `main`, rewrite it or delete it.
- **Under the MIT licence** you can copy and adapt the pack in your own repository without asking.

## Setup

```bash
uv sync
```

```bash
uv run pytest
```

```bash
uv run ruff check src tests
```

## The rules

1. **Tests first.** Write the failing test, watch it fail for the right reason, then make it pass.
   New Python code keeps the suite at 100% branch coverage
   (`uv run pytest --cov=aididit --cov=tools`).
2. **Every guard must be able to fail and to pass.** When you add a check, record in the PR the
   mutation that turns it red, and show it green on the unmutated tree.
3. **Fakes state a contract.** The unit tests fake the `specify` CLI. If you change how the CLI
   calls Spec Kit, read Spec Kit's installed source for that command and extend
   `tests/e2e/test_install_e2e.py` so the real behaviour is exercised.
4. **Conventional Commits** for every commit: `type(scope): description`
   (see [`shared/disciplines/conventional-commits.md`](src/aididit/pack/shared/disciplines/conventional-commits.md)).
5. **Vertical slices.** A new CLI verb gets its own folder under `src/aididit/features/`; a new stage or
   persona gets its own folder under `src/aididit/pack/`. Register new commands in `extension.yml`;
   the pack contract tests will tell you if you forget.
6. **Prompts are code.** Pack files reference each other only through runtime paths
   (`.specify/extensions/aididit/...`), command tokens (`__SPECKIT_COMMAND_AIDIDIT_DRAFT__`) and config
   keys defined in `aididit-config.template.yml`. The contract tests enforce all three.
7. **No personal data.** No real names, personal emails, home-directory paths, private tracker
   URLs or real ticket keys. GitHub handles are fine, and so are GitHub's noreply commit addresses:
   both are already public on every contribution. `tests/test_no_pii.py` scans the repo. To also
   scan for your own private terms, point `AIDIDIT_PII_DENYLIST` at a file outside the repo with
   one term per line: real names and private terms, never handles. The same list checks commit
   authors and committers: `uv run python -m tools.check_commit_identity --denylist <file>`.
8. **Keep docs and code in one change.** A behaviour change updates the README, the affected pack
   files, the field guide in `docs/` and the CHANGELOG in the same commit.
9. **Diagrams wear the house style.** Every Mermaid diagram is a `flowchart` that copies the init line
   and `classDef` lines from [the brand book](docs/brand.md). `tests/test_diagrams.py` checks this and
   re-measures the palette's contrast against GitHub's light and dark themes.
10. **Cite or label.** A claim that leans on published work links to an entry in
    [`docs/sources.md`](docs/sources.md) (the anchor must exist; a test checks). A claim that goes
    beyond its source is labelled `[Inference]`; an unchecked one `[Unverified]`. Add a new source with
    its URL or DOI checked, and the check date.
11. **Every new guard gets a kill row** in [`docs/kill-tests.md`](docs/kill-tests.md), in the same
    commit, with its control observed green and its mutation observed red.

## Releasing

1. Bump the version in `pyproject.toml`, `src/aididit/__init__.py`, `src/aididit/pack/extension.yml` and
   `src/aididit/pack/workflows/aididit-lane.yml` (a contract test checks they agree).
2. Add a CHANGELOG entry.
3. Dry-run the release zip: `uv run python -m tools.build_pack_zip --out dist/aididit.zip`.
4. Tag `vX.Y.Z` on main and push the tag. `.github/workflows/release.yml` checks that the tag
   matches the pack version, builds the zip and attaches it to a GitHub release. That release
   asset is the `download_url` for Spec Kit's community catalog.

## Maintainers

- **Commit identity.** Commit as the project, not as yourself:
  `git config user.name "Rubber Duck Engineering"` and
  `git config user.email admin@rubberduckengineering.com` in your clone. A collaborator who
  commits as themselves uses their GitHub handle and noreply address, never a real name.
- **Commit in UTC.** A git date keeps your UTC offset, which narrows down where you live. Commit
  with `TZ=UTC` set (`TZ=UTC git commit ...` in Git Bash, or `$env:TZ = 'UTC'` first in
  PowerShell). `tools/check_commit_timezone.py` fails CI on a commit made as the project with any
  other offset; collaborators committing as themselves keep their own.
- **The identity check in CI.** Store the private denylist as the `AIDIDIT_PII_DENYLIST` Actions
  secret (one term per line: real names and private terms, not GitHub handles, and not the names of
  maintainers who merge with GitHub's button). Without it the check is skipped with a warning. Both
  history checks read the commits the event brings, from `tools/commit_range.py`: a pull request's
  base to its head, or a push's commit before to its commit after. A commit already on `main` is
  judged once, when it lands, so accepting one doesn't turn every later push red.
- **Repository protection.** Pull request creation is set to collaborators only. The `protect main`
  ruleset blocks deleting or force-pushing `main` and requires a pull request with one approval
  (given after the latest push) from a code owner, resolved threads and every CI job green.
  `.github/CODEOWNERS` makes the `@RubberDuckEngineering/maintainers` team the owner of every file;
  owners are always teams, never people (`tests/test_codeowners.py`), so who approves is changed in
  the team, not in a commit. Only the admin role bypasses it, which is what lets a maintainer merge
  their own pull request. GitHub Actions may not approve pull requests, so a workflow cannot stand
  in for a maintainer. The ruleset names each CI job, so renaming or adding a job means updating the
  ruleset in the same change, or that check waits forever.
- **Bumping an action.** Workflows pin every action to a full commit SHA with the release in a
  comment (`uses: owner/action@<sha> # vX.Y.Z`); `tests/test_ci_workflows.py` enforces it. To bump,
  resolve the release tag to its commit (`gh api repos/<owner>/<action>/git/ref/tags/<tag>`,
  following an annotated tag to its commit), check that commit's `action.yml` runtime, and update
  every use of that action at once.
- **Security scans.** `.github/workflows/security.yml` runs gitleaks over every commit and Trivy
  over `uv.lock` on each pull request, each push to `main` and weekly. A finding fails the run.
  `main` and the weekly run also publish results to the Security tab; a pull request does not,
  because Dependabot's runs cannot write there. Its two jobs, `no secret anywhere in the history`
  and `no dependency with a high or critical CVE`, belong in the `protect main` ruleset with the
  others. Dependabot proposes Action and `uv` updates weekly, grouped into one pull request each.
- **Bumping a scanner.** Dependabot does not see gitleaks or Trivy, because the workflow downloads
  them. To bump one, change its `*_VERSION` and take `EXPECTED_SHA256` for the `linux_x64` /
  `Linux-64bit` archive from that release's checksums file; `tests/test_security_workflow.py`
  requires both, and the checksum is verified before the archive is unpacked.
- **Merging.** GitHub's merge button is fine. It writes the merging account's profile name and
  local time zone into the merge commit it creates, which maintainers accept for their own
  merges. To keep your name out of history instead, merge locally with `git merge --ff-only` after
  rebasing the branch, and push `main`. Either way, the push to `main` checks the new commits.
