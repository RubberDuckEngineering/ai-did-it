"""Print the git revision range a CI run should check.

Usage: python -m tools.commit_range --event-name NAME --event-path FILE

A pull request is checked from its base to its head. A push is checked over the commits it pushed,
so a commit already on the branch is judged once, when it lands, and not again by every later push.
A push that created the branch has no commit before it and is checked over all it reaches.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

NO_COMMIT = "0" * 40


def range_for(event_name: str, event: Mapping[str, Any]) -> str:
    if event_name == "pull_request":
        pull_request = event["pull_request"]
        return f"{pull_request['base']['sha']}..{pull_request['head']['sha']}"
    if event["before"] == NO_COMMIT:
        return event["after"]
    return f"{event['before']}..{event['after']}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--event-name", required=True, help="GITHUB_EVENT_NAME")
    parser.add_argument("--event-path", required=True, type=Path, help="GITHUB_EVENT_PATH")
    args = parser.parse_args(argv)

    event = json.loads(args.event_path.read_text(encoding="utf-8"))
    print(range_for(args.event_name, event))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
