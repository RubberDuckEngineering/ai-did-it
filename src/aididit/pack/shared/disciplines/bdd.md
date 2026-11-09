# Behaviour-Driven Development and ATDD: The Outer Loop

BDD is the shared language: concrete examples written in the words the business uses, so the specification, the conversation and the executable check are one artifact instead of three drifting copies. Acceptance Test-Driven Development (ATDD) is the loop that makes those examples executable: the acceptance test is the user's intent, run against a production-like system, and it defines when the work is done. TDD (`.specify/extensions/aididit/shared/disciplines/tdd.md`) is the inner loop that the red acceptance test pulls you into.

Used by: Ideate (B4, falsifiable ACs), Draft (acceptance criteria in `spec.md`), Iterate (acceptance tests first), Investigate (each AC verified against the running system).

## Principles

- **Examples beat abstractions.** "Handles invalid input gracefully" cannot be falsified. "Given a balance of 40, when 100 is withdrawn, then it is refused with Insufficient Funds" can be argued with, agreed and executed.
- **One vocabulary.** The business word appears in the scenario, the test name and the code. Every translation layer leaks meaning.
- **Outside-in.** Start from the behaviour someone wants; the data model follows from it.
- **What, not how.** A scenario that mentions a button, an endpoint or a table is already coupled to a design that will change.
- **The conversation is the point.** A scenario written alone is a guess with formatting.

## Given-When-Then

| Clause | Means | Rule |
|---|---|---|
| **Given** | The world before | State only. No action hides in the setup |
| **When** | The behaviour under test | Exactly one. Two `When`s is two scenarios |
| **Then** | The observable outcome | What an outsider could see; never internal state or storage |

`And` / `But` extend a clause; they never introduce a second `When`.

Imperative, bound to the interface:

```gherkin
Given I open the login page
And I type "jo@example.com" into the email field
And I click the button with id "submit"
Then I see a div with class "error"
```

Declarative, bound to the behaviour:

```gherkin
Given a registered account for "jo@example.com"
When she signs in with the wrong password
Then she is refused
And she is told her credentials were not recognised
```

The second one survives a redesign, and a product owner can read and correct it.

## Scenario craft

- Name for the behaviour: `WithdrawalIsRefusedWhenBalanceIsInsufficient`.
- One scenario, one rule.
- Concrete, meaningful data that makes the rule visible. Cover the boundary, not the space: for a limit of 100, test 99, 100, 101.
- Scenario outlines vary values for one rule; they never bundle different rules.
- Keep `Background` to a few lines.
- Third person, present tense. State behaviour as fact, not "should".
- Synthetic data only. Scenarios are committed and read aloud; never paste real customer records, credentials or personal details.

## The outer loop: Discuss, Distill, Develop, Demo

1. **Discuss.** Business, development and testing (the Three Amigos) work the item with concrete examples. Each asks what the others miss: what outcome is worth paying for; what it costs and where it breaks; what happens when it is empty, huge, wrong or arrives twice. Example mapping is the cheap form: story, rules, an example under each rule, and open questions. Red question cards mean the item is not ready. In a lane, the practitioner panel plays these roles and records answers in the spec's Clarifications.
2. **Distill.** Turn each acceptance criterion into at least one executable specification in domain language. Watch it fail.
3. **Develop.** Work outside-in: the red acceptance test pulls you into many red-green-refactor cycles until it goes green. No production code without a failing test demanding it.
4. **Demo.** Show the behaviour against the green specifications. A demo without a green spec is a performance, not evidence.

Shape: one red acceptance test, many unit cycles, one green acceptance test, next criterion.

## The four-layer model

Dave Farley's structure for acceptance tests that survive change:

```text
Layer 1  Test cases         executable specifications in pure domain language
Layer 2  DSL                the vocabulary the test cases speak
Layer 3  Protocol drivers   translate DSL calls into UI, REST or messages; the only layer that knows HOW
Layer 4  System under test  deployed and configured like production
```

- Each layer talks only to the one below. Test cases never touch drivers.
- Stability lives in the language, volatility in the driver. A UI change means one driver change, not a thousand test edits.
- Swap drivers to run one specification against several channels.

## Isolation

- **Temporal:** every run generates unique accounts, IDs and names, so a test can repeat forever without cleanup collisions.
- **From other tests:** no shared mutable state; parallel-safe and order-independent.
- **From external systems:** stub at the boundary, then verify each stub with a contract test against the real system. An unverified stub is a fiction everyone trusts.

## Before you start

- **No agreed acceptance criteria?** There is nothing to distill. Send the item back through Ideate.
- **Cannot name the actor or outcome in domain words?** The domain is not understood yet; run example mapping rather than inventing vocabulary.
- **Existing scenarios use another word for this concept?** Adopt it, or rename across the whole suite deliberately.

## Anti-patterns

- UI mechanics, selectors, URLs, payloads or SQL in scenarios.
- Multiple `When`s; asserting internal state.
- Feature files written only for automation and never read by the business.
- Scenarios or acceptance tests written after the code.
- Tolerated flakiness. Re-running until green is risk acceptance in disguise: quarantine, diagnose, fix or delete.
- A specification per implementation path. Branch coverage is the unit suite's job.

## Definition of done

- [ ] Every acceptance criterion has at least one executable specification
- [ ] Specifications were written, and observed failing, before production code
- [ ] Each scenario has exactly one `When`; `Given` is state only; `Then` is observable
- [ ] Layer 1 is domain language only; drivers are the only layer that knows how
- [ ] Vocabulary matches the business and the code; boundaries are covered
- [ ] Specifications run against a production-like environment in the pipeline
- [ ] Suite is temporally isolated, parallel-safe and order-independent
- [ ] Every stub of an external system has a contract test
- [ ] Zero red, flaky or skipped acceptance tests
- [ ] No real customer data, credentials or personal details in any example
