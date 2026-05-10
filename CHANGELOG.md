# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
once it reaches v1.0. Pre-1.0 releases may break the API in minor versions, with a
deprecation warning of at least one minor release.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/);
this changelog is generated from them.

## [Unreleased]

### Added

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

[Unreleased]: https://github.com/geekabel/carla-evidence/compare/HEAD...HEAD
