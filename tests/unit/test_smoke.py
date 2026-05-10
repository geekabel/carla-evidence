"""Phase-0 smoke tests: the package imports and exposes a version string.

These minimal tests guarantee CI is green on an empty PR and detect packaging
regressions (e.g. a broken ``setuptools-scm`` configuration).
"""

from __future__ import annotations

import importlib

import carla_evidence


def test_package_imports() -> None:
    assert carla_evidence is not None


def test_version_is_a_nonempty_string() -> None:
    assert isinstance(carla_evidence.__version__, str)
    assert carla_evidence.__version__


def test_subpackages_import() -> None:
    for name in (
        "core",
        "combination",
        "discounting",
        "decision",
        "metrics",
        "construction",
        "viz",
        "benchmarks",
        "testing",
    ):
        importlib.import_module(f"carla_evidence.{name}")
