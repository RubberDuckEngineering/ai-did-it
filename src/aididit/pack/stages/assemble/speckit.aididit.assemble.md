---
description: "Assemble (the A in A-I-DID-IT): read every implementable item in the board's Ready column and ship each one autonomously as its own lane of Ideate, Draft, Iterate, Deliver, Investigate and Tidy links, with the merge as the only human gate. Trigger: 'Agents Assemble'."
---

## User Input

```text
$ARGUMENTS
```

Consider the input if non-empty: a board or status override, or an item cap (`cap:N`). Default: every implementable item in the configured board's Ready column.

### Trigger phrases

This command answers to all of these, in any casing or spacing:

- **"Agents Assemble"**: the canonical trigger.
- **"assemble my agents"**, **"assemble my agents on my &lt;board&gt;"**: the `<board>` fragment is a hint resolved against configuration, not a filter to parse literally.
- **"mob the board"**: older phrasing, still honoured.
- **"hockety pockety walkity wack"**: the magic phrase. Accept any close-sounding variant ("hockety pockety wockety wack", "hokety pokety walkity whack", misspellings, transpositions, extra or missing syllables). Match on rough phonetic shape, not the exact string; a magic word has to work when half-remembered.

**The trigger phrase is never an argument.** Strip it before parsing, never pass it through the input guard, never read it as a status filter or a cap. If it comes with a real argument ("Agents Assemble, cap:2"), strip the phrase and honour the rest.

---

## Overview

Assemble reads the board, takes **all** implementable items in Ready, and ships each through the full delivery arc autonomously. Each item becomes a **lane**; each lane is a **chain of single-purpose links** so no single context holds the whole arc. File-disjoint lanes run in parallel (up to `lanes.max_parallel`); file-overlapping items are serialized into one lane.

| Link | Stage | Scope | Then |
|---|---|---|---|
| 1 | **Ideate** (Mode B) | Interrogate the item: premises against the code, bundled scope, blocks/blocked-by overlap, testable ACs | Draft |
| 2 | **Draft** | specify, clarify, plan, tasks, analyze (loop budget: lane contract §5) | Iterate |
| 3 | **Iterate** | Implement test-first, commit, push, open the PR, post-implementation analyze | Deliver |
| 4 | **Deliver** | Practitioner panel on the PR, bot and CI loop, retro | **STOP: PR green, awaiting the merge** |
| 5 | **Investigate** | Verify the merged change against the running system; sweep for collateral damage | Tidy (after the merge) |
| 6 | **Tidy** | Item to Done, delivery comment, board triage, retro action set | End of lane |

`A` assembles the lanes; each lane runs `I-DID-IT`. Ideate's mode is chosen by the caller: a lane always starts Ideate in **Mode B**, which never asks the user and never halts the lane. A bundled-scope finding goes to the panel, which rules on the split; Ideate creates the spun-off items, narrows the current one and hands off to Draft.

**No human gates.** Every decision a human would normally make goes to a fresh, cited practitioner panel. The only human action is the merge, and Full Auto Mode delegates even that.

**Read these before launching any lane:**

- `.specify/extensions/aididit/shared/lane-contract.md`: link chain, kickoff arguments, transition, ledger, autonomous overlay, loop budget, parallel-run discipline, stop points, kickoff template.
- `.specify/extensions/aididit/shared/lane-runner.md`: how each link starts the next under `lanes.runner`.
- `.specify/extensions/aididit/shared/practitioner-panel.md`: the fresh-each-summon, cited decision panel.
- `.specify/extensions/aididit/shared/board-adapters.md`: every board read and write.

**Pipeline order (do not skip or reorder):** 0 Preflight, 1 Roster and lane assignment, 2 Launch lanes, 3 Post-merge Investigate, 4 Aggregate report, 5 Board triage.

### Lanes are observable runs, not hidden subagents

Every lane runs through the configured lane runner, which keeps it visible to the human and persists its handoff note to `.specify/aididit/lanes/<lane-id>/handoff.md` before each next link starts.

