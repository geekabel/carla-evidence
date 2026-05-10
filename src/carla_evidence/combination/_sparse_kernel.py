"""Factored sparse kernel shared by every cartesian-product combination rule.

Every rule in the conjunctive family (conjunctive, Dempster, disjunctive,
Yager, Dubois-Prade, PCR5) iterates the cartesian product of focal pairs
``(B, m1(B)) x (C, m2(C))`` and routes the product mass ``m1(B) * m2(C)`` to
one or more target subsets. This module exposes that factored loop as
:func:`cartesian_combine`, parametrised by a *conflict router* (a Protocol) and
an optional Dempster-style normalisation.

Complexity is :math:`O(|F_1| \\cdot |F_2|)` where :math:`|F_i|` is the number
of focal elements of :math:`m_i` — well below the dense :math:`O(2^{|\\Theta|}
\\cdot 2^{|\\Theta|})` reference loop in :mod:`tests._references`.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from carla_evidence.combination.base import check_same_frame
from carla_evidence.core.exceptions import TotalConflictError
from carla_evidence.core.mass import DEFAULT_TOL, MassFunction, Mode


class ConflictRouter(Protocol):
    """Where the focal-pair product ``(B, m1(B)) x (C, m2(C))`` should land.

    Implementations yield ``(target_mask, mass_to_add)`` pairs. Most rules
    yield exactly one tuple per call; PCR5 yields up to two when the pair is
    in conflict (``B & C == 0``) and the product is split between ``B`` and
    ``C`` proportionally.
    """

    def __call__(
        self,
        B: int,
        m1_B: float,
        C: int,
        m2_C: float,
        full_mask: int,
    ) -> Iterable[tuple[int, float]]: ...


def cartesian_combine(
    m1: MassFunction,
    m2: MassFunction,
    router: ConflictRouter,
    *,
    out_mode: Mode = "shafer",
    normalize: bool = False,
    tol: float = DEFAULT_TOL,
) -> MassFunction:
    """Combine two BBAs via cartesian product over focals with custom routing.

    Args:
        m1: First mass function.
        m2: Second mass function. Must share the frame of ``m1``.
        router: A :class:`ConflictRouter` deciding how the product mass of
            each focal pair is distributed.
        out_mode: Mode of the output BBA. ``"shafer"`` enforces
            ``m(empty-set) = 0``; ``"tbm"`` allows it (e.g. raw conjunctive).
        normalize: If True, apply Dempster's normalisation: divide every
            focal mass by ``1 - K`` where ``K = m_intersected(empty-set)``.
            Raises :class:`TotalConflictError` if ``K >= 1 - tol``.
        tol: Numerical tolerance forwarded to :class:`MassFunction`.

    Returns:
        A new :class:`MassFunction` on the shared frame.

    Raises:
        FrameMismatchError: If the frames differ.
        TotalConflictError: If ``normalize=True`` and the conflict is total.
    """
    check_same_frame(m1, m2)
    full_mask = m1.frame.full_mask
    accumulated: dict[int, float] = {}
    for B, m1B in m1.focals:
        for C, m2C in m2.focals:
            for target, contribution in router(B, m1B, C, m2C, full_mask):
                if contribution == 0.0:
                    continue
                accumulated[target] = accumulated.get(target, 0.0) + contribution

    if normalize:
        K = accumulated.pop(0, 0.0)
        if 1.0 - tol <= K:
            raise TotalConflictError(
                f"Total conflict: K = {K} (within tol {tol} of 1). Dempster's rule "
                "is undefined when the two sources fully disagree. Consider Yager, "
                "Dubois-Prade, or PCR5/PCR6 instead."
            )
        scale = 1.0 / (1.0 - K)
        accumulated = {mask: mass * scale for mask, mass in accumulated.items()}

    return MassFunction(m1.frame, accumulated, mode=out_mode, tol=tol)


__all__ = ["ConflictRouter", "cartesian_combine"]
