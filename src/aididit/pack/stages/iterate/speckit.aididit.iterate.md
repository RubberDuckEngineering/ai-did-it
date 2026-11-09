---
description: "Iterate stage (link 3 of a lane): implement tasks.md test-first with a kill-test ledger, commit in Conventional Commits, push, open the PR and run the budgeted post-implementation analyze loop."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). In a lane the input is `lane:<lane-id> item:<item-ref>`. Otherwise it is `item:<item-ref>` (the single-lane workflow passes this), a `specs/<feature>/` path, or a work item id. **Without `lane:` this is a direct run:** it never starts the next link; it writes the handoff note and tells the human or caller the next command.

Read the branch and the spec directory from the handoff note first (`.specify/aididit/lanes/<lane-id>/handoff.md`; a direct run derives `<lane-id>` from the item ref by the rule in `.specify/extensions/aididit/shared/lane-contract.md` §3). Only when there is no note, infer them: the branch from `git branch --show-current` (`<item-id>-<slug>`), the spec directory from the input or the branch. If neither works, ask.

> "Build it the way you said you would. The tests drive the code."

This is the **Iterate** stage, the second I of the A·I·DID·IT lifecycle and **link 3 of a lane**. Iterate is producer mode: writing code and accumulating commits. The next stage, Deliver, is reviewer mode. Lifecycle overview: `.specify/extensions/aididit/shared/lifecycle.md`. Conventions: `.specify/extensions/aididit/shared/pipeline-guide.md`.

**Output:** every task in `tasks.md` done test-first; a kill-test ledger in `specs/<feature>/evidence.md`; a pushed branch; an open PR; a post-implementation analyze loop closed within budget; a retro; a handoff note for Deliver.

---

## Load-When Map

