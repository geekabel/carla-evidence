"""PCR6 — N-source Proportional Conflict Redistribution (Martin-Osswald 2006).

PCR6 generalises PCR5 to arbitrarily many sources while remaining stable in
terms of decision (the maximum-belief decision is preserved as new sources
are added). For each tuple of focal elements
:math:`(B_1, \\dots, B_N) \\in \\prod_i \\mathrm{Focal}(m_i)`:

.. math::

    P = \\prod_i m_i(B_i), \\qquad I = \\bigcap_i B_i.

If :math:`I \\neq \\emptyset` the product is committed to ``I`` (conjunctive
behaviour). Otherwise (the tuple is in conflict) the product :math:`P` is
redistributed onto each ``B_j`` weighted by ``m_j(B_j) / S`` where
:math:`S = \\sum_i m_i(B_i)`:

.. math::

    \\Delta m(B_j) \\mathrel{+}= P \\cdot \\frac{m_j(B_j)}{S}.

For two sources, PCR6 reduces to PCR5; the binary :meth:`PCR6Rule.combine`
delegates to :mod:`pcr5` for that exact reason.

References:
    Martin, A. & Osswald, C. (2006). A new generalization of the
    Proportional Conflict Redistribution rule stable in terms of decision —
    PCR6. In *Advances and Applications of DSmT for Information Fusion*, vol. 2.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from itertools import product

from carla_evidence.combination.base import CombinationRule, check_all_same_frame
from carla_evidence.combination.pcr5 import pcr5
from carla_evidence.core.mass import MassFunction


class PCR6Rule(CombinationRule):
    """PCR6. Output is in Shafer mode."""

    name = "pcr6"

    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        # For two sources, PCR6 is identical to PCR5 (Martin-Osswald 2006, §III).
        return pcr5.combine(m1, m2)

    def combine_many(self, masses: Sequence[MassFunction]) -> MassFunction:
        ms = list(masses)
        if not ms:
            raise ValueError("pcr6.combine_many requires at least one MassFunction")
        if len(ms) == 1:
            return ms[0]
        if len(ms) == 2:
            return self.combine(ms[0], ms[1])
        check_all_same_frame(ms)
        accumulated: dict[int, float] = {}
        for tuple_focals in product(*(m.focals for m in ms)):
            masks = [B for B, _ in tuple_focals]
            ms_vals = [v for _, v in tuple_focals]
            intersection = masks[0]
            for b in masks[1:]:
                intersection &= b
            product_mass = math.prod(ms_vals)
            if intersection != 0:
                accumulated[intersection] = accumulated.get(intersection, 0.0) + product_mass
            else:
                total = math.fsum(ms_vals)
                # total > 0 because each focal has positive mass
                for B, m_val in zip(masks, ms_vals, strict=True):
                    accumulated[B] = accumulated.get(B, 0.0) + product_mass * m_val / total
        return MassFunction(ms[0].frame, accumulated, mode="shafer")


pcr6 = PCR6Rule()

__all__ = ["PCR6Rule", "pcr6"]
