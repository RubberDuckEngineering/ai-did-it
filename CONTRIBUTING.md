# Contributing

Thanks for helping. This project eats its own cooking: every change follows the same rules the
pack asks of your agent.

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
7. **No personal data.** No names, emails, home-directory paths, private tracker URLs or real
   ticket keys. `tests/test_no_pii.py` scans the repo. To also scan for your own private terms,
   point `AIDIDIT_PII_DENYLIST` at a file outside the repo with one term per line. The same list
   checks commit authors and committers: `uv run python -m tools.check_commit_identity
   --denylist <file>`.
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
  `git config user.email admin@rubberduckengineering.com` in your clone.
- **The identity check in CI.** Store the private denylist as the `AIDIDIT_PII_DENYLIST` Actions
  secret (one term per line). Without it the check is skipped with a warning, which is what
  pull requests from forks see.
- **Merging.** GitHub's merge buttons write the merging account's profile name into the commit
  they create. To keep that name out of history, merge locally with `git merge --ff-only` after
  rebasing the branch, and push `main`.