- Under `lanes.runner: claude` or `claude-remote`, every link of every lane is its own session started by `spawn-lane`. **An in-process subagent is never a lane or a link.** It has no session the human can open and dies with its parent, taking uncommitted work with it.
- Under `lanes.runner: inline`, this session runs the lanes itself, one after another, re-grounding from the handoff note at each link boundary.
- Subagents are fine for **sub-work** inside the orchestrator or a link: blast-radius estimates, panel personas, board reads and writes.
- **Uncertainty defaults to lane.** Calling a unit of work "just verification", "just docs" or "just a PR fix-up" does not make it sub-work: if it moves an item toward merge, it is a lane.

---

## Configuration

From `.specify/extensions/aididit/aididit-config.yml`:

| Key | Use here |
|---|---|
| `board.*` | Which board to read; see the board adapter |
| `lanes.runner` | `inline`, `claude` or `claude-remote` |
| `lanes.max_parallel` | Most lanes running at once; further lanes queue. `inline` is always 1 |
| `delivery.merge` | `human` (default) or `auto` (Full Auto Mode) |
| `delivery.default_branch` | Base for worktrees and merges |
| `panel.*`, `loops.*` | Passed through to lanes via the lane contract |

---

## Full Auto Mode (`delivery.merge: auto`)

By default Assemble keeps one human gate: the merge. Full Auto Mode removes it for the run. It is active when `delivery.merge: auto`, or when the invocation explicitly says "full auto mode" (or a plain equivalent such as "merge them yourself"); the invocation form applies to this run only. Once active it holds for the whole run. It grants three things:

1. **Merge authority at the ping point, held by Deliver.** Each lane's Deliver link merges its own PR, in every runner mode, at exactly the state where default mode would stop and wait for the human: PR green, all required checks (`lane-contract.md` §7) passed (measured, not assumed), every bot and review thread resolved, no unresolved panel escalation. The orchestrator never merges. Lanes learn the mode from the `merge:` field of their handoff note, so set it to `auto` in every kickoff. The safety rails do not relax: never merge with a red or pending required check, an open thread or a merge conflict, and never merge to get past a stuck lane. A merge a human would hesitate at goes to the panel, not to a click. Deliver then starts Investigate, and Investigate starts Tidy.
2. **Panel before escalation.** The orchestrator's own judgement calls (is this lane stuck, is this check failure flaky or real, what order to sequence) go to a fresh, cited panel first. Escalate to the human only when the panel cannot resolve: its grounding retries are exhausted, or it splits on a premise only the human owns.
3. **Active lane pooling.** Full Auto Mode overrides the "all parallel means no watcher" default (Phase 3). The orchestrator keeps a pool loop for the whole run: poll every lane's ledger, PR, CI and threads; detect stuck lanes; re-run a flaky check; convene the panel on a blocker; start the next queued item of a serialized group once its predecessor merges. Poll every 4 to 5 minutes while a merge or unblock is expected, every 20 minutes or more otherwise. Persist pool state in the resume file below.

**Usage-limit pacing.** The loop budget stops one lane spinning; pacing stops the whole pool hitting a usage limit mid-step. If your agent or provider reports that a usage limit is near, at each pool check-in:

- start no new lane links;
- tell every running lane (through its ledger) to reach a committed safe point before any long step such as a mutation sweep, a full suite or a container build. A safe point is tests green and committed, or a work-in-progress commit naming the failing test, with the handoff note updated;
- make sure the resume file is exact.

Resume normal starts when the limit resets. **Why:** a pool that runs into a hard limit stops every lane mid-step at once, sometimes inside a merge, and loses hours until the reset.

**What Full Auto Mode does not change:** a `REGRESSED` Investigate verdict still stops the lane and goes to the human; overlapping lanes still serialize; no secret is ever echoed; the panel is still cited, with no offline fallback. The merge gate is delegated; the engineering bars are not.

