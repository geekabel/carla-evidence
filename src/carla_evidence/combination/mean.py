"""Mean rule of combination (Murphy 2000).

The arithmetic mean of N BBAs:

.. math::

    m_{\\overline{}}(A) = \\frac{1}{N} \\sum_{i=1}^N m_i(A) \\quad \\forall A.

The mean is mathematically a valid BBA whenever the inputs are. It does **not**
sharpen the support — averaging two highly conflicting Bayesian BBAs simply
returns their midpoint — but it is robust to total conflict (no division by
``1 - K``) and is sometimes used as a sanity baseline against which
Dempster-style rules are compared.

The mean is **commutative and associative across N sources** but iterating
the binary form does not give the same result as the N-ary mean (binary mean
of A and the binary mean of A and B re-weights A). Use
:meth:`MeanRule.combine_many` for multi-source averaging.

References:
    Murphy, C. K. (2000). Combining belief functions when evidence conflicts.
    *Decision Support Systems*, 29(1), 1–9.
"""

from __future__ import annotations

from collections.abc import Sequence

from carla_evidence.combination.base import CombinationRule, check_all_same_frame
from carla_evidence.core.mass import MassFunction, Mode


class MeanRule(CombinationRule):
    """Arithmetic mean of N BBAs."""

    name = "mean"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        return self.combine_many([m1, m2])

    def combine_many(self, masses: Sequence[MassFunction]) -> MassFunction:
        ms = list(masses)
        if not ms:
            raise ValueError("mean.combine_many requires at least one MassFunction")
        if len(ms) == 1:
            return ms[0]
        check_all_same_frame(ms)
        # Output mode follows the inputs: TBM if any allows m(empty-set), else Shafer.
        out_mode: Mode = "tbm" if any(m.mode == "tbm" for m in ms) else "shafer"
        n = len(ms)
        accumulated: dict[int, float] = {}
        for m in ms:
            for mask, mass in m.focals:
                accumulated[mask] = accumulated.get(mask, 0.0) + mass / n
        return MassFunction(ms[0].frame, accumulated, mode=out_mode)


mean = MeanRule()

__all__ = ["MeanRule", "mean"]
