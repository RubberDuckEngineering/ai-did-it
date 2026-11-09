# Retro: the End-of-Stage Retrospective

> "The AI watched the session. The AI owns the synthesis."

Every lane link except Tidy ends with this retro: Ideate (Mode B), Draft, Iterate, Deliver and Investigate. Assemble runs none (its lessons surface inside the lanes), Ideate Mode A runs none (it is a human conversation), and Tidy runs none (its phases *are* the retro action). Cadence and reasons: `.specify/extensions/aididit/shared/lifecycle.md`.

The retro is the agent's own accountability loop: evidence-based observation turned into concrete actions, each with an owner. It is not a summary for the human.

## Rules That Always Apply

- **Unconditional.** The calling stage runs it without asking. A retro that can be declined gets declined exactly when it was needed.
- **Never ask the human to narrate.** You observed the session; you write the synthesis. Ask only for a fact you could not have observed, and say why.
- **Every friction point has a root cause.** A vague observation is not a finding.
- **Every action has an owner stage and an evidence pointer.** No exceptions (Step 3).
- **Label claims.** `[Verified]`, `[Inference]`, `[Speculation]` or `[Unverified]`. A count or status is reported "as at `<SHA>` / `<UTC time>`", not as a standing fact.
- **The retro proposes; it does not legislate.** It never edits the constitution, the agent instruction file, a guide or a pack file directly. Those changes become actions; Tidy files them as work items.
- **No silent writes.** Report every file written, with its path.

---

## Inputs

| Input | Source |
|---|---|
| Stage | The calling stage: `ideate`, `draft`, `iterate`, `deliver` or `investigate` |
| Lane id | From the stage's arguments (`lane:<lane-id>`). Invoked directly: derived from the item ref by the direct-run lane-id rule in `lane-contract.md` §3 |
| Work item | `item:<item-ref>`, read with the board adapter's `read_item` |
| Evidence | The session itself, `git log` and `git diff` for this stage's commits, PR threads and checks, the handoff note, `specs/<feature>/decisions.md` |

Read `.specify/extensions/aididit/aididit-config.yml` for `retro.directory` and `panel.practitioners`.

---

## Step 0 — Pre-flight

Run in parallel, before drafting anything:

1. Read the retros this lane already has in `<retro.directory>/<lane-id>/`, so you do not re-propose an action an earlier stage already raised. If it recurs, say so: recurrence is evidence for Tidy's graduation criteria.
2. Skim the constitution (`.specify/memory/constitution.md`) and the agent instruction file only where you need to check whether a rule already exists. Do not reload them in full.
3. Note whether `<retro.directory>/<lane-id>/` exists; create it when writing (Step 5).

---

## Step 1 — Identify the Session

From the session record: the stage, the work item and feature, the session boundary (first meaningful tool call to now), and the outcome (artifacts produced, PR opened, checks green, verdict returned).

---

## Step 2 — Reflect (AI-synthesised)

### What went well (2 to 4 items)

Name the step, gate or pattern that delivered value, with its evidence. No generic praise.

### What hurt (2 to 4 items)

For each:

- **What happened**: concrete (the file, tool, step or gate).
- **Impact**: time lost, rework, quality risk, extra round trips.
- **Root cause**: an instruction gap in a stage file, a tool limitation, context pressure, a missing guard, or a human workflow issue.

### Pattern scan

Look at this stage's commits for mistake patterns: fix-up commits, reverts, the same file edited repeatedly to correct itself, findings that recurred across loop rounds, guards that could not fail or could not pass. A pattern that recurs within the stage, or that an earlier retro in the lane already named, is an action candidate.

### Stage efficiency (Deliver must include it; others where useful)

| Command or sub-agent | Times run | Context cost (High / Med / Low) | Improvement |
|---|---|---|---|

Every High row needs a concrete improvement, and the improvement has a route: it becomes an action in Step 3 (counted against the five), or, when the actions are full, it is listed in the handoff note's proposed edits as an unvetted candidate. An improvement written only here is lost.

### Context

Usage (Low, Moderate, High, Critical), the biggest consumers, and whether context pressure forced a shortcut, a truncated read or a skipped step.

### Token usage (optional)

If your agent exposes token usage for the session, record it with its source. Label estimates with `~` and name the estimator. A measurement of what files cost to *load* is a footprint, not spend; never add footprints from several sessions together.

---

## Step 3 — Actions

Turn what hurt (and what went well, where it should become standard) into **one to five actions**. Each action has:

| Field | Content |
|---|---|
| Action | What should change, specific enough to act on. For a rule, the exact proposed wording |
| Kind | `rule` (constitution or agent instruction file), `guide`, `stage` (a pack command or shared file), `follow-up` (a defect, test, instrumentation or cleanup item), `learning` (worth remembering, changes no rule) |
| Owner stage | Who acts on it: `tidy` (the default: Tidy files it as a work item), or the current stage when it can and must be done before this stage ends (for example a factual error in a file this branch already changes) |
| Evidence | A pointer someone else can follow: a commit SHA, `file:line`, a PR thread URL, a check run, a log line, a decisions-ledger entry |
| Target | For `rule`, `guide` and `stage`: the file and section it would change |

An action without an owner is not acted on. An action without evidence cannot be judged by the panel or by the Tidy graduation criteria.