Without Full Auto Mode, every "do not merge" rule below stands.

---

## Orchestrator resume file (always on)

**Why:** if the orchestrator session dies or its agent hits a usage limit, a human must be able to paste one file into a different agent or session and carry on. State held only in one agent's memory or tools does not survive that switch.

**Where:** `.specify/aididit/lanes/ORCHESTRATOR-RESUME.md`, plain Markdown.

**When:** rewrite the whole file (not a diff) at run start; at every lane start and link handoff the orchestrator learns of; at every PR opened, merged or blocked; at every panel decision of note; at every pool check-in where something changed. Stamp it `as at <UTC time> / <default-branch SHA>`. A resume file older than the latest merge is a defect.

**Write it for an agent with no special tools.** It must stand alone and contain:

1. **Mission and mode:** the run, Full Auto status with the exact merge conditions, `lanes.runner`, the lane cap.
2. **Lane table:** each lane's item, current link, worktree, branch, allowed paths (widenings marked), PR, CI state, ledger folder, and what comes next.
3. **Merged so far** (SHA, PR) and the **queue** in order, with blockers and anything awaiting the human.
4. **How to check state with plain commands:** `git -C <worktree> log/status`, the git host CLI for PRs and checks, the board adapter for items.
5. **How to continue without starting new sessions:** work the queue sequentially in one session, picking up the furthest-along lane from its worktree and its `handoff.md`.
6. **The safety rules:** no secrets, never merge outside the conditions above, files never to touch.
7. **Pointers:** the lane contract, the lane runner, each lane's ledger folder, the decision records.
8. **Return path:** how to resume orchestration here from this file.

Never write a secret into it; it gets the same scan as kickoff prompts (Phase 0d).

---

## Tracker neutrality

Never hard-code a tracker, project key, board name or instance. Resolve the board in this order:

1. An explicit board or status given in the input (including a `<board>` hint from the trigger phrase).
2. `board.*` in the config, through the board adapter.
3. Ask the user once, then use the answer for the whole run.

**Query shape**, in the adapter's terms: `list_ready`, excluding **container** items (epics; label `epic`), which have no code scope of their own, and **child** items (sub-tasks), which lanes create their own copies of.

A board this command cannot read is a hard stop, never an assumed-empty column. Offer a manual roster instead: the user pastes the items and the run proceeds from that list.

---

## Phase 0: Preflight (fail fast, before any lane starts)

> Status: "Assembling: preflight checks..."

**0a. Input guard.** After stripping any trigger phrase, accept only a board or status override, `cap:N` (a positive integer), or "full auto mode". Reject shell metacharacters and path traversal; stop with usage.

**0b. Tooling and connectivity** (run the probes in parallel):

- The board is readable (a `list_ready` smoke read). If not, stop.
- `git status --short` is clean in the primary checkout. Changes to `board.markdown_path` and anything under `.specify/aididit/lanes/` are expected runtime state (`lane-contract.md` §2), not a dirty tree. Otherwise stop and name the dirty files.
- The git host CLI is authenticated; language toolchains are present (soft warning; only lanes that need them care).
- **Runner probe.** For `claude` or `claude-remote`, run the spawn script once with `--dry-run` / `-DryRun` and a scratch prompt file, then confirm the claude binary resolves (`$AIDIDIT_CLAUDE_BIN` or `claude` on `PATH`). If it does not, stop with: "Lanes start as Claude Code sessions and no claude binary was found. Install it, set AIDIDIT_CLAUDE_BIN, or set lanes.runner: inline to run lanes one at a time in this session." For `claude-remote`, also confirm Remote Control is available to the account. For `inline`, no probe.

**0c. Board read.** For each Ready item fetch ref, title, body, labels, links and priority. Zero results: stop with "The Ready column is empty: nothing to assemble." With `cap:N`, take the top N in board order.

