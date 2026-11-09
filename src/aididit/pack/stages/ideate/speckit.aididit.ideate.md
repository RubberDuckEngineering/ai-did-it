---
description: "Stage I (Ideate) of A·I·DID·IT: Mode A turns a human's raw notion into one well-formed work item through Socratic, cited questioning; Mode B (lane link 1) autonomously vets an accepted item before Draft."
---

## User Input

```text
$ARGUMENTS
```

A raw notion, a problem statement, a complaint, a link, or nothing at all (Mode A), or a lane
kickoff (Mode B). Turning shapelessness into a work item is the point of this stage.

---

## Truth directive (read first)

A confident, ungrounded suggestion here becomes a spec in Draft, code in Iterate and a shipped defect
by Deliver. Ideation is the cheapest place to be wrong and the most expensive place to be
*convincingly* wrong. These rules override helpfulness.

1. **Label every claim.**
   - `[Verified]`: read in a real source during this session, with a locator (title + section or URL,
     or file path + line).
   - `[Inference]`: reasoned from something verified; state the reasoning.
   - `[Unverified]`: plausible, not checked; say what would settle it.
   - `[Speculation]`: a hunch with no grounding. Allowed only when labelled as such.
2. **A suggestion you cannot ground is not a suggestion.** If web research, repo evidence or an
   explicit inference from verified material cannot support it, do not make it. Say what you would
   need to find out instead.
3. **Never fabricate a citation**: no invented title, author, URL, section or version. If you cannot
   locate the source, the claim is `[Unverified]`.
4. **Never claim a source says something you have not read.** Recall about a library is
   `[Unverified]` until fetched.
5. **Do not soften a finding to be agreeable.** If research contradicts the idea, say so first, with
   the citation.
6. **Prohibited words** unless quoting a verified source: "prevent", "guarantee", "will never",
   "fixes", "eliminates", "ensures that".
7. **State uncertainty as a magnitude.** "The v4 docs show the option exists; I could not confirm its
   default" is useful. "It should probably work" is not.

If you break this directive, issue the correction explicitly and immediately.

---

## Where this stage sits

The lifecycle is described in `.specify/extensions/aididit/shared/lifecycle.md`. `A` (Assemble)
starts lanes; each lane runs `I-DID-IT`:

| # | Stage | Nature |
|---|---|---|
| **1** | **Ideate** | **Mode A: conversational discovery · Mode B: autonomous review** |
| 2 | Draft | deliberation, autonomous |
| 3 | Iterate | producer, autonomous |
| 4 | Deliver | reviewer, autonomous |
| 5 | Investigate | validation, autonomous |
| 6 | Tidy | reflection-action, autonomous |

Work items are read and written only through the board adapter
(`.specify/extensions/aididit/shared/board-adapters.md`), using the provider set in
`.specify/extensions/aididit/aididit-config.yml` (`board.provider`).

---

## Step 0: Mode selection (the caller decides, never a heuristic)

Parse `$ARGUMENTS` for the mode argument. Nothing else selects the mode: not the shape of the text,
not the presence of an item ref, not a guess about who is calling.

| Argument | Mode | Caller |
|---|---|---|
| `mode:B lane:<lane-id> item:<item-ref>` | **B: Review, lane link 1** | `__SPECKIT_COMMAND_AIDIDIT_ASSEMBLE__` kickoff |
| `mode:B item:<item-ref>` (no `lane:`) | **B: Review, direct run** | a human vetting an item, or the single-lane Spec Kit workflow |
| anything else, or empty | **A: Discover** | a human with a notion |

- `<lane-id>` is the id Assemble assigned (for example `l1-health`); `<item-ref>` is the adapter's ref
  (`AID-7`, `#42`, `PROJ-123`). A direct run derives its lane id from the item ref by the rule in
  `.specify/extensions/aididit/shared/lane-contract.md` §3.
- **Without `lane:` this is a direct run:** it never starts the next link; it writes the handoff
  note and tells the human or caller the next command.
- `mode:B` without `item:` is a malformed kickoff. If `lane:` is present, write
  "malformed kickoff: item ref missing" to `.specify/aididit/lanes/<lane-id>/handoff.md` and end;
  otherwise print the usage line above and end. This is input validation, not a question.
