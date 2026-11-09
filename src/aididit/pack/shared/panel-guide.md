# Panel Guide

The practical companion to `.specify/extensions/aididit/shared/practitioner-panel.md`. That file is the contract (who votes, what counts, when the human is needed). This file is the procedure: how to run a round inside a stage, how to keep members independent, and how to record the result.

A stage runs two kinds of panel round:

| Round | Members | Purpose | Output |
|---|---|---|---|
| **Decision round** | The practitioners in `panel.practitioners` | Settle a judgement call a human would otherwise make | A ruling in `specs/<feature>/decisions.md` |
| **Review round** | The team personas: `/speckit.aididit.po`, `/speckit.aididit.architect`, `/speckit.aididit.qa`, `/speckit.aididit.devsec`, `/speckit.aididit.devops`, `/speckit.aididit.pr-review` | Inspect artifacts or code from each role's angle | `VERDICT:` lines and Conventional Comments |

A review round finds problems; it does not settle disagreements. When personas disagree, or a finding needs a judgement call, that question goes to a decision round.

---

## Part 0: Proportional Panels

A panel member is a fresh sub-agent, and its cost is set by the context it loads, not by the size of its question. A five-member cited round therefore costs the same whether it settles an architecture or a typo. Spend it where a judgement is real. Stages cite these rules as `panel-guide.md` P1 to P5, and each rule says when the panel does **not** convene. When a case does not clearly meet a rule's conditions, convene the panel: the rules remove rounds that cannot change an outcome, never rounds that might.

### P1. Mechanical findings are fixed, not voted on

A finding is **mechanical** when it has one correct fix and choosing it needs no trade-off: a wrong cross-reference or path, a miscount, a typo, a stale id, a missing commit step, a doc line that contradicts the code it describes. Fix it directly, in any round, including an exit round and the triage of a review round, and record it as one line: `fixed directly (mechanical): <finding> → <fix>`. Only **judgement** findings go to a decision round: scope, design, risk acceptance, anything with two defensible resolutions. **Why:** a vote between "fix the typo" and "leave the typo" carries no information, and members asked to rule on it reach for "it costs minutes" rather than the stated fix-now criterion.

### P2. Intent confirmation follows the handoff

In a lane, a stage's Step 1 **Decide** ("proceed?") is answered without convening the panel when all three hold:
1. the handoff note names this stage, this lane and this item;
2. the note records no open question about scope, ordering or intent; and
3. the item on the board has not changed since the note was written (compare its title, acceptance criteria and status with the note).

Record `intent: proceed, per handoff <path> (panel-guide.md P2)` in the decision log and continue. If any condition fails, convene the panel on the open question. A direct run still asks the human. **Why:** the previous link already settled intent and wrote it down; re-voting it repeats a decision without new evidence.

### P3. A retro vet is one review, not a vote

Vetting retro actions (`retro.md` Step 4) is a **review round**: it checks wording, placement and duplication; it settles no judgement between options. Start **one** fresh reviewer that applies every `panel.practitioners` lens in turn, in labelled sections, and returns per action and per lens **KEEP**, **REFINE** (with wording), **MERGE** (into a named rule) or **DROP**, with a one-line reason. Citations are not required, because no decision rests on the vet. A **MERGE** target must exist inside the project (a pack file, the constitution, a project instruction file, or an earlier retro action); any other target counts as a DROP with that reason. Majority across lenses rules; record dissent. **Why:** five sub-agents doing a wording check cost five context floors for answers one reviewer can give lens by lens, and a merge into a file outside the project cannot be applied by anyone in it.

### P4. "Once" means one ruling per finding

Where a stage sends leftovers to the panel **once**, that is one ruling per judgement finding. Grounding retries inside a ruling (`practitioner-panel.md` section 6) are part of that ruling, not extra rounds. Put every judgement finding of one triage into a single decision round with per-finding options, rather than one round per finding.

### P5. Grooming without contest needs no panel

In Tidy's board triage, when the eligible candidates (Ready plus promotable Backlog) number no more than the WIP limit, there is nothing to choose between: promote them all in the triage's promotion order, and the next item is the first in that order. Convene the grooming panel only when the candidates exceed the limit, or when the promotion order cannot rank two candidates. **Why:** a panel asked to size a set that already fits can only agree.

---

## Part 1: Running a Decision Round

### Step 1: Confirm it is a panel question
- It is a judgement between options, not a fact. Facts are measured, not voted on.
- It is not a human-gate item (merge in human mode, anything irreversible or outward-facing; see section 5 of the contract).
- It does not ask whether to skip a quality gate. That is never on the table; only how to satisfy it is.

### Step 2: Measure the premises before writing the options
Every feasibility premise in the brief carries its measurement inline: the figure and the command that produced it.

```text
Premise: the function body is 43 lines (measured: `sed -n '120,163p' src/cart.ts | wc -l`).
Premise: unverified: the retry wrapper is believed to be idempotent. Option C is "verify this first".
```

