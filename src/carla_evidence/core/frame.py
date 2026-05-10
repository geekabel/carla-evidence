"""Frame of discernment Theta: a finite, ordered tuple of distinct hypotheses.

A :class:`Frame` is a frozen, hashable value object. The element order fixes
the bitmask encoding (see :mod:`carla_evidence.core.encoding`):
``Frame(("a", "b", "c"))`` assigns bit 0 to ``"a"``, bit 1 to ``"b"``, bit 2
to ``"c"``.

References:
    Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton UP. §1.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property

from carla_evidence.core.encoding import full_mask
from carla_evidence.core.exceptions import FrameError


@dataclass(frozen=True, init=False)
class Frame:
    """A finite frame of discernment Theta = {t_0, t_1, ..., t_{n-1}}.

    The frame is an *ordered* tuple of distinct strings. The order is
    significant — it fixes the bitmask encoding used by every other component
    of the library.

    Args:
        elements: An iterable of distinct, non-empty strings. The iterable is
            consumed once and stored as a tuple.

    Raises:
        FrameError: If ``elements`` is empty, contains a non-string, contains
            duplicates, or contains an empty string.

    Examples:
        >>> theta = Frame(("car", "truck", "pedestrian"))
        >>> len(theta)
        3
        >>> theta.size
        8
        >>> theta.full_mask
        7
        >>> theta.to_bitmask(("car", "pedestrian"))
        5
        >>> theta.from_bitmask(5)
        ('car', 'pedestrian')
        >>> Frame.of("a", "b", "c") == Frame(("a", "b", "c"))
        True
    """

    elements: tuple[str, ...]

    def __init__(self, elements: Iterable[str]) -> None:
        elems = tuple(elements)
        if not elems:
            raise FrameError("Frame must have at least one element")
        seen: set[str] = set()
        for e in elems:
            if not isinstance(e, str):
                raise FrameError(f"Frame elements must be strings; got {type(e).__name__}: {e!r}")
            if not e:
                raise FrameError("Frame elements must be non-empty strings")
            if e in seen:
                raise FrameError(f"Frame elements must be unique; {e!r} appears twice")
            seen.add(e)
        # frozen dataclass: bypass the immutability for one-time initialisation
        object.__setattr__(self, "elements", elems)

    @classmethod
    def of(cls, *elements: str) -> Frame:
        """Variadic convenience constructor: ``Frame.of('a', 'b', 'c')``."""
        return cls(elements)

    # -- core properties -----------------------------------------------------

    def __len__(self) -> int:
        return len(self.elements)

    @property
    def size(self) -> int:
        """``|2^Theta|`` — the size of the (Shafer) powerset, ``2 ** len(self)``."""
        return 1 << len(self.elements)

    @property
    def full_mask(self) -> int:
        """The bitmask representing :math:`\\Theta` itself (``2 ** n - 1``)."""
        return full_mask(len(self.elements))

    @property
    def omega(self) -> tuple[str, ...]:
        """Theta itself, as a tuple of element names (alias of ``elements``)."""
        return self.elements

    # -- name <-> bitmask translation ----------------------------------------

    @cached_property
    def _index(self) -> dict[str, int]:
        return {el: i for i, el in enumerate(self.elements)}

    def to_bitmask(self, subset: Iterable[str]) -> int:
        """Convert a subset (iterable of element names) to its bitmask.

        Repeated names within ``subset`` are silently deduplicated.

        Raises:
            FrameError: If any element of ``subset`` is not in the frame.
        """
        mask = 0
        for el in subset:
            try:
                bit = self._index[el]
            except KeyError as exc:
                raise FrameError(f"Element {el!r} not in frame {self.elements}") from exc
            mask |= 1 << bit
        return mask

    def from_bitmask(self, mask: int) -> tuple[str, ...]:
        """Convert a bitmask to its tuple of element names (in frame order).

        Raises:
            FrameError: If ``mask`` is negative or out of range for this frame.
        """
        if mask < 0 or mask >= self.size:
            raise FrameError(
                f"bitmask {mask} out of range for frame of size {len(self)} (max {self.size - 1})"
            )
        return tuple(el for i, el in enumerate(self.elements) if mask & (1 << i))

    # -- iteration / membership ---------------------------------------------

    def __iter__(self) -> Iterator[str]:
        return iter(self.elements)

    def __contains__(self, item: object) -> bool:
        return isinstance(item, str) and item in self._index

    def __repr__(self) -> str:
        return f"Frame({self.elements!r})"
