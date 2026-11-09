---
description: "Draft stage (link 2 of a lane): specify, a budgeted clarify loop, plan, tasks and a budgeted analyze loop, producing the spec, plan, tasks, contracts and ADRs that Iterate builds against."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). In a lane the input is `lane:<lane-id> item:<item-ref>`. Otherwise it is `item:<item-ref>` (the single-lane workflow passes this), a bare work item id (for example `PROJ-123`), or a natural-language feature description. If it is empty, ask for one before Step 0. **Without `lane:` this is a direct run:** it never starts the next link; it writes the handoff note and tells the human or caller the next command.

> "Decide what you will build. The artifact set is the bet."

This is the **Draft** stage, the first D of the A·I·DID·IT lifecycle (assemble, ideate, draft, iterate, deliver, investigate, tidy) and **link 2 of a lane**. Ideate (Mode B) has already interrogated the work item when Draft runs in a lane. Draft closes deliberation; Iterate opens execution. Lifecycle overview: `.specify/extensions/aididit/shared/lifecycle.md`. Conventions for artifact locations, branches, commits and loop budgets: `.specify/extensions/aididit/shared/pipeline-guide.md`.

**Output:** `specs/<feature>/` containing `spec.md`, `plan.md`, `tasks.md`, `contracts/`, plus `research.md`, `data-model.md` and `decisions.md` where they apply; any new ADRs; a retro; a handoff note for Iterate.

---

## Load-When Map

Load reference material only when the step needs it.

