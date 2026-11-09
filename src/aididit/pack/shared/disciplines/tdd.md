# Test-Driven Development: The Inner Design Loop

TDD is a design technique that leaves tests behind. The test comes first because that is the only way it can push back on the design; a test written afterwards can only describe what was already built. The acceptance-test loop in `.specify/extensions/aididit/shared/disciplines/bdd.md` asks whether the system does what the user needs. This loop asks whether the code does what the developer intends, and it turns many times inside one turn of the outer loop.

Used by: Iterate (every task), Deliver (every fix commit), Investigate (never: it files, it does not fix).

## Principles

- **The failing test comes first, always.** A test that has never been red has never been shown to test anything.
- **Red for the right reason.** Read the failure message. A test failing on a missing import is a compile error, not the test you meant.
- **Simplest thing that could work.** Green is a checkpoint. Cleverness written during green is untested cleverness.
- **Hard to test means badly designed.** Six mocks is a design signal; the answer is fewer collaborators, not a seventh mock.
- **Never refactor on red.** You cannot show behaviour was preserved against a suite that is already failing.

## The cycle

1. **Red.** Write one small failing test for the next increment. Run it and watch it fail. For numeric behaviour, cover the boundaries now: zero, one, negative, the limit, limit plus one, rounding.
2. **Green.** Write the least production code that passes. Duplication is allowed here.
3. **Refactor.** With the suite green, remove duplication and improve names (`.specify/extensions/aididit/shared/disciplines/clean-code.md`). Change structure, never behaviour. Re-run after every step.

Cycles take minutes. If one runs past about ten minutes, the step was too big: revert, split, take a smaller bite.

### Getting to green

| Strategy | What you do | When it fits |
|---|---|---|
| Obvious implementation | Type the real answer | You know it and it is small |
| Fake it | Return the literal, then generalize | You are unsure of the shape |
| Triangulate | Add a second example a constant cannot satisfy | The fake felt too comfortable |

## What makes a test worth keeping

- One behaviour per test, named for the behaviour (`WithdrawalExceedingBalanceIsRejected`, not `TestWithdraw2`).
- Arrange, Act, Assert, visibly separated.
- Assert specific values. "Does not throw" as the only assertion proves the code ran, not that it was right.
- Every branch predicate has a test on each side.
- No logic in tests. Use parameterized cases instead of `if` or loops.
- Test through the public surface. Tests bound to private methods break on every refactor.
- Deterministic and independent: clock, randomness and I/O are injected; any order, every run.

## Every guard must be able to fail, and to pass

A test, assertion, CI check or lint rule is a guard. A guard that cannot fail reads as rigour and survives review while guarding nothing. For every guard you add:

1. **Observe it green** on the unmutated tree.
2. **Name the concrete mutation that turns it red** and observe that red. Mutate from outside the guard's own blast radius: a mutation that disables, skips or de-collects the test produces "did not run", which is not red.
3. **Record both observations** in a kill-test table that ships in the same commit as the code:

```markdown
| Guard | Mutation applied | Control (unmutated) | Under mutation |
|---|---|---|---|
| RejectsOverdraft | change `>` to `>=` in Withdraw | green | red: expected Rejected, got Accepted |
```

A claimed red with no recorded mutation does not count. A guard that cannot pass on a clean tree is as useless as one that cannot fail.

## Test doubles: weakest that works

Reach down this list, not up:

1. **Real object**, when it is fast.
2. **Stub**: canned answers, no interaction assertions.
3. **Fake**: a working lightweight implementation (in-memory repository).
4. **Mock**: asserts the interaction, only when the interaction is the behaviour (a message must be published).

### Contract fidelity

A double states a contract about a real dependency, and an unverified contract is fiction.

- Before faking a dependency, read its **installed** source for the path you fake and note the version in the test or the plan.
- A double must not **produce** anything the real one cannot (values, errors, timings).
- A double must not **omit an ordering** the real one can produce. This half is the dangerous one, because it leaves the whole suite green.
- Re-verify on every dependency upgrade.
- Where a stub replaces an external system, verify it with a contract test against the real thing.

**Why:** fakes that invoke a callback earlier than the real dependency does can leave an entire suite green while production hangs, because the tests encode the same wrong belief as the code.

## Bug-fix protocol

1. Write a failing test that reproduces the defect. If it will not fail, you have not reproduced it; do not proceed on belief.
2. Confirm the failure matches the reported symptom.
3. Fix the code; the test goes green.
4. Keep the test permanently. It is the regression guard and the only proof the bug was real.

Never fix first and test after: that proves the fix does something, not that it fixed this.

## Before the first red

- **No runner?** Scaffold it first. A red you cannot execute is a guess.
- **Suite not green on the default branch?** Establish a clean baseline; new red on old red is unattributable.
- **Legacy code with no seam?** Write characterization tests pinning current behaviour, including behaviour you think is wrong, then refactor toward a seam.
- **Behaviour crosses the system boundary?** Start in the outer loop (`bdd.md`) and come back for the units it pulls in.

## Anti-patterns

- Test-after backfill: coverage without design pressure.
- Never watching it fail: an assertion typo guards nothing, forever.
- Refactoring on red.
- Skipping, ignoring or suppressing tests, including mutation-disable comments. If it cannot be tested, change the design until it can.
- Asserting call orders nobody depends on.
- One giant test per class; shared mutable fixtures.
- Coverage as proof of need. Coverage proves execution only; dead code is found by deleting it and seeing the suite stay green.

## Definition of done

- [ ] Every behaviour change was driven by a test observed failing first, for the expected reason
- [ ] Each test asserts one behaviour with specific values
- [ ] Every branch predicate has a test on both sides
- [ ] New production code is at 100% coverage, measured, with the figure cited "as at `<SHA>`"
- [ ] Every new guard has a kill-test row with both a green control and a red mutation
- [ ] Doubles are the weakest that work, and each was checked against the installed dependency
- [ ] Every fixed bug has a regression test that failed before the fix
- [ ] Zero skipped, ignored or suppressed tests
- [ ] Refactoring happened only on green; the suite is deterministic and fast
