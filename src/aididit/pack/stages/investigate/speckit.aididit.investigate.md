---
description: "Investigate stage (link 5 of a lane): adversarial post-merge check that the change works in the running system and broke nothing around it, returning a CLEAR, DEGRADED, REGRESSED or UNVERIFIABLE verdict with cited evidence."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). In a lane the input is `lane:<lane-id> item:<item-ref>`. Otherwise it is `item:<item-ref>` (the single-lane workflow passes this), a bare item ref, a PR number, or nothing (use the most recently merged PR on the current repository). **Without `lane:` this is a direct run:** it never starts the next link; it writes the handoff note and tells the human or caller the next command.

> "The null hypothesis is that it did not work. Report success only when refutation fails."

This is the **Investigate** stage of the A·I·DID·IT lifecycle and **link 5 of a lane**. It runs after the merge, consumes the change Deliver shipped, and hands to Tidy only when the verdict allows. Lifecycle overview: `.specify/extensions/aididit/shared/lifecycle.md`.

| Stage | Question it answers |
|---|---|
| Ideate | What should we build? |
| Draft | What exactly, and how? |
| Iterate | Does the code do it? |
| Deliver | Is it reviewed and merged? |
| **Investigate** | **Did it actually work, and did it break anything else?** |
| Tidy | What did we learn, and what is now stale? |

**Why this stage exists.** Every earlier gate is self-referential: it checks the change against its own definition. A green pipeline proves the written tests passed. It does not prove the change did what the work item asked, and it says nothing about the blast radius. Investigate is the first stage that checks the change against **reality**. The failure it catches is the expensive one: a delivery that is green, merged, closed and quietly wrong.

**Timebox: tight.** This is a scene sweep, not a forensic teardown. When it finds something it files a work item; it does not fix. A fix made here would land unreviewed, under a work item that is about to close, in a session with no spec.

---

## What This Stage Writes

Investigate produces **findings, not artifacts**. It runs after the merge, so it has no feature branch and no PR. It never creates or edits code, specs, docs or standards files, never commits, and never opens a branch.

| Output | Where it goes |
|---|---|
| Findings | New work items via the board adapter's `create_item` (Phase 4) |
| QA record | A `comment` on the work item via the board adapter (Phase 6) |
| Retro | Appended to the QA record under `## Retro`, and copied into the handoff note (Step 7) |
| Candidate rules and guide promotions | Actions in the retro and the handoff note; Tidy files them as work items |
| Handoff note | `.specify/aididit/lanes/<lane-id>/handoff.md` (git-ignored runtime state) |
| Board unreachable | The full content in your response **and** in the handoff note. Never a new tracked file |

**Where it runs.** In the primary checkout, on a detached `origin/<delivery.default_branch>`: `git fetch origin && git switch --detach origin/<delivery.default_branch>`. Never in a lane worktree.

