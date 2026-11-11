# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- **Diagrams no longer lose their bottom on GitHub.** GitHub shrinks a diagram wider than the page
  column but sizes its frame to the shrunk height, which cut off 18 of the 34 diagrams on a 1280 px
  screen. Every diagram now fits the 838 px column: long chains run top to bottom, wide fans split
  onto two rows, the Ideate flow in the stage guide is two diagrams, and the house init line trims
  the padding to 8 px. Phones still crop, because their column is too narrow for almost any diagram.

### Added

- **A width check for diagrams.** `tests/test_diagrams.py` draws every diagram in Edge with the
  Mermaid build and settings GitHub's viewer uses (12.2.0) and fails one wider than the column. It
  needs the new `diagrams` dependency group; CI runs it on the Windows, Python 3.13 leg and refuses
  to skip it there.

## [0.2.3] - 2026-11-11

### Added

- **Security scans.** A new `security` workflow runs gitleaks over every commit for secrets and
  Trivy over `uv.lock` for dependencies with a HIGH or CRITICAL CVE. It runs on each pull request,
  each push to `main` and weekly, and `main` and the weekly run publish results to the Security tab.
  Both scanners are pinned and checksum-verified before they run.
- **Dependabot.** Weekly grouped updates for the GitHub Actions and the `uv` dependencies.
- **Release zips carry build provenance.** The release workflow attests each zip before it
  publishes the release, so `gh attestation verify aididit-vX.Y.Z.zip --repo
  RubberDuckEngineering/ai-did-it` proves which workflow and commit built it. Its token now has no
  default permissions; the job alone gets `contents`, `id-token` and `attestations` write.
- **The README names the Spec Kit catalog listing.** `specify extension search aididit` finds the
  pack. The community catalog is for discovery only, so installing still uses `--from`.

### Changed

- **The lockfile resolves Spec Kit 1.3.2.** CI and a source checkout now run `specify-cli` 1.3.2
  (was 1.3.0); the supported range, `>=1.3.0,<2`, is unchanged.

## [0.2.2] - 2026-11-10

### Fixed

- **Links name the renamed repository.** The repository is now `RubberDuckEngineering/ai-did-it`.
  The package metadata, the extension manifest the Spec Kit catalog reads, the README and the issue
  template still used the old name, which works only while GitHub's redirect lasts. A test now
  reads every tracked file for links into the organisation.

## [0.2.1] - 2026-11-10

### Fixed

- **A Spec Kit install gets a board too.** `specify extension add`, the route the Spec Kit catalog
  uses, never seeded `.specify/aididit/board.md`, and only `aididit install` did. The markdown board
  provider now has a Step 0, like the github and jira providers: it copies the starter board when
  none is there and never overwrites one that is. The README describes both install routes.
- **The starter board's demo item is `AID-0`.** It was `AID-1`, the id a user's first item should
  get, so a lookup for a real `AID-1` could find the demo. The next-id rule is unchanged, and a
  user's first item is now `AID-1`.

### Added

- **A time-zone check.** `tools/check_commit_timezone.py` fails when a commit made as the project
  (author or committer `admin@rubberduckengineering.com`) is dated with any offset but `+0000`, and
  CI runs it on every push and pull request. A hit names the commit and which date, never the
  offset. Contributors committing as themselves keep their own offset.

### Changed

- **CI checks each push over the commits it pushed.** The identity and time-zone checks used to
  read all of `HEAD` on a push to `main`, so one accepted commit turned every later push red.
  `tools/commit_range.py` now reads the range from the GitHub event: a pull request's base to its
  head, or a push's commit before to its commit after (everything reachable when the push creates
  the branch).
- **GitHub handles are not personal data here.** CONTRIBUTING now says handles and GitHub's
  noreply commit addresses are fine, since every contribution shows them, while real names never
  are. The private denylist holds real names and private terms, not handles.
- **Maintainers may merge with GitHub's button.** The merge commit carries the merging account's
  profile name, which maintainers accept for their own merges; merging locally with
  `git merge --ff-only` remains the way to keep a name out of history.
