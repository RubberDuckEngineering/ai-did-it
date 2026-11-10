# Board

<!--
AI Did It Kanban board (board.provider: markdown).
Format and rules: .specify/extensions/aididit/shared/board-adapters.md
- One "## <Column>" heading per column, in this order. Do not rename or reorder them.
- Each work item is a "### AID-<n> — <title>" block inside its column.
- Next id = 1 + the highest AID number anywhere in this file. Never reuse an id.
- The demo item below is AID-0, so your first item is AID-1.
- Moving an item = cut its whole block and paste it at the bottom of the target column.
- Comments are appended "> <timestamp> <stage>: <text>" lines at the end of the item.
- Ready is ordered by priority: the top item is the next one to work.
-->

## Backlog

### AID-0 — Add a /health endpoint

- labels: story
- blocks: none
- blocked-by: none
- split-from: none
- lane: none

#### Problem Statement

**As an** operator running the service behind a load balancer, **I need** a cheap endpoint that reports whether the process is up and can reach its dependencies, **which** lets the load balancer stop routing to an unhealthy instance instead of failing user requests.

#### Acceptance Criteria

- **Given** the service is running and its dependencies are reachable, **when** a client sends `GET /health`, **then** the response is `200` with a JSON body `{"status":"healthy"}` within 500 ms.
- **Given** a required dependency is unreachable, **when** a client sends `GET /health`, **then** the response is `503` with a JSON body naming the failing dependency and no stack trace or secret.
- **Given** the endpoint is called without credentials, **when** it responds, **then** the body contains no version numbers, hostnames or configuration values.

#### Notes

- Demo item showing the board format. Delete it, or move it to Ready to try a lane.
- [Unverified] Whether the load balancer expects a specific path or status code; check its documentation before Draft.
- Out of scope: deep checks that write test data to dependencies.

> 2026-01-01T00:00Z ideate: Example comment. Stages append lines like this one; never edit an earlier comment.

## Ready

## In Progress

## In Review

## Done
