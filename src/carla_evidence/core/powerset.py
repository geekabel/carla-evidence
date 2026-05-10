"""Powerset enumeration helpers.

These helpers complement :mod:`carla_evidence.core.encoding` by exposing
named-subset views of the powerset on top of the bitmask representation.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from carla_evidence.core.frame import Frame


def iter_powerset_masks(frame: Frame) -> Iterator[int]:
    """Yield every bitmask in ``range(2 ** len(frame))``.

    Order matches the natural bitmask order: ``0, 1, 2, ..., 2 ** n - 1``,
    so the empty set is first and Theta is last.
    """
    return iter(range(frame.size))


def iter_powerset(frame: Frame) -> Iterator[tuple[str, ...]]:
    """Yield every subset of ``frame`` as a tuple of element names."""
    for mask in iter_powerset_masks(frame):
        yield frame.from_bitmask(mask)


def iter_focal_pairs(frame: Frame) -> Iterator[tuple[int, tuple[str, ...]]]:
    """Yield ``(bitmask, name_tuple)`` pairs for every subset of ``frame``."""
    for mask in iter_powerset_masks(frame):
        yield (mask, frame.from_bitmask(mask))