| Step | Load |
|---|---|
| Step 0, Step 1 | `.specify/extensions/aididit/aididit-config.yml`; in a lane, `.specify/extensions/aididit/shared/lane-contract.md` |
| Any decision gate | `.specify/extensions/aididit/shared/practitioner-panel.md` (in a lane, or to gather options for an architectural question) |
| Phase 1 Specify | `.specify/extensions/aididit/shared/disciplines/bdd.md` |
| Phase 4 Tasks | `.specify/extensions/aididit/shared/disciplines/tdd.md` |
| Phase 5 Analyze loop | `.specify/extensions/aididit/shared/pipeline-guide.md` § Analyze practice |
| Phase 6 Team review | `.specify/extensions/aididit/shared/panel-guide.md` Part 2 |
| Step N Retro | `.specify/extensions/aididit/shared/retro.md` |
| Step N+1 Handoff | `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, `.specify/extensions/aididit/shared/lane-runner.md` |
| Any work item read or write | `.specify/extensions/aididit/shared/board-adapters.md` |

---

## Decision Gates

Every judgement call in this stage goes through one procedure, **Decide**. Who answers depends on how the stage was started:

| How Draft was started | Who answers |
|---|---|
| **In a lane** (the input carries `lane:<lane-id>`) | The practitioner panel, per `.specify/extensions/aididit/shared/practitioner-panel.md`, using `panel.practitioners` and honouring `panel.require_citations`. **Never the human.** The lane's only human gate is the merge. |
| **Invoked directly** by a human | The human. For an architectural, format or scope-boundary question, convene the panel first to gather pros and cons, and present those as the options. |

**Decide(question, options):**

1. State the question and two to four concrete options. Never pose a question the filesystem can answer (see Phase 2).
2. Get the answer from whoever the table above names.
3. Append an entry to `specs/<feature>/decisions.md` (create it if missing) in the decision-record format (`practitioner-panel.md` section 8).
4. Apply the decision and continue. A panel that splits applies the decision rule in `.specify/extensions/aididit/shared/practitioner-panel.md` (section "4. Decision Rule") and records the split.

Decision points in this stage: intent confirmation (Step 1), each clarify question (Phase 2), each judgement-call analyze finding (Phase 5), the closing panel ruling on anything the analyze loop leaves open, and the triage of team-review findings (Phase 6).

Hard halts are not decisions. A dirty tree, a failed pull, or a missing prerequisite stops the stage and is reported; no panel overrides it.

---

## Step 0 — Prerequisites and Context

> Report: "Validating prerequisites and inferring project context..."

Run these probes in parallel:

1. **Repository.** `git rev-parse --show-toplevel`, `git remote get-url origin`, `git status --short`. No repository or no `origin`: **STOP** with "Draft needs a git repository with a remote named origin."
2. **Spec Kit.** Confirm `.specify/` exists and the core commands are installed. Missing: **STOP** and tell the user to run `specify init`.
3. **Config.** Read `.specify/extensions/aididit/aididit-config.yml`. Missing: **STOP** and point at the extension's install step. Cache `board.provider`, `delivery.default_branch`, `loops.clarify_max_rounds`, `loops.analyze_max_rounds`, `lanes.runner`.
4. **Board.** Reach the configured board provider as `.specify/extensions/aididit/shared/board-adapters.md` describes (for `github`, `gh auth status` must pass; for `jira`, the agent needs an Atlassian MCP server). If the input is a work item id, read the item: title, description, acceptance criteria, links (blocks / blocked by / parent).
5. **Lane or direct.** Decide which row of the Decision Gates table applies. In a lane, read the handoff note and confirm it names this stage, the lane id, the assigned branch and any pre-assigned spec or ADR numbers.
6. **Resume point.** A link can be re-entered after it already finished. Check both signals before doing any work:

   | Draft's durable output (`specs/<feature>/tasks.md`, a Draft entry in `decisions.md`, a Draft comment on the work item) | Iterate's artifact (a handoff note addressed to Iterate, or task commits) | Action |
   |---|---|---|
   | absent | absent | run the stage normally |
   | present | absent | **resume at the handoff**: re-verify the artifacts' load-bearing premises against the code, then hand off. Do not re-decide. |
   | present | present | the chain has moved on; you are a duplicate. Stop and report. |

Report what was detected (repository, board provider and work item, lane id or "direct", mode) in one block. Any inference failure halts before a file is written.

---

## Step 1 — Diagnose Intent

> Report: "Diagnosing intent before drafting..."

State in three lines: **what** is being drafted, **for which work item** (or "new work item"), and **why** (what the spec enables). If the user supplied a partial spec, list what is present and what is missing.

**Decide**: "Proceed as stated" / "Adjust scope (say how)" / "Cancel". In a lane, `panel-guide.md` P2 decides whether this needs the panel: a handoff with no open intent question is answered "proceed, per handoff". Do not start Phase 0 until the answer is proceed.

---

## Phase 0 — Git Baseline (hard halt on any failure)

**In a lane:** do not switch branches. Verify `git branch --show-current` equals the assigned branch, run `git fetch origin`, and record how far `HEAD` is behind `origin/<delivery.default_branch>`. Then do 0.4 only; skip 0.5.

**Invoked directly:**

- **0.1 Clean tree.** `git status --short` must be empty apart from runtime state (`lane-contract.md` §2). Otherwise **STOP** and list the files; the human commits, stashes or removes them. Never auto-stash; local work may be load-bearing.
- **0.2 Current default branch.** `git checkout <delivery.default_branch>` then `git pull --ff-only`. A non-fast-forward or an unreachable remote is a **STOP**: a spec drafted from a stale base drifts downstream.
- **0.3 Verify.** `git rev-parse HEAD` must equal `git rev-parse origin/<delivery.default_branch>`. If not, **STOP**.
- **0.4 Related work triage.** List open work items (and open issues on the git host, if separate) and pick out those this work depends on, unblocks or resolves. Record them in a `## Related Work Items` table in `spec.md` (id, relation, disposition) so Tidy can close what this delivery resolves. Before creating any new work item, search the board for an existing one with the same intent; a create that timed out may have landed, so re-read before retrying.
- **0.5 Branch.** A direct run creates its branch itself: if the work item id is known, `git checkout -b <item-id>-<slug>`. Only with no work item id (a natural-language description) let the specify step name the branch.

Move the work item to **In Progress** with the board adapter's `move(ref, In Progress)` if it is not there already.

---

## Phase 1 — Specify

Run `__SPECKIT_COMMAND_SPECIFY__` with the work item content or the description. It creates `specs/<feature>/spec.md`. In a lane, pass `SPECIFY_FEATURE_DIRECTORY=specs/<reserved>` so Spec Kit uses the reserved directory. Specify switches branches only through the git extension's `before_specify` hook; where that hook is installed, also pass `GIT_BRANCH_NAME=<assigned branch>` so it reuses the lane branch. In a lane, specify's `[NEEDS CLARIFICATION]` markers never wait for a reply: they go to the clarify loop (Phase 2).

Copy any entries from `.specify/aididit/lanes/<lane-id>/decisions.md` into `specs/<feature>/decisions.md`, IDs unchanged. If Ideate left its retro at `.specify/aididit/lanes/<lane-id>/ideate-retro.md` (a direct run with no branch yet), copy it to `<retro.directory>/<lane-id>/ideate.md` and commit it by explicit path as its own commit, `chore(retro): ideate-stage retro for <item-ref>`.

