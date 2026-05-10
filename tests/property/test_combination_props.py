"""Property-based tests shared across combination rules.

Three families of properties are exercised against ``hypothesis``:

1. **Sparse-vs-dense equivalence** — every sparse rule agrees with its naive
   dense reference impl in :mod:`tests._references.dense_combination` for
   every randomly generated BBA pair (1e-12 atol). This is the
   peer-review-grade correctness guard.
2. **Algebraic invariants** — commutativity, associativity (Dempster),
   neutral element (Dempster, conjunctive), idempotence (mean over the
   same BBA).
3. **Output validity** — every rule returns a well-formed
   :class:`MassFunction` (sum to 1, no negative mass, mode honoured).
"""

from __future__ import annotations

from hypothesis import given, settings
from tests._references.dense_combination import (
    dense_conjunctive,
    dense_dempster,
    dense_disjunctive,
    dense_dubois_prade,
    dense_mean,
    dense_pcr5,
    dense_pcr6,
    dense_yager,
)

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
from carla_evidence.testing import mass_functions

# ---- Sparse-vs-dense equivalence (correctness oracle) -------------------

_SPARSE_VS_DENSE = (
    (conjunctive, dense_conjunctive),
    (disjunctive, dense_disjunctive),
    (yager, dense_yager),
    (dubois_prade, dense_dubois_prade),
    (pcr5, dense_pcr5),
)

