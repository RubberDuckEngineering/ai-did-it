#!/usr/bin/env bash
# spawn-lane.sh: start the next link of an AI Did It lane as a detached Claude Code session.
#
# Usage (run from the project root):
#   spawn-lane.sh --lane <id> --link <stage> --prompt-file <path> [--mode claude|claude-remote] [--dry-run]
#
#   --lane         lane id, ^[a-z0-9][a-z0-9-]{0,62}$
#   --link         ideate | draft | iterate | deliver | investigate | tidy
#   --prompt-file  existing, non-empty file holding the link's prompt (max 32000 chars)
#   --mode         claude (default): claude -p "<prompt>"
#                  claude-remote:    claude --remote-control "<lane>-<link>" "<prompt>"
#   --dry-run      print one line "DRY-RUN: <bin> <args...>" and exit 0; creates nothing.
#                  Newlines in the prompt are shown as \n and \r so the line stays single.
#
# The claude binary is $AIDIDIT_CLAUDE_BIN if set, else `claude` on PATH.
# Output on success: SPAWNED lane=<lane> link=<link> pid=<pid> log=<path>
# Exit codes: 0 ok, 2 usage/validation error, 3 claude binary not found.
# The prompt is always passed as a single argv element; it is never evaluated by a shell.

set -euo pipefail

readonly LANE_CHARS='abcdefghijklmnopqrstuvwxyz0123456789'
readonly LANE_PATTERN="^[${LANE_CHARS}][${LANE_CHARS}-]{0,62}\$"
readonly VALID_LINKS=(ideate draft iterate deliver investigate tidy)
readonly MAX_PROMPT_CHARS=32000
readonly LEDGER_ROOT='.specify/aididit/lanes'
readonly EXIT_USAGE=2
readonly EXIT_NO_CLAUDE=3

usage() {
    printf 'Usage: %s --lane <id> --link <stage> --prompt-file <path> [--mode claude|claude-remote] [--dry-run]\n' \
        "$(basename "$0")"
}

fail_usage() {
    printf 'spawn-lane: %s\n' "$1" >&2
    usage >&2
    exit "$EXIT_USAGE"
}

lane="" link="" prompt_file="" mode="claude" dry_run=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --lane|--link|--prompt-file|--mode)
            [ "$#" -ge 2 ] || fail_usage "missing value for $1"
            case "$1" in
                --lane) lane="$2" ;;
                --link) link="$2" ;;
                --prompt-file) prompt_file="$2" ;;
                --mode) mode="$2" ;;
            esac
            shift 2
            ;;
        --dry-run) dry_run=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail_usage "unknown argument: $1" ;;
    esac
done

[ -n "$lane" ] || fail_usage "--lane is required"
[ -n "$link" ] || fail_usage "--link is required"
[ -n "$prompt_file" ] || fail_usage "--prompt-file is required"
[[ "$lane" =~ $LANE_PATTERN ]] || fail_usage "invalid lane id '$lane' (must match ^[a-z0-9][a-z0-9-]{0,62}\$)"

link_is_valid=0
for valid_link in "${VALID_LINKS[@]}"; do
    if [ "$link" = "$valid_link" ]; then link_is_valid=1; fi
done
[ "$link_is_valid" -eq 1 ] || fail_usage "invalid link '$link' (one of: ${VALID_LINKS[*]})"

case "$mode" in
    claude|claude-remote) ;;
    *) fail_usage "invalid mode '$mode' (claude or claude-remote)" ;;
esac

if [ ! -f "$prompt_file" ] || [ ! -r "$prompt_file" ]; then
    fail_usage "prompt file not found or unreadable: $prompt_file"
fi
prompt="$(cat -- "$prompt_file")"
[ -n "$prompt" ] || fail_usage "prompt file is empty: $prompt_file"
[ "${#prompt}" -le "$MAX_PROMPT_CHARS" ] || fail_usage "prompt exceeds $MAX_PROMPT_CHARS characters"

claude_bin="${AIDIDIT_CLAUDE_BIN:-claude}"
if [ "$mode" = "claude-remote" ]; then
    claude_args=(--remote-control "${lane}-${link}" "$prompt")
else
    claude_args=(-p "$prompt")
fi

if [ "$dry_run" -eq 1 ]; then
    display="DRY-RUN: $claude_bin"
    for arg in "${claude_args[@]}"; do
        display+=" $arg"
    done
    display="${display//$'\r'/\\r}"
    printf '%s\n' "${display//$'\n'/\\n}"
    exit 0
fi

if [ -n "${AIDIDIT_CLAUDE_BIN:-}" ] && [ -f "$claude_bin" ] && [ -x "$claude_bin" ]; then
    resolved_bin="$claude_bin"
elif resolved_bin="$(command -v -- "$claude_bin" 2>/dev/null)" && [ -n "$resolved_bin" ]; then
    :
else
    printf 'spawn-lane: claude binary not found: %s (set AIDIDIT_CLAUDE_BIN or put claude on PATH)\n' "$claude_bin" >&2
    exit "$EXIT_NO_CLAUDE"
fi

lane_dir="$LEDGER_ROOT/$lane"
log_path="$lane_dir/$link.log"
mkdir -p -- "$lane_dir"

# setsid (where available) detaches the session from this shell's process group so it
# survives the caller exiting; nohup covers hangups. Both exec in place, so $! is claude's pid.
launcher=(nohup)
if command -v setsid >/dev/null 2>&1; then
    launcher=(setsid nohup)
fi
"${launcher[@]}" "$resolved_bin" "${claude_args[@]}" >"$log_path" 2>&1 </dev/null &
spawned_pid=$!
disown "$spawned_pid" 2>/dev/null || true

printf 'SPAWNED lane=%s link=%s pid=%s log=%s\n' "$lane" "$link" "$spawned_pid" "$log_path"
