"""Conjunctive rule of combination (Smets 1990).

The unnormalised conjunctive rule combines two BBAs via the cartesian product:

.. math::

    m_{\\cap}(A) = \\sum_{B \\cap C = A} m_1(B) \\, m_2(C).

The conflict mass :math:`K = m_{\\cap}(\\emptyset)` is *retained* on the empty
set, so the result is naturally a TBM mass function. Use :mod:`dempster` to
normalise it back into a Shafer BBA, or :mod:`yager` / :mod:`dubois_prade` /
:mod:`pcr5` to redirect the conflict elsewhere.

References:
    Smets, P. (1990). The combination of evidence in the Transferable Belief
    Model. *IEEE TPAMI*, 12(5), 447–458, §3.
"""

from __future__ import annotations

from collections.abc import Iterable

from carla_evidence.combination._sparse_kernel import cartesian_combine
from carla_evidence.combination.base import CombinationRule
from carla_evidence.core.mass import MassFunction


def _conjunctive_router(
    B: int, m1_B: float, C: int, m2_C: float, full_mask: int
) -> Iterable[tuple[int, float]]:
    yield (B & C, m1_B * m2_C)


class ConjunctiveRule(CombinationRule):
    """Smets's unnormalised conjunctive rule.

    The output is in TBM mode (``m(empty-set) >= 0``).
    """

    name = "conjunctive"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return cartesian_combine(m1, m2, _conjunctive_router, out_mode="tbm")


conjunctive = ConjunctiveRule()
"""Module-level callable: ``conjunctive(m1, m2)`` returns a TBM-mode BBA."""

__all__ = ["ConjunctiveRule", "conjunctive"]
