"""Unit tests for :class:`carla_evidence.core.frame.Frame`."""

from __future__ import annotations

import pytest

from carla_evidence import Frame, FrameError


class TestFrameConstruction:
    def test_from_tuple(self) -> None:
        f = Frame(("a", "b", "c"))
        assert f.elements == ("a", "b", "c")

    def test_from_list_is_normalised(self) -> None:
        assert Frame(["a", "b"]) == Frame(("a", "b"))

    def test_variadic_factory(self) -> None:
        assert Frame.of("a", "b", "c") == Frame(("a", "b", "c"))

    def test_empty_raises(self) -> None:
        with pytest.raises(FrameError, match="at least one"):
            Frame(())

    def test_duplicates_raise(self) -> None:
        with pytest.raises(FrameError, match="unique"):
            Frame(("a", "b", "a"))

    def test_non_string_raises(self) -> None:
        with pytest.raises(FrameError, match="strings"):
            Frame(("a", 1))  # type: ignore[list-item]

    def test_empty_string_raises(self) -> None:
        with pytest.raises(FrameError, match="non-empty"):
            Frame(("a", ""))


class TestFrameProperties:
    def test_len(self) -> None:
        assert len(Frame.of("a", "b", "c")) == 3

    def test_size(self) -> None:
        assert Frame.of("a", "b", "c").size == 8

    def test_full_mask(self) -> None:
        assert Frame.of("a", "b", "c").full_mask == 0b111

    def test_omega_aliases_elements(self) -> None:
        f = Frame.of("a", "b")
        assert f.omega == f.elements


class TestBitmaskTranslation:
    def test_to_bitmask_singleton(self) -> None:
        f = Frame.of("a", "b", "c")
        assert f.to_bitmask(("a",)) == 1
        assert f.to_bitmask(("c",)) == 0b100

    def test_to_bitmask_pair(self) -> None:
        f = Frame.of("a", "b", "c")
        assert f.to_bitmask(("a", "c")) == 0b101

    def test_to_bitmask_full(self) -> None:
        f = Frame.of("a", "b", "c")
        assert f.to_bitmask(("a", "b", "c")) == 0b111

    def test_to_bitmask_empty(self) -> None:
        assert Frame.of("a", "b").to_bitmask(()) == 0

    def test_to_bitmask_unknown_raises(self) -> None:
        with pytest.raises(FrameError, match="not in frame"):
            Frame.of("a", "b").to_bitmask(("c",))

    def test_to_bitmask_accepts_duplicates(self) -> None:
        # Repeated names in the input are silently deduplicated.
        assert Frame.of("a", "b").to_bitmask(("a", "a")) == 1

    def test_from_bitmask(self) -> None:
        f = Frame.of("a", "b", "c")
        assert f.from_bitmask(0) == ()
        assert f.from_bitmask(0b101) == ("a", "c")
        assert f.from_bitmask(0b111) == ("a", "b", "c")

    def test_from_bitmask_out_of_range(self) -> None:
        f = Frame.of("a", "b")
        with pytest.raises(FrameError, match="out of range"):
            f.from_bitmask(8)
        with pytest.raises(FrameError, match="out of range"):
            f.from_bitmask(-1)

    def test_round_trip(self) -> None:
        f = Frame.of("a", "b", "c", "d")
        for mask in range(f.size):
            assert f.to_bitmask(f.from_bitmask(mask)) == mask


class TestFrameDunder:
    def test_iter(self) -> None:
        assert list(Frame.of("a", "b", "c")) == ["a", "b", "c"]

    def test_contains(self) -> None:
        f = Frame.of("a", "b")
        assert "a" in f
        assert "c" not in f
        assert 1 not in f  # type: ignore[operator]

    def test_eq(self) -> None:
        assert Frame.of("a", "b") == Frame.of("a", "b")
        assert Frame.of("a", "b") != Frame.of("b", "a")  # order matters

    def test_hash(self) -> None:
        f1 = Frame.of("a", "b")
        f2 = Frame.of("a", "b")
        assert hash(f1) == hash(f2)
        assert {f1, f2} == {f1}

    def test_repr(self) -> None:
        assert repr(Frame.of("a", "b")) == "Frame(('a', 'b'))"
