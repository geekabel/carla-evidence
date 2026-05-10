"""Dempster's rule of combination (Shafer 1976).

The conjunctive product is normalised by ``1/(1 - K)`` where ``K`` is the
conflict mass:

.. math::

    m_{1 \\oplus 2}(A) = \\frac{1}{1 - K} \\sum_{B \\cap C = A} m_1(B) \\, m_2(C),
    \\qquad m_{1 \\oplus 2}(\\emptyset) = 0,
    \\qquad K = \\sum_{B \\cap C = \\emptyset} m_1(B) \\, m_2(C).

When ``K = 1`` the rule is undefined; this implementation raises
:class:`carla_evidence.core.exceptions.TotalConflictError` rather than silently
returning NaN (``CLAUDE.md`` §"Domain knowledge — pièges critiques", point 2).

References:
    Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton UP, §3.1.
"""

from __future__ import annotations

from carla_evidence.combination._sparse_kernel import cartesian_combine
from carla_evidence.combination.base import CombinationRule
from carla_evidence.combination.conjunctive import _conjunctive_router
from carla_evidence.core.mass import MassFunction


class DempsterRule(CombinationRule):
    """Dempster's normalised rule of combination.

    The output is in Shafer mode (``m(empty-set) = 0``).

    Raises:
        TotalConflictError: When ``K = 1`` (combination undefined).
    """

    name = "dempster"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return cartesian_combine(m1, m2, _conjunctive_router, out_mode="shafer", normalize=True)


dempster = DempsterRule()
"""Module-level callable: ``dempster(m1, m2)`` returns a Shafer-mode BBA."""

__all__ = ["DempsterRule", "dempster"]
