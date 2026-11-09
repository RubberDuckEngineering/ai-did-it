# Clean Code: The Refactor Step's Rulebook

Code is read far more often than it is written, usually by someone without the context that made it obvious. Clean code pays the reading cost once, at authoring time. This file governs writing and changing code. Grading someone else's code belongs to `/speckit.aididit.pr-review`.

Used by: Iterate (the refactor step of every TDD cycle), Deliver (every review-fix commit), Draft (naming in the spec and plan).

## Principles

- **Names are the primary interface.** Most readers meet the name and never read further. A lying name corrupts everything downstream.
- **A function does one thing.** Describe it aloud; if the description needs "and", it is two functions.
- **Reveal intent, hide mechanism.** Every mechanism leaked into a signature is a change you have pre-committed to.
- **Duplication is a symptom.** Two copies of the same *decision* must converge. Two pieces of text that merely look alike must not be merged; that couples things that were only accidentally similar.
- **Leave it cleaner than you found it** (the Boy Scout Rule), inside the scope you were asked to touch.
- **Refactor only on green** (`.specify/extensions/aididit/shared/disciplines/tdd.md`).

## Naming

- Difficulty naming something means you do not yet know what it is. Reconsider the boundary, not the thesaurus.
- Searchable beats short: `elapsedDays`, not `d`.
- Use the domain's exact word. If the business says "policy", the type is `Policy`, not `PolicyRecord` or `PolicyInfo`. This is the same ubiquitous language as in `bdd.md`.
- One concept, one word, in every file.
- Encode the unit or constraint where ambiguity is possible: `timeoutMilliseconds`, not `timeout`.

## Smell to move

| Smell | Move |
|---|---|
| Long function | Extract Method until each level of abstraction is uniform |
| Deep nesting | Guard clauses and early return; invert the condition |
| Long parameter list | Introduce Parameter Object or Preserve Whole Object |
| Boolean parameter | Split into two intention-revealing functions |
| Magic number or string | Named constant stating the reason, not the value |
| Primitive obsession | A value type that makes invalid states unrepresentable |
| Feature envy | Move Method to the type whose data it keeps reaching for |
| Large class | Extract Class along the axis where fields cluster |
| Repeated conditional on type | Replace Conditional with Polymorphism |
| Temporal coupling (call A before B) | Fold the sequence into one operation that cannot be misordered |
| Comment explaining *what* | Extract a function named after the comment; delete the comment |

`MaxRetries = 3` restates the value. `RetriesBeforeEscalation = 3` tells the reader when to change it.

## DRY, YAGNI and being early

- The most expensive code is the wrong abstraction: duplication is cheap to find and fix, a wrong abstraction is defended by every caller.
- Wait for the third occurrence before abstracting.
- Abstract along the axis of change, not the axis of similarity (Single Responsibility as a refactoring rule).
- YAGNI applies to flexibility: a configuration point, a one-implementation interface or a hook for an imagined requirement costs today for a benefit that may never come.
- When an abstraction fights you, inline it while that is still cheap.

## Dead code

**The test is deletion, not coverage.** Coverage proves code ran; it never proves code is needed. Delete the suspect code and run the suite. If it stays green, the code was dead, or the tests do not cover a behaviour that matters. Decide which, then either remove the code or add the missing test. Commented-out code is dead code.

## Comments

Keep: why a non-obvious decision was made, warnings about consequences, legal headers, public API documentation.

Delete: restatements of the code, change history and authorship that version control already holds, commented-out code, apologies for hacks. An apologetic comment is an unfiled work item: file it or fix it.

## Before you start

- **Suite not green?** Stop; get to green first.
- **No coverage over the region?** A refactor there is an unverified rewrite. Pin current behaviour with characterization tests first.
- **Renaming across the codebase?** Search every reference first, including strings, serialized names, configuration, reflection and documentation. A rename that compiles is not necessarily complete.
- **Change alters documented behaviour?** Update the spec artifacts (`spec.md`, `data-model.md`, `contracts/`) in the same commit. Code and documentation are one change.
- **Tempted to clean code you were not asked to touch?** Note it, finish the task, offer it separately.

## Anti-patterns

- Refactoring and behaviour change in one commit. Nobody can review it and bisect cannot isolate it.
- Renaming by blind find-and-replace.
- Extracting for line count, which creates two names for one idea.
- `Utility` and `Helper` types: the methods belong on the type that owns the data.
- A comment instead of a rename.
- Deleting a test to make a refactor pass. The test was the only evidence behaviour was preserved.

## Definition of done

- [ ] Every name states intent in the domain's vocabulary, consistently across files
- [ ] Each function does one thing, describable without "and"
- [ ] No magic numbers or strings; constants are named for their reason
- [ ] Shallow nesting; no boolean parameters selecting behaviour
- [ ] Duplication removed only where the decision is shared; no abstraction before its third case
- [ ] No dead or commented-out code (checked by deletion, not by coverage)
- [ ] Comments explain why; every what-comment became a name
- [ ] Refactoring commits contain no behaviour change, and the suite stayed green
- [ ] Documented behaviour updated in the same commit as the code