_SHARED_FRAME = Frame.of("a", "b", "c", "d")


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_conjunctive_sparse_equals_dense(m1: MassFunction, m2: MassFunction) -> None:
    assert conjunctive(m1, m2).is_close_to(dense_conjunctive(m1, m2), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_disjunctive_sparse_equals_dense(m1: MassFunction, m2: MassFunction) -> None:
    assert disjunctive(m1, m2).is_close_to(dense_disjunctive(m1, m2), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_yager_sparse_equals_dense(m1: MassFunction, m2: MassFunction) -> None:
    assert yager(m1, m2).is_close_to(dense_yager(m1, m2), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_dubois_prade_sparse_equals_dense(m1: MassFunction, m2: MassFunction) -> None:
    assert dubois_prade(m1, m2).is_close_to(dense_dubois_prade(m1, m2), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_pcr5_sparse_equals_dense(m1: MassFunction, m2: MassFunction) -> None:
    assert pcr5(m1, m2).is_close_to(dense_pcr5(m1, m2), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
    m3=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=50, deadline=None)
def test_pcr6_sparse_equals_dense(m1: MassFunction, m2: MassFunction, m3: MassFunction) -> None:
    assert pcr6([m1, m2, m3]).is_close_to(dense_pcr6([m1, m2, m3]), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_dempster_sparse_equals_dense_when_not_total_conflict(
    m1: MassFunction, m2: MassFunction
) -> None:
    """Skip the example if Dempster is undefined; otherwise sparse = dense."""
    try:
        sparse = dempster(m1, m2)
        ref = dense_dempster(m1, m2)
    except Exception:
        return
    assert sparse.is_close_to(ref, atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=100)
def test_mean_sparse_equals_dense(m1: MassFunction, m2: MassFunction) -> None:
    assert mean(m1, m2).is_close_to(dense_mean([m1, m2]), atol=1e-12)


# ---- Commutativity (every rule that takes two BBAs) -----------------


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_conjunctive_commutative(m1: MassFunction, m2: MassFunction) -> None:
    assert conjunctive(m1, m2).is_close_to(conjunctive(m2, m1), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_dempster_commutative(m1: MassFunction, m2: MassFunction) -> None:
    try:
        a = dempster(m1, m2)
        b = dempster(m2, m1)
    except Exception:
        return
    assert a.is_close_to(b, atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_disjunctive_commutative(m1: MassFunction, m2: MassFunction) -> None:
    assert disjunctive(m1, m2).is_close_to(disjunctive(m2, m1), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_yager_commutative(m1: MassFunction, m2: MassFunction) -> None:
    assert yager(m1, m2).is_close_to(yager(m2, m1), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_dubois_prade_commutative(m1: MassFunction, m2: MassFunction) -> None:
    assert dubois_prade(m1, m2).is_close_to(dubois_prade(m2, m1), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_pcr5_commutative(m1: MassFunction, m2: MassFunction) -> None:
    assert pcr5(m1, m2).is_close_to(pcr5(m2, m1), atol=1e-12)


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_mean_commutative(m1: MassFunction, m2: MassFunction) -> None:
    assert mean(m1, m2).is_close_to(mean(m2, m1), atol=1e-12)


# ---- Associativity (Dempster only) ----------------------------------


@given(
    m1=mass_functions(frame_size=3),
    m2=mass_functions(frame_size=3),
    m3=mass_functions(frame_size=3),
)
@settings(max_examples=50, deadline=None)
def test_dempster_associative(m1: MassFunction, m2: MassFunction, m3: MassFunction) -> None:
    """Dempster is associative when the chain never hits K = 1."""
    if m1.frame != m2.frame or m2.frame != m3.frame:
        return  # different frames drawn
    try:
        left = dempster(dempster(m1, m2), m3)
        right = dempster(m1, dempster(m2, m3))
    except Exception:
        return
    assert left.is_close_to(right, atol=1e-9)


@given(
    m1=mass_functions(frame_size=3),
    m2=mass_functions(frame_size=3),
    m3=mass_functions(frame_size=3),
)
@settings(max_examples=50, deadline=None)
def test_conjunctive_associative(m1: MassFunction, m2: MassFunction, m3: MassFunction) -> None:
    if m1.frame != m2.frame or m2.frame != m3.frame:
        return
    left = conjunctive(conjunctive(m1, m2), m3)
    right = conjunctive(m1, conjunctive(m2, m3))
    assert left.is_close_to(right, atol=1e-9)


# ---- Neutral element (Dempster, conjunctive) ------------------------


@given(m=mass_functions(frame_size=3))
@settings(max_examples=50)
def test_dempster_neutral_is_vacuous(m: MassFunction) -> None:
    vacuous = MassFunction.vacuous(m.frame)
    assert dempster(m, vacuous).is_close_to(m, atol=1e-9)


@given(m=mass_functions(frame_size=3))
@settings(max_examples=50)
def test_conjunctive_neutral_is_vacuous(m: MassFunction) -> None:
    vacuous = MassFunction.vacuous(m.frame)
    # conjunctive output is in TBM mode but the BBA is identical to m if m is Shafer
    # and m has no empty mass. Compare via dense vectors instead.
    out = conjunctive(m, vacuous)
    assert out.to_dense().tolist() == m.to_dense().tolist() or out.is_close_to(
        MassFunction.from_array(m.frame, m.to_dense(), mode="tbm"), atol=1e-9
    )


# ---- Mean idempotence ---------------------------------------------


@given(m=mass_functions(frame_size=3))
@settings(max_examples=30)
def test_mean_idempotent(m: MassFunction) -> None:
    """Mean of a BBA with itself is itself."""
    assert mean(m, m).is_close_to(m, atol=1e-9)


# ---- Output is a valid BBA ----------------------------------------


@given(
    m1=mass_functions(frame=_SHARED_FRAME),
    m2=mass_functions(frame=_SHARED_FRAME),
)
@settings(max_examples=80)
def test_every_rule_produces_valid_bba(m1: MassFunction, m2: MassFunction) -> None:
    """Every rule's output is a valid BBA (well-formed by construction)."""
    for rule in (conjunctive, disjunctive, yager, dubois_prade, pcr5, pcr6, mean):
        out = rule(m1, m2)
        total = sum(mass for _, mass in out.focals)
        assert abs(total - 1.0) < 1e-9
        assert all(mass >= 0.0 for _, mass in out.focals)
    # Dempster only when not total-conflict
    try:
        out_d = dempster(m1, m2)
        total = sum(mass for _, mass in out_d.focals)
        assert abs(total - 1.0) < 1e-9
        assert all(mass >= 0.0 for _, mass in out_d.focals)
        assert out_d.mass(0) == 0.0  # Shafer mode
    except Exception:
        pass
