<!-- Thanks for contributing! Please make sure your PR title follows
     Conventional Commits (e.g. `feat(combination): add Dubois-Prade rule`). -->

## Summary

<!-- One or two sentences on the change and the why. -->

## Type of change

- [ ] Bug fix (`fix:`)
- [ ] New feature (`feat:`)
- [ ] Refactor (`refactor:`) — no behaviour change
- [ ] Performance (`perf:`)
- [ ] Documentation (`docs:`)
- [ ] Tests (`test:`)
- [ ] Build / CI / chore (`chore:` / `ci:` / `build:`)
- [ ] Breaking change

## Academic reference(s)

<!-- For combination rules, discounting, decision, metrics, or construction layers,
     please cite the paper(s) the implementation follows. -->

## Checklist

- [ ] Tests added (unit + property when applicable + at least one regression test
      against a literature example for combination rules / decision transforms / metrics).
- [ ] Coverage for new code meets the per-module target (`CLAUDE.md` §"Tests").
- [ ] Public API has Google-style docstrings with Args / Returns / Raises / Examples /
      References.
- [ ] `pre-commit run --all-files` passes locally.
- [ ] `pytest -n auto` passes locally.
- [ ] `mypy src/carla_evidence` passes.
- [ ] `CHANGELOG.md` Unreleased section updated.
- [ ] Public-API breakage is either avoided or accompanied by a deprecation warning
      and a note in `CHANGELOG.md`.

## Performance

<!-- For perf-sensitive changes (PCR5/PCR6, vectorisation), include before/after
     numbers from `pytest-benchmark`. -->

## Notes for reviewers

<!-- Pointers to subtle invariants, edge cases (K=1, vacuous BBA, single-element frame),
     or numerical stability concerns. -->
