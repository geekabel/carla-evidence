"""Canonical mass functions used across the regression suite.

Names follow the literature so individual tests can cite the source. See
``CLAUDE.md`` §"Tests" — every regression test must reference an academic
example.
"""

from __future__ import annotations

from tests.fixtures.small_frames import THETA_OBJECTS, THETA_SUSPECTS

from carla_evidence import Frame, MassFunction

# ---- Vacuous / categorical / bayesian baselines --------------------------


def vacuous_suspects() -> MassFunction:
    """Total ignorance over the suspects frame."""
    return MassFunction.vacuous(THETA_SUSPECTS)


def categorical_peter() -> MassFunction:
    """Certainty that Peter is the culprit."""
    return MassFunction.categorical(THETA_SUSPECTS, ("peter",))


def bayesian_uniform_objects() -> MassFunction:
    """Uniform Bayesian BBA over the objects frame."""
    return MassFunction.bayesian(THETA_OBJECTS, [0.25, 0.25, 0.25, 0.25])


# ---- Worked examples for Bel / Pl / Q -----------------------------------


def shafer_three_element_example() -> MassFunction:
    """Three-element BBA whose Bel/Pl/Q have been hand-verified.

    Frame: Theta = {a, b, c}. Masses:

        m({a})       = 0.6
        m({a, b})    = 0.3
        m(Theta)     = 0.1

    The expected dense vectors (indexed by bitmask 0..7) are:

        Bel = [0.0, 0.6, 0.0, 0.9, 0.0, 0.6, 0.0, 1.0]
        Pl  = [0.0, 1.0, 0.4, 1.0, 0.1, 1.0, 0.4, 1.0]
        Q   = [1.0, 1.0, 0.4, 0.4, 0.1, 0.1, 0.1, 0.1]

    The structure follows Shafer (1976) §2 worked examples: a focal element
    on a singleton, on a pair, and on Theta itself.
    """
    theta = Frame.of("a", "b", "c")
    return MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})


def smets_open_world_example() -> MassFunction:
    """TBM-mode BBA with non-zero ``m(empty-set)``.

    Frame: Theta = {a, b}. Masses:

        m(empty-set) = 0.2
        m({a})       = 0.5
        m(Theta)     = 0.3

    Smets's TBM (1990) interprets ``m(empty-set) = 0.2`` as the share of
    evidence assigned to the open-world hypothesis "the truth lies outside Theta".
    """
    theta = Frame.of("a", "b")
    return MassFunction(
        theta,
        {(): 0.2, ("a",): 0.5, ("a", "b"): 0.3},
        mode="tbm",
    )
