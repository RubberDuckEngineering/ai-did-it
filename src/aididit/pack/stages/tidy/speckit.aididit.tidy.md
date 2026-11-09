---
description: "Tidy stage (link 6 of a lane): after the merge and a non-REGRESSED Investigate verdict, act on the lane's retros: move the work item to Done, triage the board, file graduations and follow-ups as work items, and sweep working artifacts."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). In a lane the input is `lane:<lane-id> item:<item-ref>`. Otherwise it is `item:<item-ref>` (the single-lane workflow passes this), a bare item ref, a merge SHA, or nothing (infer the work item from the most recently merged PR and the lane folder). **Without `lane:` this is a direct run:** it never starts another stage; it records the lane status and tells the human or caller what comes next. A direct run takes its lane id from the direct-run rule in `.specify/extensions/aididit/shared/lane-contract.md` §3.

> "Leave the campground cleaner than you found it. The lessons are the artifact."

This is the **Tidy** stage, the T of the A·I·DID·IT lifecycle and **link 6 of a lane**: the reflection-action phase. It runs only after the merge **and** after Investigate returned a verdict that permits it. It consumes the retros from Ideate (Mode B), Draft, Iterate, Deliver and Investigate, plus the QA record and findings Investigate filed, and executes the action set they produced. Lifecycle overview: `.specify/extensions/aididit/shared/lifecycle.md`. Practitioner lineage: Kent Beck's *Tidy First?* and Robert C. Martin's Boy Scout Rule.

**Tidy does not run another retro.** Its phases are the retro action. A retro on Tidy could only ask whether the retro actions were acted on, and the post-Tidy state answers that directly.

---

## What This Stage Writes: It Files, It Does Not Author

Tidy runs after the merge, so it has no feature branch. Its outputs go to the **board**, never into tracked files.

| Output | Where it goes |
|---|---|
| Work item to Done, delivery comment, board moves | The board adapter (`move_done`, `comment`, column moves) |
| Rule graduations, guide promotions, process fixes, follow-ups | **New work items** via `create_item`, each carrying the proposed wording and the panel verdict |
| Changes to the installed pack | An upstream draft in `.specify/aididit/lanes/<lane-id>/upstream.md`, per the upstream route (`lane-contract.md` §6) |
| Lane status | `.specify/aididit/lanes/<lane-id>/handoff.md` (git-ignored runtime state) |
| Learnings (optional) | Your agent's own persistent memory, if it has one (Phase 2f) |
| Board unreachable | The full content in your response. Never a new tracked file |