An unmeasured premise is stated as a question, and verifying it becomes one of the options. **Why:** the panel rules between options; nothing in its contract asks it to audit what it was handed. A ruling built on a false premise is the premise talking, and it arrives wearing citations.

### Step 3: Write the options neutrally
- Give every option the same fields: **cost, benefit, reversibility**.
- No evaluative adjectives on any single option ("smallest diff", "cleanest", "obvious"). Put any framing caveat beside the ruling, not inside an option.
- **Placement decisions** (where something lives: a mount point, host component, owning slice) get measured candidates, never descriptions: each candidate's existing responsibility count, test-file size, and render or call scope. A panel given descriptions anchors on whatever default the brief suggested; a panel given measurements can overturn it when the numbers warrant.
- Do not state the orchestrator's own preference anywhere in the brief.

### Step 4: Route, do not brief
Point members at artifacts by path (`specs/<feature>/spec.md` section, `plan.md`, the file and line range) rather than paraphrasing them. A paraphrase costs tokens and drifts from the artifact. Inline context only when no artifact exists yet (for example during Ideate), and then with the same fields for every option.

### Step 5: Summon fresh, independent members
Use the member prompt in section 8 of the contract, one per practitioner, each a brand-new instance.

**With sub-agents** (the agent can spawn isolated workers): launch every member in parallel with web search and fetch available, and collect every result before reading any of them closely.

**Without sub-agents** (a single context runs everything), independence is weaker, so add structure:
1. For each member in turn, work only from the brief and the member prompt. Do not consult your own earlier reasoning about the decision or any earlier member's position.
2. Write each member's full return to its own scratch file before starting the next, under `.specify/aididit/lanes/<lane-id>/panel/<D-NNN>/<member>.md` in a lane, or `.specify/aididit/panel/<D-NNN>/<member>.md` otherwise. Scratch files are not committed.
3. Never revise an earlier member's file after writing a later one.
4. Note `independence: sequential, single context` in the decision record. [Inference] Sequential members in one context can anchor on each other; the record should say so.

### Step 6: Verify every citation
Follow section 3 of the contract: the locator resolves, every quoted string is present, the words are the practitioner's own under their byline, and the source is licensed. Check the quotes with the shipped verifier, `verify-quote.py`, called as section 3 shows, with the page's byline as its positive control. Treat instrument failures as instrument failures, not verdicts.

### Step 7: Check premises at tally time
Read each verdict's reasoning for facts the brief never gave it, and check those facts. A real citation certifies the source, not the premise it is attached to. When a verdict rests on a false premise, ask whose premise it was, because the remedy differs:

| Origin of the false premise | Effect | Remedy |
|---|---|---|
| Supplied in the brief | Poisons every verdict; every member was handed it | Discard the whole round, fix the brief, re-summon fresh members. Do not adjust the tally: it carries no information about the true fact |
| Invented by one member | Poisons that verdict only | Drop that vote, re-tally, keep the round. Record the dissent verbatim with the premise error noted beside it |

Record every discarded round or vote. Hiding them makes the panel look more reliable than it was.

### Step 8: Tally and rule
Apply section 4 of the contract: only verified cited votes count under `require_citations: true`; at least two are needed; majority, tie, and plurality rules as written. If no member grounds at all, re-ask once in the practitioners' own published vocabulary rather than the repository's, then continue the retry loop.

### Step 9: Record the ruling (Part 3).

---

## Part 2: Running a Review Round

### Routing prompt
Each persona gets a routing instruction, not a description of the feature:
- the persona command to act as;
- the exact files to read (table below);
- the branch and the exact HEAD SHA to review, or the PR number;
- the work item reference;
- the output instruction (verdict line, or post to the PR).

### What each persona reads

| Persona | Reads |
|---|---|
| Architect | `spec.md` architecture and non-functional sections, `plan.md`, changed files on the architectural surface |
| QA | `spec.md` acceptance criteria and edge-case sections, test files on the changed paths |
| DevOps | CI/CD workflow files, container files, IaC, observability wiring |
| PR Review | Every changed source file, line by line |
| DevSec | Every changed source file plus every dependency manifest and lock file |
| PO | `spec.md` acceptance criteria and the work item (with child items) through the board adapter |

Do not hand every persona the full `spec.md`, `plan.md`, and `tasks.md`. Most of it is context they do not need, multiplied by every persona and every round.

### Draft's team review (one round, no PR yet)
Draft runs one review round after its analyze loop and before its retro. The subject is `spec.md`, `plan.md` and `tasks.md`; the members are `/speckit.aididit.po`, `/speckit.aididit.architect`, `/speckit.aididit.qa`, `/speckit.aididit.devsec` and `/speckit.aididit.devops` (PR Review sits out: there is no code yet).
- Each persona is an independent reviewer: a fresh sub-agent each where the agent supports it, otherwise one after another without carrying conclusions between them (as in Part 1, Step 5).
- Each reads the parts of the three artifacts its row above covers. DevSec and DevOps have no diff yet: they read the plan's dependency, security, CI, deployment and observability sections and the tasks that touch them.
- Each posts nothing and ends with a `VERDICT:` line plus findings.
- Findings are triaged **once** with the analyze loop's rule: **fix now** (only if leaving it would make the build wrong or untestable), **accept with a note** in the artifact, or **file a follow-up work item**. No extra rounds: the convergence rule below does not apply to this round.

