# Practitioner Panel

> The panel decides, not the human. Each position is grounded in something the practitioner actually published, cited and checked, not paraphrased from memory.

This is the decision contract every A·I·DID·IT stage uses wherever a workflow would otherwise stop and wait for a person: clarify answers, plan trade-offs, scope calls, analyze-loop leftovers, review disagreements, retro ratification, and go/no-go between lane links. It is what lets a lane run end to end without a human, while keeping every decision defensible and auditable.

How to run a round in practice (prompt shape, independence, recording) is in `.specify/extensions/aididit/shared/panel-guide.md`. This file is the contract; that file is the procedure.

Configuration, from `.specify/extensions/aididit/aididit-config.yml`:

| Key | Meaning |
|---|---|
| `panel.practitioners` | The members. Default: Kent Beck, Martin Fowler, Dave Farley, Udi Dahan, Robert C. Martin |
| `panel.require_citations` | `true` (default): only cited, verified positions vote. `false`: uncited positions vote but are labelled [Inference] |
| `delivery.merge` | `human` (default): the merge is a human gate. `auto` (Full Auto Mode): it is not |

---

## 1. Members and Seed Sources

The panel is the practitioners listed in `panel.practitioners`. The table below is a **search seed** for the defaults: places to start looking, not citations. Every source must still be found, fetched, and verified in the round that uses it. For a practitioner not listed here, the orchestrator builds the seed list by searching for that person's own published books, essays, and talks.

| Practitioner | Lens | Where to start searching |
|---|---|---|
| Kent Beck | TDD, YAGNI, the simplest thing that could work, test desiderata, tidying | *Test-Driven Development: By Example*; *Extreme Programming Explained* (2nd ed.); *Tidy First?*; *Implementation Patterns*; his "Test Desiderata" essays; his newsletter |
| Martin Fowler | Refactoring, evolutionary design, code smells, enterprise patterns, the economics of quality | *Refactoring* (2nd ed.); *Patterns of Enterprise Application Architecture*; the martinfowler.com bliki |
| Dave Farley | Continuous delivery, testability, deployability, empirical engineering | *Continuous Delivery* (with Jez Humble); *Modern Software Engineering*; his Continuous Delivery channel and essays |
| Udi Dahan | Service boundaries, messaging, consistency, distributed-systems design | His blog at udidahan.com; his talks on service boundaries and reliable messaging |
| Robert C. Martin | Clean code, SOLID, boundaries, Clean Architecture | *Clean Code*; *Clean Architecture*; *Agile Software Development: Principles, Patterns, and Practices*; *The Clean Coder*; his blog |

---

## 2. Summoning Rules

- **Fresh members every summon.** Each decision round gets brand-new member instances: one per practitioner, with no memory of earlier rounds, earlier decisions, or each other. Never reuse a member across rounds and never continue a prior member's conversation. Zero carryover is the defence against drift and against one confident hallucination spreading to the others.
- **Independent within a round.** No member sees another member's position before giving its own. Where the agent can run sub-agents, launch all members in parallel and collect every result before tallying. Where it cannot, follow the isolated sequential procedure in `panel-guide.md`.
- **Web-cited.** Each member gets web search and fetch, and grounds its position in a real, locatable source **that practitioner published**: quote or closely paraphrase the passage and give title plus chapter, section, or URL. The seed table is a starting point, not a ceiling.
- **Citations under `panel.require_citations: true`.** A position with no verified citation is labelled **[Inference]**, recorded, and **does not vote**. It may contribute a condition that a cited position already permits; it never decides, breaks a tie, or forms part of a majority. A member that finds nothing returns `VERDICT: ABSTAIN` with one line saying what it searched for. Abstaining is always correct and always available.
- **Citations under `panel.require_citations: false`.** Uncited positions vote, each labelled [Inference]. If the winning side depends on any uncited vote, the ruling itself is labelled [Inference] in the record, and between options of similar support the more reversible one wins.
- **Never fabricate.** No invented title, chapter, page, quote, or URL under either setting. A fabricated locator is the worst possible output, because it survives review by looking rigorous.
- **Authentic voice.** Each member argues as that practitioner does: their conclusions and their manner (vocabulary, rhythm, formality, characteristic framing). Beck's spare, question-led minimalism does not read like Martin's declarative, principle-named style; Farley's feedback-and-systems framing does not read like Fowler's example-first essays. If the positions could be swapped between names unnoticed, the panel has collapsed into one reviewer wearing several labels.
- **Concise return.** Each member returns only the verdict, three to six sentences of reasoning, and the citation lines (format in section 8). No preamble.