- **CI actions run on Node 24 and are pinned to commits.** `actions/checkout` moves from v4 to
  v7.0.1 and `astral-sh/setup-uv` from v6 to v10.3.3, which clears GitHub's Node.js 20 deprecation
  warning. Each `uses:` names a full commit SHA with the release in a comment, so a moved tag
  cannot change what CI runs. `tests/test_ci_workflows.py` checks every workflow for this.
- **Pull requests are open to collaborators only.** Anyone can still open an issue. Every change
  to `main` needs a pull request with green CI, resolved threads and an approval from the
  maintainers team, which `.github/CODEOWNERS` makes the owner of every file. CONTRIBUTING and the
  README now say so, and CONTRIBUTING describes the `protect main` ruleset.

## [0.2.0] - 2026-11-09

### Added

- **A release zip Spec Kit can install by URL.** Pushing a `vX.Y.Z` tag runs
  `.github/workflows/release.yml`, which builds the pack with `extension.yml` at the archive root
  (plus the README and LICENSE) and attaches it to a GitHub release. It refuses to build when the
  tag and the pack version disagree. A GitHub source archive cannot serve this: Spec Kit looks for
  `extension.yml` at most one folder deep.
- **A commit-identity check.** `tools/check_commit_identity.py` fails when a commit's author or
  committer name or email holds a term from a private denylist. CI runs it when the
  `AIDIDIT_PII_DENYLIST` Actions secret is set; a hit names the commit and field, never the term.
- A code of conduct, issue and pull-request templates, and an email fallback in the security
  policy.
- The README's Quick Start names the Python floor (3.11), checked against `pyproject.toml`.
- The field guide in `docs/`: a lifecycle guide, a flow for each of the seven stages, the
  practitioner panel, boards and lane runners, the CLI, a brand book, and a sources page holding
  every citation, checked and dated.
- A branded Mermaid house style. It is light and dark safe by measurement: every diagram must use it,
  and `tests/test_diagrams.py` re-checks its WCAG 2.2 contrast against GitHub's light, dark and dark
  dimmed page colours.
- Citation anchors are now link-checked, so a citation to a missing source fails the suite.
- A banner for the README.
- **A citation verifier.** The pack ships `scripts/verify-quote.py`, a standard-library Python
  script that checks quoted strings against a cited page (URL or file) on any OS. It removes tags,
  folds case, whitespace, curly quotes and dashes, and checks a positive and a negative control on
  every run. Exit `0` is FOUND, `3` is MISSING, and `4` is INSTRUMENT-FAILURE; a crash is never
  reported as a missing quote, and neither is a quote missing from text the controls cannot vouch
  for (a byline found only in a script's data, or bytes the page's charset could not decode). The
  charset comes from the server, then the page's `<meta>` tag, decoded the way browsers do. A quote
  missing from a page whose controls passed is a finding about the citation, however many are
  missing; an elided quote is checked one continuous piece at a time. Lanes stop improvising a matcher with `grep`, which aborts on
  Windows Git Bash and was read as "every quote missing".

### Changed

- **Citation checks use the verifier.** `practitioner-panel.md` section 3 shows how to call
  `verify-quote.py` and treats any exit other than `0` or `3` as an instrument failure. The panel
  guide's Step 6 and the failure-mode table point at it.

- **Proportional panels.** The practitioner panel now convenes only where a judgement is real. The
  rules live once, in `panel-guide.md` Part 0, and each stage cites the one it obeys:
  - P1: mechanical findings are fixed directly, in every round.
  - P2: in a lane, a handoff with no open question answers Step 1's intent check.
  - P3: a retro vet is one reviewer applying every lens, with no citations.
  - P4: "once" means one ruling per finding, in one round.
  - P5: grooming skips the panel when the candidates already fit the WIP limit.
