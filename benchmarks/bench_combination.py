"""Performance benchmarks for the combination rules.

Targets from ``carla-evidence-architecture.md`` §"Phase 2 — Performance":

- Dempster: >= 1e5 pairs/sec on |Theta| = 4
- PCR6:     >= 1e4 pairs/sec on |Theta| = 8

These targets become CI guards (alert if regression > 20%) once
``benchmark-action/github-action-benchmark`` is wired up in
``.github/workflows/ci.yml``.

Run locally:

    pytest benchmarks/ --benchmark-only -q
"""

from __future__ import annotations

import random

import pytest

from carla_evidence import Frame, MassFunction
from carla_evidence.combination import (
    conjunctive,
    dempster,
    disjunctive,
    dubois_prade,
    mean,
    pcr5,
    pcr6,
    yager,
)

_SEED = 42


def _random_bba(frame: Frame, n_focals: int, rng: random.Random) -> MassFunction:
    """Build a pseudo-random Shafer BBA on ``frame`` with ``n_focals`` focals."""
    n_focals = min(n_focals, frame.size - 1)
    masks = rng.sample(range(1, frame.size), n_focals)
    weights = [rng.uniform(0.1, 1.0) for _ in masks]
    total = sum(weights)
    masses = {mask: w / total for mask, w in zip(masks, weights, strict=True)}
    drift = 1.0 - sum(masses.values())
    largest = max(masses, key=masses.__getitem__)
    masses[largest] += drift
    return MassFunction(frame, masses)


@pytest.fixture
def small_pair() -> tuple:
    """Two BBAs on |Theta|=4 with 4 focals each (Dempster target)."""
    rng = random.Random(_SEED)
    frame = Frame.of("a", "b", "c", "d")
    return _random_bba(frame, 4, rng), _random_bba(frame, 4, rng)


@pytest.fixture
def medium_pair() -> tuple:
    """Two BBAs on |Theta|=6 with 8 focals each."""
    rng = random.Random(_SEED)
    frame = Frame.of("a", "b", "c", "d", "e", "f")
    return _random_bba(frame, 8, rng), _random_bba(frame, 8, rng)


@pytest.fixture
def large_pair() -> tuple:
    """Two BBAs on |Theta|=8 with 16 focals each (PCR6 binary target)."""
    rng = random.Random(_SEED)
    frame = Frame.of("a", "b", "c", "d", "e", "f", "g", "h")
    return _random_bba(frame, 16, rng), _random_bba(frame, 16, rng)


# ---- Dempster: target >= 1e5 pairs/s on |Theta|=4 -----------------


@pytest.mark.benchmark(group="dempster")
def test_dempster_theta4(benchmark, small_pair) -> None:
    m1, m2 = small_pair
    benchmark(dempster, m1, m2)


@pytest.mark.benchmark(group="dempster")
def test_dempster_theta6(benchmark, medium_pair) -> None:
    m1, m2 = medium_pair
    benchmark(dempster, m1, m2)


@pytest.mark.benchmark(group="dempster")
def test_dempster_theta8(benchmark, large_pair) -> None:
    m1, m2 = large_pair
    benchmark(dempster, m1, m2)


# ---- Other binary rules on |Theta|=4 ---------------------------


@pytest.mark.benchmark(group="binary_theta4")
def test_conjunctive_theta4(benchmark, small_pair) -> None:
    benchmark(conjunctive, *small_pair)


@pytest.mark.benchmark(group="binary_theta4")
def test_disjunctive_theta4(benchmark, small_pair) -> None:
    benchmark(disjunctive, *small_pair)


@pytest.mark.benchmark(group="binary_theta4")
def test_yager_theta4(benchmark, small_pair) -> None:
    benchmark(yager, *small_pair)


@pytest.mark.benchmark(group="binary_theta4")
def test_dubois_prade_theta4(benchmark, small_pair) -> None:
    benchmark(dubois_prade, *small_pair)


@pytest.mark.benchmark(group="binary_theta4")
def test_pcr5_theta4(benchmark, small_pair) -> None:
    benchmark(pcr5, *small_pair)


@pytest.mark.benchmark(group="binary_theta4")
def test_mean_theta4(benchmark, small_pair) -> None:
    benchmark(mean, *small_pair)


# ---- PCR6: target >= 1e4 pairs/s on |Theta|=8 (binary) ----------


@pytest.mark.benchmark(group="pcr6")
def test_pcr6_binary_theta8(benchmark, large_pair) -> None:
    benchmark(pcr6, *large_pair)


# ---- PCR6 multi-source on |Theta|=4 (3 sources) ----------------


@pytest.mark.benchmark(group="pcr6_nsrc")
def test_pcr6_three_source_theta4(benchmark) -> None:
    rng = random.Random(_SEED)
    frame = Frame.of("a", "b", "c", "d")
    ms = [_random_bba(frame, 3, rng) for _ in range(3)]
    benchmark(pcr6, ms)