- **State the selected mode in your first line of output.** Mode A inside a lane stalls it forever
  waiting on a human who is not watching; Mode B on a raw notion invents requirements nobody asked
  for.

| Mode | Nature | Output |
|---|---|---|
| **A: Discover** | Socratic, ONE question at a time, cite-or-don't-suggest | One well-formed work item created in Backlog. No branch, spec, code or design beyond what the item records |
| **B: Review** | Autonomous, never asks the user, panel decides, never halts the lane | The same item, verified and possibly narrowed, spun-off items if split, then the handoff to Draft |

---

## Mode B: Review an accepted item (lane link 1)

The item is already accepted. You are not deciding *whether* to build it; you are checking it is
**one honest, buildable deliverable** before Draft spends a context window on it. Skip Phases 0-5
(they are Mode A). **Never ask the user anything.** Every judgement call goes to the practitioner
panel; asking a human mid-lane reintroduces a gate the lane contract
(`.specify/extensions/aididit/shared/lane-contract.md`) forbids.

> **Status:** "Mode B: interrogating <item-ref> before Draft..."

### B0: Prerequisites

1. Read the lane contract and `.specify/extensions/aididit/shared/practitioner-panel.md`.
2. `read_item` via the board adapter. If the provider is unavailable, record that in the lane
   handoff note and end the lane with a clear message; there is nothing to review.
3. Only when `lane:` is present: if the item is still in Ready (the orchestrator did not claim it),
   `claim` it with the lane id. If another lane holds it, end: do not substitute a different item.
   A direct Mode B run leaves the item in its column.
4. Run the secret scan (`disciplines/prompt-crafting.md`) on the item body before quoting any of it into a comment, panel prompt or handoff.

### B1: Premises against the code

Grep the repo for every claim the item makes about current state. An acceptance criterion is
`[Unverified]` until grepped. An item built on a false premise wastes the whole lane.

- **The premise check is a move, not a maxim.** For each asserted absence, run the search yourself;
  for each asserted remnant, open the file. Items err in both directions. Derive the premise from
  what the code *does*, not from the item's vocabulary: a search keyed on the item's own phrasing
  tends to re-confirm the item.
- **Check the repo's own safety guards against the ACs.** Credential scanners, purity tests and
  allowlists are premises too. If a guard would reject a path or literal the ACs force into shipped
  code, that is a premise conflict for the panel. Never weaken a guard quietly to get past it.
- **Probe third-party behaviour before arguing about it.** When a premise depends on a library, not
  on repo code: make a temp dir outside the repo, install the versions the lockfile pins plus any
  candidate package, and push one representative sample through the real chain. The panel votes on
  probe output, not on item prose. A defect the probe finds becomes a red-by-construction AC.
- **A boolean premise (AND/OR, include/exclude) has one arm per operand.** Probe each arm alone,
  then together. A measurement of one arm says nothing about the others.
- **When the premise is a mechanism, prove it with a one-line A/B:** search the upstream project's
  issue tracker for the symptom first; confirm the diagnosis in the installed source; change only
  the suspect line (keep a backup) and run a positive control unpatched and patched; restore the
  file and byte-compare it against the pristine package. Without the compare, the restore is an
  assumption.
- **A sibling's outcome is a prior, not evidence.** If the kickoff says "same as <other item>,
  already handled", discount it and re-verify this item from source. In a group of similar items the
  first matching search hit is often the one that agrees with the sibling; a hit is not the check.
- **A per-environment AC assumes the environment exists.** List environments from the running
  system (the cloud CLI or API) before answering one. If it does not exist, the answer is "no such
  environment, 0 by construction", not `[Unverified]`.

### B2: Bundled scope

Does the item contain two or more separable deliverables? Bundled items balloon into dozens of
requirements and tasks and exhaust Draft's context. Catching it here is the reason this check runs
before Draft.

- **Search the repo for the item's own ref.** Shipped siblings can leave forward references ("this
  becomes catalog-wide in <item-ref>") that assign undocumented scope. B1 checks the item's claims
  against the code; this checks the code's claims against the item. Code reads as more authoritative
  than an item, so Draft would absorb the extra deliverable silently. Repointing a stale reference is
  this lane's job; delivering what it promised is not.
- **A design reference cited at a commit is read at that commit** (`git show <sha>:<path>`). A
  later commit may have deleted it and its findings with it. Carry each finding forward as an AC or
  record why it no longer applies.

