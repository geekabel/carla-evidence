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

- Repository bootstrap (Phase 0): packaging metadata (`pyproject.toml` with
  `setuptools-scm`), BSD-3-Clause license, `CITATION.cff`, contributor docs,
  pre-commit hooks (ruff, ruff-format, mypy, nbstripout, codespell), minimal CI
  workflow, Sphinx + Read the Docs configuration, empty but importable
  `src/carla_evidence/` package tree, `tests/` skeleton with markers.

[Unreleased]: https://github.com/geekabel/carla-evidence/compare/HEAD...HEAD
