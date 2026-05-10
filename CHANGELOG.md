# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
once it reaches v1.0. Pre-1.0 releases may break the API in minor versions, with a
deprecation warning of at least one minor release.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/);
this changelog is generated from them.

## [Unreleased]

(No entries yet — open a new section below this one once v0.3.0 work starts.)

## [0.2.0] — 2026-05-10

- Zenodo concept DOI: `10.5281/zenodo.20114179`
- Zenodo v0.2.0 DOI:  `10.5281/zenodo.20114180`
- GitHub release:     <https://github.com/geekabel/carla-evidence/releases/tag/v0.2.0>
- Test PyPI:          <https://test.pypi.org/project/carla-evidence/0.2.0/>

### Added

- **Combination layer v0.2.0 (Phase 2)** — eight rules (`feat(combination)`):
  - `conjunctive` (Smets 1990) — TBM-mode, retains conflict on `empty-set`.
  - `dempster` (Shafer 1976) — normalised by `1/(1-K)`; raises
    `TotalConflictError` if `K = 1`.
  - `disjunctive` (Dubois-Prade 1986) — least-committal fusion via union.
  - `yager` (Yager 1987) — conflict redirected to `Theta`.
  - `dubois_prade` (Dubois-Prade 1988) — conflict redirected to `B union C`.
  - `pcr5` (Smarandache-Dezert 2005) — proportional conflict redistribution
    for two sources; refuses three-or-more (PCR5 is not associative).
  - `pcr6` (Martin-Osswald 2006) — N-source generalisation of PCR5; binary
    case delegates to PCR5.
  - `mean` (Murphy 2000) — arithmetic mean baseline.
- All rules expose a callable instance (`dempster(m1, m2)`,
  `pcr6([m1, m2, m3])`) plus the explicit `combine` / `combine_many`
  API. The dispatcher accepts binary, iterable, and variadic forms.
- Sparse kernel (`combination/_sparse_kernel.py`): a single
  `cartesian_combine` shared by the seven cartesian-product rules,
  parameterised by a `ConflictRouter` Protocol. Each rule body is ~30 lines
  describing its conflict policy.
- Dense reference impls (`tests/_references/dense_combination.py`):
  literal `O(2^|Theta| × 2^|Theta|)` translations of every formula, used as
  oracles by hypothesis property tests asserting
  `sparse(m1, m2) ≈ dense(m1, m2)` to `atol=1e-12`.
- **Tutorial 2** (`examples/02_zadeh_paradox.ipynb`) walks through Zadeh's
  two-doctors paradox and demonstrates how each rule handles severe
  conflict.
- **Concept primer** (`docs/source/concepts/combination_rules.md`) with the
  rules table, conflict-routing trade-offs, and three traps to avoid.
- **Benchmark suite** (`benchmarks/bench_combination.py`) measured locally:
  - Dempster `|Theta|=4`: **~107k ops/s** (target ≥10⁵ ✓)
  - PCR6 binary `|Theta|=8`: **~11.3k ops/s** (target ≥10⁴ ✓)
  - Other binary rules on `|Theta|=4`: 100–164k ops/s.

### Notes

- Cautious and bold rules (Denoeux 2008) are deferred to **v0.2.1**: they
  require the canonical decomposition of a non-dogmatic BBA into its weight
  function (Möbius / log-Möbius transform of the commonality vector,
  Kennes 1992 algorithm). The placeholder `combination/_dense_kernel.py`
  reserves the namespace.
- DSmT hyperpowerset support remains deferred. PCR5 and PCR6 ship for the
  Shafer/TBM modes only (the standard powerset); on those frames they are
  already mathematically well-defined.
- ABC `CombinationRule` exposes `combine`, `combine_many`, and a smart
  `__call__` that routes binary, iterable, and variadic invocations.

- **Core layer (Phase 1)** — `Frame` and `MassFunction` (`feat(core)`):
  - `Frame`: frozen, hashable, ordered tuple of distinct hypotheses with
    cached element-name ↔ bitmask translation. Constructors `Frame(...)`
    and `Frame.of(*elements)`.
  - `MassFunction`: immutable Basic Belief Assignment with **sparse-first**
    storage (canonical sorted tuple of `(bitmask, mass)`, hashable). Modes
    `"shafer"` (`m(empty-set)=0` enforced) and `"tbm"` (`m(empty-set)>=0`
    allowed). Mode `"dsmt"` raises `NotImplementedError` until v0.2.0
    where it ships alongside PCR5/PCR6.
  - Helper constructors: `vacuous`, `categorical`, `bayesian`, `from_dict`,
    `from_array`, `from_json`.
  - Belief / plausibility / commonality: scalar `bel`, `pl`, `q` and
    vectorised `to_bel_vector`, `to_pl_vector`, `to_q_vector` via
    Möbius/Yates transform in `O(n * 2^n)`.
  - Introspection: `core`, `is_normal`, `is_bayesian`, `is_vacuous`,
    `is_categorical`, `__iter__`, `is_close_to`.
  - Serialisation: `to_dict`, `to_json`, `from_json` (frame + mode + focals
    round-trip).
- **Bitmask encoding utilities** (`carla_evidence.core.encoding`):
  `full_mask`, `is_subset`, `is_proper_subset`, `intersection`, `union`,
  `complement`, `cardinality`, `iter_subsets_of`.
- **Powerset enumeration** (`carla_evidence.core.powerset`):
  `iter_powerset_masks`, `iter_powerset`, `iter_focal_pairs`.
- **Domain exceptions** (`carla_evidence.core.exceptions`):
  `EvidenceError` (root), `FrameError`, `FrameMismatchError`,
  `InvalidMassError`, `ModeError`, `TotalConflictError` (the last reserved
  for v0.2.0).
- **Hypothesis strategies** (`carla_evidence.testing`): `frames`,
  `frame_names`, `mass_functions`, `vacuous_bbas`, `categorical_bbas`,
  `bayesian_bbas` for downstream property testing.
- **Tutorial 1**: `examples/01_mass_functions.ipynb` walking through
  `Frame`, `MassFunction` modes, helpers, bel/pl/q, and JSON round-trip.
- **Concept primer**: `docs/source/concepts/mass_functions.md` covering
  the mathematics behind each mode and the storage rationale.

### Notes

- DSmT mode is intentionally deferred to v0.2.0 to keep the hyperpowerset
  enumeration close to the PCR5/PCR6 rules that need it (avoids a
  half-finished implementation per `CLAUDE.md` DON'Ts).
- Storage is **sparse-first** by design (`tuple[(bitmask, mass), ...]` sorted
  canonically); dense numpy materialisation is on demand. There is no
  dense/sparse threshold.

- Repository bootstrap (Phase 0): packaging metadata (`pyproject.toml` with
  `setuptools-scm`), BSD-3-Clause license, `CITATION.cff`, contributor docs,
  pre-commit hooks (ruff, ruff-format, mypy, nbstripout, codespell), minimal CI
  workflow, Sphinx + Read the Docs configuration, empty but importable
  `src/carla_evidence/` package tree, `tests/` skeleton with markers.

[Unreleased]: https://github.com/geekabel/carla-evidence/compare/v0.2.0...HEAD
[0.2.0]:      https://github.com/geekabel/carla-evidence/releases/tag/v0.2.0