The only files this stage writes are runtime state: the lane folder under `.specify/aididit/lanes/`, and the board file at `board.markdown_path` when `board.provider` is `markdown` (edit it only in the primary checkout, never a lane worktree's copy). Nothing goes into `<retro.directory>`: retro files are committed with the work, and a post-merge stage has no branch to commit on.

**Why:** a record written to a branch nobody opened a PR for, or left as an orphan file in a worktree, is lost while the board says the work is done. The board needs no branch, which is why it is the home for findings and evidence.

**Pre-handoff gate:** `git status --porcelain` shows no change outside runtime state (`lane-contract.md` §2), that is `board.markdown_path` and `.specify/aididit/lanes/` (a file under `<retro.directory>` is a change, not an exemption). Anything else is a write this stage should not have made: stop and name the files. Do not commit them and do not open a branch for them.

---

## Load-When Map

| Step | Load |
|---|---|
| Phase 0 | `.specify/extensions/aididit/aididit-config.yml`; in a lane, `.specify/extensions/aididit/shared/lane-contract.md` and the handoff note |
| Phase 1b, Phase 2 | Your agent's web search and fetch tools, for cited interpretations |
| Phase 4, Phase 6 | `.specify/extensions/aididit/shared/board-adapters.md` |
| Step 7 Retro | `.specify/extensions/aididit/shared/retro.md` |
| Step 8 Handoff | `.specify/extensions/aididit/shared/disciplines/prompt-crafting.md`, `.specify/extensions/aididit/shared/lane-runner.md` |

---

## Phase 0 — Establish the Subject

> Report: "Identifying what shipped..."

**0a — Lane.** In a lane, read the handoff note and confirm it names this stage and the work item, and that you can reach its `report to:` address ("report" is defined in `lane-contract.md` §3). Judgement calls in a lane go to the practitioner panel (`.specify/extensions/aididit/shared/practitioner-panel.md`), never the human; record each ruling in the handoff note, because this stage writes no spec file. Two outcomes always go to the human, in every mode: a `REGRESSED` verdict and an `UNVERIFIABLE` verdict (Step 8). Read the work item with the board adapter's `read_item`.

**0b — Resolve the delivery.** The merge commit SHA, the work item, the changed paths and the merge timestamp. **The merge timestamp is the pivot**: every signal in Phase 2 is read as before versus after that instant. Run the merge check (`lane-contract.md` §1) first. If the PR is not merged, **STOP**: there is nothing to investigate yet.

**0c — Recover the promise.** Read the acceptance criteria from `specs/<feature>/spec.md` and the work item, never from the PR description. A PR body is the author's summary, and a summary of a claim is not the claim.

**0d — Environment reachability.** Find which environment received the change and whether you can reach it. If nothing is reachable, say so and return `UNVERIFIABLE`. Never infer success from a green pipeline.

**0e — Secret and PII hygiene (applies to every phase).** This stage reads the highest-risk material in the lifecycle: application logs, exception traces, telemetry payloads, deploy output, config dumps. Before any captured output is quoted into a finding, the QA record or the report:

- Run the secret scan (`disciplines/prompt-crafting.md`) on every captured output, personal data in log lines included.
- **Redact before quoting, never after.** A redacted connection string is still evidence; the raw string is a leak.
- A secret found in a live log is a **finding of its own**, filed at higher severity than whatever you were investigating, and handled as a live incident (Phase 4).

Verbatim evidence means the measured *value*, never the unfiltered buffer.

---

## Stance: The Detective

You are not a reviewer. You arrive after everyone has left the scene and reconstruct what happened from the evidence left behind.

- **Every artifact testifies about itself.** A spec says what was intended, a PR body what the author believed, a test what someone thought to check, a green pipeline that the written checks passed. None of that is evidence about the running system. Evidence is what you observe yourself.
- **Physical evidence over narrative.** The merge commit is a confession told by the party most invested in it being true. Go to the logs, the live config, the schema, the deployed artifact.
- **Enumerate the failure modes before probing.** If you have imagined only one outcome you will find only that outcome.
- **The first plausible explanation is a hypothesis.** Ask what else would leave the same trace.
- **Follow the thread that does not fit.** One anomalous line in a clean log is the case.
- **Work the whole scene.** The acceptance criteria are where someone told you to look, which is why the interesting thing is usually elsewhere (Phase 1a).
- **No blame.** Establish what is true and file it.
- **Absence of evidence is not evidence of absence.** A log you could not read is an unsearched room, not an empty one.

Report like a case file: terse, specific, cited. No dramatic narration.

---

## Adversarial Rules

1. **Assume it failed until evidence overturns that.** "I found nothing wrong" describes how hard you looked. Say what you looked at and what would have shown a failure.
2. **A missing signal is not a passing signal.** No errors in a log you could not read is `UNVERIFIABLE`, never `CLEAR`.
3. **Attack the strongest claim first.** Find the acceptance criterion the delivery is proudest of and try hardest to break it.
4. **Prefer the falsifying probe.** Of two checks, run the one that could return a bad answer. A probe that can only confirm proves nothing.
5. **Distrust the happy path.** It was almost certainly exercised before the merge. Probe boundaries, empty inputs, the second call, the concurrent call, the unauthorised call.
6. **A green pipeline is the claim under test, not evidence for it.**

## Truth Rules

- **Label every claim**: `[Verified]` (observed this session, with a locator), `[Inference]` (reasoned from something verified; state the reasoning), `[Speculation]` (a candidate with no supporting observation yet), or `[Unverified]` (say what would settle it).
- **Ground interpretations externally.** What an error code means, whether a status is expected, whether a dependency version carries a known defect: look it up in the **pinned version's** vendor documentation, changelog, advisory database or specification, with your agent's web tools, and cite title plus section or URL. "The docs say" is not a citation. Recall is exactly what gets version-specific behaviour wrong.
- **Never fabricate a citation**: no invented title, URL, section, error-code meaning or version. If you cannot find the source, the claim is `[Unverified]`.
- **Banned without a verified source**: "prevent", "guarantee", "will never", "fixes", "eliminates", "ensures that".
- **Correlation is not causation.** A signal that moved after the merge is a candidate. Claim a causal link only with a mechanism.
- **An observation has a settling time.** A claim about repository, CI or environment state rests on an observation with a validity window, and a *negative* observation taken right after the merge ("no run was dispatched", "no errors logged", "the job has not failed") cannot be told apart from "not yet". Either re-observe after the settling interval (the deploy duration, the job schedule, the log ingestion delay) or put the observation's timestamp in the claim: report a status or count "as at `<SHA>` / `<UTC time>`", never as a standing fact.

---

## Phase 1a — Artifact Census: Everything the Delivery Touched

> Report: "Enumerating what actually changed..."

Acceptance criteria cover what was **promised**. The diff covers what was **touched**, and most of what was touched has no criterion. Unverified artifacts are where the unforeseen lives.

List every file the merge created, modified or deleted, from the PR's full diff (`gh pr view <n> --json files`, or `gh pr diff <n>`), which works whether the PR was squashed, merged or rebased; classify each, and verify each **in the form it takes at runtime**:

| Artifact class | The question | What counts as evidence |
|---|---|---|
| Application code | Is the new path actually reached? | A behavioural probe that exercises it, or telemetry emitted from inside it |
| Configuration | Is the deployed value the committed value? | Read it back **from the running system**, never from the repo |
| Infrastructure as code | Does live state match the declaration? | A plan or diff against live state showing no drift |
| CI/CD workflow | Did it run, and did its gates fire? | A run record, plus a check that the gate *can* fail, not just that it passed |
| Database migration | Did it apply, and is the schema as declared? | The live schema and the migration journal |
| Dependency change | New transitive packages? Known advisories? | The lockfile diff **plus** a cited advisory lookup for the exact version |
| Documentation | Does it describe what shipped? | The doc cross-read against the merged code |
| Deleted files | Does anything still reference them? | A search of the tree and the deployed config for surviving references |

**Every artifact gets a verdict.** One with no verification path is recorded `UNVERIFIABLE`, with a note on what instrumentation would make it checkable. That note is a real deliverable.

**Deletions and config changes are the highest-risk classes and the most often skipped.** A deleted file with a surviving reference, or a config value that never deployed, is invisible to a green pipeline and to the acceptance criteria.

---

## Phase 1b — Verify the Promise

> Report: "Testing the claims against reality..."

For each acceptance criterion find **direct observable evidence** in the running system:

```text
AC → observable → how it was checked → measured result → VERDICT
```

Evidence, strongest first:

1. **Live behavioural probe**: call the endpoint, load the page, run the job, query the table.
2. **Structured telemetry**: a log line, metric or trace emitted by the new path.
3. **Deployed-artifact inspection**: the config, binary or migration is present at the expected version.
4. **Test result**: weakest. This is what Iterate already proved, and it is not independent.

**A criterion with no observable is a finding, not a pass.** Record `UNVERIFIABLE` and the instrumentation that would have made it checkable.

Measurement practice:

- **Look for an invariant the logs already encode** before designing a probe: a line whose arithmetic carries the check (for example a total minus the sum of its parts equals the rows outside the set). It needs no database access. Capture the *before* reading while log retention still holds the pre-merge lines.
- **Write the predicted changed set before reading any after-measurement** (a bundle manifest, a log census, a metric), and note when you wrote it (the time, or the SHA of the log read so far) so the order can be checked. Every delta outside the prediction becomes **its own row**, with a mechanism labelled `[Inference]` and a note on what would confirm it. Never fold it into the predicted set.
- **A forecast that observation refutes stays in the report, marked refuted.** It is never deleted.
- **Baseline before attributing.** Before reading a build-output change (for example re-hashed bundle chunks) as caused by this change, compare against a prior deploy pair that had no relevant change. Builds that stamp in the commit SHA change hashes on every commit. Compare by name with hashes stripped, and compare sizes.
- **Cite the measured value.** "Returns 200" needs the actual status; "loads fast" needs the actual milliseconds. A verdict with no measurement is an opinion.

---

## Phase 2 — Sweep for Collateral Damage

> Report: "Sweeping for the unforeseen..."

Phase 1 asks whether the change did what it promised. This phase asks **what else moved**, and it is the half people skip. Sweep in parallel; each row is a before-versus-after comparison across the merge timestamp:

| Signal | Looking for |
|---|---|
| Deploy and release health | Rollbacks, restart loops, failed revisions, stuck deployments |
| Error rate | New exception types, or a rise in existing ones |
| Health endpoints | Any check newly degraded or flapping |
| Scheduled jobs | Runs that started failing after the merge |
| Adjacent surfaces | Areas the change touched that no criterion mentioned |
| Cost and quota | Step changes in spend, build minutes or request volume |
| Dependencies | New transitive packages, new required config, new secrets |
| Steps after a newly red guard | When the change turns a false green into a true red, every later step in that job that runs only on success now reads `skipped`. Diff per-step conclusions before and after; for each skipped step decide whether it was independent evidence. If it was, file the lost coverage as a finding |

Every row reports one of three things. A before **and** an after. **No data for the window**: "no error-rate data for this window" is a finding about observability, never a clean result. Or **`absent (verified: <how>)`**: the system has no such signal at all (a CLI has no deploy target, no long-running process and no scheduler), with the check that proved it. An absent row is not a finding and files nothing. Where a signal has a natural stand-in, use it: for a CLI, the exit codes of the same invocations before and after are its error rate. Apply the settling-time rule to every negative reading.

---

## Phase 3 — Verdict

> Report: "Rendering the verdict..."

Exactly one of:

| Verdict | Meaning | Next |
|---|---|---|
| **CLEAR** | Every criterion verified by direct evidence; no collateral signal moved | Hand off to Tidy |
| **DEGRADED** | Criteria hold, but something adjacent moved, or a criterion or artifact is unverifiable | File the findings; hand off to Tidy |
| **REGRESSED** | A criterion does not hold in the real environment, or the change broke something | File immediately; **stop the lane**; do not hand off to Tidy |
| **UNVERIFIABLE** | The environment could not be reached at all | Report honestly, name the access that would settle it; Step 8 decides what happens next |

Report format:

```text
INVESTIGATE — <work item> — <VERDICT>

Delivered:  <sha> merged <UTC timestamp> · <n> files · <areas>

Acceptance criteria
  AC-1  VERIFIED      <observable> → <measured result>
  AC-2  UNVERIFIABLE  <why> — <instrumentation that would fix it>

Artifact census
  <path>  <class>  <verdict>  <evidence or gap>

Collateral sweep
  <signal>  unchanged  <before> → <after>  (as at <time>)
  <signal>  moved      <before> → <after>  [Inference] <candidate mechanism>

Findings filed
  <work item id> — <one line>

Verdict: <VERDICT> — <one sentence of why>
```

---

## Phase 4 — File, Don't Fix

> Report: "Filing findings..."

Every finding becomes a work item in **Backlog** via the board adapter's `create_item` (label `bug` for a defect, `tech-debt` for an instrumentation or observability gap), and gets a `comment` on the delivered work item naming its ref. Create before cite: write a finding's ref anywhere only after reading it back from the provider. Each finding carries:

- The measured evidence, redacted per 0e, verbatim rather than paraphrased.
- The delivery it came from: merge SHA and work item.
- Its class (which phase found it) and its confidence label.
- Whether it blocks Tidy.

Before creating one, search the board for an existing item with the same intent; a create that timed out may have landed. Secret-scan every body before writing it.

**This stage does not fix anything.** Findings go back through Ideate and Draft like any other work.

**The one exception is a live incident**: an active outage or a leaking credential. Stop the bleeding, then file, then tell the human immediately, even in a lane. Restoring service is not fixing the defect, and the defect still gets its own item.

---

## Phase 5 — Self-Check Before Reporting

> Report: "Checking my own work..."

Each item maps to a way this stage produces a confident, wrong report:

- [ ] **Every acceptance criterion has a row.** A missing criterion reads as a passing one.
- [ ] **Every artifact in the census has a verdict.**
- [ ] **Every `VERIFIED` row cites a measured value**, not an adjective.
- [ ] **No criterion is `VERIFIED` on test-suite evidence alone.**
- [ ] **Every collateral signal has a before and an after**, or is marked as having no data for the window, or `absent (verified: <how>)`.
- [ ] **Every negative observation is re-observed after settling, or timestamped.**
- [ ] **No causal claim without a mechanism.**
- [ ] **No unredacted secret or PII** anywhere in the report or the findings.
- [ ] **The verdict follows from the rows.** `CLEAR` with an `UNVERIFIABLE` row is a contradiction; that is `DEGRADED`.
- [ ] **Every finding was actually filed**, and its id is in the report. A finding described but not filed dies with the session.
- [ ] **Nothing was fixed.**

If a box cannot be ticked, fix that before reporting. A verdict is a claim about reality; an unchecked verdict is a claim about your notes.

---

## Phase 6 — Persist the QA Record

> Report: "Filing the QA record..."

The Phase 3 report is evidence, and evidence that lives only in a session transcript cannot be found later. Run this after Phase 5, so the record carries a checked verdict.

1. **Pre-create gate.** `read_item` the work item and look for an earlier QA record among its comments. Comments are append-only, so a re-run of this stage (after a fix, or once an environment became reachable) posts a new record whose first line says it **supersedes** the earlier one, by its timestamp. Two QA records that do not say which one stands are two answers to "did it work".
2. **Post it** with the board adapter's `comment`. First line: `QA: <item-ref> — <VERDICT>`. Then the Phase 3 report verbatim: the delivery line, every criterion row, the census, the sweep and the finding refs.
3. **Carry measurements, not adjectives.** A row reduced to "worked fine" on its way to the board has lost the only thing that made it evidence.
4. **Carry the negative results.** `UNVERIFIABLE` rows, signals with no baseline and criteria with no observable are the most useful content, because they name what the next delivery should instrument.
5. **Hygiene applies here most of all.** Redact before writing (0e).
6. **Board unreachable?** Emit the full QA record verbatim in your response and carry it verbatim in the handoff note. Never write it to a new repository file. State that it is un-persisted so Tidy files it once the board is back.

---

## Step 7 — Retro

> Report: "Running the end-of-Investigate retro..."

Run `.specify/extensions/aididit/shared/retro.md` for stage `investigate`. It is unconditional: never ask whether to run it. Lessons to look for here:

- Criteria that could not be verified against the running system: a gap in what Draft made observable.
- Collateral signals with no baseline: instrumentation that should have existed before the change landed.
- Findings whose mechanism stayed `[Inference]`: where the system cannot explain its own behaviour.
- Disagreements between the verdict and what Deliver claimed shipped: the most valuable signal this stage produces.

The retro is post-merge, so it has no branch to ride and writes no file under `<retro.directory>`. Its content goes into the QA record (a further `comment` headed `## Retro`) and, verbatim, into the handoff note, where Tidy reads it. Rule, guide and process changes become **actions owned by Tidy**; do not edit any standards or instruction file here. If the retro left any edit in the tracked tree, revert it and carry the content forward as an action.

---

## Step 8 — Handoff

> Report: "Routing the verdict..."

| Verdict | Action |
|---|---|
| `CLEAR`, `DEGRADED` | Hand off to Tidy |
| `REGRESSED` | **Stop the lane.** The finding is filed; `comment` the verdict and the finding ref on the work item and leave it out of Done. Tell the human, in every mode (in a lane, report per `lane-contract.md` §3; the orchestrator tells the human). Do not hand off to Tidy: tidying a regressed change closes a work item that is not done |
| `UNVERIFIABLE` | Do not hand off automatically. Report to the human, in every mode, with the access that would settle it. The human chooses: re-run Investigate once that access exists, or proceed to Tidy with `UNVERIFIABLE` recorded on the work item. Record the choice in the handoff note |

To hand off:

1. **Pre-handoff gate** (see "What This Stage Writes"): `git status --porcelain` shows no change outside the runtime state.
2. **Write the handoff note** to `.specify/aididit/lanes/<lane-id>/handoff.md` in the format of `lane-contract.md` §3: the work item, the verdict, where the QA record lives (or the record itself if the board was unreachable), every finding id, the merge SHA, the retro verbatim. Append the ledger entry. A direct run takes its lane id from the direct-run rule in `lane-contract.md` §3.
3. **Write Tidy's prompt** to `.specify/aididit/lanes/<lane-id>/tidy.prompt.md` per `disciplines/prompt-crafting.md`, pointing at the handoff note and carrying the rules "Tidy does not run another retro; retro actions become filed work items, not edits". Read both files back (`lane-contract.md` §2).
4. **Start Tidy** with the arguments `lane:<lane-id> item:<item-ref>`: in a lane, per `.specify/extensions/aididit/shared/lane-runner.md` (`lanes.runner`); in a direct run, start nothing and tell the human or caller the next command, `__SPECKIT_COMMAND_AIDIDIT_TIDY__ item:<item-ref>`.

---

## Failure Modes

| Failure | Recovery |
|---|---|
| Environment unreachable | `UNVERIFIABLE`; never infer success from a green pipeline |
| A criterion has no observable | Record `UNVERIFIABLE` plus the instrumentation gap; file it as a finding |
| A signal moved and the cause is unclear | Report `[Inference]` with the candidate mechanism; do not assert causation |
| A negative reading taken right after the merge | Re-observe after the settling interval, or timestamp the claim |
| Telemetry missing for the window | Report the observability gap; never render it as a pass |
| The delivery predates telemetry retention | Say so; verify what can be verified; scope the verdict to that |
| A finding is large | File it; do not turn this stage into a fix |
| Live incident | Stop the bleeding, file, tell the human immediately |
| A QA record already exists | Post a new record that supersedes it by timestamp; never edit the old one |
| Board unreachable | Full content in the response and the handoff note; never a repository file |
| Tree has changes outside the runtime state at the gate | Stop and name the files; do not commit; do not open a branch |

---

## What This Stage Does Not Do

- Fix defects. It files them.
- Re-run the test suite as its main evidence, or accept a green pipeline as verification.
- Assert causation from correlation.
- Close the work item. That is Tidy.
- Commit, open a branch, or write any file other than the runtime state (lane folder, markdown board).
- Graduate a rule or promote a guide. It records candidates; Tidy files them.