---

## 3. Verifying Citations

The orchestrator verifies every citation before tallying. A citation certifies the source, not the premise it is used to support, so verification covers both.

1. **The locator resolves.** If it does not, treat the citation as fabricated: discard the vote, record the attempt, and re-summon (section 6).
2. **Every quoted string is on the fetched page.** If the locator resolves but a quote has drifted, keep the vote only if the argument stands without the quote, cite only the verified text, and record the correction. A resolving URL is not a verified quote.
3. **The words are the practitioner's own.** Check the byline and whether the passage is itself quoted from someone else (inside quotation marks or a blockquote), or is a guest article on the practitioner's site. Either is an attribution failure: discard the vote.
4. **The source is licensed.** Cite only pages served by the practitioner, their publisher, or a licensed preview. Text reachable only through an unlicensed copy is not counted and is not fetched; re-summon the member.

**Instrument discipline.** Check quotes with the pack's verifier, not an improvised `grep`:

```
python .specify/extensions/aididit/scripts/verify-quote.py --source <url-or-file> --control "<byline phrase>" --quote "<quoted string>" [--quote "<another>"]
```

It uses only Python's standard library, so it runs the same on every OS (use `python3` or `py -3` where that is the interpreter's name). It fetches the URL or reads the file, removes tags, scripts and styles, and folds case, whitespace, curly quotes and dashes before matching. Every run also checks a fresh nonsense phrase as a negative control. Exit `0` is FOUND (every quote is on the page), `3` is MISSING (at least one quote is not, and the controls vouch for the text it was looked for in), and `4` is INSTRUMENT-FAILURE (a control failed, the source could not be read, the verifier crashed, or a quote is missing from text the controls cannot vouch for). **Any exit other than `0` or `3` is an instrument failure**, never a missing quote. **Why:** on Windows Git Bash, grep aborts (exit 134) on minified HTML and even on plain markdown, and a check that reads every non-zero exit as "no match" records each quote as missing.

The positive control (`--control`) is one string known to be present, taken from the page's byline markup (for example a `rel="author"` element, a JSON-LD `"author"` field, or "Posted by" text) or the author's own domain. A name appearing anywhere on the page is not a control. The verifier matches the control against the raw page as well as its text, so a JSON-LD byline counts; quotes are matched against the visible text only. So a missing quote is exit `3` only when the control was found in that visible text and every byte of the page decoded. A control found only in the markup (a page whose text is rendered by script) or bytes the page's charset could not decode make it exit `4`. The verifier reads the charset from the server's header, then from a `<meta>` tag, and decodes the `iso-8859-1` family as windows-1252 the way browsers do.
- A failed control or a verifier crash (exit `4`) is an **instrument failure**, not a verdict. Re-check the source (a saved copy, the text extract) before discarding anything. Never fall back to a shell matcher.
- A missing quote on a page whose controls passed is a finding about the citation, however many of that page's quotes are missing: the controls have shown the verifier can read the text. Find the passage by a distinctive keyword and read it, and check that the locator is the version the member cited (an archived copy if the page has changed), before recording drift or discarding the vote.
- The verifier looks for each quote as one continuous string. Pass each piece of an elided quote (one with `...` or `[...]` in it) as its own `--quote`.
- The verifier refuses a PDF (exit `4`). Extract the text to a file, rejoin words hyphenated across line breaks, and verify that file.

---

## 4. Decision Rule

