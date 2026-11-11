# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository (Security tab → "Report a vulnerability"). If that button is not there, email
**admin@rubberduckengineering.com** instead. Do not open a public issue.

## What is in scope

- The `aididit` CLI and the lane spawn scripts under `src/aididit/pack/scripts/`.
- Prompt content in the pack that could lead an agent to leak secrets, run untrusted content as
  instructions, or take irreversible actions without the human gate.

## Design notes

- The CLI never runs a shell; every external command is an argument list.
- The spawn scripts pass the handoff prompt as a single argument, never through `eval`.
- Lane handoff notes are git-ignored and must never contain credentials. The pack's prompt-crafting
  discipline requires a secret scan before a note is written.
- Work-item and PR text is treated as untrusted data by every stage.
- CI scans every commit for secrets (gitleaks) and `uv.lock` for dependencies with a HIGH or
  CRITICAL CVE (Trivy), on each change and weekly. Dependabot proposes dependency updates.
