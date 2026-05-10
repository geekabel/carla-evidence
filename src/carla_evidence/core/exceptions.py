"""Domain exceptions raised by ``carla_evidence``.

All exceptions inherit from :class:`EvidenceError`, so user code can catch the
whole library with a single ``except EvidenceError``.
"""

from __future__ import annotations


class EvidenceError(Exception):
    """Base class for every exception raised by ``carla_evidence``."""


class FrameError(EvidenceError):
    """Raised when constructing or manipulating a :class:`Frame` fails.

    Examples include empty frames, duplicate elements, out-of-range bitmasks,
    and references to elements that the frame does not contain.
    """


class FrameMismatchError(EvidenceError):
    """Raised when an operation requires two BBAs to share the same frame.

    Lands alongside the combination rules in v0.2.0 (Phase 2).
    """


class InvalidMassError(EvidenceError):
    """Raised when a candidate :class:`MassFunction` violates a domain constraint.

    Triggers include negative masses and totals that fail to sum to 1 within
    the configured tolerance.
    """


class ModeError(EvidenceError):
    """Raised when an operation is incompatible with the BBA's theoretical mode.

    The two cases enforced today are:

    - ``mode="shafer"`` with ``m(empty-set) > 0`` — Shafer's framework forbids it
      (``CLAUDE.md`` §"Domain knowledge — pièges critiques", point 1).
    - An unknown ``mode`` string.

    Will also cover DSmT-vs-Shafer conflicts when DSmT lands in v0.2.0.
    """


class TotalConflictError(EvidenceError):
    """Raised by Dempster's rule when ``K = 1`` (combination undefined).

    Reserved for v0.2.0 (Phase 2). Defined here so users can ``except
    TotalConflictError`` from day one, even though no rule raises it yet.
    See ``CLAUDE.md`` §"Domain knowledge — pièges critiques", point 2.
    """
