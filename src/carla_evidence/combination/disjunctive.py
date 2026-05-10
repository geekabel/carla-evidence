"""Disjunctive rule of combination (Dubois-Prade 1986).

.. math::

    m_{\\cup}(A) = \\sum_{B \\cup C = A} m_1(B) \\, m_2(C).

The disjunctive rule never produces conflict mass (``B \\cup C \\neq \\emptyset``
whenever either operand is non-empty), so the result is always a Shafer BBA.
Operationally it represents the *least committal* fusion: the joint evidence
supports the *union* of the two sources' supports.

References:
    Dubois, D. & Prade, H. (1986). On the combination of uncertain or
    imprecise pieces of information in rule-based systems — A discussion in
    the framework of possibility theory. *International Journal of Approximate
    Reasoning*, 1(3), 173–197.
"""

from __future__ import annotations

from collections.abc import Iterable

from carla_evidence.combination._sparse_kernel import cartesian_combine
from carla_evidence.combination.base import CombinationRule
from carla_evidence.core.mass import MassFunction


def _disjunctive_router(
    B: int, m1_B: float, C: int, m2_C: float, full_mask: int
) -> Iterable[tuple[int, float]]:
    yield (B | C, m1_B * m2_C)


class DisjunctiveRule(CombinationRule):
    """Disjunctive rule. Output is in Shafer mode."""

    name = "disjunctive"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return cartesian_combine(m1, m2, _disjunctive_router, out_mode="shafer")


disjunctive = DisjunctiveRule()

__all__ = ["DisjunctiveRule", "disjunctive"]