| Step | Load |
|---|---|
| Step 0, Step 1 | `.specify/extensions/aididit/aididit-config.yml`; `specs/<feature>/tasks.md` and the acceptance criteria in `spec.md`; in a lane, `.specify/extensions/aididit/shared/lane-contract.md` |
| Phase 1, before the first red | `.specify/extensions/aididit/shared/disciplines/tdd.md`, `.specify/extensions/aididit/shared/disciplines/bdd.md`, `.specify/extensions/aididit/shared/disciplines/clean-code.md`; any project guide that governs the paths `tasks.md` names (key on the paths, not the task wording) |
| Phase 2 | `.specify/extensions/aididit/shared/disciplines/conventional-commits.md` |
| Phase 3 | `__SPECKIT_COMMAND_AIDIDIT_PR-PREP__`; `.specify/extensions/aididit/shared/board-adapters.md` |
| Phase 4 | `.specify/extensions/aididit/shared/pipeline-guide.md` § Analyze practice |
| Step N | `.specify/extensions/aididit/shared/retro.md` |
| Step N+1 | `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, `.specify/extensions/aididit/shared/lane-runner.md` |

---

## Decision Gates

Same procedure as the Draft stage (**Decide**): in a lane, the practitioner panel answers per `.specify/extensions/aididit/shared/practitioner-panel.md` and never the human; invoked directly, the human answers. Every decision is appended to `specs/<feature>/decisions.md` with a generated UTC timestamp.

Most of Iterate is mechanical. Decision points: intent confirmation (Step 1), the occasional design judgement inside a task ("unit or integration test?", "which seam to fake?"), and judgement-call analyze findings (Phase 4).

**Pre-commit gates are hard halts, never decisions.** Linters, security scanners and the local test suite must pass before every commit. A failure stops the loop until fixed; no panel waives it, and `git commit --no-verify` is never used without the human's explicit say-so.

---

## Step 0 — Prerequisites and Context

> Report: "Validating prerequisites..."

1. **Repository and config** as in Draft Step 0: git root, `origin`, `.specify/`, `.specify/extensions/aididit/aididit-config.yml`.
2. **Spec artifacts.** `specs/<feature>/` and `specs/<feature>/tasks.md` must exist. If not, **STOP**: run `__SPECKIT_COMMAND_AIDIDIT_DRAFT__` first.
3. **Git host CLI.** `gh auth status` must pass (or the equivalent CLI if `origin` is not GitHub). Without it Phase 3 cannot open the PR: **STOP** now rather than after the work.
4. **Branch.** `git branch --show-current` must match the branch named in the handoff note (with no note, the feature's `<item-id>-<slug>`). Mismatch: in a lane, **STOP**; invoked directly, ask the human whether to switch or continue, and record the answer.
5. **Lane or direct**, and **resume point**: read the handoff note if there is one. If tasks are already marked `[X]`, or an Iterate entry exists in `decisions.md`, resume from the first unfinished task instead of starting over. If a handoff note addressed to Deliver already exists, you are a duplicate: stop and report.

---

## Step 1 — Diagnose Intent

> Report: "Diagnosing Iterate intent before the first test..."

State in three lines: which spec, how many tasks (and how many already `[X]`), and the first task to take. **Decide**: "Proceed with TDD on <task>" / "Start from a different task (say which)" / "Cancel". In a lane, `panel-guide.md` P2 decides whether this needs the panel: a handoff with no open ordering question is answered "proceed, per handoff".

---

## Phase 1 — Test-Driven Implementation

> Report: "Beginning the TDD loop..."

Execute `tasks.md` in its dependency order, as `__SPECKIT_COMMAND_IMPLEMENT__` would, but one task at a time under this cycle (`.specify/extensions/aididit/shared/disciplines/tdd.md`):

1. **Red.** Write the failing test. Run it. Record the failure message you saw. A test that has never been seen failing has not been shown to test anything.
2. **Green.** Write the least code that passes. Run it; see it pass.
3. **Refactor.** Clean names and structure, remove duplication (`.specify/extensions/aididit/shared/disciplines/clean-code.md`); the suite stays green.
4. **Mark the task `[X]`** in `tasks.md`.
5. **Commit** (Phase 2 rules).

### Per-task gates

- **Branches.** Every new conditional (`if`, ternary, `&&`, `||`, guard clause) has at least one test that takes the true branch and one that takes the false branch.
- **Public contracts.** A change to an interface in `contracts/` needs a behavioural test. A structural test (the type exists, the method has this name) is not enough.
- **No dead code.** The test is deletion, not coverage: delete the code, run the suite, and if it stays green the code was dead. Coverage proves execution, never need.
- **Delegated work.** If a sub-agent implements a task, its brief must require a red observation (the failure message seen before the code existed) for every test it reports. A test written after its code is reported as such and gets a kill row before the task counts as done.

### Every guard must be able to fail, and to pass

A guard is anything that asserts: a test, a CI check, a validation script, a lint rule. For each guard this work adds, record a row in the kill-test table in `specs/<feature>/evidence.md` (format in `.specify/extensions/aididit/shared/pipeline-guide.md`). A row needs **both** observations:

- **Green control:** the guard passes on the unmutated tree. A guard that cannot pass on a clean tree is as useless as one that cannot fail.
- **Red under a named mutation:** you changed the production code (or input) the guard protects, and the guard failed. Name the exact mutation.

Mutate from **outside** the guard's own blast radius. A mutation that disables, skips or de-collects the asserting test produces "did not run", which is **not** red. Revert every mutation after observing it. A claimed red with no recorded mutation does not count.

**Why:** a guard that cannot fail reads as rigour and survives review while protecting nothing.

### Test-double contract fidelity

A fake, stub or mock states a contract about a real dependency, and an unverified contract is fiction. Before faking any part of a third-party dependency:

1. Read that dependency's **installed** source for the behaviour you fake (the copy in the lockfile-resolved package directory, not its docs or your memory). Cite the version in a comment beside the double or in `evidence.md`.
2. The double must not **produce** anything the real dependency cannot (a value, an error, a synchronous return where the real one is async).
3. The double must not **omit an ordering** the real dependency can produce (a callback that fires only after network round-trips, an event that can arrive before the response). This half is the dangerous one: it leaves the whole suite green.
4. Re-verify on every dependency version bump.

**Why:** fakes that invoke a callback earlier than the real dependency does can leave a whole suite green while production hangs, because the tests encode the same wrong belief as the code.

### Evidence labels

Any claim in a commit message, `evidence.md`, the PR body or the handoff note that you have not observed is labelled `[Inference]`, `[Speculation]` or `[Unverified]`. Counts, sizes and statuses are stated "as at `<SHA>`" or "as at `<UTC time>`". A negative observation ("no run was triggered") made right after an action may just mean "not yet": re-observe after a settling interval, or put the time in the claim.

### Mid-Iterate handoff

If the work will not fit in one session, stop at a task boundary with a clean tree, run the retro (Step N), and hand off (Step N+1) to `__SPECKIT_COMMAND_AIDIDIT_ITERATE__` itself. The note names the last finished task; the next session resumes from it.

---

## Phase 2 — Commit Discipline

- **Format:** Conventional Commits, `type(scope): description`, per `.specify/extensions/aididit/shared/disciplines/conventional-commits.md`. Reference the work item id in a `Refs: <item-id>` footer.
- **One commit per task** by default.
- **Atomic doc-code commits.** A production change that alters behaviour documented in a spec artifact (`spec.md`, `plan.md`, `data-model.md`, `contracts/`, `quickstart.md`) updates those artifacts **in the same commit**. Separate commits create drift that analyze must clean up later.
  - **Evidence ledgers are spec artifacts.** If a commit message presents measured results ("12 mutations, each observed red with a green control"), `evidence.md` with those rows is in that commit's diff. Otherwise the claim exists only in prose nobody can re-run.
  - **Other features' artifacts too.** If a change alters behaviour another feature documents, grep `specs/` for the changed behaviour (a status code, a log level, a renamed test) and update those artifacts in the same commit.
  - **Timing.** While iterating on a hypothesis that is not yet green, spec amendments may wait in the working tree; they land with the code in the commit that turns it green, so documented behaviour matches verified code.
- **Stage by explicit path.** Never `git add -A` or `git add .`; in a lane, sibling lanes may share the object store.
- **Never** `--no-verify` without the human's say-so. **Never** force-push in Iterate.
- **Ordering with a mutation sweep.** If `tasks.md` schedules a kill-sweep commit group, run one post-implementation analyze pass (Phase 4) and land its fixes to asserting files **before** the sweep. That pass is Phase 4's round 1 and counts toward `loops.analyze_max_rounds`. An edit to an asserting file after the sweep invalidates the rows already recorded.

---

## Phase 3 — Push and Open the PR

> Report: "Pushing the branch and opening the PR..."

1. **Reconcile the Definition-of-Done checkboxes** in `tasks.md` before pushing: tick each one the work genuinely satisfies, and leave the rest with a reason. `grep -c '^- \[ \]' specs/<feature>/tasks.md` tells you what is open. A box ticked to appease a gate is a false delivery signal.
2. **Merge the default branch:** `git fetch origin && git merge origin/<delivery.default_branch>`; resolve conflicts; re-run every gate (tests, coverage, linters, scanners). If a lockfile changed, reinstall dependencies first.
3. **Push:** `git push -u origin <branch>` on the first push, `git push` after.
4. **Open the PR** with `__SPECKIT_COMMAND_AIDIDIT_PR-PREP__`, which composes the body from `spec.md`, `tasks.md` and `evidence.md` and opens it with `gh pr create --title "<conventional title>" --body-file <path>` (write the body to a temporary file outside the repository, or to a git-ignored path). The body links the work item, summarises the acceptance criteria and their tests, includes the kill-test table, and, if the diff changes rendered UI, embeds before/after screenshots or says `No visual change — <reason>`.
5. Record the PR URL. Move the work item to **In Review** via the board adapter (`move_in_review`), with a comment linking the PR.

---

## Phase 4 — Post-Implementation Analyze Loop (at most `loops.analyze_max_rounds` rounds)

> Report: "Running the post-implementation analyze loop..."

The same budgeted loop as Draft Phase 5, now comparing the code as shipped against the spec as planned. Each round runs `__SPECKIT_COMMAND_ANALYZE__` (in a fresh read-only sub-agent if your agent supports one):

1. **First round: reconcile the whole spec directory at once.** Grep all of `specs/<feature>/` and the ADRs for planning-tense vocabulary, for example `forecast|\(planned\)|Proposed|\[Unverified|will be`, and reconcile every hit. A hand-picked file list misses files. Typical findings: `~` estimates in `tasks.md` that now have real counts (add an as-shipped row with any consolidation reason), stale Constitution Check rows, ADR status still Proposed, requirement citations that drifted in refactors.
2. **Fix atomically.** One commit per fix batch touching every affected artifact. Check drift introduced by the previous round first.
3. **Keep fixes out of the kill ledger's blast radius.** Put rationale in spec artifacts, never in comments inside asserting files (the guard, its helpers, its fixtures). If a fix must change an asserting file, even a comment, re-observe the affected kill rows from their green control before any ledger claim.
4. **Order heavy runs** as coverage, then the last sweep round, then the full suite. An analyze fix after implementation reopens coverage before the next sweep round.
5. **Exit** after a round with no CRITICAL or HIGH finding, or at `loops.analyze_max_rounds`. Fix the mechanical leftovers directly (`panel-guide.md` P1). The panel then rules **once**, in one decision round (`panel-guide.md` P4), on every judgement finding left: **fix now** (only if it would make the build wrong or untestable), **accept with a note**, or **follow-up work item**. No further rounds. A red test or a coverage gap is never accepted with a note; the budget changes how findings are handled, not the quality bar. After applying the fix-now items, re-run the gates they touch (the kill rows of any changed asserting file, coverage, the full suite) and grep every changed id across `specs/<feature>/`. That is a check, not another round.

Record per-round counts in `spec.md` and the handoff note. Push the fixes.

---

## Step N — Retro

Run the retro per `.specify/extensions/aididit/shared/retro.md`, unconditionally, into `<retro.directory>/`. Iterate-specific things to look for: tests written after their code, missed branches, double-fidelity problems, guards that could not fail or could not pass, commit-format drift, PR-body friction, analyze findings that recurred two or more times (candidates for Tidy to graduate into rules).

Commit the retro file (`chore(retro): iterate-stage retro for <item-ref>`, the retro commit subject in `retro.md`) and push. Uncommitted retro output is a **STOP**. Proposed edits to the constitution, instruction files or pack files go into the handoff note for Tidy to file as work items, never into the files themselves.

---

## Step N+1 — Handoff to Deliver

1. **Clean tree gate.** `git status --short` must be empty apart from runtime state (`lane-contract.md` §2), and the branch pushed. Never hand off a dirty tree.
2. **Write the handoff note** to `.specify/aididit/lanes/<lane-id>/handoff.md`, in the format of `.specify/extensions/aididit/shared/lane-contract.md` §3, before the next link starts: work item id, lane id, branch, spec directory, PR URL, head SHA, analyze round counts, findings accepted with notes, follow-ups filed, any kill rows still `[Unverified]`.
3. **Write Deliver's prompt** to `.specify/aididit/lanes/<lane-id>/deliver.prompt.md` per `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`:
   - Task: run `__SPECKIT_COMMAND_AIDIDIT_DELIVER__` on PR `<URL>`: panel review, bot review rounds, resolve threads, drive required checks green, stop for the merge.
   - Context: the handoff note, the spec directory, `evidence.md`, the retro, the PR URL.
   - In a lane: "Operate under `.specify/extensions/aididit/shared/lane-contract.md`."

   Read both files back.
4. **Start the next link:** in a lane, start Deliver per `.specify/extensions/aididit/shared/lane-runner.md`. In a direct run, start nothing: report the handoff note path and the PR URL and tell the human or caller the next command, `__SPECKIT_COMMAND_AIDIDIT_DELIVER__ item:<item-ref>` (or `<PR URL>`).

---

## Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| No spec directory or `tasks.md` | Draft did not run | **STOP**; run `__SPECKIT_COMMAND_AIDIDIT_DRAFT__`. |
| Wrong branch | Started from another checkout | Lane: **STOP**. Direct: ask, record the answer, note it in the retro. |
| Test framework will not run | Not installed, wrong invocation | **STOP** the loop; report what was tried. |
| A guard will not go red under any outside mutation | It asserts nothing the code controls | Rewrite the guard; do not record the row as killed. |
| A guard is red on the clean tree | It cannot pass by construction | Fix the guard before claiming it. |
| `gh pr create` fails | Auth expired, network, bad body path | Report the error, retry once, then hand the human the exact command. |
| Analyze still finding at the cap | Noise floor reached | Panel rules once; apply fix-now items; hand off. CRITICAL or HIGH it cannot settle: **STOP**. |
| Context running out | `tasks.md` too large for one session | Mid-Iterate handoff to Iterate. |

---

## Self-Check Before Handoff

- [ ] Every task in `tasks.md` is `[X]`, each with a recorded red observation.
- [ ] Every new guard has a kill row with a green control and an observed red under a named outside mutation.
- [ ] Every faked third-party behaviour cites the installed version whose source was read.
- [ ] All commits are Conventional Commits; doc and evidence changes rode with their code.
- [ ] PR is open; work item is In Review.
- [ ] Post-implementation analyze closed within budget, per-round counts recorded, every remaining finding carries one panel ruling.
- [ ] Retro written, committed and pushed; `git status --short` is empty.
- [ ] Handoff note exists on disk at `.specify/aididit/lanes/<lane-id>/handoff.md`.
