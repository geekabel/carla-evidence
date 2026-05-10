"""PCR5 — Proportional Conflict Redistribution rule no. 5 (Smarandache-Dezert 2005).

For each focal pair ``(B, C)`` with ``B \\cap C = \\emptyset`` and ``m_1(B), m_2(C) > 0``,
the conflicting mass ``m_1(B) m_2(C)`` is redistributed to ``B`` and ``C``
proportionally to the sources' own commitments:

.. math::

    \\Delta m(B) = \\frac{m_1(B)^2 \\, m_2(C)}{m_1(B) + m_2(C)},
    \\qquad
    \\Delta m(C) = \\frac{m_2(C)^2 \\, m_1(B)}{m_1(B) + m_2(C)}.

PCR5 is **only defined for two sources**. Iterating it over three or more
sources via ``combine_many`` is a methodological error (``CLAUDE.md``
§"Domain knowledge — pièges critiques", point 3) — :meth:`PCR5Rule.combine_many`
raises :class:`NotImplementedError` for ``len(masses) > 2`` and points users
to :mod:`carla_evidence.combination.pcr6`.

References:
    Smarandache, F. & Dezert, J. (2005). *Information Fusion Based on New
    Proportional Conflict Redistribution Rules*. In *Proc. 8th Int'l Conf. on
    Information Fusion*, Philadelphia.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from carla_evidence.combination._sparse_kernel import cartesian_combine
from carla_evidence.combination.base import CombinationRule
from carla_evidence.core.mass import MassFunction


def _pcr5_router(
    B: int, m1_B: float, C: int, m2_C: float, full_mask: int
) -> Iterable[tuple[int, float]]:
    intersection = B & C
    if intersection != 0:
        yield (intersection, m1_B * m2_C)
        return
    denom = m1_B + m2_C
    if denom == 0.0:  # pragma: no cover  (impossible — focals carry positive mass)
        return
    # Redistribute the conflict m1(B)*m2(C) proportionally to m1(B) and m2(C).
    yield (B, m1_B * m1_B * m2_C / denom)
    yield (C, m1_B * m2_C * m2_C / denom)


class PCR5Rule(CombinationRule):
    """PCR5. Output is in Shafer mode. Defined for two sources only.

    Use :class:`carla_evidence.combination.pcr6.PCR6Rule` for three or more
    sources.
    """

    name = "pcr5"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return cartesian_combine(m1, m2, _pcr5_router, out_mode="shafer")

    def combine_many(self, masses: Sequence[MassFunction]) -> MassFunction:
        ms = list(masses)
        if len(ms) > 2:
            raise NotImplementedError(
                "PCR5 is only defined for two sources. Iterating it over 3+ sources "
                "via associativity is a methodological error (PCR5 is not associative). "
                "For multi-source fusion, use carla_evidence.combination.pcr6."
            )
        return super().combine_many(ms)


pcr5 = PCR5Rule()

__all__ = ["PCR5Rule", "pcr5"]
