"""Unit tests for :class:`carla_evidence.core.mass.MassFunction`."""

from __future__ import annotations

import math

import numpy as np
import pytest

from carla_evidence import (
    Frame,
    FrameError,
    InvalidMassError,
    MassFunction,
    ModeError,
)


@pytest.fixture
def theta() -> Frame:
    return Frame.of("a", "b", "c")


# ---- construction ------------------------------------------------------


class TestConstruction:
    def test_dict_form(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        assert m.mass(("a",)) == pytest.approx(0.6)
        assert m.mass(("a", "b")) == pytest.approx(0.3)
        assert m.mass(theta.omega) == pytest.approx(0.1)

    def test_iterable_form(self, theta: Frame) -> None:
        m = MassFunction(
            theta,
            [(("a",), 0.6), (("a", "b"), 0.3), (theta.omega, 0.1)],
        )
        assert m.mass(("a",)) == pytest.approx(0.6)

    def test_bitmask_keys(self, theta: Frame) -> None:
        m = MassFunction(theta, {1: 0.6, 3: 0.3, 7: 0.1})
        assert m.mass(("a",)) == pytest.approx(0.6)

    def test_frozenset_keys(self, theta: Frame) -> None:
        m = MassFunction(
            theta,
            {frozenset({"a"}): 0.6, frozenset({"a", "b"}): 0.3, frozenset({"a", "b", "c"}): 0.1},
        )
        assert m.mass(("a",)) == pytest.approx(0.6)

    def test_zero_mass_dropped(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("b",): 0.0, theta.omega: 0.4})
        assert ("b",) not in m.to_dict()
        assert len(m) == 2

    def test_repeated_subset_accumulated(self, theta: Frame) -> None:
        m = MassFunction(theta, [(("a",), 0.3), (("a",), 0.3), (theta.omega, 0.4)])
        assert m.mass(("a",)) == pytest.approx(0.6)

    def test_focals_canonical_sorted(self, theta: Frame) -> None:
        m = MassFunction(theta, {theta.omega: 0.1, ("a", "b"): 0.3, ("a",): 0.6})
        # Sorted by bitmask: 1 ({a}), 3 ({a,b}), 7 (Theta)
        assert [mask for mask, _ in m.focals] == [1, 3, 7]

    def test_immutable(self, theta: Frame) -> None:
        m = MassFunction(theta, {theta.omega: 1.0})
        with pytest.raises((AttributeError, TypeError)):
            m.mode = "tbm"  # type: ignore[misc]

    def test_hashable(self, theta: Frame) -> None:
        m = MassFunction(theta, {theta.omega: 1.0})
        assert {m} == {m}


class TestValidation:
    def test_negative_mass(self, theta: Frame) -> None:
        with pytest.raises(InvalidMassError, match="Negative"):
            MassFunction(theta, {("a",): -0.1, theta.omega: 1.1})

    def test_does_not_sum_to_one(self, theta: Frame) -> None:
        with pytest.raises(InvalidMassError, match="sum to 1"):
            MassFunction(theta, {("a",): 0.4, ("b",): 0.4})

    def test_unknown_element(self, theta: Frame) -> None:
        with pytest.raises(FrameError, match="not in frame"):
            MassFunction(theta, {("z",): 1.0})

    def test_bitmask_out_of_range(self, theta: Frame) -> None:
        with pytest.raises(FrameError, match="out of range"):
            MassFunction(theta, {99: 1.0})

    def test_bool_subset_rejected(self, theta: Frame) -> None:
        with pytest.raises(FrameError, match="bool"):
            MassFunction(theta, {True: 1.0})


class TestModeValidation:
    def test_shafer_rejects_empty_mass(self, theta: Frame) -> None:
        with pytest.raises(ModeError, match="empty-set"):
            MassFunction(theta, {(): 0.2, theta.omega: 0.8})

    def test_tbm_accepts_empty_mass(self, theta: Frame) -> None:
        m = MassFunction(theta, {(): 0.2, theta.omega: 0.8}, mode="tbm")
        assert m.mass(()) == pytest.approx(0.2)
        assert m.is_normal is False

    def test_dsmt_not_implemented(self, theta: Frame) -> None:
        with pytest.raises(NotImplementedError, match="DSmT"):
            MassFunction(theta, {theta.omega: 1.0}, mode="dsmt")

    def test_unknown_mode(self, theta: Frame) -> None:
        with pytest.raises(ModeError, match="Unknown mode"):
            MassFunction(theta, {theta.omega: 1.0}, mode="bogus")  # type: ignore[arg-type]


# ---- alternative constructors -----------------------------------------