Then check the spec against these rules before moving on:

- **Acceptance criteria are Given-When-Then**, one to five scenarios, in domain language (`.specify/extensions/aididit/shared/disciplines/bdd.md`).
- **Every criterion can fail on its own.** For each criterion, name a system behaviour that would make it fail while its siblings still pass. If you cannot, it restates a sibling: fold it in or sharpen it into the distinct bound it was reaching for. Record which.
- **Re-check every absence claim.** "X does not exist yet" or "nothing calls Y" in the work item was true when written; a blocker that has since shipped often created X. Grep for the mechanism (the route, the exported symbol), not the item's own wording, and correct the spec. Label anything not re-measured `[Unverified]`.
- **Constitution beats a weaker criterion.** If a work item threshold is weaker than a constitution principle (for example 80% where the constitution says 100%), encode the constitution value and annotate the line: `(constitution principle <N> override; work item said <original>)`. Analyze cannot see this drift because the tracker is not a spec artifact.
- **Blocked-item overlap.** For each item this one blocks, compare its summary with the spec's requirements. If they overlap, note it in the spec and route "is the downstream item still needed?" through **Decide**.
- **Skip carryover.** Grep earlier specs and the git log for skipped or deferred tests that name this work item. If any exist, read the deferred contract before clarify and note the carryover in the spec.

---

## Phase 2 — Clarify Loop (at most `loops.clarify_max_rounds` rounds)

> Report: "Running clarify loop (max <loops.clarify_max_rounds> rounds)..."

1. Run `__SPECKIT_COMMAND_CLARIFY__`. In a lane, run it non-interactively: collect its questions rather than letting it wait on a human.
2. **Resolve filesystem facts mechanically.** A question about whether a path exists, which file format is in use, or the next free ADR number is answered with `ls`, a glob or a read, never posed. Record it in the spec's Clarifications section as `Q: ... → A: <value> (verified from the filesystem)`.
3. Put every remaining question through **Decide** and write the answer into `spec.md`.
4. Re-run clarify. Exit when it raises no questions or when the round count reaches `loops.clarify_max_rounds`.
5. If questions are still open at the cap, the panel rules **once** on each: answer it now, record it as an open edge case with a note, or file a follow-up work item. No extra round.

Record each round's question count in `spec.md` (for example `clarify rounds: 5 → 2 → 0`).

---

## Phase 3 — Plan

Run `__SPECKIT_COMMAND_PLAN__`. It should produce:

1. `plan.md` with a Constitution Check that passes, or a recorded and justified deviation.
2. A phase structure and a test strategy (which layer proves each requirement: unit, integration, acceptance).
3. `contracts/`, one per externally visible interface the requirements touch.
4. `data-model.md` if schemas are involved; `research.md` for any decision that needed investigation.
5. **ADRs** for architectural decisions, in the project's ADR directory (`docs/adr/` unless the constitution names another). Take the next free number. In a lane, use the pre-assigned number and re-derive it against `origin/<delivery.default_branch>` and sibling lane branches; local enumeration undercounts.

**Evidence-source census.** For every telemetry source, log query or metric the spec names as post-merge evidence, run it once now and record a non-zero control count in `research.md`, timestamped. A source that returns zero of everything is dead, not quiet; pick another before Investigate depends on it.

---

## Phase 4 — Tasks

Run `__SPECKIT_COMMAND_TASKS__` with the TDD request in its arguments, because Spec Kit's tasks step writes test tasks only when TDD is asked for: `TDD: a test task precedes every implementation task; each guard names its kill mutation`. Then check `tasks.md`:

1. Tests come before the code they drive (`.specify/extensions/aididit/shared/disciplines/tdd.md`): a test task precedes each implementation task.
2. Pre-implementation test counts carry a `~` (for example `~12`). They are estimates; analyze reconciles them after implementation.
3. **Citation check.** Grep every requirement id a task cites against `spec.md`; a task citing a requirement that does not say what the task claims fails fast here.
4. **Changed invariants.** If the work grants something a previous delivery forbade (a new dependency, write access to a store that was read-only, a capability another component must not have), add a task to grep for regression guards asserting the old rule (names like `*Absence*`, `MustNot*`, `DoesNotRegister*`) and rewrite them against the new rule, citing the requirement or ADR that supersedes them. Rewrite, never delete.
5. **Guards get kill rows.** Every task that adds a guard (a test, a check, a gate) also names the mutation that should turn it red. A mutation shared by guards in different layers must reach each layer. Iterate fills in the observations (see the kill-test table in `.specify/extensions/aididit/shared/pipeline-guide.md`).

