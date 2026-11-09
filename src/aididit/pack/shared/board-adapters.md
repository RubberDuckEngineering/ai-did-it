# Board adapters

Every AI Did It stage reads and writes work items through this contract. Stages never call a
tracker directly; they say "claim the work item via the board adapter" and this file says what that
means for the configured provider.

Configuration (from `.specify/extensions/aididit/aididit-config.yml`):

| Key | Used by |
|---|---|
| `board.provider` | Selects the adapter: `markdown` (default), `github`, `jira` |
| `board.markdown_path` | markdown: path of the Kanban file (default `.specify/aididit/board.md`) |
| `board.github_ready_label` | github: the label that marks the Ready column (default `ready`) |
| `board.jira_project_key` | jira: the project to read and write |
| `board.jira_ready_status` | jira: the status name that is the Ready column |

## 1. Columns

Every provider maps onto the same five columns, in this order:

`Backlog` → `Ready` → `In Progress` → `In Review` → `Done`

- **Backlog**: accepted ideas, not yet prioritised. Ideate Mode A creates items here.
- **Ready**: prioritised and implementable. Assemble drains this column; the top item is next.
- **In Progress**: claimed by a lane (Ideate, Draft, Iterate).
- **In Review**: a pull request is open (entered by Iterate when it opens the PR; Deliver works it).
- **Done**: merged and tidied, or declined by the panel. The outcome says which.

## 2. Operations

An **item ref** is the provider's own id: `AID-<n>` (markdown), `#<n>` (github), the issue key
(jira, for example `PROJ-123`). Never invent or forecast one.

| Operation | Input | Result |
|---|---|---|
| `list_ready` | optional cap | Ready items in priority order: ref, title, labels, links |
| `read_item` | ref | Title, column, labels, links (blocks, blocked-by, split-from), lane, body, comments |
| `claim` | ref, lane id | Item moves Ready → In Progress, lane recorded, claim comment added |
| `comment` | ref, stage, text | Comment appended; earlier comments untouched |
| `move_in_review` | ref, PR URL | Item moves In Progress → In Review, comment names the PR |
| `move_done` | ref, outcome (`delivered` or `declined`), summary | Item moves to Done with the outcome recorded |
| `move` | ref, column (`Backlog`, `Ready`, `In Progress`, `In Review`) | Item moves to that column; comment names the stage and the reason. For Done use `move_done` |
| `create_item` | title, labels, body, column (default Backlog) | The new item's ref, read back from the provider |
| `link_items` | ref A, relation, ref B | Relation recorded on both items. Relations: `blocks`, `blocked-by`, `split-from` |

Board triage (Tidy) promotes and demotes items between Backlog and Ready with `move`.

### Rules every operation follows

1. **Create before cite.** Create the item, read back the ref the provider returned, then write that
   ref anywhere else. A forecast ref (the "next number" you expect) is never written.
2. **Re-read before write, verify after write.** Read the item's current state immediately before
   changing it, and read it again afterwards to confirm the column, labels and links say what you
   intended. A write you have not re-read is an assumption.
3. **Claims are race-safe.** `claim` first confirms the item is still in Ready. If it is not,
   another lane took it: skip it, do not steal it.
4. **Comment before a terminal move.** For `move_done` with outcome `declined`, post the closure
   comment first and move second, so the item never reads as delivered without its explanation.
5. **Run the secret scan (`disciplines/prompt-crafting.md`) on every body and comment** before writing it. A
   credential, token or connection string never reaches a board.
6. **Bodies use the story format** (Problem Statement, Acceptance Criteria, Notes) described in
   `.specify/extensions/aididit/stages/ideate/speckit.aididit.ideate.md`.
7. **Never assume a status, label or link type exists.** Derive it from the provider each time. Board
   configuration is live state and changes.

### Declined items

`move_done` with outcome `declined` additionally:

- applies the labels `declined-by-panel` and `wont-do`;
- uses the provider's "not planned" / "declined" closure where one exists (derived, never assumed);
- requires a closure comment whose first line says the item was declined and nothing was built,
  followed by the reason, the decisive finding, any spun-off refs, and "do not reopen this item; if
  the need returns, it is `<spun-off ref>`".

## 3. Provider: markdown (default)

The board is one Markdown file at `board.markdown_path`. The starter file is copied from
`.specify/extensions/aididit/templates/board.md` at install time.

### File format

```markdown
# Board

## Backlog

### AID-1 — Add a /health endpoint

- labels: story
- blocks: none
- blocked-by: none
- split-from: none
- lane: none

#### Problem Statement

**As a** ..., **I** ..., **which** ...

#### Acceptance Criteria

- **Given** ..., **when** ..., **then** ...

#### Notes

- ...

> 2026-11-05T10:20Z ideate: Premises verified against the code; no bundled scope.

## Ready

## In Progress

## In Review

## Done
```

Format rules:

