# Conventional Commits and Conventional Comments

Every commit message follows Conventional Commits. Every review comment follows Conventional Comments. Both make history and review machine-readable and quick to scan, and neither has an exception for "quick fixes".

Used by: Iterate (one commit per task), Deliver (one commit per finding family, review comments from the panel), and every stage's pre-handoff commit.

---

## Conventional Commits

### Format

```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Use for | SemVer impact |
|---|---|---|
| `feat` | New capability | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | none |
| `style` | Formatting, whitespace; no logic change | none |
| `refactor` | Restructuring with no feature or fix | none |
| `perf` | Performance improvement | none |
| `test` | Adding or correcting tests | none |
| `build` | Build system or dependencies | none |
| `ci` | CI configuration and scripts | none |
| `chore` | Maintenance; no production code change | none |
| `revert` | Reverting an earlier commit | depends |

### Rules

- **Scope** names the area affected: `feat(auth): add PKCE flow`.
- **Description** is imperative, lowercase, no trailing period, under 72 characters.
- **Body** explains why, not what, after a blank line.
- **Breaking change:** `!` after the type or scope, or a `BREAKING CHANGE:` footer. Either means a MAJOR bump.
- **Footers** use `token: value`, for example `Refs: PROJ-123` or `Closes #42`.
- **One concern per commit.** Refactoring and behaviour change go in separate commits.
- **Stage by explicit path.** Never `git add -A` or `git add .` in a lane; sibling lanes share the object store.

### Lifecycle conventions

| Moment | Commit |
|---|---|
| A TDD task completes in Iterate | `feat(...)`, `fix(...)` or `test(...)` for that task, with the kill-test rows it produced |
| Retro output before a handoff | `chore(retro): <stage>-stage retro for <item-ref>` (`retro.md`); Deliver checks these exist before it stops |
| A review finding family in Deliver | One commit per family, typed by what the fix is, not `fix: address review comments` |
| CI needs to attach to the PR head after a merge commit | A small non-merge commit, for example `chore(ci): trigger required checks` |
| A spike | Say `spike` in the description; spikes are not delivered work |

A commit that reports measured results ("all mutations killed", "coverage 100%") carries the evidence record in its own diff. Otherwise the claim lives only in prose nobody can re-run.

### Commit anti-patterns

- `fix stuff`, `update`, `WIP`: no type, no information. Squash WIP before merge.
- `address review comments`: use the type of the actual change.
- Mega-commits touching many files across several concerns.

---

## Conventional Comments

### Format

```text
<label> [decorations]: <subject>

[discussion]
```

### Labels

| Label | Meaning | Blocking by default? |
|---|---|---|
| `praise:` | Something done well; say what and why | No |
| `nitpick:` | Trivial preference | No |
| `suggestion:` | A proposed improvement; say what and why | No |
| `issue:` | A problem that needs addressing; pair with a suggestion where you can | Yes |
| `question:` | Seeking understanding; may turn into an issue | No |
| `thought:` | An idea worth considering; no action required | No |
| `note:` | Information the reader should have | No |
| `chore:` | Maintenance triggered by this change | No |
| `todo:` | Small, necessary follow-up | No |

### Decorations

| Decoration | Meaning |
|---|---|
| `(blocking)` | Must be resolved before merge |
| `(non-blocking)` | Author decides |
| `(if-minor)` | Fix only if trivial |

Example:

```text
issue (blocking): withdrawal accepts an amount equal to balance plus one

The guard uses `>=` where the rule says strictly greater. Add a test at the
boundary (balance, balance + 1) and flip the comparison.
```

### In the panel

Every panel and bot finding the Deliver stage records is phrased as a Conventional Comment, so its blocking status is never in doubt. Blocking findings must be resolved or ruled on by the panel under the loop budget before the PR can be called green. Group findings into families (same root cause, same correction, same artifact) before fixing.

### Comment anti-patterns

- Unlabelled comments that leave the author guessing at intent.
- `nitpick:` on something that is really an `issue:`.
- "LGTM" with no substance.
- Criticism with no reasoning; passive-aggressive suggestions.

---

## Self-check before delivering

- [ ] Commit follows `type(scope): description`, imperative, lowercase, under 72 characters
- [ ] Type matches the change; breaking changes are marked
- [ ] Body explains why when present; footers reference the work item
- [ ] One concern per commit; files staged by explicit path
- [ ] Measured claims carry their evidence in the same commit
- [ ] Every review comment has a label, and blocking status is unambiguous
- [ ] Every comment includes reasoning, not just a verdict