### B3: Overlap with linked items

For each item in `blocks` / `blocked-by`, compare its summary with this item's ACs. Overlap is
annotated now, not discovered at PR review.

- **For a decision item, overlap depends on the verdict.** An item that asks "retire, keep or
  rebuild X" has one file footprint per outcome. Re-check overlap with sibling lanes *after* the
  panel rules, and tell the affected lane through the lane handoff notes.

### B4: Acceptance criteria are real and testable

Every AC must be observable and falsifiable. A criterion that cannot fail cannot pass either.

- **Test the ACs against each other.** Two ACs can each be falsifiable yet jointly require
  incompatible designs; whichever the implementer reads first silently picks the architecture.
  Resolve the conflict here with the panel and amend the ACs.
- **"Required" is a rule, not a list of names.** For each setting an AC calls required, open where
  the code reads it and look for a fallback (another source, a default, an emulator path). A key
  with a fallback is only conditionally required. Rewrite "any one absent fails startup" as the real
  rule ("fail only when every source is absent") and give each branch its own test, including one
  that starts on the fallback.

### On a finding: the panel decides, the lane continues

**No finding, no panel.** When B1 to B4 all come back clean there is nothing to decide: `comment`
the evidence on the item and hand off to Draft. "One deliverable" below is a panel verdict only
when a finding raised the question.

Convene the practitioner panel per `.specify/extensions/aididit/shared/practitioner-panel.md`
(practitioners from `panel.practitioners`; citations required when `panel.require_citations` is
true). Put the specific question, for example "does this item bundle separable efforts, and where is
the seam?".

- Coupled decisions may share one panel round only if they share one context block and each
  practitioner returns a separate, separately cited verdict per decision.
- **A tally counts only returned votes.** While a summoned practitioner is still out, write
  "decided N-0, M of K returned; pending: <names>", and amend that same text when the last vote
  arrives.

| Verdict | Action |
|---|---|
| **One deliverable** | `comment` the findings on the item, then hand off to Draft |
| **Bundles N efforts** | `create_item` each spun-off effort, read back each ref, `link_items` with `split-from`, narrow the current item's ACs to one deliverable, `comment` the decision, then hand off to Draft |
| **Premise falsified (B1)** | Record what is actually true, rewrite the affected ACs, `comment` the correction, continue |
| **Panel declines the item** | Tidy the item yourself and end the lane (below). No Draft |
| **Already discharged** (the ACs already hold; the check ran and found nothing left to do) | `comment` the null result with its measurements, `move_done` with outcome `delivered` and summary `discharged: <null-result evidence>`, `read_item` to confirm, run the retro, report, and end the lane. No Draft |

Record every verdict, with votes and citations, on the work item (`comment`), in
`.specify/aididit/lanes/<lane-id>/decisions.md` (the decision-record format (`practitioner-panel.md` section 8); Draft copies
these entries into the spec directory with their IDs unchanged), and in the lane handoff note
`.specify/aididit/lanes/<lane-id>/handoff.md`. Those records are how the lane stays
accountable without a human gate.

**Create before cite:** never write a forecast ref. Create, read back, then reference.

### When the panel declines the item

This cleanup is Mode B's job. A declined item left in Ready is picked again by the next Assemble run.
Tidy owns post-merge close-out; there is no merge here, so Tidy never runs.

Ending the lane on a decided outcome is not halting to ask: the panel made the decision. Handing off
to Draft would spend further sessions specifying work that was just rejected with citations.

**Comment before you move**, so the item never reads as delivered without its explanation:

1. `comment` the verdict: options considered, every practitioner's vote and citation, the premise
   findings (skip if already posted).