- **Columns**: exactly five level-2 headings, `## Backlog`, `## Ready`, `## In Progress`,
  `## In Review`, `## Done`, in that order. Nothing else in the file uses a level-2 heading.
- **Item heading**: `### AID-<n> — <title>`, with an em dash (U+2014) between spaces. Readers also
  accept an en dash or a hyphen there; writers always use the em dash.
- **Item block**: runs from its `###` heading to the line before the next `###` or `##` heading, or
  the end of the file.
- **Metadata list**: immediately after the heading, these five lines in this order:
  - `- labels:` comma-separated lowercase labels (type first: `story`, `bug`, `tech-debt`, `spike`;
    then any others such as `declined-by-panel`);
  - `- blocks:` comma-separated refs, or `none`;
  - `- blocked-by:` comma-separated refs, or `none`;
  - `- split-from:` the ref this item was split from, or `none`;
  - `- lane:` the lane id that claimed the item, or `none`.
- **Body**: the story sections use level-4 headings (`#### Problem Statement`,
  `#### Acceptance Criteria`, `#### Notes`) so they never collide with column or item headings.
- **Comments**: lines at the end of the item block, in the form `> <timestamp> <stage>: <text>`.
  Timestamp is UTC `YYYY-MM-DDTHH:MMZ`. A multi-line comment continues on following lines that
  start with `> ` and carry no timestamp. Comments are append-only.
- **Ids**: `AID-<n>`, sequential. The next id is 1 + the highest `n` found in any `### AID-<n>`
  heading anywhere in the file (all columns, Done included). Ids are never reused, so items are
  never deleted; a declined or delivered item stays in Done.
- **Priority**: order within Ready is priority order. The top item is next.

### Operations

| Operation | Edit |
|---|---|
| `list_ready` | Return the item blocks under `## Ready`, top to bottom. Exclude items labelled `epic` (containers have no code scope of their own) |
| `read_item` | Find the `### <ref> —` heading; return its block and the column heading it sits under |
| `claim` | Confirm the item is under `## Ready`. Cut the block, paste it at the bottom of `## In Progress`, set `- lane: <lane id>`, append `> <ts> <stage>: claimed by lane <lane id>` |
| `comment` | Append `> <ts> <stage>: <text>` as the last line(s) of the item block |
| `move_in_review` | Cut the block, paste at the bottom of `## In Review`, append a comment naming the PR URL |
| `move` | Cut the block, paste it at the bottom of the target column's `##` heading, append `> <ts> <stage>: moved to <column> — <reason>` |
| `move_done` | Cut the block, paste at the bottom of `## Done`, append `> <ts> <stage>: done (<outcome>) — <summary>`. For `declined`, add the labels and the closure comment first (section 2) |
| `create_item` | Compute the next id, write the block at the bottom of the target column (default `## Backlog`), metadata fields set to `none` where empty. Read the file back and confirm the heading appears exactly once; that heading's id is the returned ref |
| `link_items` | `blocks`: add B to A's `- blocks:` and A to B's `- blocked-by:`. `blocked-by`: the mirror. `split-from`: set A's `- split-from: B` and comment on B `split into A`. Replace `none` when adding the first ref |

### Write discipline

- **One board, one place.** Always read and write the board file in the primary checkout (the
  directory Assemble runs in), never a lane worktree's copy; a worktree copy diverges silently.
- **Small, whole edits.** Re-read the file immediately before each edit and make each operation one
  write. When several lane processes run at once (`lanes.runner: claude` or `claude-remote`) they
  share this file: if the after-write check fails, re-read and redo the operation from fresh state.
- **The adapter does not commit.** The board file is runtime state (`lane-contract.md` §2): no lane
  commits it, and every clean-tree gate ignores it. The human commits it when the team wants its
  history. The lane folders under `.specify/aididit/lanes/` are runtime state too; nothing else
  under `.specify/aididit/` is exempt (retros are committed).

## 4. Provider: github

GitHub Issues through the `gh` CLI. Columns are labels on open issues; Done is a closed issue.

| Column | Representation |
|---|---|
| Backlog | open, none of the column labels below |
| Ready | open, label `board.github_ready_label` |
| In Progress | open, label `in-progress` |
| In Review | open, label `in-review` |
| Done | closed |

**Step 0 for this provider:** `gh auth status` must succeed, and the column labels must exist. Create
any missing one with `gh label create <name> --force` (idempotent). If `gh` is missing or not
authenticated, stop with: "Board provider github needs an authenticated gh CLI. Run `gh auth login`,
or set board.provider to markdown in aididit-config.yml."

Write every body and comment to a temporary file and pass it with `--body-file`; inline Markdown is
mangled by shell quoting.

