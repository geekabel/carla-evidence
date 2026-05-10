"""Unit tests for ``carla_evidence.core.encoding``."""

from __future__ import annotations

import pytest

from carla_evidence.core.encoding import (
    cardinality,
    complement,
    full_mask,
    intersection,
    is_proper_subset,
    is_subset,
    iter_subsets_of,
    union,
)


class TestFullMask:
    def test_zero_elements(self) -> None:
        assert full_mask(0) == 0

    def test_three_elements(self) -> None:
        assert full_mask(3) == 0b111

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            full_mask(-1)


class TestSubsetRelations:
    def test_empty_subset_of_anything(self) -> None:
        assert is_subset(0, 0b111) is True
        assert is_subset(0, 0) is True

    def test_self_subset(self) -> None:
        assert is_subset(0b101, 0b101) is True

    def test_strict_subset(self) -> None:
        assert is_subset(0b001, 0b101) is True
        assert is_proper_subset(0b001, 0b101) is True

    def test_self_not_proper_subset(self) -> None:
        assert is_proper_subset(0b101, 0b101) is False

    def test_disjoint_not_subset(self) -> None:
        assert is_subset(0b010, 0b101) is False


class TestSetOperations:
    def test_intersection(self) -> None:
        assert intersection(0b110, 0b011) == 0b010

    def test_union(self) -> None:
        assert union(0b110, 0b011) == 0b111

    def test_complement(self) -> None:
        assert complement(0b010, 3) == 0b101
        assert complement(0, 3) == 0b111
        assert complement(0b111, 3) == 0


class TestCardinality:
    @pytest.mark.parametrize(
        ("mask", "expected"),
        [(0, 0), (0b1, 1), (0b101, 2), (0b1111, 4)],
    )
    def test_cardinality(self, mask: int, expected: int) -> None:
        assert cardinality(mask) == expected

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            cardinality(-1)


class TestIterSubsetsOf:
    def test_empty(self) -> None:
        assert list(iter_subsets_of(0)) == [0]

    def test_singleton(self) -> None:
        assert sorted(iter_subsets_of(0b100)) == [0, 0b100]

    def test_three_element(self) -> None:
        # All subsets of {a,b,c} = full mask 7
        assert sorted(iter_subsets_of(0b111)) == list(range(8))

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            list(iter_subsets_of(-1))

    def test_yields_each_once(self) -> None:
        result = list(iter_subsets_of(0b1011))
        assert len(result) == len(set(result))
        # popcount(0b1011) = 3 elements -> 2^3 = 8 subsets
        assert len(result) == 8