**Allowed writes.** Project runtime state: the board file at `board.markdown_path` when `board.provider` is `markdown` (edited in the primary checkout only, never a lane worktree's copy) and the lane folder under `.specify/aididit/lanes/` (handoff note, ledger). Tidy writes no retro file. Nothing else in the tree.

**Propagate versus author.** This stage may *propagate* a decision that already passed a gate: moving a card, closing an item the QA record shows was fixed, copying merged content back to where it was merged from. It may not *author* one that has not: a new rule in the constitution or the agent instruction file, a new project guide section. Those are filed as work items and land later, as their own small branch and PR, in the lane that picks the item up, with acceptance criteria and a reviewer. An edit to the installed pack (a stage command, a shared guide, a persona) is never filed here, because no lane may make it: it goes upstream per the upstream route (`lane-contract.md` §6).

**Why:** a rule that shapes every future session is the most review-worthy change in the system, not the least. "It is only a doc edit" is how an ungated change enters the standards.

**Where it runs.** In the primary checkout, on a detached `origin/<delivery.default_branch>`: `git fetch origin && git switch --detach origin/<delivery.default_branch>`. Never in a lane worktree.

**Pre-completion gate:** `git status --porcelain` shows no change outside runtime state (`lane-contract.md` §2), that is `board.markdown_path` and `.specify/aididit/lanes/`. Anything else: stop and name the files, do not commit them, do not open a branch for them, and file their content as a work item instead.

---

## Load-When Map

| Step | Load |
|---|---|
| Step 0, Step 1 | `.specify/extensions/aididit/aididit-config.yml`; in a lane, `.specify/extensions/aididit/shared/lane-contract.md` and the handoff note |
| Any board read or write | `.specify/extensions/aididit/shared/board-adapters.md` |
| Any decision gate, Phase 5 grooming | `.specify/extensions/aididit/shared/practitioner-panel.md` |
| Phase 2 | `.specify/extensions/aididit/shared/retro.md` (action format), the project constitution and agent instruction file (read only, to quote current wording) |

---

## Decision Gates

Judgement calls use the same **Decide** procedure as the other stages. Tidy writes no spec file, so it records each ruling in the handoff note and in the delivery comment.

| How Tidy was started | Who answers |
|---|---|
| **In a lane** | The practitioner panel. **Never the human.** |
| **Invoked directly** | The human; convene the panel first for governance questions. |

| Decision | Where | Options |
|---|---|---|
| Intent confirmation | Step 1 | Proceed / Skip a phase (say which) / Defer Tidy |
| A graduation that barely qualifies | Phase 2 | File it / Leave it as a learning / Decline with reason |
| Unfinished child items at the Done move | Phase 3 | Resolve each / Cancel the move / Override |
| A sweep target that might be canonical | Phase 6 | Delete / Preserve (default on doubt: preserve) |

Most of Tidy is autonomous by design: board moves follow the adapter, filing follows the criteria below.

---

## Step 0 — Prerequisites and Context

> Report: "Confirming the merge and the verdict, gathering the retros..."

1. **Config.** Read `.specify/extensions/aididit/aididit-config.yml`. Cache `board.provider`, `board.markdown_path`, `delivery.default_branch`, `lanes.max_parallel`, `panel.practitioners`, `retro.directory`.
2. **Lane or direct.** In a lane, read `.specify/aididit/lanes/<lane-id>/handoff.md` and confirm it names this stage and the work item, and that you can reach its `report to:` address ("report" is defined in `lane-contract.md` §3).
3. **Merge confirmed** by the merge check (`lane-contract.md` §1); read `gh pr view <n> --json state,mergeCommit,mergedAt,url` for the merge SHA too. Not merged: **STOP**. Tidy never runs on an unmerged change. `git fetch origin && git switch --detach origin/<delivery.default_branch>`, so the retros committed on the branch are readable.
4. **Verdict confirmed.** From the handoff note or the QA record on the work item:

   | Verdict | Action |
   |---|---|
   | `CLEAR`, `DEGRADED` | Proceed |
   | `UNVERIFIABLE` | Proceed only if the human's choice to proceed is recorded; otherwise **STOP** |
   | `REGRESSED`, or no verdict found | **STOP.** Tidying a regressed or uninvestigated change closes a work item that is not done |

5. **Gather the action list.** Read every retro for the lane and collect its actions:
   - `<retro.directory>/<lane-id>/*.md` from `origin/<delivery.default_branch>` (Ideate, Draft, Iterate, Deliver).
   - Investigate's retro, from the handoff note or the `## Retro` comment on the work item.
   - The QA record, the finding refs, and any candidates Investigate carried forward.

   Each action should carry an owner stage and an evidence pointer (`retro.md`). Tidy executes the actions owned by `tidy`. An action owned by an earlier stage that was never done is reported, and filed as a follow-up if it still matters. A lane with no retro files is itself a finding: name which stages produced none.
6. **Work item and related items.** `read_item` the work item. Read the `## Related Work Items` table in `specs/<feature>/spec.md` (Draft's triage of what this delivery resolves) and the item's links.
7. **Resume point.** If the work item is already in Done with a delivery comment, resume at Phase 5. If the lane status in the handoff note says Tidy finished, you are a duplicate: stop and report.

---

## Step 1 — Diagnose Intent

> Report: "Diagnosing tidy scope..."

In four lines: **which item** shipped (ref, merge SHA, verdict); **how many retro actions** reached Tidy; **candidate graduations** (lessons that recurred); **candidate cleanup** (working artifacts to sweep).

**Decide**: "Proceed with all phases" / "Skip a phase (say which)" / "Defer Tidy". In a lane, `panel-guide.md` P2 decides whether this needs the panel.

---

## Phase 1 — Resolve What This Delivery Fixed

> Report: "Closing the items this delivery resolved..."

For each item Draft's triage marked as resolved by this delivery (board items, and issues on the git host if they are tracked separately):

1. **Verify the concern was addressed**, against the QA record rather than the PR description. A PR body is what the author believed; the QA record is what was measured.
2. If verified: `move_done` with outcome `delivered` and a summary naming the PR and the merge SHA (a git-host issue: close it with the same comment).
3. If not verified: **leave it open** and `comment` why. A closed item looks the same whether or not it was fixed, which is why closing an unverified one is invisible afterwards.

The QA record is evidence: never edit or remove it.

If the board was unreachable when Investigate ran, its QA record and findings are in the handoff note: post and file them now, before anything else.

---

## Phase 2 — Turn Retro Actions Into Work Items

> Report: "Filing graduations and follow-ups..."

### 2a — Route by the kind of change, not its destination

| Kind of action | What it looks like | How it persists |
|---|---|---|
| **Authors** new normative content | A lesson becoming a rule in the constitution or the agent instruction file; a project guide section nobody has agreed yet | File a work item |
| **Changes the installed pack** | A stage command, shared guide or persona under `.specify/extensions/aididit/` | Draft an upstream issue in `.specify/aididit/lanes/<lane-id>/upstream.md` per the upstream route (`lane-contract.md` §6). Never a project work item: no lane could do it |
| **Propagates** an already-gated decision | Copying merged content back to its source; a board move | Do it; it is not a graduation |
| **Follow-up work** | A defect, a missing test, an instrumentation gap, a cleanup a retro named | File a work item |
| **A learning, not a standard** | Something worth remembering that changes no rule | Phase 2f, or leave it in the retro |

### 2b — Rule graduation criteria

A lesson qualifies to be proposed as a rule only when **all three** hold:

| # | Criterion | How to check |
|---|---|---|
| 1 | Recurred 2+ times across work items | The same lesson appears in two or more retros (grep `<retro.directory>`), or its evidence lists two incidents |
| 2 | Scope is project-wide | It applies to two or more distinct areas, files or workflows |
| 3 | Missing it has real blast radius | It catches real defects (data loss, security, broken CI, false-green tests), not style preferences |

Cite the evidence for each criterion before filing:

```text
Rule: <one-line summary>
  ✓ 1: recurred in <retro path> and <retro path>
  ✓ 2: applies to the API, the UI and CI
  ✓ 3: missing it produced a false-green test suite
→ File a graduation item; proposed target: constitution, section "Testing"
```

If any criterion fails, do not file it. It stays in the retro and may qualify later.

### 2c — Guide promotion

When a rule in the constitution or the agent instruction file has grown to three or more paragraphs, or has several sub-rules, it belongs in a guide, with a one-line pointer left behind. That judgement is Tidy's; the change is not. File it as a work item carrying the full text as proposed, the pointer that would replace it, and the destination file. Naming a new guide file is part of the proposal; creating it is the implementing lane's work.

If an always-loaded file (the constitution, the agent instruction file) is getting large, say so in the filed item as evidence. Do not resolve it here by choosing a different destination and acting on it.

### 2d — Filing mechanics

1. **Pre-create gate.** Search the board for an open item that already covers the lesson; if one exists, `comment` on it with the new evidence and file nothing. A guard that has never returned a hit has never been shown to work, so exercise the search once against a lesson you know is already filed and confirm it returns that item's ref.
2. **Every filed item carries**: the exact proposed wording, the panel verdict that chose it (from the retro's panel vetting; convene the panel now if there was none), the target file and section, the evidence pointer, and, for a graduation, the criteria check from 2b. Wording without the verdict invites re-litigation; the verdict without the wording leaves the next lane to reinvent the sentence.
3. **Create** with `create_item` in **Backlog** (labels: `tech-debt` for graduations and promotions, `bug` for defects), using the story format. Read back the ref (create before cite), then `comment` on the delivered work item naming it.
4. **Leave the source untouched.** The retro that raised the lesson stays as it is; the change lands in the filed item's own diff.

### 2e — Declined actions

An action that is not filed is declined on the record: its one-line reason goes into the delivery comment (Phase 3). An action dropped silently is indistinguishable from one never raised.

### 2f — Agent memory (optional)

If your agent keeps a persistent memory outside the repository, record learnings there: lead with the rule, then a **Why:** line and a **How to apply:** line, with absolute dates. Read an existing entry before writing and merge into it; sibling lanes may share the store. Memory records what was learned. It never stands in for a standards change, which is always filed.

---

## Phase 3 — Move the Work Item to Done

> Report: "Closing the work item with a delivery comment..."

1. **Child-item gate.** If the provider has child items for this work item (sub-tasks, a task list) and any is unfinished, **fail fast**: list them and **Decide**: resolve each (Done, or explicitly deferred with a reason), cancel the move, or override. A direct-mode override must be typed by the human verbatim. **Why:** a parent closed over unfinished children claims work nobody did, and a closed parent looks the same either way.
2. **Delivery comment.** The one-screen summary of the whole work item. Someone reading only this comment learns that it shipped, how it was verified, and what follows from it:
   - PR URL and merge SHA; what was delivered (a short list); what it unblocks.
   - Investigate's verdict and where the QA record is; finding refs.
   - Refs of the graduation and follow-up items filed in Phase 2, the path of any upstream draft and the pack repository it is for, and the declined actions with reasons.
   - Test count, coverage and check status as Deliver measured them.
   - Optional: token usage per stage, if the retros recorded it. Label estimates with `~` and name the estimator. Never add up repeated measurements of the same always-loaded files and call the result spend; a footprint measured several times is still one footprint.
3. **Move** with `move_done`, outcome `delivered`, and the summary. Re-read the item afterwards and confirm it is in Done with the comment.

---

## Phase 4 — Preview Environments (if the project uses them)

> Report: "Tearing down the preview environment and sweeping orphans..."

Some hosting platforms create a preview environment per PR and do not reliably delete it on merge. Leaked previews pile up against the platform's environment cap, and once the cap is full every later PR's preview fails to provision. Close-out is the natural place to clean up, because it is the moment the preview stopped being needed. Idempotent; safe every time:

1. **Discover** the hosting resource by query; never hard-code a name. If the cloud CLI is missing or unauthenticated, report the manual delete command and **continue**: this never blocks close-out.
2. **Delete this PR's preview.** "Not found" means it is already gone: note it and continue.
3. **Sweep orphans.** List every preview, map each back to its PR, and delete only those whose PR is **merged or closed**.
4. **Report** what was deleted and how many remain, against the count of open PRs.

**Never delete a preview whose PR is still open**: a sibling lane may depend on it for its own end-to-end checks. When a mapping is unclear, leave it and report it.

---

## Phase 5 — Board Triage

> Report: "Grooming the board..."

**Lane guard.** If this Tidy is one lane of an Assemble run and sibling lanes are still in flight, **skip this phase**: the orchestrator triages the board once, after every lane completes. Promoting mid-run over-commits Ready and races the other lanes. Report the board state and move on.

Otherwise:

1. **The limit.** Ready is kept at **the team's WIP limit**: a column limit the board itself exposes, if the adapter can read one; else a value the orchestrator or human passed in; else `lanes.max_parallel` (default 3). State which source you used.
2. **Snapshot** In Progress, Ready (`list_ready`) and Backlog. In Progress should not contain the item just closed; if it holds an item with no live lane, report it as a possible orphan.
3. **Groom with the panel, when there is something to choose.** If the eligible candidates fit within the limit, skip the panel and promote them in step 5's order (`panel-guide.md` P5). Otherwise give each practitioner lens the three snapshots and this lane's retros. Each returns a proposed Ready set sized to the limit, the single item that should be next with a one-to-two-line rationale, and a confidence (high, medium, low).
   Run one lens per `panel.practitioners` member. With the default panel, for example:
   - Kent Beck: which items have clear, testable acceptance criteria and fit one iteration?
   - Martin Fowler: which items pay down design debt rather than add to it?
   - Dave Farley: which items unblock the most downstream value?
   - Udi Dahan: which items keep service boundaries and ownership clear?
   - Robert C. Martin: which items respect or repair architectural boundaries?
4. **Aggregate**: the Ready composition with a reason per item; promotions and demotions; the next-item pick with the combined rationale; any disagreement stated plainly ("Beck favours X for testability; Farley favours Y for flow").
5. **Apply** with the board adapter's `move`: `move(ref, Ready)` to promote, `move(ref, Backlog)` to demote. Promotion order: items unblocked by this merge, then items whose prerequisites are all Done, then dependency order, then priority, then age. Never promote a blocked item, a child item, an epic, or anything In Progress or Done. Over the limit is the real WIP violation: demote the lowest-ranked excess to Backlog. Under the limit for lack of ready candidates is fine; report the shortfall.

---

## Phase 6 — Working-Artifact Sweep

> Report: "Sweeping working artifacts..."

Sweep **untracked and ignored** working files only (`git status --porcelain --ignored`): PR body files, panel and reviewer output dumps, retro scratch notes, `*-draft.md` and `*.backup-*` files this lane created. A tracked working file that reached the default branch is not deleted here: deleting it is a change to the trunk, so file a cleanup work item instead.

**Never delete**: canonical spec artifacts (`spec.md`, `plan.md`, `tasks.md`, `contracts/`, `data-model.md`, `research.md`, `decisions.md`), decision records, retro files, the board, the constitution or the agent instruction file, or the lane's handoff note, upstream drafts and logs. On any doubt, preserve and report.

---

## Step 7 — Finish

> Report: "Checking the post-Tidy state..."

1. **Pre-completion gate** (see "What This Stage Writes").
2. **The audit is the post-Tidy state.** Confirm each, measured:
   - Every retro action owned by `tidy` is a filed item with a ref, an upstream draft on disk, or a declination on record.
   - No standards or instruction file was written by this stage.
   - The work item is in Done with its delivery comment; related items are closed or left open with a reason.
   - Working artifacts are gone; previews swept (if applicable).
3. **Record the lane as complete** in `.specify/aididit/lanes/<lane-id>/handoff.md` and append the final ledger entry (`lane-contract.md` §2, §3): final status, the refs filed, the board triage result.
4. **Next work item.**
   - **In a lane:** report per `lane-contract.md` §3 and stop. Choosing the next item is Assemble's.
   - **Invoked directly:** present the panel's next-item pick and rationale and **wait for the human**. This gate is never auto-decided. If the human approves, tell them the next command (`__SPECKIT_COMMAND_AIDIDIT_DRAFT__ item:<item-ref>`, or `__SPECKIT_COMMAND_AIDIDIT_ASSEMBLE__` for a board run) and start it only when asked.

---

## Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| PR not merged | Tidy started early | **STOP** |
| Verdict is `REGRESSED` or missing | Investigate stopped the lane, or never ran | **STOP**; nothing here may close the item |
| No retro files for the lane | Earlier stages skipped their retros | Proceed; name the missing stages in the delivery comment as a finding |
| Board unreachable | Provider down, no auth | Emit the delivery comment, filings and board plan in your response and stop; never write them to a tracked file |
| A move fails | Missing transition, permissions, stale state | Re-read and retry once; report the error; continue with the other phases |
| Unfinished child items at the Done move | Children still in flight | **Fail fast**; resolve, cancel, or a verbatim override |
| A related item cannot be verified as fixed | The merge did not address it | Leave it open with a comment |
| The pre-create search was skipped | Treated as ceremony | File nothing until it has run and been shown to return a known hit |
| Tempted to edit a rule or guide directly | No branch exists after the merge | **Do not.** File it (Phase 2) |
| WIP limit source unclear | No board limit, nothing passed in | Use `lanes.max_parallel` and say so |
| A preview maps to an open PR | Sibling lane in flight | Leave it; report it |
| Sweep target might be canonical | Ambiguous name | Preserve and report |
| Tree has changes outside the runtime state at the gate | This stage wrote a tracked file | Stop and name the files; do not commit; file the content as a work item |

---

## Self-Check Before Declaring Done

- [ ] Merge and a permitting verdict confirmed before any write.
- [ ] Every retro action owned by Tidy was filed (ref reported) or declined with a reason; nothing dropped silently.
- [ ] Every filed graduation carries the exact wording, the panel verdict, the target and the criteria evidence; the pre-create search was exercised against a known hit.
- [ ] No standards, instruction or stage file was edited by this stage.
- [ ] Related items closed only where the QA record shows the fix; the rest left open with a reason.
- [ ] Child-item gate ran before the Done move.
- [ ] Work item in Done via `move_done` (`delivered`), with a delivery comment carrying the verdict, the QA record location and the filed refs.
- [ ] Board triage ran (or was skipped by the lane guard), sized to the stated WIP limit, nothing left over the limit.
- [ ] No preview deleted whose PR is open.
- [ ] Pre-completion gate passed; lane recorded as complete.
- [ ] No retro run by this stage.

Any unchecked box: fix it before declaring Tidy done.