**0d. Secret scan.** Item text is copied into kickoff prompts, so anything pasted into a description travels. Run the secret scan (`disciplines/prompt-crafting.md`) on every item body. On a hit, the kickoff references the field by context, and the roster flags it.

> Status: "Preflight green. {N} items queued. Runner: {runner}."

---

## Phase 1: Roster and lane assignment

> Status: "Carving lanes: overlap analysis and number reservations..."

**1a. Blast-radius estimate.** For each item, estimate the top-level areas and files it will touch, from its description, labels and any cited files. Subagents may do this in parallel. One line of areas per item.

**1b. Overlap grouping.** Items with disjoint areas each get their own lane and may run in parallel. Items sharing an area or file are folded into **one serialized lane**: the next item starts only after the previous item's PR merges. **Uncertainty defaults to serialized**: a wrongly serialized pair costs wall-clock time; a wrongly parallel pair costs a conflict.

**1c. Pre-assign per lane** (collision-safe):

- **Lane id**: `l<n>-<slug>`, matching `^[a-z0-9][a-z0-9-]{0,62}$`.
- **Spec dir number**: the next free number, incremented per lane so no two lanes claim the same one. It names the spec directory, `specs/<spec-num>-<slug>/`.
- **Branch**: `<item-id>-<slug>`; **worktree** created from the latest `origin/<delivery.default_branch>`.
- **ADR numbers** (only if needed): derive the maximum across the default branch **and all branches** (`git log --all` / `git branch -a`), then give each lane a distinct number. Merged history alone undercounts, because sibling lanes hold reservations that exist only on their own branches.
- **Migration numbers** are derived inside the lane at implementation time.
- **Ledger folder**: `.specify/aididit/lanes/<lane-id>/` in the primary checkout, one per lane, never shared.

**1d. Create worktrees** for all lanes up front (for `inline`, worktrees are optional; a branch per lane worked in sequence is enough). Confirm `git -C <worktree> branch --show-current` matches each lane's branch. Worktrees serve links 1 to 4 only: Investigate and Tidy run after the merge in the primary checkout on a detached `origin/<delivery.default_branch>`, and their clean-tree gate is `git status --porcelain` only.

**1e. Claim the items** through the board adapter (`claim`, with the lane id). A claim that finds the item already gone from Ready means another run took it: drop it from the roster.

> Status: "{L} lanes assigned ({p} parallel, {s} serialized). Worktrees live."

Report the lane table: lane id, item, areas, branch, worktree, spec number, reserved ADR, parallel or serialized group.

---

## Phase 2: Launch lanes

> Status: "Agents away..."

For each lane, up to `lanes.max_parallel` at once (for a serialized group, only its first item):

