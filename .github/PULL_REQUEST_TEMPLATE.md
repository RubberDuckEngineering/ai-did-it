## What and why

<!-- One paragraph: the behaviour this changes and the reason. -->

## Checklist

- [ ] Tests written first and seen failing for the right reason
- [ ] `uv run pytest --cov=aididit --cov=tools` passes at 100% coverage
- [ ] Each new guard has a row in `docs/kill-tests.md`: control green, named mutation red
- [ ] Docs, pack files and `CHANGELOG.md` changed in the same commit as the behaviour
- [ ] Commits follow Conventional Commits (`type(scope): description`)
- [ ] A change to a diagram or to CLI output shows before and after, or says why there is no visible change