class TestAlternativeConstructors:
    def test_vacuous(self, theta: Frame) -> None:
        m = MassFunction.vacuous(theta)
        assert m.is_vacuous
        assert m.mass(theta.omega) == 1.0

    def test_categorical(self, theta: Frame) -> None:
        m = MassFunction.categorical(theta, ("a", "b"))
        assert m.is_categorical
        assert m.mass(("a", "b")) == 1.0

    def test_categorical_shafer_rejects_empty(self, theta: Frame) -> None:
        with pytest.raises(ModeError, match="empty-set"):
            MassFunction.categorical(theta, 0)

    def test_categorical_tbm_accepts_empty(self, theta: Frame) -> None:
        m = MassFunction.categorical(theta, 0, mode="tbm")
        assert m.mass(()) == 1.0

    def test_bayesian(self, theta: Frame) -> None:
        m = MassFunction.bayesian(theta, [0.2, 0.3, 0.5])
        assert m.is_bayesian
        assert m.mass(("a",)) == pytest.approx(0.2)
        assert m.mass(("b",)) == pytest.approx(0.3)
        assert m.mass(("c",)) == pytest.approx(0.5)

    def test_bayesian_wrong_length(self, theta: Frame) -> None:
        with pytest.raises(FrameError, match="probabilities"):
            MassFunction.bayesian(theta, [0.5, 0.5])

    def test_from_array(self, theta: Frame) -> None:
        arr = np.zeros(theta.size)
        arr[1] = 0.6  # {a}
        arr[3] = 0.3  # {a, b}
        arr[7] = 0.1  # Theta
        m = MassFunction.from_array(theta, arr)
        assert m.mass(("a",)) == pytest.approx(0.6)
        assert m.mass(theta.omega) == pytest.approx(0.1)

    def test_from_array_wrong_shape(self, theta: Frame) -> None:
        with pytest.raises(InvalidMassError, match="shape"):
            MassFunction.from_array(theta, np.zeros(4))

    def test_from_dict(self, theta: Frame) -> None:
        m1 = MassFunction.from_dict(theta, {theta.omega: 1.0})
        m2 = MassFunction(theta, {theta.omega: 1.0})
        assert m1.is_close_to(m2)


# ---- bel / pl / q scalar accessors -----------------------------------


