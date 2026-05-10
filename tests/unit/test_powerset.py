"""Unit tests for :mod:`carla_evidence.core.powerset`."""

from __future__ import annotations

from carla_evidence import Frame
from carla_evidence.core.powerset import (
    iter_focal_pairs,
    iter_powerset,
    iter_powerset_masks,
)


def test_iter_powerset_masks_size() -> None:
    f = Frame.of("a", "b", "c")
    assert list(iter_powerset_masks(f)) == list(range(8))


def test_iter_powerset_yields_all_subsets() -> None:
    f = Frame.of("a", "b")
    assert list(iter_powerset(f)) == [
        (),
        ("a",),
        ("b",),
        ("a", "b"),
    ]


def test_iter_focal_pairs() -> None:
    f = Frame.of("a", "b")
    pairs = list(iter_focal_pairs(f))
    assert pairs == [
        (0, ()),
        (1, ("a",)),
        (2, ("b",)),
        (3, ("a", "b")),
    ]


def test_iter_focal_pairs_count() -> None:
    f = Frame.of("a", "b", "c", "d")
    assert len(list(iter_focal_pairs(f))) == 16
