"""Naive dense reference implementations of every combination rule.

Each function iterates the **full** dense ``2^|Θ| × 2^|Θ|`` cartesian product —
slow, but mathematically transparent. These are oracles for hypothesis
property tests asserting ``sparse_rule(m1, m2) ≈ dense_rule(m1, m2)``.

For each rule, the formula maps directly to the function body so that an
auditor can verify correctness against the cited literature with no
indirection.
"""

from __future__ import annotations

from itertools import product

import numpy as np

from carla_evidence import MassFunction
from carla_evidence.core.exceptions import TotalConflictError
from carla_evidence.core.mass import Mode


def _accumulate_to_mass(
    frame, accumulated: dict[int, float], mode: Mode = "shafer"
) -> MassFunction:
    """Build a MassFunction from a {bitmask: mass} dict (filtering tiny noise)."""
    return MassFunction(frame, accumulated, mode=mode, tol=1e-9)


def dense_conjunctive(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """``m_∩(A) = sum_{B ∩ C = A} m1(B) m2(C)`` (Smets 1990, §3)."""
    arr1 = m1.to_dense()
    arr2 = m2.to_dense()
    size = m1.frame.size
    out = np.zeros(size, dtype=np.float64)
    for B in range(size):
        if arr1[B] == 0.0:
            continue
        for C in range(size):
            if arr2[C] == 0.0:
                continue
            out[B & C] += arr1[B] * arr2[C]
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(m1.frame, accumulated, mode="tbm")


def dense_dempster(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """Dempster: conjunctive normalised by ``1/(1 - K)`` (Shafer 1976, §3.1)."""
    arr1 = m1.to_dense()
    arr2 = m2.to_dense()
    size = m1.frame.size
    out = np.zeros(size, dtype=np.float64)
    for B in range(size):
        if arr1[B] == 0.0:
            continue
        for C in range(size):
            if arr2[C] == 0.0:
                continue
            out[B & C] += arr1[B] * arr2[C]
    K = float(out[0])
    if K >= 1.0 - 1e-9:
        raise TotalConflictError(f"Total conflict: K = {K}")
    out[0] = 0.0
    out /= 1.0 - K
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(m1.frame, accumulated, mode="shafer")


def dense_disjunctive(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """``m_∪(A) = sum_{B ∪ C = A} m1(B) m2(C)`` (Dubois-Prade 1986)."""
    arr1 = m1.to_dense()
    arr2 = m2.to_dense()
    size = m1.frame.size
    out = np.zeros(size, dtype=np.float64)
    for B in range(size):
        if arr1[B] == 0.0:
            continue
        for C in range(size):
            if arr2[C] == 0.0:
                continue
            out[B | C] += arr1[B] * arr2[C]
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(m1.frame, accumulated, mode="shafer")


def dense_yager(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """Yager: conflict mass redirected to ``Theta`` (Yager 1987)."""
    arr1 = m1.to_dense()
    arr2 = m2.to_dense()
    size = m1.frame.size
    out = np.zeros(size, dtype=np.float64)
    full = m1.frame.full_mask
    for B in range(size):
        if arr1[B] == 0.0:
            continue
        for C in range(size):
            if arr2[C] == 0.0:
                continue
            inter = B & C
            target = inter if inter != 0 else full
            out[target] += arr1[B] * arr2[C]
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(m1.frame, accumulated, mode="shafer")


def dense_dubois_prade(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """Dubois-Prade: conflict redirected to ``B union C`` (Dubois-Prade 1988)."""
    arr1 = m1.to_dense()
    arr2 = m2.to_dense()
    size = m1.frame.size
    out = np.zeros(size, dtype=np.float64)
    for B in range(size):
        if arr1[B] == 0.0:
            continue
        for C in range(size):
            if arr2[C] == 0.0:
                continue
            inter = B & C
            target = inter if inter != 0 else (B | C)
            out[target] += arr1[B] * arr2[C]
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(m1.frame, accumulated, mode="shafer")


def dense_pcr5(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """PCR5: conflict redistributed onto ``B`` and ``C`` (Smarandache-Dezert 2005)."""
    arr1 = m1.to_dense()
    arr2 = m2.to_dense()
    size = m1.frame.size
    out = np.zeros(size, dtype=np.float64)
    for B in range(size):
        if arr1[B] == 0.0:
            continue
        for C in range(size):
            if arr2[C] == 0.0:
                continue
            if B & C != 0:
                out[B & C] += arr1[B] * arr2[C]
            else:
                denom = arr1[B] + arr2[C]
                # denom > 0 since both masses are positive
                out[B] += arr1[B] * arr1[B] * arr2[C] / denom
                out[C] += arr1[B] * arr2[C] * arr2[C] / denom
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(m1.frame, accumulated, mode="shafer")


def dense_pcr6(masses: list[MassFunction]) -> MassFunction:
    """PCR6 N-source (Martin-Osswald 2006)."""
    if not masses:
        raise ValueError("dense_pcr6 requires at least one MassFunction")
    if len(masses) == 1:
        return masses[0]
    if len(masses) == 2:
        return dense_pcr5(masses[0], masses[1])
    arrs = [m.to_dense() for m in masses]
    frame = masses[0].frame
    size = frame.size
    out = np.zeros(size, dtype=np.float64)
    full = frame.full_mask  # noqa: F841 (kept for symmetry with sparse path)
    for tup in product(*(range(size) for _ in masses)):
        masses_at = [arrs[i][tup[i]] for i in range(len(masses))]
        if any(m == 0.0 for m in masses_at):
            continue
        prod_mass = 1.0
        for m in masses_at:
            prod_mass *= m
        intersection = tup[0]
        for b in tup[1:]:
            intersection &= b
        if intersection != 0:
            out[intersection] += prod_mass
        else:
            total = sum(masses_at)
            for B, m in zip(tup, masses_at, strict=True):
                out[B] += prod_mass * m / total
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(frame, accumulated, mode="shafer")


def dense_mean(masses: list[MassFunction]) -> MassFunction:
    """Arithmetic mean of N BBAs (Murphy 2000)."""
    if not masses:
        raise ValueError("dense_mean requires at least one MassFunction")
    if len(masses) == 1:
        return masses[0]
    arrs = [m.to_dense() for m in masses]
    out = np.mean(arrs, axis=0)
    out_mode: Mode = "tbm" if any(m.mode == "tbm" for m in masses) else "shafer"
    size = masses[0].frame.size
    accumulated = {int(mask): float(out[mask]) for mask in range(size) if out[mask] != 0.0}
    return _accumulate_to_mass(masses[0].frame, accumulated, mode=out_mode)