0. **Only verified, cited positions vote** (under `require_citations: true`). A round is **grounded** when at least two members return a verified citation. Fewer than two: there is no ruling; go to the retry loop (section 6). Never assemble a majority from ungrounded opinion.
1. **Majority wins.** A strict majority of the counted votes takes the option.
2. **Tie.** Rule for the position with the most directly on-point grounding, and record the dissent verbatim.
   - First read each dissenter's own citation for scope. A source that permits the majority's option makes that dissent a **condition** on the option (it argues how, not whether). Fold the condition into the ruling and record it with its citation.
   - When both sides' citations permit "do it as a separate item", rule for the narrower scope. If the losing option still stands on its own after the ruling, file it as its own work item through the board adapter (`.specify/extensions/aididit/shared/board-adapters.md`) in the same session, with each side's conditions. Do not file options the ruling has dissolved.
3. **Plurality without a majority** (for example 2-1-1-1). Group the options by the outcome they share and record the grouping. If one group holds a majority, its outcome is decided; within it, choose the option whose citations support it directly rather than by analogy, and record why each other member of the group lost. If no group holds a majority, apply rule 2. A fragmented vote also says something about how the options were framed; consider re-framing before the next round.
4. **All split with weak grounding.** Choose the option that best preserves reversibility (the cheapest to change later) and record why.
5. **Record the ruling** in the decision log (section 8) and in the artifact it changes.

**Quality gates are not negotiable.** The panel may decide how to make something testable, never whether to test it. A ruling that would skip, suppress, or weaken a quality gate (a test, coverage, mutation score, a security check, a required CI check) is overridden by the gate.

**The panel is terminal for judgement, not for facts.** It rules between options; it cannot audit the premises it was handed. Measured premises, and what to do when a verdict rests on a false one, are covered in `panel-guide.md`.

---

## 5. When the Human Is Still Required

The panel replaces human approval for reversible judgement calls inside the project. It never replaces the human for:

1. **The merge**, when `delivery.merge` is `human`. In `auto` (Full Auto Mode) the merge is not a human gate; the items below still are.
2. **Anything irreversible or outward-facing:**
   - publishing outside the project's own repository and board (package or release publication, public posts, messages or emails to people);
   - deleting data or history (production data, force-pushing over shared branches, deleting branches with unmerged work, purging records);
   - spending money (purchases, paid resources, plan or quota upgrades);
   - changing access, security, or account settings, granting permissions, or accepting terms.
3. **A grounding failure** that survives the retry loop (section 6).
4. **Anything the agent's own safety rules reserve for the user.** The panel never overrides those.

When a lane reaches one of these, record the decision with `Human required: yes` and the reason, write the blocker into the lane's handoff note (`.specify/aididit/lanes/<lane-id>/handoff.md`), and stop that lane per `.specify/extensions/aididit/shared/lane-contract.md`. Other lanes continue.

---

## 6. Grounding Retry Loop

There is no degrade path under `require_citations: true`. An ungrounded verdict, once recorded, carries the same authority downstream as a grounded one: it enters the spec, the ADR, and the code. So the panel stops and tries again, and failing that, asks the human.

```text
attempt := 1
while attempt <= 5:
    summon FRESH members (all, or only those that failed to ground)
    verify every returned citation (section 3)
    if grounded: apply the decision rule (section 4) and proceed
    attempt := attempt + 1
    change the approach before the next attempt
STOP and escalate to the human
```

**Change the approach each attempt.** Repeating a failing query five times is one attempt made five times. Escalate: different phrasing, then a different work in the practitioner's corpus, then a broader concept search, then re-framing the question itself (an unciteable question is often a badly posed one). On a round where no member grounds at all, re-ask once in the practitioners' own published vocabulary rather than the repository's.

**No web access at all.** If the run has no web search or fetch, the panel cannot ground under `require_citations: true`. Do not loop; escalate at once (or the project may choose `require_citations: false`, making every position [Inference]).

**Escalation report.** State the decision and its options; what was searched across all attempts; which members grounded and what each found; and the human's choices: (a) decide it, (b) supply a source the panel missed, (c) re-frame or narrow the question, (d) defer it and proceed with the most reversible option, recorded as an explicit ungrounded choice.

