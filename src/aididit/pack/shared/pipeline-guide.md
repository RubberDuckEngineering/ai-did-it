# Pipeline Guide

How the A·I·DID·IT stages chain, where their artifacts live, and the conventions every stage shares: branches, numbering, commits, pull requests, decisions, loop budgets and evidence. Stage commands point here instead of repeating these rules. Stack-agnostic: nothing here assumes a language, framework or cloud.

Related shared files: `.specify/extensions/aididit/shared/lifecycle.md` (the lifecycle overview), `.specify/extensions/aididit/shared/lane-contract.md` (rules for autonomous lanes), `.specify/extensions/aididit/shared/lane-runner.md` (how one link starts the next), `.specify/extensions/aididit/shared/practitioner-panel.md` (how the panel decides), `.specify/extensions/aididit/shared/board-adapters.md` (work item operations per tracker), `.specify/extensions/aididit/shared/retro.md` (the retro procedure), `.specify/extensions/aididit/shared/disciplines/` (TDD, BDD, clean code, Conventional Commits, prompt crafting).

---

## 1. How the stages chain

`A` assembles the lanes; each lane runs `I-DID-IT`, one link per letter.

| # | Stage | Command | Does | Produces | Then |
|---|---|---|---|---|---|
| 0 | Assemble | `/speckit.aididit.assemble` | Reads the board's Ready column, starts one lane per work item (at most `lanes.max_parallel` at once) | Lanes | Each lane starts at Ideate |
| 1 | Ideate | `/speckit.aididit.ideate` | Mode A (human-invoked): turns a raw idea into a work item. Mode B (lane link 1): interrogates an accepted item: premises, bundled scope, overlaps | A vetted, single-deliverable work item | Draft, or the lane ends if the item is declined (`move_done` `declined`) or already discharged (`move_done` `delivered`, summary `discharged: <null-result evidence>`) |
| 2 | Draft | `/speckit.aididit.draft` | Specify, clarify loop, plan, tasks, analyze loop | `specs/<feature>/` artifact set, ADRs | Iterate |
| 3 | Iterate | `/speckit.aididit.iterate` | TDD implementation, commits, push, PR, post-implementation analyze loop | Open PR, kill-test ledger | Deliver |
| 4 | Deliver | `/speckit.aididit.deliver` | Panel review, bot review rounds, thread resolution, required checks green | A green PR | **Stop for the merge** (`delivery.merge: human`); see `.specify/extensions/aididit/shared/lifecycle.md` for `auto` |
| 5 | Investigate | `/speckit.aididit.investigate` | After the merge: verifies the change against the running system, sweeps for collateral damage | Verdict: CLEAR, DEGRADED, REGRESSED or UNVERIFIABLE | Tidy, if the verdict permits |
| 6 | Tidy | `/speckit.aididit.tidy` | Closes the work item, files follow-ups, acts on the retros | Board and rules updated | End of lane |

Ideate (Mode B), Draft, Iterate, Deliver and Investigate each end with a retro (`.specify/extensions/aididit/shared/retro.md`). Tidy does not: it acts on the others' retros.

### Rules for every link

- **One stage per session where the runner allows it.** A fresh session per link starts re-grounded in the instructions, the repository and the handoff note, which limits context bloat and drift. `lanes.runner` decides how the next link starts (`.specify/extensions/aididit/shared/lane-runner.md`).
- **Clean tree before every handoff.** `git status --short` is empty apart from runtime state (`lane-contract.md` §2), that is changes to `board.markdown_path` and anything under `.specify/aididit/lanes/`; everything the stage produced, its retro included, is committed (and, from Iterate on, pushed).
- **The handoff note is on disk before the next link starts**, at `.specify/aididit/lanes/<lane-id>/handoff.md`, always in the format of `.specify/extensions/aididit/shared/lane-contract.md` §3. A killed session must not take state with it. The prompt for the next session goes beside it, at `.specify/aididit/lanes/<lane-id>/<next-link>.prompt.md`, written per `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`.
- **A run without `lane:` is a direct run** (a human, or the single-lane workflow): it never starts the next link; it writes the handoff note and tells the human or caller the next command.
- **In a lane, nobody asks the human anything** except at the merge. Judgement calls go to the practitioner panel (section 6).
- **Locate the resume point before re-running a stage.** A link can be re-entered after it finished but before its handoff fired. Check the stage's durable output and the next stage's artifact:

  | This stage's output | Next stage's artifact | Action |
  |---|---|---|
  | absent | absent | run the stage |
  | present | absent | resume at the handoff: re-verify load-bearing premises from the code, do not re-decide |
  | present | present | the chain moved on; you are a duplicate, stop and report |

  Re-running a decision stage blindly files duplicate work items and re-decides settled questions.