---

## Phase 5 — Analyze Loop (at most `loops.analyze_max_rounds` rounds)

> Report: "Running analyze loop (max <loops.analyze_max_rounds> rounds)..."

Core analyze is a single read-only pass. This stage runs the loop around it:

1. **Run `__SPECKIT_COMMAND_ANALYZE__`.** If your agent can start a fresh read-only sub-agent, run each pass there rather than in the author's context; independent eyes find more. Ask for each finding's root cause and, where it is a regression, the commit that introduced it.
2. **Check drift from the previous round first.** When a fix added or changed an id (requirement, success criterion, edge case, acceptance criterion), grep that id across spec, plan, tasks, contracts and ADRs, and update all of them in the same batch.
3. **Fix.** CRITICAL and HIGH first.
   - *Mechanical* findings (a count mismatch, a stale path, an unfilled ADR number): fix directly, in every round including the exit round (`panel-guide.md` P1).
   - *Judgement* findings (an ambiguous scope boundary, an ADR that contradicts a requirement, amend versus new ADR): put through **Decide** with two or three resolutions.
   - **Measure before you write.** Any count, line range, control or completeness claim ("every", "no other", "cannot") a fix adds is measured first and stated "as at `<SHA>`".
4. **Exit** after a round that leaves no CRITICAL or HIGH finding, or when the round count reaches `loops.analyze_max_rounds`.
5. **Stop rule inside the budget.** If most of a round's findings trace to this stage's own fix commits, stop fixing piecemeal: group the findings by root cause, fix each group once, and let the next round confirm.
6. **One panel ruling on what is left.** Fix the mechanical leftovers directly (`panel-guide.md` P1). Whatever judgement findings remain (at the cap, or MEDIUM and LOW after an early exit) go to the panel **once**, together in one decision round (`panel-guide.md` P4). Each finding gets exactly one ruling: **fix now** (only if leaving it would make the build wrong or untestable), **accept with a note** in the artifact, or **file a follow-up work item** via the board adapter. Apply the fix-now items. No further rounds. A constitution conflict is never accepted with a note. A CRITICAL or HIGH finding the panel cannot settle is a **STOP**, reported to the human.

Record the per-round counts in `spec.md` and in the handoff note, for example `analyze rounds: 24 → 13 → 5; panel ruled on 5: fix now 1, note 3, follow-up 1`.

Commit the artifact set: `docs(spec): draft <feature> spec, plan, tasks and contracts` with the work item id in a `Refs:` footer (`.specify/extensions/aididit/shared/disciplines/conventional-commits.md`).

---

## Phase 6 — Team Review (one round)

> Report: "Running the team review on spec, plan and tasks..."

Run the persona review round from `.specify/extensions/aididit/shared/panel-guide.md` (Part 2, "Draft's team review") on `spec.md`, `plan.md` and `tasks.md`, with `__SPECKIT_COMMAND_AIDIDIT_PO__`, `__SPECKIT_COMMAND_AIDIDIT_ARCHITECT__`, `__SPECKIT_COMMAND_AIDIDIT_QA__`, `__SPECKIT_COMMAND_AIDIDIT_DEVSEC__` and `__SPECKIT_COMMAND_AIDIDIT_DEVOPS__`, each as an independent reviewer.

1. Collect every persona's `VERDICT:` line and findings.
2. Fix mechanical findings directly (`panel-guide.md` P1). Triage each judgement finding **once** through **Decide**, all of them in one decision round (`panel-guide.md` P4), with the analyze loop's rule: **fix now** (only if leaving it would make the build wrong or untestable), **accept with a note** in the artifact, or **file a follow-up work item** via the board adapter. A constitution conflict is never accepted with a note.
3. Apply the fix-now items, grep any changed id across every artifact, and commit (`docs(spec): apply team review to <feature>`). No extra rounds.

Record each persona's verdict and the triage counts in `spec.md` and the handoff note, for example `team review: 5 personas, 7 findings; fix now 2, note 4, follow-up 1`.

---

## Step N — Retro

> Report: "Running the end-of-Draft retro..."

Run the retro per `.specify/extensions/aididit/shared/retro.md`. It is unconditional: never ask whether to run it. Write it to `<retro.directory>/`. It covers non-obvious lessons, decisions the panel or human corrected, approaches that worked, and analyze or clarify patterns that recurred.

