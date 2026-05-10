"""Numerical regression tests against the canonical literature.

Each test reproduces a worked example whose Bel / Pl / Q have been computed by
hand and cross-checked against the cited reference. These guard against silent
numerical drift across versions.
"""

from __future__ import annotations

import numpy as np
import pytest
from tests.fixtures.canonical_bbas import (
    shafer_three_element_example,
    smets_open_world_example,
)

from carla_evidence import Frame, MassFunction


class TestShaferThreeElementExample:
    """Three-element BBA; structure follows Shafer (1976) §2 worked examples.

    Frame: Theta = {a, b, c}; m({a}) = 0.6, m({a, b}) = 0.3, m(Theta) = 0.1.
    """

    @pytest.fixture
    def m(self) -> MassFunction:
        return shafer_three_element_example()

    def test_bel_dense_vector(self, m: MassFunction) -> None:
        # bitmask:    0    1    2    3    4    5    6    7
        # subset:     {}   {a}  {b}  {ab} {c}  {ac} {bc} Th
        expected = np.array([0.0, 0.6, 0.0, 0.9, 0.0, 0.6, 0.0, 1.0])
        np.testing.assert_allclose(m.to_bel_vector(), expected, atol=1e-12)

    def test_pl_dense_vector(self, m: MassFunction) -> None:
        expected = np.array([0.0, 1.0, 0.4, 1.0, 0.1, 1.0, 0.4, 1.0])
        np.testing.assert_allclose(m.to_pl_vector(), expected, atol=1e-12)

    def test_q_dense_vector(self, m: MassFunction) -> None:
        expected = np.array([1.0, 1.0, 0.4, 0.4, 0.1, 0.1, 0.1, 0.1])
        np.testing.assert_allclose(m.to_q_vector(), expected, atol=1e-12)

    def test_bel_is_total_mass_at_theta(self, m: MassFunction) -> None:
        assert m.bel(m.frame.omega) == pytest.approx(1.0)


class TestSmetsOpenWorldExample:
    """TBM-mode BBA with non-zero ``m(empty-set)`` (Smets 1990).

    Frame: Theta = {a, b}; m(empty-set) = 0.2, m({a}) = 0.5, m(Theta) = 0.3.
    Bel and Pl exclude the conflict mass; Bel(Theta) = 0.8 = 1 - m(empty-set).
    """

    @pytest.fixture
    def m(self) -> MassFunction:
        return smets_open_world_example()

    def test_bel_at_theta_equals_one_minus_m_empty(self, m: MassFunction) -> None:
        assert m.bel(m.frame.omega) == pytest.approx(1.0 - m.mass(0))

    def test_bel_singletons(self, m: MassFunction) -> None:
        # Bel({a}) = m({a}) = 0.5; Bel({b}) = 0
        assert m.bel(("a",)) == pytest.approx(0.5)
        assert m.bel(("b",)) == pytest.approx(0.0)

    def test_pl_singletons(self, m: MassFunction) -> None:
        # Pl({a}) = m({a}) + m(Theta) = 0.8
        # Pl({b}) = m(Theta) = 0.3
        assert m.pl(("a",)) == pytest.approx(0.8)
        assert m.pl(("b",)) == pytest.approx(0.3)


class TestVacuousBBA:
    """Vacuous BBA invariants (Shafer 1976 §2)."""

    def test_bel_vector(self) -> None:
        theta = Frame.of("a", "b", "c")
        m = MassFunction.vacuous(theta)
        bel = m.to_bel_vector()
        # Bel(A) = 0 for every A != Theta; Bel(Theta) = 1.
        expected = np.zeros(theta.size)
        expected[theta.full_mask] = 1.0
        np.testing.assert_allclose(bel, expected)

    def test_pl_vector(self) -> None:
        theta = Frame.of("a", "b", "c")
        m = MassFunction.vacuous(theta)
        pl = m.to_pl_vector()
        # Pl(A) = 1 for every A != empty-set; Pl(empty-set) = 0.
        expected = np.ones(theta.size)
        expected[0] = 0.0
        np.testing.assert_allclose(pl, expected)


class TestBayesianBBA:
    """Bayesian BBA collapses to ordinary probability (Shafer 1976 §2.5)."""

    def test_bel_equals_probability_on_singletons(self) -> None:
        theta = Frame.of("a", "b", "c")
        probs = [0.2, 0.3, 0.5]
        m = MassFunction.bayesian(theta, probs)
        for i, p in enumerate(probs):
            assert m.bel(1 << i) == pytest.approx(p)

    def test_pl_equals_bel_for_bayesian(self) -> None:
        theta = Frame.of("a", "b", "c")
        m = MassFunction.bayesian(theta, [0.2, 0.3, 0.5])
        for A in range(theta.size):
            assert m.pl(A) == pytest.approx(m.bel(A))
