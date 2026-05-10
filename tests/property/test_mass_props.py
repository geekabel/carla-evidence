"""Property-based tests for :class:`MassFunction` (Shafer 1976 invariants)."""

from __future__ import annotations

import math

from hypothesis import given, settings
from pytest import approx

from carla_evidence import MassFunction
from carla_evidence.testing import (
    bayesian_bbas,
    categorical_bbas,
    frames,
    mass_functions,
    vacuous_bbas,
)

# ---- Construction invariants ---------------------------------------


@given(m=mass_functions(frame_size=4))
def test_mass_sums_to_one(m: MassFunction) -> None:
    """Σ m(A) = 1 for every well-formed BBA."""
    total = math.fsum(mass for _, mass in m.focals)
    assert math.isclose(total, 1.0, abs_tol=1e-6)


@given(m=mass_functions(frame_size=4))
def test_masses_are_non_negative(m: MassFunction) -> None:
    for _, mass in m.focals:
        assert mass >= 0.0


@given(m=mass_functions(frame_size=4))
def test_focals_are_canonically_sorted(m: MassFunction) -> None:
    masks = [mask for mask, _ in m.focals]
    assert masks == sorted(masks)


@given(m=mass_functions(frame_size=4))
def test_no_zero_focals(m: MassFunction) -> None:
    for _, mass in m.focals:
        assert mass > 0.0


# ---- Belief / plausibility / commonality invariants ----------------


@given(m=mass_functions(frame_size=3))
def test_bel_at_empty_set_is_zero(m: MassFunction) -> None:
    assert m.bel(0) == 0.0


@given(m=mass_functions(frame_size=3))
def test_bel_at_theta_equals_one_minus_m_empty(m: MassFunction) -> None:
    """Bel(Theta) = 1 - m(empty-set). In Shafer mode this is 1."""
    assert math.isclose(m.bel(m.frame.full_mask), 1.0 - m.mass(0), abs_tol=1e-9)


@given(m=mass_functions(frame_size=3))
def test_pl_dominates_bel(m: MassFunction) -> None:
    """Pl(A) >= Bel(A) for every A (Shafer 1976, §2.3)."""
    for A in range(m.frame.size):
        assert m.pl(A) >= m.bel(A) - 1e-9


@given(m=mass_functions(frame_size=3))
def test_bel_is_super_additive_on_disjoint(m: MassFunction) -> None:
    """Bel(A) + Bel(B) <= Bel(A union B) when A intersect B = empty-set
    (Shafer 1976, §2 axiom B2)."""
    n = m.frame.size
    for A in range(n):
        for B in range(n):
            if A & B == 0:  # disjoint
                lhs = m.bel(A) + m.bel(B)
                rhs = m.bel(A | B)
                assert lhs <= rhs + 1e-9


@given(m=mass_functions(frame_size=3))
def test_bel_subadditive_complement_in_shafer(m: MassFunction) -> None:
    """In Shafer mode, Bel(A) + Bel(neg A) <= 1 (sub-additive complement,
    Shafer 1976, §2.3)."""
    full = m.frame.full_mask
    for A in range(m.frame.size):
        not_A = full ^ A
        assert m.bel(A) + m.bel(not_A) <= 1.0 + 1e-9


@given(m=mass_functions(frame_size=3))
def test_pl_super_additive_complement_in_shafer(m: MassFunction) -> None:
    """In Shafer mode, Pl(A) + Pl(neg A) >= 1 (dual to the Bel bound)."""
    full = m.frame.full_mask
    for A in range(m.frame.size):
        not_A = full ^ A
        assert m.pl(A) + m.pl(not_A) >= 1.0 - 1e-9


@given(m=mass_functions(frame_size=3))
@settings(max_examples=50)
def test_dense_vectors_match_scalar(m: MassFunction) -> None:
    """``to_*_vector()`` agrees with the scalar accessors at every bitmask.

    Float drift up to a few ulp is allowed: the vector path uses Möbius/Yates
    transforms (and the identity Pl = 1 - Bel(neg) for Pl), whereas the scalar
    path sums focals directly via ``math.fsum``.
    """
    bel_vec = m.to_bel_vector()
    pl_vec = m.to_pl_vector()
    q_vec = m.to_q_vector()
    for A in range(m.frame.size):
        assert bel_vec[A] == approx(m.bel(A), abs=1e-12)
        assert pl_vec[A] == approx(m.pl(A), abs=1e-12)
        assert q_vec[A] == approx(m.q(A), abs=1e-12)


# ---- Mode-specific invariants -------------------------------------


@given(m=mass_functions(frame_size=3, mode="shafer"))
def test_shafer_has_zero_empty_mass(m: MassFunction) -> None:
    assert m.mass(0) == 0.0
    assert m.is_normal


@given(m=mass_functions(frame_size=3, mode="tbm"))
def test_tbm_remains_valid_with_empty_mass(m: MassFunction) -> None:
    """A TBM BBA can have m(empty-set) > 0 and still satisfies Σ m = 1."""
    total = math.fsum(mass for _, mass in m.focals)
    assert math.isclose(total, 1.0, abs_tol=1e-6)


# ---- Helper-constructor invariants --------------------------------


@given(m=vacuous_bbas(frame_size=3))
def test_vacuous_bel_is_zero_except_at_theta(m: MassFunction) -> None:
    full = m.frame.full_mask
    for A in range(m.frame.size):
        assert m.bel(A) == (1.0 if full == A else 0.0)


@given(m=vacuous_bbas(frame_size=3))
def test_vacuous_pl_is_one_except_at_empty(m: MassFunction) -> None:
    for A in range(m.frame.size):
        assert m.pl(A) == (0.0 if A == 0 else 1.0)


@given(m=categorical_bbas(frame_size=3))
def test_categorical_has_single_focal(m: MassFunction) -> None:
    assert len(m) == 1
    assert m.is_categorical


@given(m=bayesian_bbas(frame_size=3))
def test_bayesian_pl_equals_bel_on_singletons(m: MassFunction) -> None:
    """For a Bayesian BBA, Pl({x}) = Bel({x}) = m({x}) on every singleton."""
    for i in range(len(m.frame)):
        singleton = 1 << i
        assert math.isclose(m.bel(singleton), m.pl(singleton), abs_tol=1e-9)


# ---- Frame strategy sanity ----------------------------------------


@given(f=frames())
def test_frame_strategy_produces_valid_frames(f) -> None:  # type: ignore[no-untyped-def]
    assert len(f) >= 2
    assert f.size == 1 << len(f)
    assert len(set(f.elements)) == len(f)


# ---- Serialisation round-trip ------------------------------------


@given(m=mass_functions(frame_size=3))
@settings(max_examples=50)
def test_json_round_trip(m: MassFunction) -> None:
    recovered = MassFunction.from_json(m.to_json())
    assert recovered.is_close_to(m, atol=1e-6)