---

## 2. Where artifacts live

| What | Where | Notes |
|---|---|---|
| Feature artifacts | `specs/<feature>/` | Spec Kit convention; `<feature>` is the directory the specify step creates, usually `NNN-short-name` |
| Spec, plan, tasks | `specs/<feature>/spec.md`, `plan.md`, `tasks.md` | From the core specify, plan and tasks commands |
| Contracts, data model, research | `specs/<feature>/contracts/`, `data-model.md`, `research.md`, `quickstart.md` | Produced by plan where they apply |
| Decision ledger | `specs/<feature>/decisions.md` | Every gate decision (section 6) |
| Evidence ledger | `specs/<feature>/evidence.md` | Kill-test table, coverage figures, measured gate results (section 9) |
| ADRs | The project's ADR directory, `docs/adr/` unless the constitution names another | One file per decision, sequentially numbered |
| Constitution | `.specify/memory/constitution.md` | Spec Kit core; analyze treats conflicts as CRITICAL |
| Board (markdown provider) | `board.markdown_path`, default `.specify/aididit/board.md` | See `.specify/extensions/aididit/shared/board-adapters.md` |
| Retros | `retro.directory`, default `.specify/aididit/retros/` | One file per stage run |
| Lane state | `.specify/aididit/lanes/<lane-id>/` | `handoff.md`, plus `<link>.log` when the runner spawns processes |
| Extension files | `.specify/extensions/aididit/` | Replaced on upgrade; never write project state here |

Project-owned runtime state always lives under `.specify/aididit/`.

---

## 3. Branches

- **Name:** `<item-id>-<slug>`, for example `PROJ-123-rate-limit-login`. The slug is a few lowercase, hyphenated words from the work item title.
- No work item id (a direct Draft from a description): use the branch name the core specify step creates.
- Cut from an up-to-date `delivery.default_branch` (`git pull --ff-only`, then confirm `HEAD` equals `origin/<default_branch>`).
- In a lane, the branch (and worktree, if any) is assigned at kickoff. Confirm `git branch --show-current` before every commit; never touch another lane's branch, worktree or spec directory.

---

## 4. Numbers that must not collide

Spec directory numbers, ADR numbers and requirement ids are allocated sequentially, and concurrent lanes enumerate from the same base.

- In a lane, use the numbers pre-assigned at kickoff.
- Before finalising any number, re-derive it against `origin/<default_branch>` **and** every sibling lane branch. Local enumeration undercounts: sibling reservations exist only on their own branches.
- On a clash, **the work already on the default branch keeps its numbers.** The trailing lane renumbers from the maximum plus one, leaves the default branch's entries byte-identical, and fixes every reference to the renumbered entries.
- The same rule applies to any shared, append-only, numbered file. The structural fix is to key entries by lane or work item instead of by sequence.

---

## 5. Commits and pull requests

### Commits

- **Conventional Commits**, `type(scope): description`, per `.specify/extensions/aididit/shared/disciplines/conventional-commits.md`. Reference the work item in a `Refs: <item-id>` footer.
- **One commit per task** by default.
- **Atomic doc-code commits.** A code change that alters behaviour documented in a spec artifact updates that artifact in the same commit. This includes another feature's artifacts when the change crosses into its territory (grep `specs/` for the changed behaviour). Evidence ledgers are spec artifacts: a commit whose message presents measured results carries the ledger rows in its own diff. While iterating on a hypothesis that is not yet green, doc amendments may wait in the working tree and land with the commit that turns it green.
- **Stage by explicit path.** Never `git add -A` or `git add .`.
- Never `--no-verify` without the human's say-so. Never force-push before Deliver.
- Pre-commit gates (linters, scanners, local tests) are hard halts, not decisions.

### Pull requests

