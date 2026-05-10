"""Hypothesis strategies for property-based testing of evidential code.

Public surface (lands in v0.1.0): ``mass_functions``, ``frames``, ``frame_names``,
``categorical_bbas``, ``bayesian_bbas``, ``vacuous_bbas``. See
:mod:`carla_evidence.testing.strategies` for full docstrings.
"""

from carla_evidence.testing.strategies import (
    bayesian_bbas,
    categorical_bbas,
    frame_names,
    frames,
    mass_functions,
    vacuous_bbas,
)

__all__ = [
    "bayesian_bbas",
    "categorical_bbas",
    "frame_names",
    "frames",
    "mass_functions",
    "vacuous_bbas",
]
