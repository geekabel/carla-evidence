"""Hypothesis strategies for property-based testing of evidential code.

These strategies are public so downstream users can write their own property
tests against the same canonical generators that the library's own tests use.

Examples:
    >>> from hypothesis import given
    >>> from carla_evidence.testing import mass_functions
    >>> @given(m=mass_functions(frame_size=4))
    ... def test_my_invariant(m):
    ...     pass
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Literal, cast

from hypothesis import strategies as st

from carla_evidence.core.frame import Frame
from carla_evidence.core.mass import MassFunction, Mode

# Lower bound on each generated weight before normalisation. Far above the
# constructor's default ``tol = 1e-9`` so no focal is stripped during
# canonicalisation, which would silently break ``Σm = 1``.
_MIN_WEIGHT = 0.01

_DEFAULT_NAMES: Sequence[str] = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j")


def frame_names(min_size: int = 2, max_size: int = 5) -> st.SearchStrategy[tuple[str, ...]]:
    """Strategy for tuples of distinct, non-empty element names."""
    if min_size < 1:
        raise ValueError("min_size must be >= 1 (frames cannot be empty)")
    if max_size < min_size:
        raise ValueError("max_size must be >= min_size")
    if max_size > len(_DEFAULT_NAMES):
        raise ValueError(
            f"max_size must be <= {len(_DEFAULT_NAMES)} (extend _DEFAULT_NAMES if needed)"
        )
    return st.integers(min_value=min_size, max_value=max_size).flatmap(
        lambda n: st.just(tuple(_DEFAULT_NAMES[:n])),
    )


def frames(min_size: int = 2, max_size: int = 5) -> st.SearchStrategy[Frame]:
    """Strategy for :class:`Frame` instances of size in ``[min_size, max_size]``."""
    return frame_names(min_size=min_size, max_size=max_size).map(Frame)


@st.composite
def _focals_distribution(
    draw: st.DrawFn,
    frame: Frame,
    mode: Mode,
    max_focals: int,
) -> dict[int, float]:
    """Draw a normalised mass distribution over a subset of bitmasks."""
    n_focals = draw(st.integers(min_value=1, max_value=max_focals))

    # In Shafer mode the empty set is excluded; TBM allows it.
    candidate_masks = list(range(1, frame.size)) if mode == "shafer" else list(range(frame.size))

    n_focals = min(n_focals, len(candidate_masks))
    masks = draw(
        st.lists(
            st.sampled_from(candidate_masks),
            min_size=n_focals,
            max_size=n_focals,
            unique=True,
        )
    )
    weights = draw(
        st.lists(
            st.floats(
                min_value=_MIN_WEIGHT,
                max_value=1.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            min_size=len(masks),
            max_size=len(masks),
        )
    )
    total = math.fsum(weights)
    masses = [w / total for w in weights]
    # Absorb floating-point drift into the largest mass so the sum is exactly 1.0
    # bit-for-bit (otherwise a JSON round-trip with a stricter tol can falsify).
    drift = 1.0 - math.fsum(masses)
    if masses:
        i_max = max(range(len(masses)), key=masses.__getitem__)
        masses[i_max] += drift
    return dict(zip(masks, masses, strict=True))


def mass_functions(
    *,
    frame: Frame | None = None,
    frame_size: int | None = None,
    mode: Mode = "shafer",
    max_focals: int = 6,
) -> st.SearchStrategy[MassFunction]:
    """Strategy for :class:`MassFunction` instances.

    Args:
        frame: A specific frame to draw on. If ``None``, a frame is drawn
            from :func:`frames`.
        frame_size: If ``frame`` is ``None``, the size of the random frame.
            ``None`` means draw a size in ``[2, 5]``.
        mode: ``"shafer"`` or ``"tbm"``. DSmT is rejected by the constructor
            in v0.1.0.
        max_focals: Maximum number of focal elements per BBA.

    Returns:
        A hypothesis strategy producing :class:`MassFunction` instances.
    """
    if mode not in ("shafer", "tbm"):
        raise ValueError(
            f"Unsupported mode for property testing: {mode!r}. DSmT mode lands in v0.2.0."
        )

    if frame is not None:
        frame_strategy = st.just(frame)
    elif frame_size is not None:
        frame_strategy = frames(min_size=frame_size, max_size=frame_size)
    else:
        frame_strategy = frames()

    @st.composite
    def _build(draw: st.DrawFn) -> MassFunction:
        f = draw(frame_strategy)
        focals = draw(_focals_distribution(f, mode, max_focals))
        return MassFunction(f, focals, mode=mode)

    return _build()


def vacuous_bbas(
    *,
    frame: Frame | None = None,
    frame_size: int | None = None,
    mode: Mode = "shafer",
) -> st.SearchStrategy[MassFunction]:
    """Strategy for vacuous BBAs (``m(Theta) = 1``)."""
    if frame is not None:
        frame_strategy = st.just(frame)
    elif frame_size is not None:
        frame_strategy = frames(min_size=frame_size, max_size=frame_size)
    else:
        frame_strategy = frames()
    return frame_strategy.map(
        lambda f: MassFunction.vacuous(f, mode=cast(Literal["shafer", "tbm"], mode))
    )


def categorical_bbas(
    *,
    frame: Frame | None = None,
    frame_size: int | None = None,
    mode: Mode = "shafer",
) -> st.SearchStrategy[MassFunction]:
    """Strategy for categorical BBAs (a single non-empty subset carries mass 1)."""
    if frame is not None:
        frame_strategy = st.just(frame)
    elif frame_size is not None:
        frame_strategy = frames(min_size=frame_size, max_size=frame_size)
    else:
        frame_strategy = frames()

    @st.composite
    def _build(draw: st.DrawFn) -> MassFunction:
        f = draw(frame_strategy)
        # In Shafer mode forbid empty-set; in TBM allow it.
        low = 0 if mode == "tbm" else 1
        mask = draw(st.integers(min_value=low, max_value=f.size - 1))
        return MassFunction.categorical(f, mask, mode=mode)

    return _build()


def bayesian_bbas(
    *,
    frame: Frame | None = None,
    frame_size: int | None = None,
    mode: Mode = "shafer",
) -> st.SearchStrategy[MassFunction]:
    """Strategy for Bayesian BBAs (only singleton focals)."""
    if frame is not None:
        frame_strategy = st.just(frame)
    elif frame_size is not None:
        frame_strategy = frames(min_size=frame_size, max_size=frame_size)
    else:
        frame_strategy = frames()

    @st.composite
    def _build(draw: st.DrawFn) -> MassFunction:
        f = draw(frame_strategy)
        weights = draw(
            st.lists(
                st.floats(
                    min_value=_MIN_WEIGHT,
                    max_value=1.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
                min_size=len(f),
                max_size=len(f),
            )
        )
        total = math.fsum(weights)
        probs = [w / total for w in weights]
        # Absorb drift into the largest probability for bit-exact normalisation.
        drift = 1.0 - math.fsum(probs)
        i_max = max(range(len(probs)), key=probs.__getitem__)
        probs[i_max] += drift
        return MassFunction.bayesian(f, probs, mode=mode)

    return _build()


__all__ = [
    "bayesian_bbas",
    "categorical_bbas",
    "frame_names",
    "frames",
    "mass_functions",
    "vacuous_bbas",
]
