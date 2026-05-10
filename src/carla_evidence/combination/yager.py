"""Yager's rule of combination (Yager 1987).

The conjunctive product is computed; conflict mass that would land on
:math:`\\emptyset` is redirected to :math:`\\Theta` (total ignorance) instead
of being normalised away:

.. math::

    m_Y(A) =
    \\begin{cases}
        \\sum_{B \\cap C = A} m_1(B) m_2(C)
            & \\text{if } A \\neq \\emptyset, A \\neq \\Theta, \\\\
        m_{\\cap}(\\Theta) + K
            & \\text{if } A = \\Theta, \\\\
        0
            & \\text{if } A = \\emptyset,
    \\end{cases}

with :math:`K = \\sum_{B \\cap C = \\emptyset} m_1(B) m_2(C)`.

This makes Yager well-defined even at ``K = 1`` (everything collapses on
:math:`\\Theta`) and avoids the counter-intuitive normalisation of Dempster
in the Zadeh paradox (Zadeh 1986).

References:
    Yager, R. R. (1987). On the Dempster-Shafer framework and new combination
    rules. *Information Sciences*, 41(2), 93–137.
"""

from __future__ import annotations

from collections.abc import Iterable

from carla_evidence.combination._sparse_kernel import cartesian_combine
from carla_evidence.combination.base import CombinationRule
from carla_evidence.core.mass import MassFunction


def _yager_router(
    B: int, m1_B: float, C: int, m2_C: float, full_mask: int
) -> Iterable[tuple[int, float]]:
    intersection = B & C
    if intersection != 0:
        yield (intersection, m1_B * m2_C)
    else:
        # conflict mass redirected to Theta
        yield (full_mask, m1_B * m2_C)


class YagerRule(CombinationRule):
    """Yager's rule. Output is in Shafer mode."""

    name = "yager"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return cartesian_combine(m1, m2, _yager_router, out_mode="shafer")


yager = YagerRule()

__all__ = ["YagerRule", "yager"]
