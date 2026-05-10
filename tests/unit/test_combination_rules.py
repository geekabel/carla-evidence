"""Unit tests for the eight combination rules shipped in v0.2.0.

Each ``Test<Rule>`` class verifies the rule-specific behaviour (output mode,
conflict routing, error handling). Shared invariants — commutativity,
neutral element, sparse-vs-dense equivalence — live in
:mod:`tests.property.test_combination_props`.
"""

from __future__ import annotations

import pytest

from carla_evidence import (
    Frame,
    FrameMismatchError,
    MassFunction,
    TotalConflictError,
)
from carla_evidence.combination import (
    conjunctive,
    dempster,
    disjunctive,
    dubois_prade,
    mean,
    pcr5,
    pcr6,
    yager,
)


@pytest.fixture
def theta() -> Frame:
    return Frame.of("a", "b", "c")


@pytest.fixture
def m1(theta: Frame) -> MassFunction:
    """Common BBA #1: m({a}) = 0.6, m({a,b}) = 0.3, m(Θ) = 0.1."""
    return MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})


@pytest.fixture
def m2(theta: Frame) -> MassFunction:
    """Common BBA #2: m({a}) = 0.5, m({b,c}) = 0.4, m(Θ) = 0.1."""
    return MassFunction(theta, {("a",): 0.5, ("b", "c"): 0.4, theta.omega: 0.1})


# ---------------------------------------------------------------------------
# Conjunctive
# ---------------------------------------------------------------------------


class TestConjunctive:
    def test_output_is_tbm(self, m1: MassFunction, m2: MassFunction) -> None:
        assert conjunctive(m1, m2).mode == "tbm"

    def test_conflict_mass_is_retained(self, m1: MassFunction, m2: MassFunction) -> None:
        # K = m({a})*m({b,c}) = 0.6 * 0.4 = 0.24 (only conflicting pair)
        assert conjunctive(m1, m2).mass(0) == pytest.approx(0.24)

    def test_frame_mismatch_raises(self) -> None:
        m_a = MassFunction.vacuous(Frame.of("a", "b"))
        m_b = MassFunction.vacuous(Frame.of("x", "y"))
        with pytest.raises(FrameMismatchError):
            conjunctive(m_a, m_b)


# ---------------------------------------------------------------------------
# Dempster
# ---------------------------------------------------------------------------


class TestDempster:
    def test_output_is_shafer(self, m1: MassFunction, m2: MassFunction) -> None:
        assert dempster(m1, m2).mode == "shafer"
        assert dempster(m1, m2).mass(0) == 0.0

    def test_normalization(self, m1: MassFunction, m2: MassFunction) -> None:
        # Dempster = conjunctive / (1 - K). Conjunctive m({a}) = 0.56, K = 0.24.
        # Dempster m({a}) = 0.56 / 0.76 ≈ 0.7368
        assert dempster(m1, m2).mass(("a",)) == pytest.approx(0.56 / 0.76)

    def test_total_conflict_raises(self, theta: Frame) -> None:
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        with pytest.raises(TotalConflictError, match="Total conflict"):
            dempster(m_a, m_b)


# ---------------------------------------------------------------------------
# Disjunctive
# ---------------------------------------------------------------------------


class TestDisjunctive:
    def test_no_empty_mass(self, m1: MassFunction, m2: MassFunction) -> None:
        # B ∪ C = ∅ requires both B and C empty; Shafer-mode inputs have no ∅ focals.
        assert disjunctive(m1, m2).mass(0) == 0.0

    def test_categorical_disjunction(self, theta: Frame) -> None:
        # Categorical {a} ∪ Categorical {b} = {a, b}
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        out = disjunctive(m_a, m_b)
        assert out.mass(("a", "b")) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Yager
# ---------------------------------------------------------------------------


class TestYager:
    def test_conflict_lands_on_theta(self, theta: Frame) -> None:
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        out = yager(m_a, m_b)
        assert out.mass(theta.omega) == pytest.approx(1.0)

    def test_total_conflict_does_not_raise(self, theta: Frame) -> None:
        # Unlike Dempster, Yager handles K = 1 gracefully (everything → Θ).
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        yager(m_a, m_b)  # no exception


# ---------------------------------------------------------------------------
# Dubois-Prade
# ---------------------------------------------------------------------------


class TestDuboisPrade:
    def test_conflict_lands_on_union(self, theta: Frame) -> None:
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        # {a} ∩ {b} = ∅ → redirect to {a, b}
        out = dubois_prade(m_a, m_b)
        assert out.mass(("a", "b")) == pytest.approx(1.0)

    def test_differs_from_yager_when_union_neq_theta(self, theta: Frame) -> None:
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        out_y = yager(m_a, m_b)
        out_dp = dubois_prade(m_a, m_b)
        # Yager dumps to Θ = {a,b,c}; Dubois-Prade keeps to {a,b}.
        assert out_y.mass(theta.omega) == pytest.approx(1.0)
        assert out_dp.mass(("a", "b")) == pytest.approx(1.0)
        assert out_dp.mass(theta.omega) == 0.0


# ---------------------------------------------------------------------------
# PCR5
# ---------------------------------------------------------------------------