---

## Step 4 — Panel Vetting of the Actions

Before anything is recorded as agreed, have the actions vetted. This is a review round, not a decision round (`panel-guide.md` P3): it checks wording, placement and duplication, so it needs no citations.

1. Start **one** fresh reviewer (a sub-agent if your agent has them) that applies every `panel.practitioners` lens in turn, in labelled sections, without carrying one lens's conclusion into the next.
2. Give each **only** the actions verbatim, the one-line evidence for each, and the titles of existing rules or earlier retro actions that might duplicate them. Tell them **not** to read the repository: this is a cheap vet of wording, placement and duplication, not a code review.
3. Each lens returns, per action: **KEEP**, **REFINE** (with tightened wording), **MERGE** (into a named existing rule or action inside the project) or **DROP**, with a one-line reason. A MERGE into anything outside the project counts as a DROP.
4. Majority rules; record dissent. Apply the refinements.

**Who ratifies:**

| How the stage was started | Ratification |
|---|---|
| In a lane | The panel's consensus **is** the ratification. Do not stop for the human. |
| Invoked directly | Present the panel-refined actions; the human approves all, approves some by number, declines, or redirects. Record the answer. |

---

## Step 5 — Write the Retro

Path: `<retro.directory>/<lane-id>/<stage>.md` (for example `.specify/aididit/retros/<lane-id>/deliver.md`). If the file exists (a stage that ran twice), append a new dated section; never overwrite an earlier retro.

```markdown
---
lane: <lane-id>
item: <item-ref>
stage: <stage>
date: <YYYY-MM-DD>
as_at: <HEAD SHA>
context: Low | Moderate | High | Critical
tokens: <figure and source, or "not exposed">
---

# Retro: <item-ref>, <stage>

## What went well
## What hurt
## Pattern scan
## Stage efficiency
## Actions

| # | Action | Kind | Owner | Evidence | Target | Panel verdict |
|---|---|---|---|---|---|---|

## Declined
<actions dropped by the panel or the human, with the reason, kept for reference>
```

### Where it goes, by stage

**Retro commit subject.** Every stage that commits its retro uses `chore(retro): <stage>-stage retro for <item-ref>`, with the stage's name; a direct run with no item ref uses the feature slug in its place.

| Stage | Persistence |
|---|---|
| Draft, Iterate, Deliver | Commit the retro file on the lane branch by explicit path with the retro commit subject, then push. It rides the PR to the default branch. Deliver's is the last that can. |
| Ideate (Mode B), lane continues | If the lane branch exists (a lane: Assemble created it), commit it on that branch by explicit path the same way; it rides the PR with the rest. If no branch exists yet (a direct run), write it to `.specify/aididit/lanes/<lane-id>/ideate-retro.md` instead; Draft copies it to `<retro.directory>/<lane-id>/ideate.md` once it has created the branch, and commits it. |
| Ideate (Mode B), lane ends at Ideate | No PR will carry it. Do not write it under `<retro.directory>` or commit it: a commit on a branch nobody opens a PR for is stranded. Put the retro in a board `comment` on the work item and in the handoff note. |
| Investigate | Post-merge: no branch. Do not write a file under `<retro.directory>`. Put the retro in the QA record (a board `comment` headed `## Retro`) and, verbatim, in the handoff note, where Tidy reads it. |

### Lane rules

- **Lanes do not edit method files** (`.specify/extensions/aididit/`, the constitution, the agent instruction files), except a lane whose allowed paths name a project method file. Actions that would change them are recorded here with owner `tidy`, and also listed in the handoff note (target, exact wording, evidence, panel verdict); Tidy routes each by the upstream route (`lane-contract.md` §6).
- **Read before you write** any file sibling lanes might also write, and merge rather than replace.
- **When the retro's target is the artifact under test.** If the lane delivered the very file a retro action would change, do not change it here: the edit would be an out-of-scope change, and it can silently invalidate the acceptance evidence the lane just took against that file. Record the action with owner `tidy` and say why.

### Agent memory (optional)

If your agent keeps persistent memory outside the repository, a `learning` action may also be written there: lead with the rule, then a **Why:** line and a **How to apply:** line, absolute dates only. Memory is pulled, not pushed, so a rule that must fire every time does not belong there; that is a `rule` or `stage` action for Tidy.

---

## Step 6 — Self-Check Before Reporting

- [ ] Nothing in the retro came from asking the human to narrate.
- [ ] Every friction point names a root cause.
- [ ] Every action has a kind, an owner stage and an evidence pointer that resolves.
- [ ] The panel vetted every action, and the ratification is recorded (panel in a lane, human when direct).
- [ ] No standards, guide or pack file was edited by the retro.
- [ ] The whole retro passed the secret scan (`disciplines/prompt-crafting.md`), personal data included, before it was written.
- [ ] The retro is persisted per the table above, and committed where the table says so.

---

## Output

Report to the calling stage, in this shape:

```text
Retro: <item-ref> <stage> — written to <path or "QA record + handoff note">
  went well: <n>   hurt: <n>   actions: <n> (tidy: <n>, this stage: <n>)   declined: <n>
  committed: <SHA | not committed (reason)>
```

The calling stage then continues with its handoff or stop.
