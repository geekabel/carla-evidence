"""Dubois-Prade rule of combination (Dubois-Prade 1988).

Like Yager, the rule keeps the conjunctive product on intersecting focal
pairs, but redirects the conflicting mass on each pair ``B \\cap C = \\emptyset``
to the *union* ``B \\cup C`` rather than to :math:`\\Theta`:

.. math::

    m_{DP}(A) =
    \\sum_{B \\cap C = A,\\, A \\neq \\emptyset} m_1(B) m_2(C)
    + \\sum_{B \\cap C = \\emptyset,\\, B \\cup C = A} m_1(B) m_2(C).

This is more commitment-conserving than Yager when conflict is local: instead
of dumping every conflict on :math:`\\Theta`, it preserves whatever joint
support the two sources actually have.

References:
    Dubois, D. & Prade, H. (1988). Representation and combination of
    uncertainty with belief functions and possibility measures. *Computational
    Intelligence*, 4(3), 244–264.
"""

from __future__ import annotations

from collections.abc import Iterable

from carla_evidence.combination._sparse_kernel import cartesian_combine
from carla_evidence.combination.base import CombinationRule
from carla_evidence.core.mass import MassFunction


def _dubois_prade_router(
    B: int, m1_B: float, C: int, m2_C: float, full_mask: int
) -> Iterable[tuple[int, float]]:
    intersection = B & C
    if intersection != 0:
        yield (intersection, m1_B * m2_C)
    else:
        # conflict mass redirected to the union B ∪ C
        yield (B | C, m1_B * m2_C)


class DuboisPradeRule(CombinationRule):
    """Dubois-Prade rule. Output is in Shafer mode."""

    name = "dubois_prade"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return cartesian_combine(m1, m2, _dubois_prade_router, out_mode="shafer")


dubois_prade = DuboisPradeRule()

__all__ = ["DuboisPradeRule", "dubois_prade"]