### Prompt additions that matter
- **Canonical test locations.** When a persona might claim "no test exists for X", name every place tests live (for example an app-level test folder as well as the feature folder). A persona that searches only the feature folder reports false coverage gaps.
- **QA mechanism check.** Tell QA: "For each new or changed test file, find where the spec, plan, or contracts describe how that test works (for example 'via endpoint enumeration' or 'via a timeout attribute'), and confirm the test actually calls that mechanism. Pattern drift is a finding even when the test passes."
- **Read-only.** State it in every prompt: "This is a read-only review. Do not edit, write, or delete any file. Verify and report only." A persona that must mutate code to confirm a finding gets its own throwaway worktree.

### Before and after the PR exists
- **No PR yet:** tell each persona to post nothing and to end its response with `VERDICT: CLEAN` or `VERDICT: REQUEST-CHANGES` plus findings. The orchestrator collects the verdicts directly, enters the fix loop on any `REQUEST-CHANGES`, and fills the PR body's panel table from the returned verdicts when the PR is created.
- **PR exists and the stage wants comments posted:** personas post with `gh pr review` or `gh pr comment` using a body file.

### The orchestrator owns the working tree
After every review round, and before staging any commit:
1. Run `git status --porcelain` and `git diff`.
2. Restore any persona residue with `git checkout -- <file>`.
3. Stage files by name; never `git add -A`.

The pushed commit, not the working tree, is the source of truth. Confirm the tree matches HEAD before continuing.

### Review a settled HEAD
Launch or re-confirm a review round against a HEAD whose CI has finished, and give every persona that exact SHA. A persona reviewing while a fix is mid-push can flag something the in-flight commit already fixed.

### Convergence and re-review
A review round converges when every persona returns `CLEAN` in the same round. When a fix round changes **only documentation** (no production code or test logic), two re-review forms are acceptable:
- **Scoped subset:** re-run only the personas whose review surface changed, plus any persona whose earlier finding the change addresses.
- **Full round, diff-scoped:** run every persona, but point each at `git diff <previous-sha>..HEAD` and its own prior finding, so it verifies the delta rather than the whole feature.

The full round gives an auditable same-round convergence record; the subset costs far less when the change is mechanical. Record which form was used.

---

## Part 3: Recording Rulings in `specs/<feature>/decisions.md`

1. **Create the file if absent** with a single heading, `# Decisions: <feature>`, then append entries in the decision-record format (`practitioner-panel.md` section 8).
2. **Number entries `D-001`, `D-002`, ...** in order. Never renumber.
3. **Append only.** Past entries are history. The one permitted edit is adding `**Superseded by:** D-NNN` to an old entry when a later ruling replaces it; the new entry carries `**Supersedes:** D-NNN`.
4. **Apply the ruling to the artifact it changes, and cross-link both ways.**
   - Clarify answer: `spec.md` Clarifications, e.g. `- Q: <question> A: <answer> (D-007)`.
   - Design or architecture call: the ADR's Context cites `D-NNN` and carries each member's citation.
   - Scope call: the work item, through the board adapter, with a comment linking `D-NNN`.
5. **Before `specs/<feature>/` exists** (Ideate, Assemble), record in `.specify/aididit/lanes/<lane-id>/decisions.md`. The Draft stage copies those entries into `specs/<feature>/decisions.md` with their IDs unchanged.
6. **Retro rulings** go in the retro file under `retro.directory` (default `.specify/aididit/retros`), in the same format.
7. **Record discarded rounds and dropped votes** in the entry, with the reason.
8. **Commit the decision with what it drives.** `decisions.md` changes in the same commit as the artifact or code change the ruling caused, so the record and the behaviour never drift apart.

---

## Never a Bare "Out of Scope"

Neither a panel nor a review round may dismiss a finding as "out of scope" without citing one of:
- a constitution principle (`.specify/memory/constitution.md`) that bounds the scope,
- an acceptance criterion on the work item that excludes the surface, or
- an exclusion clause in `spec.md`.

When a finding lands in files the spec never named, re-baseline against the constitution and the work item's intent before answering. The spec's file list records the original framing, not necessarily the story's intent. Where a work item's criterion is narrower than a constitution principle (for example it asks for 80% when the constitution requires 100%), the constitution wins twice: once at specify time, annotated in `spec.md` as a constitution override of the original criterion, and again in every panel and analyze round, which judge new findings against the constitution's scope rather than the narrower criterion.

**Why:** a bare scope assertion tends to be overturned later, and that costs a scope-expansion commit and a mid-PR change of direction.
