# Contributing to carla-evidence

Thanks for considering a contribution. This project values **mathematical rigor,
reproducibility, and a stable public API** above ergonomics or performance. Please read
this document and [`CLAUDE.md`](CLAUDE.md) before opening a pull request — `CLAUDE.md`
contains domain-specific traps (m(∅) semantics, normalisation Dempster, PCR5 vs PCR6,
Jousselme metric, …) that any contributor needs to know.

By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Quick start

```bash
git clone https://github.com/geekabel/carla-evidence
cd carla-evidence
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs,viz]"
pre-commit install
pytest
```

Python 3.10+ is required. We test against 3.10, 3.11, 3.12 in CI.

## Workflow

1. Open an issue describing the change before substantial work — especially for new
   combination rules or core API additions.
2. Fork, branch (`feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`).
3. Run `pre-commit run --all-files` and `pytest` locally before pushing.
4. Open a pull request against `main`. Reference the issue, and fill in the PR template.
5. CI must be green. Coverage targets per module are enforced (see
   [`carla-evidence-architecture.md`](carla-evidence-architecture.md) §8.4).

## Conventional Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/). Examples:

- `feat(combination): add Dubois-Prade rule`
- `fix(core): handle K=1 in dempster gracefully`
- `docs(tutorials): add Zadeh paradox notebook`
- `test(property): tighten BetP probability invariant`
- `perf(pcr6): vectorize redistribution step (3x speedup)`
- `refactor(decision): extract shared transform logic`
- `chore(deps): bump pydantic to 2.5`

The `CHANGELOG.md` is generated from these messages.

## Adding a new combination rule

1. Create `src/carla_evidence/combination/<name>.py` inheriting from
   `CombinationRule` (in `combination/base.py`).
2. Implement `combine(m1, m2)`. Override `combine_many` if a multi-source
   optimisation exists.
3. Re-export from `combination/__init__.py` and add to `__all__`.
4. Add tests:
   - `tests/unit/test_<name>.py` with at least one example from the literature
     (cite the source).
   - `tests/property/test_<name>_props.py` covering commutativity (if
     applicable) and the vacuous-BBA neutral element.
   - `tests/regression/test_<name>_regression.py` reproducing one canonical
     numerical example.
5. Document the rule in `docs/source/concepts/combination_rules.md` and add a
   row to the summary table.
6. Add a `feat(combination): add <name> rule` entry to the [Unreleased]
   section of `CHANGELOG.md`.
7. In the PR description, include: the academic reference, asymptotic
   complexity, and a `pytest-benchmark` micro-benchmark (before/after if
   applicable).

## Tests

- Coverage minimums: `core/` ≥ 95%, operators ≥ 90%, adapters ≥ 70%, viz ≥ 60%.
- Property-based tests use `hypothesis` with strategies from
  `carla_evidence.testing`.
- Never `xfail` or skip a test without an issue link in the comment.

## Documentation

Build locally with:

```bash
cd docs && make html && open build/html/index.html
```

API references are generated from Google-style docstrings (see the canonical example
in `CLAUDE.md`). Notebooks in `examples/` are stripped of outputs by pre-commit.

## Reporting bugs

Use the **Bug report** issue template. Include:

- A minimal reproducer (preferably as a property-based test if applicable).
- Expected vs. observed output, with a citation when the expected output comes
  from the literature.
- Versions: `carla-evidence`, `numpy`, `scipy`, Python.

## Security

For security issues (e.g. arbitrary code execution via maliciously crafted BBA
deserialisation), please email <koffigodwin96@gmail.com> rather than opening a public
issue.

## Release process

See `carla-evidence-architecture.md` §13 and `CLAUDE.md` "Sortie de release". Releases
are cut from `main` after CI is green; tagging triggers
`.github/workflows/release.yml`.