**Commit retro outputs before the handoff.** The retro file (and any ADR this stage wrote) is committed now so it rides this branch: `chore(retro): draft-stage retro for <item-ref>` (the retro commit subject in `retro.md`). If nothing changed, skip the commit. Uncommitted retro output is a **STOP**.

In a lane, retro learnings that would change shared or global instructions are not applied here; list each in the handoff note (target file, exact wording, evidence, panel verdict) for Tidy to file as work items.

---

## Step N+1 — Handoff to Iterate

> Report: "Composing the handoff to Iterate..."

1. **Clean tree gate.** `git status --short` must be empty apart from runtime state (`lane-contract.md` §2), which is never committed. If not, stage the other files by explicit path (never `git add -A` or `git add .`) and commit with a Conventional Commit describing the Draft work. Never hand off a dirty tree.
2. **Re-derive the allowed paths** from `tasks.md`: every path a task creates or changes. A path outside the kickoff's allowed paths is handled per widening allowed paths (`lane-contract.md` §6) before this handoff: checked against sibling lanes, recorded in the handoff note's `allowed paths` line and Decisions, and reported. A direct run records it only.
3. **Write the handoff note** to `.specify/aididit/lanes/<lane-id>/handoff.md`, in the format of `.specify/extensions/aididit/shared/lane-contract.md` §3, before anything else starts. A direct run takes its lane id from the direct-run rule in `lane-contract.md` §3 (from the item ref; with no item ref, from the feature slug). It records: work item id, lane id, branch, spec directory, last commit SHA, clarify, analyze and team-review counts, findings accepted with notes, follow-up items filed. A killed session must not take state with it.
4. **Write Iterate's prompt** to `.specify/aididit/lanes/<lane-id>/iterate.prompt.md` per `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, so a cold session can start without this conversation:
   - Task: implement `specs/<feature>/` per `tasks.md` with `__SPECKIT_COMMAND_AIDIDIT_ITERATE__`.
   - Context files: the handoff note, `spec.md`, `plan.md`, `tasks.md`, `contracts/`, `decisions.md`, the ADRs written, the retro.
   - Rules: TDD red/green/refactor per task; Conventional Commits; no scope beyond `tasks.md`; every guard needs a kill row. In a lane: "Operate under `.specify/extensions/aididit/shared/lane-contract.md`."

   Read both files back.
5. **Record progress on the work item** via the board adapter: a comment naming the spec directory, the branch and the analyze outcome.
6. **Start the next link:**
   - **In a lane:** start Iterate per `.specify/extensions/aididit/shared/lane-runner.md` (`lanes.runner`).
   - **Direct run:** start nothing. Report the handoff note path and tell the human or caller the next command, `__SPECKIT_COMMAND_AIDIDIT_ITERATE__ item:<item-ref>` (or `specs/<feature>` when there is no item ref).

---

## Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| Board unreachable in Step 0 | No `gh` auth, no Atlassian MCP server, missing board file | Direct: ask the human once. Lane: proceed from the kickoff's copy of the item and note the gap in the handoff. |
| Clarify still open at `loops.clarify_max_rounds` | Real ambiguity rounds cannot settle | Panel rules once per question: answer, open edge case with note, or follow-up item. No extra round. |
| Analyze still finding at `loops.analyze_max_rounds` | Findings are at the reviewer's noise floor, or the stage's own edits feed it | Panel rules once; apply fix-now items; hand off. CRITICAL or HIGH the panel cannot settle: **STOP**. |
| Re-entered after Draft already finished | Session restarted before the handoff | Resume-point table in Step 0. |
| Number clash on spec or ADR | Concurrent lanes enumerated from the same base | The lane already merged keeps the number; re-derive yours from `origin/<delivery.default_branch>` plus sibling branches. |
| Next link fails to start | Runner misconfigured, CLI missing | The handoff note is on disk; report its path so the human can start Iterate by hand. |

---

## Self-Check Before Handoff

- [ ] Specify, clarify loop, plan, tasks, analyze loop and the one-round team review all ran.
- [ ] Clarify and analyze each closed within budget; per-round counts recorded; every remaining finding carries one panel ruling.
- [ ] Every acceptance criterion can fail independently of its siblings.
- [ ] Every decision is in `decisions.md` with a generated timestamp.
- [ ] Retro written and committed.
- [ ] Branch is `<item-id>-<slug>` (or the lane's assigned branch); `git status --short` is empty.
- [ ] Handoff note exists on disk at `.specify/aididit/lanes/<lane-id>/handoff.md`.

Any unchecked box: stop and fix it before the handoff.