class TestBelPlQ:
    def test_bel_singleton(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        assert m.bel(("a",)) == pytest.approx(0.6)

    def test_pl_singleton(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        assert m.pl(("a",)) == pytest.approx(1.0)

    def test_q_singleton(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        assert m.q(("a",)) == pytest.approx(1.0)

    def test_bel_subset(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        assert m.bel(("a", "b")) == pytest.approx(0.9)

    def test_bel_complement(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        assert m.bel(("b", "c")) == pytest.approx(0.0)

    def test_bel_empty_set(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert m.bel(()) == 0.0

    def test_bel_full_frame(self, theta: Frame) -> None:
        # In Shafer mode, Bel(Theta) = 1.
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert m.bel(theta.omega) == pytest.approx(1.0)

    def test_pl_dominates_bel_pointwise(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        for mask in range(theta.size):
            assert m.pl(mask) >= m.bel(mask) - 1e-12

    def test_bitmask_input(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        # bitmask 1 = ("a",)
        assert m.bel(1) == pytest.approx(m.bel(("a",)))

    def test_mass_early_exit_when_query_below_smallest_focal(self, theta: Frame) -> None:
        """Mass scan exits early when the queried mask is below every focal.

        m has a single focal at mask 3 ({a,b}); querying mass(2) ({b}) must
        scan-then-break since focals is sorted ascending.
        """
        m = MassFunction(theta, {("a", "b"): 0.6, theta.omega: 0.4})
        assert m.mass(2) == 0.0  # ({b}) — between focals at 3 and 7

    def test_mass_query_above_all_focals(self, theta: Frame) -> None:
        """Mass scan exhausts the loop when the queried mask is above every focal.

        m has focals at masks 1 and 3 only; querying mass(5) iterates both and
        terminates naturally (no break, no equal hit), returning 0.0.
        """
        m = MassFunction(theta, {("a",): 0.4, ("a", "b"): 0.6})
        assert m.mass(5) == 0.0  # ({a,c})


# ---- vector materialisations -----------------------------------------


class TestDenseMaterialisation:
    def test_to_dense(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        expected = np.array([0.0, 0.6, 0.0, 0.3, 0.0, 0.0, 0.0, 0.1])
        np.testing.assert_allclose(m.to_dense(), expected)

    def test_to_bel_vector_matches_scalar(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        bel_vec = m.to_bel_vector()
        for mask in range(theta.size):
            assert bel_vec[mask] == pytest.approx(m.bel(mask), abs=1e-12)

    def test_to_pl_vector_matches_scalar(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        pl_vec = m.to_pl_vector()
        for mask in range(theta.size):
            assert pl_vec[mask] == pytest.approx(m.pl(mask), abs=1e-12)

    def test_to_q_vector_matches_scalar(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        q_vec = m.to_q_vector()
        for mask in range(theta.size):
            assert q_vec[mask] == pytest.approx(m.q(mask), abs=1e-12)


# ---- introspection ---------------------------------------------------


class TestIntrospection:
    def test_len(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert len(m) == 2

    def test_iter(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        items = list(m)
        assert items == [(("a",), 0.6), (("a", "b", "c"), 0.4)]

    def test_focal_subsets(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert list(m.focal_subsets()) == [("a",), ("a", "b", "c")]

    def test_core(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert m.core == (("a",), ("a", "b", "c"))

    def test_is_normal_shafer_always_true(self, theta: Frame) -> None:
        assert MassFunction.vacuous(theta).is_normal is True

    def test_is_normal_tbm_with_empty(self, theta: Frame) -> None:
        m = MassFunction(theta, {(): 0.2, theta.omega: 0.8}, mode="tbm")
        assert m.is_normal is False

    def test_is_bayesian(self, theta: Frame) -> None:
        assert MassFunction.bayesian(theta, [0.2, 0.3, 0.5]).is_bayesian is True
        assert MassFunction.vacuous(theta).is_bayesian is False

    def test_is_vacuous(self, theta: Frame) -> None:
        assert MassFunction.vacuous(theta).is_vacuous is True
        assert MassFunction.categorical(theta, ("a",)).is_vacuous is False

    def test_is_categorical(self, theta: Frame) -> None:
        assert MassFunction.categorical(theta, ("a", "b")).is_categorical is True
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert m.is_categorical is False


# ---- equality / approximate equality -------------------------------


class TestEquality:
    def test_strict_equality(self, theta: Frame) -> None:
        m1 = MassFunction(theta, {theta.omega: 1.0})
        m2 = MassFunction(theta, {theta.omega: 1.0})
        assert m1 == m2

    def test_different_modes_not_equal(self, theta: Frame) -> None:
        m1 = MassFunction(theta, {theta.omega: 1.0}, mode="shafer")
        m2 = MassFunction(theta, {theta.omega: 1.0}, mode="tbm")
        assert m1 != m2

    def test_is_close_to_equal(self, theta: Frame) -> None:
        m1 = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        m2 = MassFunction(theta, {("a",): 0.6 + 1e-12, theta.omega: 0.4 - 1e-12})
        assert m1.is_close_to(m2)

    def test_is_close_to_different(self, theta: Frame) -> None:
        m1 = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        m2 = MassFunction(theta, {("a",): 0.5, theta.omega: 0.5})
        assert not m1.is_close_to(m2)

    def test_is_close_to_different_frames(self) -> None:
        f1 = Frame.of("a", "b")
        f2 = Frame.of("x", "y")
        m1 = MassFunction.vacuous(f1)
        m2 = MassFunction.vacuous(f2)
        assert not m1.is_close_to(m2)


# ---- serialisation -------------------------------------------------


class TestSerialisation:
    def test_to_dict(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, theta.omega: 0.4})
        assert m.to_dict() == {("a",): 0.6, ("a", "b", "c"): 0.4}

    def test_json_round_trip_shafer(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        recovered = MassFunction.from_json(m.to_json())
        assert recovered.is_close_to(m)
        assert recovered.frame == m.frame
        assert recovered.mode == m.mode

    def test_json_round_trip_tbm(self) -> None:
        theta = Frame.of("a", "b")
        m = MassFunction(theta, {(): 0.2, ("a",): 0.5, theta.omega: 0.3}, mode="tbm")
        recovered = MassFunction.from_json(m.to_json())
        assert recovered.is_close_to(m)
        assert recovered.mode == "tbm"


# ---- repr ---------------------------------------------------------


class TestRepr:
    def test_repr_singleton(self, theta: Frame) -> None:
        m = MassFunction(theta, {("a",): 1.0})
        assert "shafer" in repr(m)
        assert "{a}" in repr(m)

    def test_repr_theta(self, theta: Frame) -> None:
        m = MassFunction.vacuous(theta)
        assert "Theta" in repr(m)

    def test_repr_empty(self) -> None:
        theta = Frame.of("a", "b")
        m = MassFunction(theta, {(): 0.5, theta.omega: 0.5}, mode="tbm")
        assert "{}" in repr(m)


# ---- numerics -----------------------------------------------------


def test_sum_check_uses_fsum_for_stability() -> None:
    """Many tiny masses should still sum to 1 within tolerance via fsum."""
    theta = Frame.of("a", "b", "c", "d", "e")
    n = theta.size - 1  # exclude empty in shafer mode
    masses = {(1 << i): 1.0 / n for i in range(n)} if n <= 5 else None
    # Use individual subset bitmasks 1..n and assign equal mass
    masses = dict.fromkeys(range(1, theta.size), 1.0 / (theta.size - 1))
    m = MassFunction(theta, masses)
    assert math.isclose(sum(mass for _, mass in m.focals), 1.0, abs_tol=1e-9)
