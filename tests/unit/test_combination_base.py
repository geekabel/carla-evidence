"""Unit tests for the :mod:`combination.base` ABC and dispatch helpers."""

from __future__ import annotations

import pytest

from carla_evidence import Frame, FrameMismatchError, MassFunction
from carla_evidence.combination import dempster, mean, pcr6
from carla_evidence.combination.base import (
    CombinationRule,
    check_all_same_frame,
    check_same_frame,
)


@pytest.fixture
def theta() -> Frame:
    return Frame.of("a", "b")


@pytest.fixture
def m_vacuous(theta: Frame) -> MassFunction:
    return MassFunction.vacuous(theta)


class TestCheckSameFrame:
    def test_same_frame_passes(self, m_vacuous: MassFunction) -> None:
        check_same_frame(m_vacuous, m_vacuous)  # no raise

    def test_mismatch_raises(self) -> None:
        m1 = MassFunction.vacuous(Frame.of("a", "b"))
        m2 = MassFunction.vacuous(Frame.of("x", "y"))
        with pytest.raises(FrameMismatchError, match="Frame mismatch"):
            check_same_frame(m1, m2)


class TestCheckAllSameFrame:
    def test_empty_list_passes(self) -> None:
        check_all_same_frame([])  # no raise

    def test_single_passes(self, m_vacuous: MassFunction) -> None:
        check_all_same_frame([m_vacuous])

    def test_all_same_passes(self, m_vacuous: MassFunction) -> None:
        check_all_same_frame([m_vacuous, m_vacuous, m_vacuous])

    def test_mismatch_raises(self) -> None:
        m1 = MassFunction.vacuous(Frame.of("a", "b"))
        m3 = MassFunction.vacuous(Frame.of("x", "y"))
        with pytest.raises(FrameMismatchError, match=r"masses\[1\]"):
            check_all_same_frame([m1, m3])


class TestDispatchEdgeCases:
    """Cover the exotic dispatch paths in ``CombinationRule.__call__``."""

    def test_zero_args(self) -> None:
        # Variadic empty -> combine_many([]) -> ValueError
        with pytest.raises(ValueError, match="at least one"):
            dempster()

    def test_iterable_form_with_singleton(self, m_vacuous: MassFunction) -> None:
        # rule([m]) returns m directly via combine_many's len==1 branch
        assert mean([m_vacuous]) is m_vacuous

    def test_variadic_with_iterable(self, m_vacuous: MassFunction) -> None:
        # rule(m1, [m2, m3]) — flattens via the variadic else-branch
        a = mean(m_vacuous, [m_vacuous, m_vacuous])
        b = mean.combine_many([m_vacuous, m_vacuous, m_vacuous])
        assert a.is_close_to(b)

    def test_repr(self) -> None:
        assert "dempster" in repr(dempster)

    def test_pcr6_combine_many_empty(self) -> None:
        with pytest.raises(ValueError):
            pcr6.combine_many([])


class TestAbstractness:
    def test_cannot_instantiate_abstract_directly(self) -> None:
        with pytest.raises(TypeError):
            CombinationRule()  # type: ignore[abstract]