- Opened by Iterate through `/speckit.aididit.pr-prep`, with `gh pr create --body-file` (or the host's equivalent).
- **Title:** a Conventional Commit header.
- **Body:** link to the work item; acceptance criteria and the tests that prove them; the kill-test table; analyze round counts and any findings accepted with a note; follow-ups filed.
- **Visual proof for UI.** If the diff changes rendered output, embed before/after screenshots or a short clip. If a UI-path change has no visible effect, say `No visual change — <reason>`.
- Reviewed by `/speckit.aididit.pr-review` and the panel in Deliver. Review comments use Conventional Comments labels.
- Merged by the human unless `delivery.merge` is `auto`, in which case Deliver merges it. The orchestrator never merges.

---

## 6. Decisions

| Started how | Who decides |
|---|---|
| In a lane | The practitioner panel (`.specify/extensions/aididit/shared/practitioner-panel.md`), using `panel.practitioners`; with `panel.require_citations: true`, each member grounds the ruling in a citable public source or abstains |
| Directly by a human | The human. For architectural, format or scope-boundary questions, gather the panel's pros and cons first and present them as the options |

Every decision is appended to `specs/<feature>/decisions.md` in the decision-record format (`practitioner-panel.md` section 8). Retros and Tidy read this ledger; the human audits it after the fact.

Hard halts (dirty tree, failed pull, missing prerequisite, red pre-commit gate) are not decisions and are never waived by the panel.

---

## 7. Loop budget

Every iterative loop in a stage has a hard cap. Draft's clarify loop runs at most `loops.clarify_max_rounds` rounds. Draft's analyze loop and Iterate's post-implementation analyze loop each run at most `loops.analyze_max_rounds` rounds. Review-fix rounds, bot-review rounds and CI fix attempts in Deliver use the same cap as analyze.

1. **Exit early** after a round that leaves no CRITICAL or HIGH finding. There is no plateau exit: the first re-review of a revised spec routinely finds about as many findings as the first.
2. **When the loop ends with anything left** (at the cap, or MEDIUM and LOW after an early exit), the **panel rules once** on each item:
   - **fix now**, only if leaving it would make the build wrong or untestable;
   - **accept with a note** in the artifact;
   - **file a follow-up work item.**
3. **No further rounds after the ruling.**
4. **Record each round's count** in `spec.md` and the handoff note, for example `analyze rounds: 24 → 13 → 5; panel ruled on 5`, so spinning is visible.
5. A CRITICAL or HIGH finding the panel cannot settle stops the stage for the human. A constitution conflict is never accepted with a note.
6. A CI failure that survives the cap goes to the panel to decide flake versus real, never to another blind retry.

**Why:** after a few rounds a reviewer mostly finds wording, not defects, and Iterate's red/green catches a remaining spec error more cheaply than another round. The budget changes how leftover findings are handled; it never lets a red test or a coverage gap ship.

### Running the analyze loop

Spec Kit's core analyze command is a single read-only pass. Draft and Iterate run the loop around it: call `/speckit.analyze`, fix, call it again, within the budget above. The pack does not replace the core command.

---

## 8. Evidence discipline

- **Label what you have not observed:** `[Inference]`, `[Speculation]` or `[Unverified]`. Avoid absolute verbs ("prevents", "guarantees", "eliminates") unless quoting a verified source.
- **State counts, sizes and statuses "as at `<SHA>`" or "as at `<UTC time>`"**, never as standing facts.
- **Observations have a settling time.** A negative observation made right after an action ("no run was triggered", "the branch is clean") cannot be told apart from "not yet". Re-observe after the settling interval or put the time in the claim.
- **Measure before you write.** Run any count, line range, control or completeness claim ("every", "no other", "cannot") before a commit records it.
- **Generate timestamps** from `date -u`, a commit time or a tracker field. Never estimate them.
- **A null result is still a result.** A check that ran and found nothing is recorded with its method and figures, plus proof the instrument could have found something.

---

## 9. The kill-test table

Every guard (test, CI check, validation script, lint rule) must be able to **fail** and to **pass**. The evidence lives in `specs/<feature>/evidence.md`:

```markdown
| # | Guard (file :: name) | Protects | Mutation (outside the guard) | Green control (unmutated) | Under mutation | As at |
|---|---|---|---|---|---|---|
| K1 | tests/login.spec :: rejects sixth attempt | rate limit, AC-2 | change limit check `>= 5` to `> 5` | pass | FAIL: expected 429, got 200 | `<SHA>` |
```

- A row needs **both** observations. Green alone or red alone is an uncontrolled experiment.
- The mutation comes from **outside** the guard's blast radius: change the production code or input it protects. Disabling, skipping or de-collecting the test yields "did not run", which is not red.
- Name the exact mutation. A claimed red with no recorded mutation does not count.
- Revert each mutation after observing it.
- **A shared mutation must reach every layer.** When guards in different layers (in-process, subprocess, deployed) share one mutation, check that it reaches each layer's entry point. A mutation keyed on an in-process detail, such as an argument list or an injected fake, does not reach a subprocess, so the subprocess guard can never go red.
- An edit to an asserting file (the guard, its helpers, its fixtures), even a comment, invalidates its rows until re-observed from the green control.

---

## 10. Test doubles

A test double states a contract about a real dependency. Before faking any third-party behaviour, read that dependency's installed source for the behaviour you fake and cite the version. The double must not produce what the real dependency cannot, and must not omit an ordering the real dependency can produce. The second half is the dangerous one: fakes that invoke a callback earlier than the real dependency does can leave a whole suite green while production hangs. Re-verify on every version bump.

---

## 11. Spec practice (Draft)

- **Resolve filesystem facts mechanically.** Whether a path exists, which format a file uses, the next free ADR number: answer with `ls`, a glob or a read, and record it in Clarifications. Never pose it as a question.
- **Every acceptance criterion can fail alone.** Name a behaviour that fails it while its siblings pass. If none exists, it restates a sibling: fold it in or sharpen it.
- **Re-check absence claims.** "X does not exist" in a work item may have been falsified by the blocker that has since shipped. Grep for the mechanism, not the item's own wording.
- **Constitution beats a weaker work item threshold.** Encode the constitution's value and annotate the override on the line.
- **Annotate scope overlap** with items this one blocks, and decide whether the downstream item is still needed.
- **Carry over skips.** If an earlier delivery skipped or deferred a test pointing at this item, read why before clarifying.
- **Estimates carry a `~`** (`~12 tests`) until analyze reconciles them after implementation.
- **Changed invariants need a regression-guard task.** When the work permits something earlier work forbade, grep for guards asserting the old rule and rewrite them against the new rule, citing what supersedes them.
- **Census evidence sources at plan time.** Any telemetry the spec relies on for post-merge evidence is queried once now and must return a non-zero control count.

## 12. Analyze practice (Draft and Iterate)

- **Fresh eyes.** Run each analyze pass in a fresh, read-only context where the agent supports it, not as the author's own pass.
- **Drift first.** Each round first checks the previous round's edits: when a fix adds or changes an id, grep that id across every artifact and update them together.
- **Tag findings** with root cause and, for regressions, the introducing commit, so churn shows up early.
- **Stop rule.** When most of a round's findings trace to the stage's own fix commits, stop fixing one by one: group by root cause, fix each group once, confirm in the next round.
- **Reconcile the whole directory after implementation.** Grep all of `specs/<feature>/` and the ADRs for planning-tense words (`forecast`, `(planned)`, `Proposed`, `[Unverified`, `will be`) in one sweep; a hand-picked file list misses files.
- **Mechanical versus judgement.** Fix mechanical drift directly; route judgement calls through the decision procedure.

## 13. Lane endings and the tracker

- **Two ways to end without a PR.** A lane can end at Ideate. If the acceptance criteria were genuinely discharged (the check ran and found nothing left to do), Ideate closes it with `move_done` outcome `delivered` and the summary `discharged: <null-result evidence>`, the measurements included, and the lane ends. If the item was rejected as not worth doing, it is **Declined**. Filing discharged work as Declined destroys the evidence that the check ran. Choose from the panel's ruling, not from the kickoff's wording.
- **Comment before status.** Write the closing comment before changing the status, and verify the status after the write.
- **Mirror before the write channel closes.** When a stage learns its branch will stop accepting commits (the PR entered a merge queue, the branch is about to be deleted), it posts any artifact that exists only in an unpushed or stranded commit to the work item verbatim, labelled as the durable copy, in the same step. Then it files a follow-up to land the artifact in the repository and lists exactly what the mirror did not cover. Post-merge stages (Investigate, Tidy) have no branch: the tracker and the handoff note are their durable homes by design.
- **Split by shape, not by unit.** When the panel splits a bundled item, group the spun-off remainder by the shape of what it builds. If several units share a shape, they become one follow-up item; two filed items should never differ only by the unit's name. For the retained proof subset, choose the units most different in shape.
- **Run Deliver's retro after the review loop has quiesced:** automated reviews completed, no unresolved threads, and no commit pushed since the last review. A review triggered by a late push can land new threads after an early retro.

## 14. When hypotheses keep falsifying

If several fix hypotheses fail and no code change is worth shipping, close the work as a diagnostic:

1. Revert production code to the base; ship no speculative change.
2. Add a falsification table to `spec.md` (variant, what it changed, outcome, why it failed), ending with the actual root cause if found.
3. Record the narrative in `research.md` and amend the relevant ADR rather than writing a new one, preserving the original text as history.
4. Point any skipped tests at the closing record, not at the follow-up item.
5. File the follow-up work item and raise its priority above anything else blocked by the same root cause.
6. Propose, through the retro, the one rule that would have caught the problem at spec or plan time.
