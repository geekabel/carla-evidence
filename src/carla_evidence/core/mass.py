"""Mass functions (Basic Belief Assignments / BBAs).

A mass function on a frame :math:`\\Theta` is a map
:math:`m: 2^\\Theta \\to [0, 1]` with :math:`\\sum_{A \\subseteq \\Theta} m(A) = 1`
and :math:`m(A) \\geq 0` for every :math:`A`.

Three theoretical modes are recognised (``CLAUDE.md`` §"Domain knowledge"):

- ``"shafer"`` — Shafer 1976: ``m(empty-set) = 0`` is enforced.
- ``"tbm"`` — Smets's Transferable Belief Model (1990): ``m(empty-set) >= 0``
  is allowed and interpreted as open-world conflict.
- ``"dsmt"`` — Smarandache-Dezert: hyperpowerset over a non-exclusive frame.
  *Reserved*; lands in v0.2.0 alongside PCR5/PCR6. Constructing with this
  mode currently raises :class:`NotImplementedError`.

Storage is **sparse-first**: the canonical internal representation is a tuple
``focals = ((mask_0, m_0), (mask_1, m_1), ...)`` sorted by ``mask`` with
zero-mass entries dropped. The mass function therefore stays hashable and
immutable for any frame size. Dense ``numpy`` materialisations are produced
on demand by :meth:`to_dense`, :meth:`to_bel_vector`, :meth:`to_pl_vector`,
and :meth:`to_q_vector`.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast

import numpy as np
import numpy.typing as npt

from carla_evidence.core.encoding import is_subset
from carla_evidence.core.exceptions import (
    FrameError,
    InvalidMassError,
    ModeError,
)
from carla_evidence.core.frame import Frame

Mode = Literal["shafer", "tbm", "dsmt"]
"""Theoretical regime selected at construction; see module docstring."""

DEFAULT_TOL: float = 1e-9
"""Default absolute tolerance for the ``Σm = 1`` and non-negativity checks."""

SubsetSpec = Iterable[str] | int
"""What the user can pass as a subset descriptor: a name iterable or a bitmask."""

_VALID_MODES: tuple[Mode, ...] = ("shafer", "tbm", "dsmt")


def _coerce_to_mask(frame: Frame, subset: Any) -> int:
    """Coerce a ``SubsetSpec`` (name iterable or int bitmask) to a bitmask."""
    if isinstance(subset, bool):
        # bool is a subclass of int — reject explicitly to avoid surprises
        raise FrameError(f"Subset spec must not be a bool; got {subset!r}")
    if isinstance(subset, int):
        if subset < 0 or subset >= frame.size:
            raise FrameError(
                f"bitmask {subset} out of range for frame of size {len(frame)} "
                f"(max {frame.size - 1})"
            )
        return subset
    return frame.to_bitmask(cast(Iterable[str], subset))


@dataclass(frozen=True, init=False)
class MassFunction:
    """Immutable mass function (BBA) on a finite frame of discernment.

    See the module docstring for the semantics of the ``mode`` parameter and
    the rationale for the sparse-first storage.

    Args:
        frame: The underlying :class:`Frame`.
        focals: A mapping ``{subset: mass}`` *or* an iterable of
            ``(subset, mass)`` pairs. Subsets may be name iterables (tuple,
            frozenset, list, ...) or raw bitmasks. Zero-mass entries are
            dropped. Repeated subsets are accumulated.
        mode: Theoretical regime — ``"shafer"`` (default), ``"tbm"``, or
            ``"dsmt"`` (raises :class:`NotImplementedError` until v0.2.0).
        tol: Absolute tolerance for the ``Σm = 1`` and non-negativity checks.

    Raises:
        InvalidMassError: If a mass is negative or the masses do not sum to
            1 within ``tol``.
        ModeError: If ``mode="shafer"`` and ``m(empty-set) > 0``, or if
            ``mode`` is unknown.
        FrameError: If a focal subset references unknown elements or an
            out-of-range bitmask.
        NotImplementedError: If ``mode="dsmt"``.

    Examples:
        Build a BBA from a name-keyed dict:

        >>> theta = Frame(("a", "b", "c"))
        >>> m = MassFunction(theta, {("a",): 0.6, ("a", "b"): 0.3, theta.omega: 0.1})
        >>> round(m.bel(("a",)), 4)
        0.6
        >>> round(m.pl(("a",)), 4)
        1.0
        >>> round(m.q(("a",)), 4)
        1.0

        Use the helper constructors:

        >>> MassFunction.vacuous(theta).is_vacuous
        True
        >>> MassFunction.bayesian(theta, [0.2, 0.3, 0.5]).is_bayesian
        True

    References:
        Shafer (1976) §2; Smets (1990) §3; Smets (2005); Smarandache & Dezert
        (2004), Vol. 1, §1.
    """

    frame: Frame
    focals: tuple[tuple[int, float], ...]
    mode: Mode

    def __init__(
        self,
        frame: Frame,
        focals: Mapping[Any, float] | Iterable[tuple[Any, float]],
        mode: Mode = "shafer",
        *,
        tol: float = DEFAULT_TOL,
    ) -> None:
        if mode == "dsmt":
            raise NotImplementedError(
                "DSmT hyperpowerset support lands in v0.2.0 alongside PCR5/PCR6 "
                "rules (free-distributive-lattice enumeration is coupled with "
                "those rules). For now, please use mode='shafer' or mode='tbm'."
            )
        if mode not in _VALID_MODES:
            raise ModeError(f"Unknown mode {mode!r}; expected one of {_VALID_MODES}.")

        if isinstance(focals, Mapping):
            pairs: Iterable[tuple[Any, float]] = focals.items()
        else:
            pairs = focals

        accumulated: dict[int, float] = {}
        for subset, mass in pairs:
            mass_f = float(mass)
            if mass_f < -tol:
                raise InvalidMassError(
                    f"Negative mass {mass_f} for subset {subset!r}; all masses must be ≥ 0."
                )
            if mass_f <= tol and mass_f >= -tol:
                # snap tiny values to exactly zero and drop them
                continue
            mask = _coerce_to_mask(frame, subset)
            accumulated[mask] = accumulated.get(mask, 0.0) + mass_f

        if mode == "shafer" and accumulated.get(0, 0.0) > tol:
            raise ModeError(
                f"Shafer mode enforces m(empty-set) = 0; got "
                f"m(empty-set) = {accumulated[0]}. "
                "Use mode='tbm' to allow non-zero conflict mass."
            )

        total = math.fsum(accumulated.values())
        if not math.isclose(total, 1.0, abs_tol=tol):
            raise InvalidMassError(
                f"Mass function must sum to 1; got Σm = {total} "
                f"(tolerance {tol}). Did you forget to normalise?"
            )

        # Canonical form: sorted by bitmask, only non-zero entries.
        focals_canon = tuple(sorted(accumulated.items()))

        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "focals", focals_canon)
        object.__setattr__(self, "mode", mode)

    # ---- alternative constructors ----------------------------------------

    @classmethod
    def vacuous(cls, frame: Frame, mode: Mode = "shafer") -> MassFunction:
        """Total ignorance: ``m(Theta) = 1``.

        Examples:
            >>> theta = Frame.of("a", "b")
            >>> MassFunction.vacuous(theta).mass(theta.omega)
            1.0
        """
        return cls(frame, {frame.full_mask: 1.0}, mode=mode)

    @classmethod
    def categorical(
        cls,
        frame: Frame,
        subset: SubsetSpec,
        mode: Mode = "shafer",
    ) -> MassFunction:
        """Certainty on a single subset: ``m(A) = 1``, every other focal is zero."""
        mask = _coerce_to_mask(frame, subset)
        if mode == "shafer" and mask == 0:
            raise ModeError(
                "Shafer mode forbids m(empty-set) = 1. "
                "Use mode='tbm' to encode total contradiction."
            )
        return cls(frame, {mask: 1.0}, mode=mode)

    @classmethod
    def bayesian(
        cls,
        frame: Frame,
        probs: Sequence[float],
        mode: Mode = "shafer",
    ) -> MassFunction:
        """Construct a Bayesian BBA: only singletons carry mass.

        ``probs[i]`` becomes the mass on ``{frame.elements[i]}``. The library
        does **not** renormalise — the caller is responsible for ``Σ probs = 1``.

        Raises:
            FrameError: If ``len(probs) != len(frame)``.
        """
        if len(probs) != len(frame):
            raise FrameError(
                f"Need {len(frame)} probabilities for a frame of size "
                f"{len(frame)}; got {len(probs)}."
            )
        return cls(
            frame,
            {(1 << i): float(p) for i, p in enumerate(probs)},
            mode=mode,
        )

    @classmethod
    def from_dict(
        cls,
        frame: Frame,
        masses: Mapping[Any, float],
        mode: Mode = "shafer",
    ) -> MassFunction:
        """Alias of the main constructor for the dict-keyed form."""
        return cls(frame, masses, mode=mode)

    @classmethod
    def from_array(
        cls,
        frame: Frame,
        arr: npt.ArrayLike,
        mode: Mode = "shafer",
    ) -> MassFunction:
        """Construct from a dense array of length ``2 ** n`` indexed by bitmask.

        Args:
            frame: The frame the BBA lives on.
            arr: Array-like of shape ``(frame.size,)``. Index ``k`` holds
                ``m(B)`` where ``B`` is the subset whose bitmask is ``k``.
            mode: Theoretical regime.

        Raises:
            InvalidMassError: If ``arr`` does not have shape ``(frame.size,)``.
        """
        a = np.asarray(arr, dtype=np.float64)
        if a.shape != (frame.size,):
            raise InvalidMassError(
                f"Dense mass array must have shape ({frame.size},) for a "
                f"frame of size {len(frame)}; got {a.shape}."
            )
        focals = {int(mask): float(a[mask]) for mask in range(frame.size) if a[mask] != 0.0}
        return cls(frame, focals, mode=mode)

    # ---- accessors -------------------------------------------------------

    def __len__(self) -> int:
        """Number of focal elements (entries with non-zero mass)."""
        return len(self.focals)

    def __iter__(self) -> Iterator[tuple[tuple[str, ...], float]]:
        """Iterate over ``(subset_names, mass)`` pairs in canonical order."""
        for mask, mass in self.focals:
            yield (self.frame.from_bitmask(mask), mass)

    def mass(self, subset: SubsetSpec) -> float:
        """Return ``m(A)`` (zero if ``A`` is not a focal element)."""
        mask = _coerce_to_mask(self.frame, subset)
        # Linear scan; len(focals) is small in practice.
        for m_mask, m_val in self.focals:
            if m_mask == mask:
                return m_val
            if m_mask > mask:
                break  # focals is sorted
        return 0.0

    def bel(self, subset: SubsetSpec) -> float:
        """``Bel(A) = sum_{B subset-or-equal A, B != empty-set} m(B)``."""
        mask = _coerce_to_mask(self.frame, subset)
        return math.fsum(m for B, m in self.focals if B != 0 and is_subset(B, mask))

    def pl(self, subset: SubsetSpec) -> float:
        """``Pl(A) = sum_{B intersect A != empty-set} m(B)``."""
        mask = _coerce_to_mask(self.frame, subset)
        return math.fsum(m for B, m in self.focals if B & mask)

    def q(self, subset: SubsetSpec) -> float:
        """``Q(A) = sum_{B superset-or-equal A} m(B)`` (commonality)."""
        mask = _coerce_to_mask(self.frame, subset)
        return math.fsum(m for B, m in self.focals if (B & mask) == mask)

    # ---- dense materialisations ------------------------------------------

    def to_dense(self) -> npt.NDArray[np.float64]:
        """Materialise as a dense ``numpy`` array of shape ``(2 ** n,)``."""
        out = np.zeros(self.frame.size, dtype=np.float64)
        for mask, mass in self.focals:
            out[mask] = mass
        return out

    def to_bel_vector(self) -> npt.NDArray[np.float64]:
        """Vectorised Bel: ``out[A] = Bel(A)`` for every bitmask ``A``.

        Computed via a Yates-style zeta transform in :math:`O(n \\, 2^n)`.
        ``out[0] = 0`` by convention.
        """
        n = len(self.frame)
        bel = self.to_dense().copy()
        for i in range(n):
            bit = 1 << i
            # Vectorised: every mask whose bit i is set absorbs mass from
            # the same mask with bit i cleared.
            indices = np.arange(self.frame.size)
            target = indices[(indices & bit) != 0]
            bel[target] += bel[target ^ bit]
        # bel now contains the zeta transform: sum_{B subset-or-equal A} m(B).
        # Bel excludes m(empty-set), so subtract it everywhere and zero bel(empty-set).
        m_empty = bel[0]
        bel -= m_empty
        bel[0] = 0.0
        return bel

    def to_pl_vector(self) -> npt.NDArray[np.float64]:
        """Vectorised Pl: ``out[A] = Pl(A)`` for every bitmask ``A``.

        Uses the identity ``Pl(A) = 1 - m(empty-set) - Bel(neg A)``.
        ``out[0] = 0`` by convention.
        """
        bel = self.to_bel_vector()
        m_empty = self.mass(0)
        full = self.frame.full_mask
        complements = np.arange(self.frame.size) ^ full
        pl: npt.NDArray[np.float64] = np.asarray(1.0 - m_empty - bel[complements], dtype=np.float64)
        pl[0] = 0.0
        return pl

    def to_q_vector(self) -> npt.NDArray[np.float64]:
        """Vectorised commonality: ``out[A] = Q(A)`` for every bitmask ``A``.

        Computed via a reverse zeta transform in :math:`O(n \\, 2^n)`.
        """
        n = len(self.frame)
        q = self.to_dense().copy()
        for i in range(n):
            bit = 1 << i
            indices = np.arange(self.frame.size)
            target = indices[(indices & bit) == 0]
            q[target] += q[target | bit]
        return q

    # ---- introspection ---------------------------------------------------

    def focal_subsets(self) -> Iterator[tuple[str, ...]]:
        """Yield focal subsets (those with non-zero mass) as element-name tuples."""
        for mask, _ in self.focals:
            yield self.frame.from_bitmask(mask)

    @property
    def core(self) -> tuple[tuple[str, ...], ...]:
        """The focal set (a.k.a. *core*): every subset with non-zero mass."""
        return tuple(self.focal_subsets())

    @property
    def is_normal(self) -> bool:
        """``True`` iff ``m(empty-set) = 0`` (always true in Shafer mode)."""
        return self.mass(0) == 0.0

    @property
    def is_bayesian(self) -> bool:
        """``True`` iff every focal element is a singleton."""
        return all(mask.bit_count() == 1 for mask, _ in self.focals)

    @property
    def is_vacuous(self) -> bool:
        """``True`` iff the only focal element is :math:`\\Theta` with mass 1."""
        return (
            len(self.focals) == 1
            and self.focals[0][0] == self.frame.full_mask
            and math.isclose(self.focals[0][1], 1.0)
        )

    @property
    def is_categorical(self) -> bool:
        """``True`` iff a single subset carries all the mass."""
        return len(self.focals) == 1 and math.isclose(self.focals[0][1], 1.0)

    # ---- (approximate) equality -----------------------------------------

    def is_close_to(self, other: MassFunction, *, atol: float = 1e-9) -> bool:
        """Test approximate equality (frame, mode, and masses within ``atol``)."""
        if self.frame != other.frame or self.mode != other.mode:
            return False
        d1 = dict(self.focals)
        d2 = dict(other.focals)
        for k in set(d1) | set(d2):
            if not math.isclose(d1.get(k, 0.0), d2.get(k, 0.0), abs_tol=atol):
                return False
        return True

    # ---- serialisation ---------------------------------------------------

    def to_dict(self) -> dict[tuple[str, ...], float]:
        """Return ``{subset_names: mass}`` for every focal element.

        This dict alone does not carry the frame or the mode; for a full
        round-trip use :meth:`to_json` / :meth:`from_json`.
        """
        return {self.frame.from_bitmask(mask): mass for mask, mass in self.focals}

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to JSON (frame + mode + focals).

        ``kwargs`` are forwarded to :func:`json.dumps`.
        """
        payload = {
            "frame": list(self.frame.elements),
            "mode": self.mode,
            "focals": [[list(self.frame.from_bitmask(mask)), mass] for mask, mass in self.focals],
        }
        return json.dumps(payload, **kwargs)

    @classmethod
    def from_json(cls, s: str) -> MassFunction:
        """Inverse of :meth:`to_json`."""
        data = json.loads(s)
        frame = Frame(cast(Iterable[str], data["frame"]))
        mode = cast(Mode, data["mode"])
        focals = [
            (tuple(cast(Iterable[str], subset)), float(mass))
            for subset, mass in cast(Iterable[Sequence[Any]], data["focals"])
        ]
        return cls(frame, focals, mode=mode)

    # ---- repr ------------------------------------------------------------

    def __repr__(self) -> str:
        if not self.focals:  # pragma: no cover  (forbidden by validation)
            return f"MassFunction(mode={self.mode!r}, [])"
        parts: list[str] = []
        for mask, mass in self.focals:
            if mask == 0:
                names_repr = "{}"
            elif mask == self.frame.full_mask:
                names_repr = "Theta"
            else:
                names_repr = "{" + ",".join(self.frame.from_bitmask(mask)) + "}"
            parts.append(f"{names_repr}: {mass:.4g}")
        return f"MassFunction(mode={self.mode!r}, {{{', '.join(parts)}}})"