- The `inline` runner's prompt files reference the lane contract by path instead of copying it.
- A retro's High-cost stage-efficiency rows must become an action or a proposed edit.
- **The lane contract closes its loops.** Five rules are defined once in `lane-contract.md`, and
  every stage that relies on one points at it:
  - Merge check: a human's "merged" is a cue to ask the host. Investigate starts only when the
    host reports `MERGED` with a merge time, never on `merge_commit_sha`.
  - Runtime state: every clean-tree gate ignores the board and the lane folders, and no lane
    commits the board. You own it.
  - Upstream route: a lesson about the installed pack is drafted as an issue for the pack's own
    repository, not filed as project work no lane may do. A project method file is edited only by
    the lane claimed for it.
  - Widening allowed paths: Draft re-derives them from `tasks.md`, and a widening is checked
    against sibling lanes before handoff.
  - Required checks: with none marked required, every check that ran on the PR head counts.
- **One rule, one place.** Rules the pack stated more than once now live in one file, and the
  others point there: the secret scan (one list of credential shapes, one `<redacted:{kind}>`
  marker, refuse only when redaction fails), the decision-record format (now with a `Recorded:`
  UTC timestamp), the retro commit subject, and the rule for PR body edits (once per phase
  boundary, not after every commit).
- Gaps the dogfood lane hit are now written down. Ideate skips the panel when B1 to B4 find
  nothing. Specify's `[NEEDS CLARIFICATION]` markers go to the clarify loop instead of waiting.
  Draft asks Spec Kit's tasks step for TDD explicitly, and passes `GIT_BRANCH_NAME` only where the
  git hook exists. A mutation shared across test layers must reach each one. Iterate counts the
  pre-sweep analyze pass as round 1 and re-runs touched gates after the panel's fixes. Deliver
  sits out lenses with nothing to review and acts on checked evidence, not bare citations.
  pr-prep accepts a terminal transcript as CLI visual proof. pr-review's verdict follows its
  blocking findings. Investigate records signals a system lacks as `absent (verified: <how>)`.
- **Breaking:** the seven short stage aliases (`speckit.assemble`, `speckit.draft`, and the rest)
  are gone. They doubled the skill list, sat in Spec Kit core's unprefixed namespace, and collided
  with other `speckit.*` workflows. Use the `speckit.aididit.*` names.
- The shared guides name commands by their canonical names (`/speckit.aididit.ideate`) instead of
  `__SPECKIT_COMMAND_*__` tokens. Spec Kit renders tokens only in registered command files and copies
  the guides verbatim, so lanes were reading raw tokens.
- `aididit` prints "AI Did It" instead of the dotted wordmark, so its output reads the same under
  every console code page.
- `aididit install` warns when the project's constitution is still Spec Kit's unfilled template,
  because the panel judges scope against it.
- The PII scan now covers `.svg` files.
- The pack's lifecycle diagrams use the house style; its handoff sequence diagram is now a flowchart.
- The lane workflow asks for the same Spec Kit range as the pack (`>=1.3.0,<2.0.0`).
- The PII scan allows the project's published contact address and no other address on its domain.

### Removed

- `docs/pr-screenshots/`: before-and-after renders that only pull requests linked to.

## [0.1.0] - 2026-11-05

### Added

- The A·I·DID·IT Spec Kit extension: seven lifecycle stages (Assemble, Ideate, Draft, Iterate,
  Deliver, Investigate, Tidy) and seven simulated teammates (Product Owner, Architect, QA, DevSec,
  DevOps, PR Prep, PR Review).
- Shared references: lifecycle, lane contract, lane runner, practitioner panel, board adapters,
  retro, and the TDD / BDD / Clean Code / Conventional Commits / prompt-crafting disciplines.
- Board providers: markdown (default), GitHub Issues, Jira (via an Atlassian MCP server).
- Lane runners: inline (default), claude (headless), claude-remote (observable sessions).
- `aididit` CLI with `install`, `uninstall` and `doctor`, bundling Spec Kit 1.3+.
- Single-lane Spec Kit workflow `aididit-lane` with a merge gate.