---

## 7. Failure Modes

| Failure | Recovery |
|---|---|
| A member returns no citation | Label the position [Inference]; it does not vote. Re-summon if the round is not grounded |
| Locator does not resolve | Fabrication. Discard the vote, record it, re-summon |
| Locator resolves, quote drifted | Keep the vote if the argument stands; cite only verified text; record the correction |
| Words belong to someone else | Attribution failure. Discard the vote |
| Source only reachable as an unlicensed copy | Do not fetch, do not count; re-summon |
| Verifier exits other than `0` or `3` | Instrument failure. Re-check the source (section 3) before judging any vote |
| All positions read in the same voice | The panel collapsed. Re-summon with the voice requirement made explicit |
| A verdict rests on a false premise | See "False premises" in `panel-guide.md`: discard the round if the brief supplied it; drop only that vote if one member invented it |
| The ruling would skip a quality gate | Overridden. The gate stands; the panel chooses how to satisfy it |

---

## 8. Formats

### Member prompt (one per practitioner, fresh each round)

```text
You are {PRACTITIONER}. Rule on the decision below through your own published methodology,
not as a generic reviewer.

Write as you actually write: your vocabulary, sentence rhythm, formality, and characteristic
framings. Someone who knows your work should recognise the voice without being told.

You have web search and fetch. Ground your position in a real, locatable source that you
published (start from: {SEEDS}, but find the most on-point one). Quote or closely paraphrase
the passage and cite it. Cite only pages served by you, your publisher, or a licensed preview,
and only words under your own byline, not words you were quoting from someone else.

{CITATION_RULE}

Never invent a title, chapter, page, quote, or URL.

DECISION:
{DECISION: the question, the options with the same fields for each (cost, benefit,
reversibility), and every premise with its measurement or marked "unverified"}

Return ONLY:
VERDICT: <option letter | ABSTAIN>
<3-6 sentences in your own voice>
CITATION: <source> | <chapter, section, or URL> | <one-line relevance>
QUOTE: "<the exact words you rely on, as they appear in the source>"
```

`{CITATION_RULE}` under `require_citations: true`:
"No citation means no decision. If you cannot find a source of yours supporting a position, return `VERDICT: ABSTAIN` and one line naming what you searched for. Abstaining is always correct; fabricating is never acceptable."

Under `require_citations: false`:
"If you cannot find a source, you may still give a position, but begin your reasoning with `[Inference]` and omit the CITATION and QUOTE lines."

### Decision record (appended to `specs/<feature>/decisions.md`)

```markdown
## D-NNN: <the question, one line>

- **Stage:** <stage and step, e.g. Draft / clarify round 2>
- **Recorded:** <UTC timestamp from `date -u`, never estimated>
- **Decided by:** panel | human (a direct run; the panel table then holds the pros and cons it gathered, or `none`)
- **Options:** A: <option>; B: <option>; ...
- **Premises:** <each fact with its measurement and the command that produced it, or "unverified: ...">
- **Panel:** <members summoned>; require_citations: <true|false>; attempt <n> of 5

| Member | Verdict | Citation (source, locator) | Verified | Notes |
|---|---|---|---|---|
| <name> | B | <source>, <locator> | yes | |
| <name> | A | <source>, <locator> | quote drifted, corrected | |
| <name> | ABSTAIN | searched: <what> | n/a | |
| <name> | B [Inference] | none | n/a | does not vote |

- **Tally:** <e.g. 3-1, 1 abstain, 1 [Inference] not counted>
- **Ruling:** <option>, <one sentence why>
- **Conditions folded in:** <condition, with its citation> or none
- **Dissent (verbatim):** "<quote>" (<member>)
- **Discarded rounds or votes:** <what and why> or none
- **Follow-up items filed:** <work item references> or none
- **Reversibility:** <how to undo this later, and at what cost>
- **Human required:** no | yes: <reason from section 5>
- **Applied to:** <artifact(s) changed, e.g. spec.md Clarifications, an ADR>
```
