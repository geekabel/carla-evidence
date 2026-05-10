"""Combination-rule abstract base class and N-ary dispatch.

Every rule shipped in this package is a :class:`CombinationRule` subclass that
implements ``combine(m1, m2)``. Multi-source dispatch is provided by
``combine_many``; the default implementation iterates left-to-right, which is
mathematically correct for **associative** rules (Dempster, conjunctive,
disjunctive, mean). Rules that *require* a dedicated multi-source algorithm
override ``combine_many``:

- :class:`PCR5Rule` rejects ``len(ms) > 2`` (iterating PCR5 on 3+ sources is a
  methodological error per ``CLAUDE.md``; use PCR6 instead).
- :class:`PCR6Rule` provides a true N-source redistribution.

Each rule is also exposed as a *callable instance* — ``dempster(m1, m2)`` is
``DempsterRule.__call__``. The dispatcher accepts ``(m1, m2)``, ``(iterable,)``,
or ``(*ms,)`` for ergonomic use at the call site.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import ClassVar

from carla_evidence.core.exceptions import FrameMismatchError
from carla_evidence.core.mass import MassFunction


class CombinationRule(ABC):
    """Abstract base for every combination rule.

    Subclasses must implement :meth:`combine` (binary). They may override
    :meth:`combine_many` (N-ary) when iteration of the binary form is not the
    methodologically correct generalisation.
    """

    name: ClassVar[str] = ""

    @abstractmethod
    def combine(self, m1: MassFunction, m2: MassFunction) -> MassFunction:
        """Combine two mass functions on the same frame.

        Raises:
            FrameMismatchError: If ``m1.frame != m2.frame``.
        """

    def combine_many(self, masses: Sequence[MassFunction]) -> MassFunction:
        """Combine N mass functions.

        Default: left-fold via :meth:`combine`. Mathematically correct for
        associative rules; subclasses override when needed.

        Raises:
            ValueError: If ``masses`` is empty.
            FrameMismatchError: If frames disagree.
        """
        ms = list(masses)
        if not ms:
            raise ValueError(f"{self.name}.combine_many requires at least one MassFunction")
        if len(ms) == 1:
            return ms[0]
        result = ms[0]
        for m in ms[1:]:
            result = self.combine(result, m)
        return result

    def __call__(
        self,
        *args: MassFunction | Iterable[MassFunction],
    ) -> MassFunction:
        """Dispatch to ``combine`` (binary) or ``combine_many`` (N-ary).

        Accepted forms:

        - ``rule(m1, m2)`` — binary.
        - ``rule(m1, m2, m3, ...)`` — variadic ⇒ ``combine_many``.
        - ``rule([m1, m2, m3, ...])`` — single iterable ⇒ ``combine_many``.
        """
        if (
            len(args) == 2
            and isinstance(args[0], MassFunction)
            and isinstance(args[1], MassFunction)
        ):
            return self.combine(args[0], args[1])
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, MassFunction):
                return arg
            return self.combine_many(list(arg))
        # variadic: arg2 isn't a MassFunction, or there are 3+ args
        ms: list[MassFunction] = []
        for a in args:
            if isinstance(a, MassFunction):
                ms.append(a)
            else:
                ms.extend(a)
        return self.combine_many(ms)

    def __repr__(self) -> str:
        return f"<CombinationRule {self.name!r}>"


def check_same_frame(m1: MassFunction, m2: MassFunction) -> None:
    """Raise :class:`FrameMismatchError` if the two BBAs do not share a frame."""
    if m1.frame != m2.frame:
        raise FrameMismatchError(
            f"Frame mismatch: {m1.frame!r} vs {m2.frame!r}. "
            "Combination requires both BBAs to live on the same frame."
        )


def check_all_same_frame(masses: Sequence[MassFunction]) -> None:
    """Raise :class:`FrameMismatchError` if any two BBAs disagree on the frame."""
    if not masses:
        return
    first = masses[0].frame
    for i, m in enumerate(masses[1:], start=1):
        if m.frame != first:
            raise FrameMismatchError(
                f"Frame mismatch: masses[0].frame = {first!r} but masses[{i}].frame = {m.frame!r}."
            )


__all__ = ["CombinationRule", "check_all_same_frame", "check_same_frame"]