1. **Compose the kickoff** from the template in the lane contract §8, filling in the lane's item, worktree, branch, numbers, allowed paths, runner and merge mode. Link 1 runs `__SPECKIT_COMMAND_AIDIDIT_IDEATE__ mode:B lane:<lane-id> item:<item-ref>`. **The kickoff is input the lane verifies, not fact it obeys:** do not assert how the repository manages something unless you checked it in the repository; otherwise mark it `[Unverified: lane must confirm]`.
2. **Shape it** per `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, then sanitize it per `lane-runner.md`.
3. **Persist it** to `.specify/aididit/lanes/<lane-id>/ideate.prompt.md`, write the initial `handoff.md` (from: assemble, to: ideate) and a first `ledger.md` entry, and read them back.
4. **Start link 1** per `lane-runner.md`. **Proceed without asking:** the trigger phrase is standing authorization for every lane start, so never ask the user "start this lane?". Under `claude` or `claude-remote`, verify the start: the pid from the `SPAWNED` line is alive now and still alive in a later step, and for `claude-remote` the session name shows in the app. Only if that check fails, tell the user.
5. **Record** the lane as `LAUNCHED` in the resume file; do not block on it.

Start disjoint lanes back to back; never wait for one before starting the next. Under `inline`, run the lanes one at a time, each to its stop point, in roster order.

> Status: "{p} lanes running. Awaiting PRs."

**Recovery:** if a lane fails to start, report its prompt file path for manual start, mark the lane `MANUAL`, and continue with the others. One lane failing never blocks the rest.

---

## Phase 3: Post-merge: Investigate

> Status: "Validating as PRs land..."

In default mode (`delivery.merge: human`), when the merge check (`lane-contract.md` §1) shows a lane's PR merged (you saw the merge, or the human said "merged <item-ref>"), start link 5, `__SPECKIT_COMMAND_AIDIDIT_INVESTIGATE__ lane:<lane-id> item:<item-ref>`, per `lane-runner.md`. Under Full Auto Mode, Deliver merges and starts Investigate itself. Either way, Investigate starts Tidy; the orchestrator never does. Investigate's verdict gates Tidy:

| Investigate verdict | Then |
|---|---|
| **CLEAR** | Tidy |
| **DEGRADED** | Tidy; findings filed as new work items |
| **REGRESSED** | **Stop the lane.** File it, tell the human, do not tidy |
| **UNVERIFIABLE** | Report honestly; the human decides whether to tidy |

Lanes keep themselves current (each merges the default branch before the PR and before final green), so the orchestrator watches only for merges, not drift.

- **All lanes parallel, default mode: no watcher.** The git host's PR view is the authoritative merge signal and the human is present to merge. Wait for "merged <item-ref>", run the merge check (`lane-contract.md` §1), then start Investigate for that lane; Investigate starts Tidy. No standing processes.
- **At least one serialized group: run a watcher.** Its job is sequencing: when the in-flight item's PR merges, start the next queued item's link 1 from the updated default branch, and start Investigate for the merged item. Poll every 4 to 5 minutes while a merge is expected, every 20 minutes or more otherwise. Persist the queue in the resume file.
- **Full Auto Mode:** the active pool loop replaces both.

Per lane: PR appears, record the URL. PR merges, Investigate starts (from you in default mode, from Deliver under Full Auto Mode) and starts Tidy itself, verdict permitting; for a serialized group, start the next queued item. Lane stuck, record `BLOCKED` with the reason; other lanes continue.

**The orchestrator never merges a PR.** In default mode a lane stops at PR green and waits for the human; under Full Auto Mode, Deliver merges.

---

## Phase 4: Aggregate report

> Status: "Tallying the assembly..."

| Lane | Item | Areas | PR | CI | Coverage | Tests | ADR | Investigate | State | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| l1-health | PROJ-123 | backend | #PR | green | 100% | NN | ADR-NN | CLEAR | **Awaiting merge** | ... |
| l2-cache | `<item-ref>` | infra | n/a | n/a | n/a | n/a | n/a | n/a | **Declined at Ideate** | panel 3-1, cited; spun off ... |

Plus: lanes run in parallel versus serialized, panel decisions of note with citations, any `BLOCKED` or `MANUAL` lanes and why, Investigate verdicts, Tidy status per merged lane, method-file edits that lanes proposed with what was done about each (upstream drafts by file path), and whether the board has uncommitted changes.

### A lane declined at Ideate is a success row

A lane whose item the panel declined ends at link 1 with no PR, by design. Ideate closes the item through the board adapter itself and stops. Report it with `n/a` in the delivery columns and `Declined at Ideate` as its state, never as blocked or failed, and never chase it for a PR. Put the panel's vote split, citations and spun-off refs in Notes: the reasoned declination is the lane's deliverable, and it cost one link instead of six.

### Self-check before delivering the report

- [ ] Every Ready item maps to exactly one lane (none dropped).
- [ ] Every launched lane has a ledger folder, a handoff note and reserved numbers, with no cross-lane collision.
- [ ] No PR was merged by the orchestrator; every merge under Full Auto Mode was Deliver's, with every merge condition held.
- [ ] No secret was copied into any prompt, ledger, resume file or report.
- [ ] Every delivering lane reports a real PR URL and **measured** CI, coverage and test counts, each "as at" a SHA or time.
- [ ] Every declined lane reports its panel split, citations and spun-off refs, is not counted as a failure, and its item was closed on the board (verified by re-reading).
- [ ] No lane tidied on a `REGRESSED` verdict.
- [ ] Every method-file edit a lane proposed was routed by Tidy per the upstream route (`lane-contract.md` §6), as a work item (ref reported) or an upstream draft (file path reported), or declined with a reason in this report. Nobody, the orchestrator included, edited a pack file.
- [ ] The report says whether the board, which is runtime state (`lane-contract.md` §2), has uncommitted changes for the human to commit.
- [ ] The resume file is current as at the latest merge.

---

## Phase 5: Board triage

> Status: "Grooming the board once, after the last lane..."

After the last lane ends, run Tidy's "Phase 5 — Board Triage" (`.specify/extensions/aididit/stages/tidy/speckit.aididit.tidy.md`) once, yourself, for the whole board. Lanes skip it while siblings are in flight, so this is the only triage of the run. Append its result (the WIP limit and its source, promotions, demotions, the next-item pick) to the aggregate report and the resume file.

---

## Failure modes

| Failure | Recovery |
|---|---|
| Ready column empty | Stop: nothing to assemble |
| Board unreachable | Stop; offer a manual roster |
| Claude binary missing under `claude`/`claude-remote` | Stop; suggest installing it, setting `AIDIDIT_CLAUDE_BIN`, or `lanes.runner: inline` |
| Two items overlap files | Serialize them into one lane (1b) |
| All-parallel run | No watcher; on the human's "merged <item-ref>", run the merge check (`lane-contract.md` §1), then start Investigate; Investigate starts Tidy |
| The human says "merged" but the host disagrees | Report the PR's state "as at" the check time per the merge check (`lane-contract.md` §1); wait for the next signal |
| Serialized item stranded after its predecessor merges | The watcher sequences it; the queue persists in the resume file |
| Numbering collision risk | Pre-assign and re-derive against all branches (1c) |
| Merge commit does not trigger CI | The lane pushes a small non-merge commit |
| Transient deploy or infrastructure collision | Re-run the job; do not "fix" it |
| One lane stuck | Mark `BLOCKED`; keep the rest running |
| A link fails to start | Report its prompt file for manual start; mark `MANUAL` |
| Investigate returns `REGRESSED` | Do not tidy; file it and tell the human |
| Usage limit near | Pause new link starts; lanes reach a committed safe point; update the resume file |
| Panel cannot cite | Grounding retry loop: up to 5 attempts, varying the search each time. No offline fallback. After 5 failures, stop that decision and ask the human; never manufacture a majority from uncited opinion |

---

## What this command does not do

- Run a lane or a link as an in-process subagent when `lanes.runner` is `claude` or `claude-remote`. Lanes are sessions the human can see and steer. The only sequential path is `lanes.runner: inline`, chosen by the user, never an orchestrator fallback.
- Merge a PR. Under Full Auto Mode, each lane's Deliver merges its own.
- Start Tidy. Investigate starts it.
- Ask the user a decision question mid-run; decisions go to the panel. It does not ask permission to start a lane; the trigger authorizes it. Verifying that a started session is alive and visible is a check, not a question, and is surfaced only when it fails.
- Run Ideate in Mode A. That conversational mode is for humans and fills the board this command drains.
- Let a lane edit pack files (`.specify/extensions/aididit/`), or the constitution and agent instruction files unless its allowed paths name them. Lanes record proposed edits in their handoff notes; Tidy routes each by the upstream route (`lane-contract.md` §6). Nobody, the orchestrator included, edits a pack file.
- Run file-overlapping lanes in parallel.
- Tidy a lane whose Investigate verdict is `REGRESSED`.
- Hard-code a tracker, project key, board or instance.
- Keep a standing poll loop for an all-parallel run, unless Full Auto Mode is active.