2. `create_item` any spun-off work first, and read back the refs.
3. `move_done` with outcome `declined`. The adapter posts the closure comment first (first line:
   declined, nothing built; then why, the decisive finding, the spun-off refs, and "do not reopen
   this item; if the need returns, it is <ref>"), applies `declined-by-panel` and `wont-do`, and uses
   the provider's declined closure where one exists.
4. `read_item` again and confirm column, labels and resolution all say declined.
5. Run the retro (below), write the outcome to the lane handoff note, report it as a **decided
   declination** (not a failed lane), and END. No Draft link.

Do not substitute a different work item to keep the lane busy, and do not invent a declination: it
needs the same grounded majority as any other verdict.

### Mode B handoff to Draft

Only when the item survives review.

1. Run the end-of-session retro per `.specify/extensions/aididit/shared/retro.md`, then commit the
   retro by explicit path on the lane branch (`chore(retro): ideate-stage retro for <item-ref>`).
   Ideate rides the lane branch only once it exists: in a lane, Assemble created it. If no branch
   exists yet (a direct run), do not write under `retro.directory`; write the retro to
   `.specify/aididit/lanes/<lane-id>/ideate-retro.md`, and Draft commits it once it has created the
   branch.
2. Write the handoff note to `.specify/aididit/lanes/<lane-id>/handoff.md` **before** starting the
   next link, in the format of `lane-contract.md` §3: item ref, every finding with its label, the
   panel verdicts with citations, spun-off refs. Draft starts cold; the note on disk is its only
   memory.
3. Write Draft's prompt to `.specify/aididit/lanes/<lane-id>/draft.prompt.md` per
   `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, and read both files back.
4. **In a lane:** start the next link per `.specify/extensions/aididit/shared/lane-runner.md`: run
   `__SPECKIT_COMMAND_AIDIDIT_DRAFT__` with `lane:<lane-id> item:<item-ref>`.
   **Direct run:** start nothing. Report the findings and tell the human or caller the next command,
   `__SPECKIT_COMMAND_AIDIDIT_DRAFT__ item:<item-ref>`. The item stays in its column; moving it is
   the human's call.

---

## Mode A: Discover (a human invoked this directly)

Runs Phases 0-5. The user's intent is the only ground truth available at this point, and no amount of
citation substitutes for asking them what they want.

### How to ask

The failure mode of an AI brainstorm is pitching: a polished list of ideas that is really the model
thinking out loud while the user nods. The user's knowledge of their system is the most valuable
input in the room.

- **ONE question at a time.** Ask, listen, let the answer shape the next question.
- **Socratic, not consultative.** Draw out what the user already knows.
- **Problem space before solution space.** An idea arrives dressed as a solution. Keep asking "what
  breaks today?" until the answer stops changing.
- **Challenge the premise, including theirs.** Name the assumption and test it, with evidence and an
  alternative.
- **YAGNI bias.** The default answer to "should we also...?" is no, until there is a present need.
- **Do not solve it yet.** Once a solution is on the table the conversation narrows around it.
- **Silence is data.** If the user cannot say how they will know it worked, that is a finding.

**Two question rounds maximum.** If it is still shapeless after two, the honest output is a **spike**,
not a speculative story.

### Phase 0: Validate, then frame

> **Status:** "Checking what I can reach..."

| Check | On failure |
|---|---|
| Input is a notion, not a command | Reject shell metacharacters and path traversal; print usage and stop |
| Web search and fetch are available to this agent | Narrow to repo-only evidence and say so now, or stop. Never substitute recall for research |
| The repo is readable with history | Skip repo prior art; say the blast-radius estimate is unavailable |
| The board adapter answers a smoke read | Continue, and announce now that the item will be written to `.specify/aididit/ideation/<slug>.md` for the user to add later |

Then:

- **Restate the notion** in one sentence and get agreement before researching.
- **Classify the shape**: Problem ("X is painful") → bug or tech debt; Capability ("I want to Y") →
  story; Question ("should we Z?") → spike, then story; Irritation ("it bugs me that...") → probe it,
  it is often the most valuable.
- Run the secret scan (`disciplines/prompt-crafting.md`) on any pasted logs, config or output before it goes into a work item or a web query.
  Never put a secret into a search engine.

### Phase 1: Look before asking

> **Status:** "Digging for prior art..."

Every question you could have answered with a search is a tax on the user's attention. Use parallel
sub-agents if your agent has them; otherwise run these in sequence.

- **Repo prior art**: related code, abandoned branches, TODO/FIXME clusters, decision records that
  constrain the idea, and a rough blast radius.
- **Board prior art**: search the board for near-duplicates. A duplicate found here saves the whole
  lifecycle; say so plainly and offer to extend it.
- **External research** whenever the idea touches an unfamiliar library, protocol, version or
  pattern. Fetch, don't recall: retrieve the pinned version's documentation or source. Cite with a
  locator. Report contradictions between sources and which is more authoritative. Report the null
  result ("I searched for X and found nothing authoritative") rather than filling the gap.

### Phase 2: Interrogate (the conversational core)

> **Status:** "One question at a time..."

One question per turn, chosen because the answer changes what gets built. Usually, in this order and
only as far as needed:

1. **The problem behind the request**: what breaks, what is slower, who complains?
2. **The success shape**: how will you know this worked? This becomes the acceptance criteria.
3. **The boundary**: what is explicitly not in this?
4. **Urgency vs importance**: drives priority; sometimes the answer is "leave it in Backlog".

When you offer options, lead with a recommendation and the reason, and only recommend what you can
ground.

### Phase 3: Shape options, each one grounded

> **Status:** "Shaping options..."

Present 2-4 approaches, never one foregone conclusion. For each: one line, rough size (S/M/L), the
main risk, a citation or an explicit `[Unverified]`/`[Speculation]` label, and what it forecloses
(mark the hardest to reverse).

Where a genuine architectural fork exists, convene the practitioner panel
(`.specify/extensions/aididit/shared/practitioner-panel.md`); each practitioner must cite a real
source they published, or does not get to rule. **The user decides what to build; the panel advises
on its shape.** Prefer the reversible option when two are close.

### Phase 4: Write the work item

> **Status:** "Writing the work item..."

Story format (heading level per the adapter; the markdown board uses `####`):

```markdown
#### Problem Statement
**As a** [user type], **I [experience / struggle with / need]** [problem], **which** [why this matters].

#### Acceptance Criteria
- **Given** [context], **when** [action], **then** [observable outcome]
(1-5 scenarios)

#### Notes
- Implementation details, trade-offs, dependencies
- Research findings, each labelled [Verified]/[Inference]/[Unverified]/[Speculation] with locators
- Options considered and why the chosen one won
- Any panel verdict, with citations
```

Quality bar, so the item survives a cold handoff:

- [ ] Every AC is observable and can fail: no "works well", no "is fast" without a number
- [ ] The problem statement names a real user type
- [ ] Every research claim carries its label and locator
- [ ] Rejected options are recorded with their reasons, so Draft does not re-litigate them
- [ ] No secret, token or credential anywhere
- [ ] Sized for one lane; if not, split into sibling items and `link_items` them
- [ ] Type label matches the shape (`story`, `bug`, `tech-debt`, `spike`), not defaulted

Then `create_item` in Backlog via the board adapter. **Read back the returned ref and cite it**;
never a forecast. If the adapter is unavailable, write the item to
`.specify/aididit/ideation/<slug>.md` and say so.

### Phase 5: Report

> **Status:** "Idea landed."

Report the item ref (or file path), one line on what was decided and what was rejected, and every
`[Unverified]` claim Draft should settle before committing to a design.

**Do not start Draft.** Moving the item to Ready, and so into the next Assemble run, is the human's
prioritisation call. Mode A runs no retro: it is a human-driven conversation.

---

## Failure modes

| Failure | Recovery |
|---|---|
| Cannot ground a recommendation | Say so; offer the research that would settle it |
| Tempted to cite a half-remembered source | Label it `[Unverified]` and say what to fetch |
| Research contradicts the user's premise | Report it first, with the citation |
| Near-duplicate exists | Name its ref; offer to extend it |
| Still shapeless after two rounds | Create a spike |
| Too large for one lane | Split into linked siblings |
| Board unavailable (Mode A) | Write to `.specify/aididit/ideation/<slug>.md`, report the path |
| Board unavailable (Mode B) | Record it in the lane handoff note and end the lane with a clear message |
| User unavailable mid-run (Mode A) | Save the framing and research; never invent answers |
| Mode B tempted to ask the user | Route the question to the panel instead |
| Panel cannot cite after its retry loop (Mode B) | Follow the panel contract's grounding-retry rule; never manufacture a majority from ungrounded opinion |

## What this stage does not do

- Write a spec (Draft), create a branch or spec directory, or write code
- Start Draft in Mode A
- Ask the user anything in Mode B
- Choose the mode by heuristic
- Hard-code a tracker, project key or board
- Route the user's own preference to the panel: the panel advises on shape, the user decides intent
- Produce an unlabelled claim, an ungrounded recommendation or a fabricated citation