| Operation | Command |
|---|---|
| `list_ready` | `gh issue list --state open --label "<ready label>" --json number,title,labels,body,createdAt --limit 200`. Drop issues that also carry `in-progress`, `in-review` or `epic`. Order by `createdAt` ascending unless the repo uses a documented priority label |
| `read_item` | `gh issue view <n> --json number,title,body,labels,state,comments,url` |
| `claim` | Re-read and confirm the ready label is still present, then `gh issue edit <n> --remove-label "<ready label>" --add-label in-progress`, then `comment` with the lane id |
| `comment` | `gh issue comment <n> --body-file <file>`; the first line is `**<stage>** <timestamp>` |
| `move_in_review` | `gh issue edit <n> --remove-label in-progress --add-label in-review`, then `comment` with the PR URL |
| `move` | Re-read the labels, then `gh issue edit <n>` with `--remove-label` for whichever column label (`<ready label>`, `in-progress`, `in-review`) the item carries and `--add-label` for the target column's label (none for Backlog), then `comment` with the reason |
| `move_done` | `gh issue edit <n> --remove-label in-review --remove-label in-progress`, then `gh issue close <n> --reason completed --comment "<summary>"`. Declined: add the labels with `gh issue edit <n> --add-label declined-by-panel,wont-do`, post the closure comment, then `gh issue close <n> --reason "not planned"` |
| `create_item` | `gh issue create --title "<title>" --body-file <file> --label <labels>`. The command prints the issue URL; the number at its end is the ref. For column Ready add the ready label |
| `link_items` | Keep a `## Links` section at the end of each issue body with lines `- blocks: #<n>`, `- blocked-by: #<n>`, `- split-from: #<n>`. Edit both bodies with `gh issue edit <n> --body-file <file>` (re-read first, change only that section). GitHub's own issue-relationship features may exist on your host [Unverified]; if you use them, the body section is still the record stages read |

## 5. Provider: jira

Jira is reached only through an Atlassian MCP server connected to the agent. This pack ships no Jira
client and stores no Jira credentials.

**Step 0 for this provider:**

1. Look for the Atlassian MCP tools in the agent's tool list. Typical names on the Atlassian remote
   MCP server are `searchJiraIssuesUsingJql`, `getJiraIssue`, `getTransitionsForJiraIssue`,
   `transitionJiraIssue`, `addCommentToJiraIssue`, `createJiraIssue`, `editJiraIssue`,
   `getIssueLinkTypes` and `createIssueLink`; other servers name them differently, so match by
   purpose.
2. If no such tools exist, **stop** with: "Board provider jira is unavailable: no Atlassian MCP
   server is connected to this agent. Connect one, or set board.provider to markdown or github in
   .specify/extensions/aididit/aididit-config.yml." Do not fall back to another provider silently.
3. If `board.jira_project_key` is empty, stop with: "Set board.jira_project_key in
   aididit-config.yml."
4. Run one smoke search. An unreachable tracker is a stop, never an assumed-empty column.

Columns map to statuses by name: Ready is `board.jira_ready_status`; the others are statuses named
`Backlog`, `In Progress`, `In Review` and `Done` (matched case-insensitively). If the workflow has
no In Review status, leave the item In Progress and say so in the comment; never invent a status.

| Operation | Call |
|---|---|
| `list_ready` | JQL `project = "<key>" AND status = "<ready status>" AND issuetype != Epic AND issuetype not in subTaskIssueTypes() ORDER BY priority DESC, created ASC` |
| `read_item` | Get the issue with summary, description, status, labels, issue links and comments |
| `claim` | Re-read and confirm the status is still the ready status, then move to In Progress (below) and comment the lane id |
| `comment` | Add a comment; first line `<stage> <timestamp>`. Use the server's Markdown content format where it offers one |
| `move_in_review` | Move to In Review (below), comment with the PR URL |
| `move` | Transition by name to the target column's status (below), then comment with the reason |
| `move_done` | Move to Done (below). Declined: see the declined procedure below |
| `create_item` | Create in `<key>` with the issue type that matches the item's shape (Story, Bug, Task, Spike), as the project actually offers them. The returned key is the ref |
| `link_items` | Read the link types first. `blocks` / `blocked-by`: the `Blocks` type, with the outward/inward direction set to match. `split-from`: a type whose name mentions split if one exists, otherwise `Relates` plus a comment naming the split |

**Moving = transitioning by name.** List the transitions available on the issue now, pick the one
whose target status matches the column, and run it. If none matches, do not guess: report the
transitions that do exist and stop that operation.

**Declined items on Jira.** Workflows differ, so derive each step:

1. Comment the panel verdict, then the closure comment (section 2), then add the labels.
2. If a transition to a declined-type status exists (for example "Declined" or "Won't Do"), use it;
   otherwise use Done, and the labels plus the closure comment carry the truth. Say which in the
   comment.
3. Set the resolution as a **separate edit after** the transition (for example `Won't Do`, if the
   instance has it). A transition screen can refuse a field, and a post-function can then set the
   resolution to the delivered value; a follow-up edit can still succeed. A refusal during one call
   is not a property of the field.
4. Re-read the issue and confirm status, resolution and labels all say "declined".

Fields such as story points can be missing from some issue types' screens. Record the value in the
description or a comment and say so; never drop it silently.
