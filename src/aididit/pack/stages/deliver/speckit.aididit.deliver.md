---
description: "Deliver stage (link 4 of a lane): practitioner panel review of the open PR, bot and CI rounds, thread resolution and every required check green, then a hard stop for the human merge (or an automatic merge when delivery.merge is auto)."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). In a lane the input is `lane:<lane-id> item:<item-ref>`. Otherwise it is `item:<item-ref>` (the single-lane workflow passes this; take the PR from the direct-run handoff note), a PR number, a PR URL, or nothing (use the open PR for the current branch). **Without `lane:` this is a direct run:** it never starts the next link; it writes the handoff note and tells the human or caller the next command.

> "Defend what you built. The merge happens when the panel and the bots are satisfied."

This is the **Deliver** stage, the second D of the A·I·DID·IT lifecycle and **link 4 of a lane**. It consumes the open PR that Iterate produced and runs in **reviewer mode**: practitioner panel, bot rounds, thread resolution, required checks green. Lifecycle overview: `.specify/extensions/aididit/shared/lifecycle.md`.

| Deliver owns | Deliver does not own |
|---|---|
| Panel review, bot and CI rounds, thread resolution, a green PR, the deliver retro | **The merge** (the human's, unless `delivery.merge` is `auto`); **closing work items** (Tidy); **verifying the deployment or the running system** (Investigate) |

**Why the split:** a stage cannot credibly verify its own delivery, and a work item closed on the strength of a green PR has not been shown to work anywhere.

Commands below are written for GitHub (`gh`). On another git host use its equivalent.

---

## Load-When Map

| Step | Load |
|---|---|
| Step 0, Step 1 | `.specify/extensions/aididit/aididit-config.yml`; in a lane, `.specify/extensions/aididit/shared/lane-contract.md` and the handoff note |
| Any decision gate | `.specify/extensions/aididit/shared/practitioner-panel.md` |
| Phase 1 Panel | `__SPECKIT_COMMAND_AIDIDIT_PR-REVIEW__` (the review method), `.specify/extensions/aididit/shared/panel-guide.md` |
| Fix commits, review comments | `.specify/extensions/aididit/shared/disciplines/conventional-commits.md` (Conventional Commits and Conventional Comments), `.specify/extensions/aididit/shared/disciplines/tdd.md` |
| Phase 4 Retro | `.specify/extensions/aididit/shared/retro.md` |
| Handoff | `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, `.specify/extensions/aididit/shared/lane-runner.md` |
| Any work item read or write | `.specify/extensions/aididit/shared/board-adapters.md` |

---

## Decision Gates

Judgement calls use the same **Decide** procedure as the Draft stage: state the question with two to four options, get the answer, record it in `specs/<feature>/decisions.md` in the decision-record format (`practitioner-panel.md` section 8), apply it.

| How Deliver was started | Who answers |
|---|---|
| **In a lane** | The practitioner panel (`practitioner-panel.md`, `panel.practitioners`, honouring `panel.require_citations`). **Never the human.** |
| **Invoked directly** | The human. For architectural or scope questions, convene the panel first and present its pros and cons as the options. |

| Decision | Where | Options |
|---|---|---|
| Intent confirmation | Step 1 | Proceed / Address blockers first / Cancel |
| Panel finding, judgement call | Phase 1 | Apply the panel's fix / Defer with rationale / Push back on the panel |
| Bot finding family | Phase 2 | Apply fix / Dismiss with reason |
| Thread disagreement | Phase 3 | Apply suggested change / Resolve with a rebuttal comment |

The stop point (Phase 5) is **not** a decision gate: nothing is asked and nothing is decided there.

Hard halts are not decisions either. A failed pre-commit gate, a missing PR or a dirty tree at handoff stops the stage and is reported; no panel overrides it.

---

## Step 0 — Prerequisites and Context

> Report: "Locating the PR and snapshotting its state..."

1. **Config.** Read `.specify/extensions/aididit/aididit-config.yml`. In a lane, take the merge mode from the handoff note's `merge:` field; otherwise from `delivery.merge`. Cache `delivery.default_branch`, `panel.practitioners`, `panel.require_citations`, `lanes.runner`, `retro.directory`, `board.provider`.
2. **Lane or direct.** In a lane, read `.specify/aididit/lanes/<lane-id>/handoff.md` and confirm it names this stage, the work item, the branch and the PR. Confirm now that you can reach the note's `report to:` address (for the `claude-remote` runner, the orchestrator session under its exact name); "report" is defined in `lane-contract.md` §3. An unreachable address found only at the stop point costs hours.
3. **Locate the PR.**
   ```bash
   gh pr view <arg-or-empty> --json number,url,state,headRefName,baseRefName,mergeable,mergeStateStatus,reviewDecision
   ```
   No open PR: **STOP** with "No open PR for this branch. Run `__SPECKIT_COMMAND_AIDIDIT_ITERATE__` first, or pass a PR number." Verify `state` is `OPEN`, `mergeable` is not `CONFLICTING`, and note `mergeStateStatus`.
4. **Snapshot.** `gh pr view <n> --json reviews,comments,labels,statusCheckRollup`. Keep it; the retro compares the before and after state.
5. **Board.** `read_item` the work item via the board adapter and confirm it is in **In Review**; if Iterate did not move it, run `move_in_review` with the PR URL.
6. **Clean-tree rule.** Every "`git status --short` is empty" check below ignores changes to `board.markdown_path` and anything under `.specify/aididit/lanes/`, which are expected runtime state (`lane-contract.md` §2). Retros under `<retro.directory>` are not exempt: this stage commits its retro by explicit path (Phase 4).
7. **Resume point.** If the deliver retro is already committed and the PR is green, resume at Phase 5. If the PR is already merged, you are a duplicate: stop and report.

---

## Step 1 — Diagnose Intent

> Report: "Diagnosing deliver intent for PR <n>..."

In three lines: **which PR** (number, title, base and head branches); **its state now** (open threads, failing checks, pending reviews); **what Iterate changed** (commits since the branch was cut). Surface merge blockers (red check, conflicts, requested changes) immediately.

**Decide**: "Proceed" / "Address blockers first (say which)" / "Cancel". In a lane, `panel-guide.md` P2 decides whether this needs the panel; blockers surfaced above are an open question, so they convene it.

---

## Phase 1 — Practitioner Panel Review

> Report: "Convening the practitioner panel on the PR diff..."

1. **Compose the panel from the surfaces the diff touches.** This stage owns the mapping; the review method has none.

   | Surface | Practitioner lens |
   |---|---|
   | Tests, TDD discipline | Kent Beck |
   | CI/CD, the deployment pipeline | Dave Farley |
   | Refactoring, architecture moves, ADRs | Martin Fowler |
   | Clean code, SOLID, comments that claim facts | Robert C. Martin |
   | Service boundaries, autonomous services | Udi Dahan |

   If `panel.practitioners` names different people, map each surface to the closest configured lens and say so. A lens whose surface the diff does not touch sits out; record which and why in the handoff note.
2. **Run each reviewer independently.** If your agent can start sub-agents, start one per lens in parallel, each with a fresh context scoped to the PR diff and its lens. Otherwise run the lenses one after another and do not carry one lens's conclusions into the next. Each applies `__SPECKIT_COMMAND_AIDIDIT_PR-REVIEW__` as its method. When `panel.require_citations` is true, every judgement cites its source per `panel-guide.md`. **Act on evidence, not on a citation.** Before acting on a finding, check its repository evidence yourself: the file and line, the measured value. A citation nobody can follow (a book chapter with no quote or locator) is context, never the reason to change code; a finding with neither checkable evidence nor a checkable citation is recorded and not acted on.
3. **Post findings as Conventional Comments** (`praise:`, `issue (blocking):`, `suggestion (non-blocking):` and so on, per `disciplines/conventional-commits.md`) with `gh pr comment` or review comments. **Reviewers never approve or request changes**: no `gh pr review --approve` and no `--request-changes`. Approval belongs to a human.
4. **Aggregate** by severity (CRITICAL / HIGH / MEDIUM / LOW, matching blocker / major / minor / nit) and by family (security, correctness, design, style).
5. **Fix.** One atomic commit per family per round, with a Conventional Commit message. Code fixes follow red/green/refactor (`disciplines/tdd.md`). Pre-commit gates (linters, security scanners, local tests) must pass before every fix commit and are never bypassed; a failing gate halts the round and is reported.
   - **Triage by the file a fix edits.** If the lane keeps a kill-test table (each guard paired with a mutation observed red and a control observed green), a refactor or assertion-tightening that edits an *asserting* file but fixes no correctness defect goes to **one follow-up work item**: editing it would invalidate recorded rows. A factual error anywhere (a false comment, a wrong doc) is fixed in the lane. A correctness defect in an asserting file is fixed in the lane, and every row it touches is re-run from its green control.
6. **Loop.** Re-run the panel if substantive code changed. Exit after a round with no new CRITICAL or HIGH finding, or at `loops.analyze_max_rounds` rounds (the loop budget in `.specify/extensions/aididit/shared/lane-contract.md`). Fix the mechanical leftovers directly (`panel-guide.md` P1). Every judgement finding left gets **one** panel ruling, all in one decision round (`panel-guide.md` P4): fix now, accept with a note, or file a follow-up work item with the board adapter's `create_item`. No further round. Record each round's finding count in the handoff note.
7. **Kill sweep, once, last.** If the lane keeps a kill-test table, re-run it only after every panel round, including the convergence round, has finished editing asserting files; a sweep run earlier is invalidated by the next edit. Scope the re-run set by intersecting `git diff --name-only origin/<delivery.default_branch>..HEAD` with every row's asserting and mutated files; the rows left out must intersect nothing. Each re-run row needs both observations: green on the unmutated tree, red under its named mutation. A large re-sweep may run as a temporary CI matrix on the branch (no secrets, mutations applied inside the job and never committed), deleted before the stop point and verified gone with `git diff --name-status <merge-base>..HEAD -- .github`. [Inference] The row count at which that pays off has not been measured.

---

## Standing Rule — Refresh the PR Body at Each Phase Boundary

Commits on the PR branch make the PR body stale: panel fixes, bot fixes, the retro commit, a merge from the default branch. Regenerate the body (for example with `__SPECKIT_COMMAND_AIDIDIT_PR-PREP__`) and apply it with `gh pr edit <n> --body-file <path>` once per phase boundary: after a panel round's fixes, after a bot round's fixes, after the retro commit, and always before the stop point. Batching follows pr-prep's **PR body edits** rule: each edit fires a `pull_request: edited` event, which can cancel in-flight CI runs. The body reflects the new commits, any architectural pivot a panel ruling caused, and any new ADR. **Why:** a reviewer reading a body that contradicts the code reviews the wrong change.

Keep the body file outside tracked paths (or in an ignored directory) so it never lands in the PR.

---

## Phase 2 — Bot and CI Rounds

> Report: "Working the automated review findings and required checks..."

For each bot that commented:

1. **Fetch every open thread, across the whole diff**, not only the latest comment.
2. **Group findings by family**: same file, same bug class, same superseded decision repeated in several places, same fragile pattern.
3. **Fix a whole family in one commit.** Fixing one instance per round produces round after round of the same finding.
4. **Resolve threads with live IDs.** On GitHub, `resolveReviewThread` takes the review **thread** node ID (prefix `PRRT_`), not the review **comment** ID (prefix `PRRC_`). Fetch it with GraphQL immediately before resolving; never reuse a cached ID.
5. **Budget.** At most `loops.analyze_max_rounds` bot-review rounds, and at most `loops.analyze_max_rounds` fix attempts per failing CI check. Stop early when no CRITICAL or HIGH finding remains. At the cap the panel rules once on what is left; a check that still fails at the cap goes to the panel to decide flake or real, never to another blind retry. Record each round's count in the handoff note.

Common bot behaviour worth knowing:

- AI review bots sometimes flag agent-instruction paths (for example `.specify/` or `.claude/`) as unusual. Dismiss with a stated reason.
- Coverage bots can report line coverage while branch coverage drifts; make sure both are reported.
- Dependency scanners: upgrade, or record a documented exception next to the dependency declaration.

---

## Phase 3 — Thread Resolution

After the Phase 1 and Phase 2 fixes land:

1. Re-fetch all open threads.
2. Resolve each thread whose finding a commit addressed, with its live thread ID.
3. Where you deliberately diverged from a bot or a reviewer, reply with the decision and its reason (as a Conventional Comment), then resolve.

---

## Phase 4 — Deliver Retro (before the stop point)

> Report: "Running the end-of-Deliver retro..."

Run `.specify/extensions/aididit/shared/retro.md` for stage `deliver`. It is unconditional: never ask whether to run it. Lessons to look for here:

- Panel finding categories that recurred: candidate rules.
- Bot finding categories that recurred: candidate pre-commit hooks or grep gates.
- Thread-resolution friction (stale IDs, thread versus comment IDs).
- Merge-readiness surprises (branch behind, checks that did not attach).

**This is the last retro that can ride the PR.** After the merge, nothing uncommitted reaches the default branch through this lane. Commit the retro file (`<retro.directory>/<lane-id>/deliver.md`) by explicit path. The retro proposes rule and guide changes as actions for Tidy; it does not edit those files itself.

```bash
git status --short
git add <retro.directory>/<lane-id>/deliver.md
git commit -m "chore(retro): deliver-stage retro for <item-ref>"
git push
```

Then refresh the PR body and let the checks re-run. Uncommitted retro output is a **STOP**.

---

## Phase 5 — Stop Point: PR Green

> Report: "Assembling the stop-point state..."

### 5a — Retro-artifact verification (hard halt)

1. `git status --short` is empty.
2. `git log origin/<delivery.default_branch>..HEAD --oneline | grep "chore(retro):"` shows one retro commit for each retro-running stage that preceded this one on the branch (Draft, Iterate, and Deliver's own; Ideate's too if it rode the branch), and the matching files exist under `<retro.directory>/<lane-id>/`.

If either fails, name exactly what is missing. The stop-point report is not emitted until the retro output is committed, or the human states that a stage produced no retro file and why.

### 5b — Merge discipline

`git fetch origin` and `git merge origin/<delivery.default_branch>`; resolve conflicts; re-run **all** gates. In many repositories a merge commit does not dispatch CI. If the required checks do not attach to the new head, push a one-line non-merge commit (a Conventional `chore:`) so they do.

### 5c — State assembly

Verify each of these and report its **measured** value, never an assumed one:

- All required checks (`lane-contract.md` §7) green: zero failing, zero pending.
- Every bot and review thread resolved, or dismissed with a stated reason.
- `mergeable` is `MERGEABLE` and `mergeStateStatus` is not `BEHIND` or `DIRTY`. `BLOCKED` is acceptable only in human merge mode and only when `reviewDecision` is `REVIEW_REQUIRED` (branch protection is waiting for the human's approval, which is the stop point itself); any other `BLOCKED` means a required check or rule is still failing.
- The PR body was refreshed after the last commit.
- The panel and the bots are clean on the latest commit, or every remaining finding carries a ruling under the loop budget.

If any is false, keep working. The stop point is defined by this list, not by the stage running out of things to do.

### 5d — Merge mode

| `delivery.merge` | Action |
|---|---|
| `human` (default) | **Report and stop.** Do not run `gh pr merge`. Do not ask whether to merge. Do not watch a deployment. The human merges in the git host's UI when they choose; Investigate is started afterwards (see the handoff below). |
| `auto` (Full Auto Mode) | Deliver is the only merge owner, in every runner mode. Only when every 5c item holds: merge with the repository's configured merge method (`gh pr merge <n> --squash`, `--merge` or `--rebase`, whichever the repository allows). Never use `--admin` and never bypass branch protection. Record the merge SHA in the handoff note. If the host refuses the merge, report why and stop exactly as in `human` mode. |

Green is the stage's definition of done, not permission to merge. Only `delivery.merge: auto` grants that.

### 5e — Report

Emit the lane report (and report it per `lane-contract.md` §3 in a lane): PR URL, work item, measured check status, coverage, test counts, panel and bot round counts, ADRs, follow-up items filed, cross-lane or merge notes, and the merge SHA if `auto` merged it. Record the same on the work item with the board adapter's `comment`. The work item stays in **In Review**; moving it to Done is Tidy's.

---

## Handoff to Investigate

> Report: "Writing the handoff note for Investigate..."

**The next link is Investigate, not Tidy.** Handing straight to Tidy closes a work item on the strength of a green PR rather than a verified running system.

1. **Clean tree gate.** `git status --short` must be empty apart from runtime state (`lane-contract.md` §2). Never hand off a dirty tree.
2. **Write the handoff note** to `.specify/aididit/lanes/<lane-id>/handoff.md` in the format of `lane-contract.md` §3 (the PR URL, the merge SHA if `auto` merged it, follow-up items filed), and append the ledger entry. A direct run takes its lane id from the direct-run rule in `lane-contract.md` §3.
3. **Write Investigate's prompt** to `.specify/aididit/lanes/<lane-id>/investigate.prompt.md` per `disciplines/prompt-crafting.md`, so a cold session can start without this conversation, and read both files back (`lane-contract.md` §2):
   - Task: run `__SPECKIT_COMMAND_AIDIDIT_INVESTIGATE__` on the merged change; verify every acceptance criterion and every touched artifact against the **running** system; sweep for collateral damage; return a verdict.
   - Context: the handoff note, the PR URL, `spec.md` acceptance criteria, the retro files from Draft, Iterate and Deliver, follow-up items filed. Investigate resolves the merge commit itself and runs in the primary checkout on a detached `origin/<delivery.default_branch>`.
   - Rules: the null hypothesis is that the delivery failed; test-suite evidence is Iterate's proof and is not independent; every VERIFIED row cites a measured value; file findings, do not fix them; a REGRESSED verdict stops the lane before Tidy.
4. **Start the next link only after the merge**, with the arguments `lane:<lane-id> item:<item-ref>`:
   - `delivery.merge: human`: Deliver stops here. In a lane, the orchestrator starts Investigate once the merge check (`lane-contract.md` §1) passes, whether it saw the merge itself or the human said "merged <item-ref>"; a human running stages directly starts `__SPECKIT_COMMAND_AIDIDIT_INVESTIGATE__ item:<item-ref>` themselves after merging. Never start Investigate against an unmerged PR.
   - `delivery.merge: auto`: in a lane, start Investigate now per `.specify/extensions/aididit/shared/lane-runner.md` (`lanes.runner`). In a direct run, tell the human or caller the next command instead.

---

## Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| No open PR | Iterate was skipped, or the PR was closed | **STOP**; point at `__SPECKIT_COMMAND_AIDIDIT_ITERATE__` |
| A reviewer sub-agent runs out of context | Scope too wide | Re-run it scoped to specific files; report if it keeps failing |
| Panel or bot loop reaches `loops.analyze_max_rounds` | Disagreement, or findings at the reviewer's noise floor | The panel rules once on what is left; no further round; note it for the retro |
| Resolving a thread fails | Stale or wrong ID (comment ID instead of thread ID) | Re-fetch the live thread ID and retry once |
| A required check will not go green | Real failure, flake, or branch behind | At most `loops.analyze_max_rounds` fix attempts; then the panel decides flake or real. The stop point is not reached until it passes |
| A pre-commit gate fails on a fix commit | The fix broke something | Halt the round; fix the cause; never bypass the hook |
| Tempted to merge because everything is green | Reading "ready" as "authorised" | **Do not**, unless `delivery.merge` is `auto`. Report and stop |
| Merge refused in `auto` mode | Branch protection, required human review | Report the reason and stop as in `human` mode |

---

## Self-Check Before Handoff

- [ ] Panel review closed within the loop budget; per-round counts recorded; anything left carries a panel ruling.
- [ ] Every review comment posted uses Conventional Comments; no reviewer approved or requested changes.
- [ ] Every bot thread resolved or dismissed with a reason; CI fix attempts within budget.
- [ ] Kill sweep (if the lane keeps a kill-test table) ran once, after the last asserting-file edit, with a green control and a red mutation per re-run row.
- [ ] Deliver retro written and committed; Phase 5a passed.
- [ ] PR open and green (`human` mode), or merged by the host's normal rules with the SHA recorded (`auto` mode).
- [ ] No work item closed and no deployment verified by this stage.
- [ ] Handoff note on disk at `.specify/aididit/lanes/<lane-id>/handoff.md`; tree clean.

Any unchecked box: stop and fix it before the handoff.