class TestPCR5:
    def test_proportional_redistribution(self, theta: Frame) -> None:
        # m1({a}) = 0.6, m2({b,c}) = 0.4, conflict = 0.24.
        # Redistribute proportionally: Δ{a} = 0.6²·0.4/(1.0) = 0.144,
        # Δ{b,c} = 0.6·0.4²/(1.0) = 0.096. Sum back = 0.24 ✓.
        m_a = MassFunction.categorical(theta, ("a",))
        m_bc = MassFunction.categorical(theta, ("b", "c"))
        out = pcr5(m_a, m_bc)
        # All conflict goes back to {a} (with weight 0.5) and {b,c} (weight 0.5).
        assert out.mass(("a",)) == pytest.approx(0.5)
        assert out.mass(("b", "c")) == pytest.approx(0.5)

    def test_three_sources_raises(self, theta: Frame, m1: MassFunction, m2: MassFunction) -> None:
        m3 = MassFunction.vacuous(theta)
        with pytest.raises(NotImplementedError, match="PCR5"):
            pcr5([m1, m2, m3])

    def test_no_conflict_equals_conjunctive(self, theta: Frame) -> None:
        m_a = MassFunction(theta, {("a",): 0.5, theta.omega: 0.5})
        m_b = MassFunction(theta, {("a", "b"): 0.5, theta.omega: 0.5})
        # No focal pair is in conflict (all intersect on {a} or include Θ),
        # so PCR5 == Dempster (which = conjunctive when K=0).
        assert pcr5(m_a, m_b).is_close_to(dempster(m_a, m_b))


# ---------------------------------------------------------------------------
# PCR6
# ---------------------------------------------------------------------------


class TestPCR6:
    def test_two_source_equals_pcr5(self, m1: MassFunction, m2: MassFunction) -> None:
        # Martin-Osswald 2006 §III: PCR6 reduces to PCR5 for N=2.
        assert pcr6(m1, m2).is_close_to(pcr5(m1, m2))

    def test_three_source_redistribution(self, theta: Frame) -> None:
        # Three categorical singletons in conflict: {a}, {b}, {c}.
        # PCR6 redistributes 1.0 onto each proportionally to mass = 1/3 each.
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        m_c = MassFunction.categorical(theta, ("c",))
        out = pcr6([m_a, m_b, m_c])
        assert out.mass(("a",)) == pytest.approx(1.0 / 3)
        assert out.mass(("b",)) == pytest.approx(1.0 / 3)
        assert out.mass(("c",)) == pytest.approx(1.0 / 3)

    def test_combine_many_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            pcr6([])

    def test_combine_many_singleton_returns_input(self, m1: MassFunction) -> None:
        assert pcr6([m1]) is m1


# ---------------------------------------------------------------------------
# Mean
# ---------------------------------------------------------------------------


class TestMean:
    def test_two_source(self, theta: Frame) -> None:
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        out = mean(m_a, m_b)
        assert out.mass(("a",)) == pytest.approx(0.5)
        assert out.mass(("b",)) == pytest.approx(0.5)

    def test_three_source(self, theta: Frame) -> None:
        m_a = MassFunction.categorical(theta, ("a",))
        m_b = MassFunction.categorical(theta, ("b",))
        m_c = MassFunction.categorical(theta, ("c",))
        out = mean([m_a, m_b, m_c])
        for x in ("a", "b", "c"):
            assert out.mass((x,)) == pytest.approx(1.0 / 3)

    def test_tbm_input_yields_tbm_output(self, theta: Frame) -> None:
        m_a = MassFunction.vacuous(theta)
        m_tbm = MassFunction(theta, {(): 0.5, theta.omega: 0.5}, mode="tbm")
        assert mean(m_a, m_tbm).mode == "tbm"


# ---------------------------------------------------------------------------
# Dispatch ergonomics on the callable instances
# ---------------------------------------------------------------------------


class TestCallableDispatch:
    def test_binary_form(self, m1: MassFunction, m2: MassFunction) -> None:
        a = dempster(m1, m2)
        b = dempster.combine(m1, m2)
        assert a.is_close_to(b)

    def test_iterable_form(self, theta: Frame) -> None:
        m_a = MassFunction(theta, {("a",): 0.4, theta.omega: 0.6})
        m_b = MassFunction(theta, {("b",): 0.4, theta.omega: 0.6})
        m_c = MassFunction(theta, {("c",): 0.4, theta.omega: 0.6})
        a = pcr6([m_a, m_b, m_c])
        b = pcr6.combine_many([m_a, m_b, m_c])
        assert a.is_close_to(b)

    def test_variadic_form(self, theta: Frame) -> None:
        m_a = MassFunction(theta, {("a",): 0.4, theta.omega: 0.6})
        m_b = MassFunction(theta, {("b",): 0.4, theta.omega: 0.6})
        m_c = MassFunction(theta, {("c",): 0.4, theta.omega: 0.6})
        a = mean(m_a, m_b, m_c)
        b = mean.combine_many([m_a, m_b, m_c])
        assert a.is_close_to(b)

    def test_singleton_returns_input(self, m1: MassFunction) -> None:
        assert dempster([m1]) is m1
