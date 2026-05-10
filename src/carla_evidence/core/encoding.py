"""Bitmask encoding for subsets of a finite frame of discernment.

For a frame :math:`\\Theta = (t_0, \\dots, t_{n-1})` every subset
:math:`A \\subseteq \\Theta` is encoded as a non-negative integer ``mask`` whose
``i``-th bit is set iff :math:`t_i \\in A`::

    mask(empty)         = 0
    mask({t_0})         = 1
    mask({t_0, t_2})    = 5
    mask(Theta)         = (1 << n) - 1

Set operations become bitwise operations:

- :math:`A \\subseteq B` :math:`\\;\\Leftrightarrow\\;` ``(mask_A & mask_B) == mask_A``
- :math:`A \\cap B` :math:`\\;\\leftrightarrow\\;` ``mask_A & mask_B``
- :math:`A \\cup B` :math:`\\;\\leftrightarrow\\;` ``mask_A | mask_B``
- :math:`\\neg A` (within :math:`\\Theta`) :math:`\\;\\leftrightarrow\\;`
  ``mask_A ^ ((1 << n) - 1)``

This module ships *pure-int* helpers; :class:`carla_evidence.core.frame.Frame`
wraps them with element-name translation. Powerset enumeration helpers are in
:mod:`carla_evidence.core.powerset`.
"""

from __future__ import annotations

from collections.abc import Iterator


def full_mask(n: int) -> int:
    """Return the bitmask of the full frame on ``n`` elements (``2 ** n - 1``).

    Args:
        n: Number of elements in the frame.

    Returns:
        ``(1 << n) - 1``.

    Raises:
        ValueError: If ``n`` is negative.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return (1 << n) - 1


def is_subset(a: int, b: int) -> bool:
    """Return ``True`` iff ``A subset-or-equal B`` on bitmasks."""
    return (a & b) == a


def is_proper_subset(a: int, b: int) -> bool:
    """Return ``True`` iff ``A`` is strictly contained in ``B`` on bitmasks."""
    return a != b and (a & b) == a


def intersection(a: int, b: int) -> int:
    """Return ``mask(A intersect B)`` on bitmasks (``a & b``)."""
    return a & b


def union(a: int, b: int) -> int:
    """Return ``mask(A union B)`` on bitmasks (``a | b``)."""
    return a | b


def complement(a: int, n: int) -> int:
    """Return the bitmask of the complement of ``A`` within an ``n``-element frame."""
    return a ^ full_mask(n)


def cardinality(mask: int) -> int:
    """Return ``|A|`` (the number of elements in the encoded subset)."""
    if mask < 0:
        raise ValueError(f"bitmask must be non-negative, got {mask}")
    return mask.bit_count()


def iter_subsets_of(mask: int) -> Iterator[int]:
    """Yield every bitmask ``b`` with ``b subset-or-equal mask``, including 0 and ``mask``.

    Uses the classic ``b = (b - 1) & mask`` enumeration in ``O(2 ** popcount(mask))``.
    """
    if mask < 0:
        raise ValueError(f"bitmask must be non-negative, got {mask}")
    if mask == 0:
        yield 0
        return
    sub = mask
    while True:
        yield sub
        if sub == 0:
            break
        sub = (sub - 1) & mask
