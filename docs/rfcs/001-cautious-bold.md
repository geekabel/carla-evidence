# RFC-001 — Cautious and bold combination rules (Denoeux 2008)

| Field        | Value                                                          |
|--------------|----------------------------------------------------------------|
| Status       | **Proposed**                                                   |
| Author       | Godwin K.                                                      |
| Created      | 2026-05-10                                                     |
| Lands in     | v0.2.1                                                         |
| Supersedes   | —                                                              |
| Tracks       | issue [TBD] (cautious/bold v0.2.1)                             |

## Context

Phase 2 (v0.2.0) shipped eight combination rules whose implementations all
fit the *sparse cartesian product + conflict router* template factored in
`combination/_sparse_kernel.py`. Cautious and bold (Denoeux 2008) do **not**
fit that template — they operate on the *weight function* derived from the
mass function's canonical decomposition, not on the focal mass directly.

The architecture roadmap (`carla-evidence-architecture.md` §"Phase 2 —
Tasks") originally listed cautious / bold in v0.2.0. We deferred them to
**v0.2.1** because the canonical-decomposition machinery is independent
work — ~250 lines plus dedicated tests, with several non-trivial design
choices that benefit from a separate RFC.

This RFC settles those choices so the v0.2.1 PR is a mechanical
implementation rather than a design pass.

## Definitions

For a non-dogmatic mass function $m$ on a finite frame $\Theta$
(``m(\Theta) > 0``), the **conjunctive weight function**
$w : 2^\Theta \setminus \{\Theta\} \to (0, +\infty)$ satisfies

$$
m = \bigotimes_{A \subsetneq \Theta} A^{w(A)}
\quad \text{where} \quad
A^{w} \text{ has mass } w \text{ on } \Theta \text{ and } 1-w \text{ on } A.
$$

Equivalently, via Kennes (1992) §3 and Denoeux (2008) eq. (12), the weight
function is computed from the commonality vector $q$ by

$$
w(A) = \prod_{B \supseteq A} q(B)^{(-1)^{|B|-|A|+1}}
\quad \text{for every } A \subsetneq \Theta.
$$

The **cautious rule** ($\bigotimes$, Denoeux 2008 eq. (16)) combines two
non-dogmatic BBAs by taking the *minimum* of their weight functions:

$$
m_1 \,\bigotimes\, m_2 \;=\; \bigotimes_{A \subsetneq \Theta}
                              A^{\min(w_1(A), w_2(A))}.
$$

The **bold rule** ($\bigoplus$, Denoeux 2008 eq. (28)) is the disjunctive
dual: it operates on the *disjunctive weight function* $v$ derived from the
implicability function $b(A) = \mathrm{Bel}(A) + m(\emptyset)$, and takes
the minimum.

## Decisions

### D1. Dogmatic-input handling

The cautious / bold rules require a **non-dogmatic** input
($m(\Theta) > 0$ for cautious; $m(\emptyset) > 0$ for bold). Three options
were considered:

| Option | Behaviour on dogmatic input                                     |
|--------|------------------------------------------------------------------|
| A      | Raise `InvalidMassError` with a precise message.                 |
| B      | Auto-discount with $\alpha = 1 - \varepsilon$ (default 1e-9).    |
| C      | Return the conjunctive (cautious) / disjunctive (bold) result, with a deprecation warning. |

**Decision: A.** Raising is consistent with `CLAUDE.md` §"Domain knowledge"
(no silent fallback when a methodological precondition fails). The
discounting alternative (Option B) is a *user choice*, not a library
default — Phase 4 will ship `classical_discount` explicitly. Option C
hides a methodological violation.

The error message will read:

> *Cautious rule requires `m(Theta) > 0` (non-dogmatic input). Got
> `m(Theta) = 0`. Apply `classical_discount(m, alpha=0.99)` first or use
> `dempster` / `pcr5`.*

A new exception class `NonDogmaticError(EvidenceError)` will be added to
`carla_evidence.core.exceptions` to allow downstream code to catch this
specific failure mode.

### D2. Numerical stability — log-space throughout

Computing $w(A) = \prod q(B)^{\pm 1}$ over a 256-element powerset
($|\Theta| = 8$) involves products of up to 256 terms whose exponents
alternate sign. For BBAs with very small commonality values, this overflows
or underflows in double precision.

**Decision: implement the entire weight pipeline in log-space.** Specifically:

1. Compute $\ln q(A)$ from $\ln m$ via a log-Möbius transform
   (`scipy.special.logsumexp` for the +1 exponents; an additional pass for
   the alternating signs).
2. Compute $\ln w(A) = \sum_{B \supseteq A} (-1)^{|B|-|A|+1} \ln q(B)$.
3. Cautious: $\ln w_{\bigotimes}(A) = \min(\ln w_1(A), \ln w_2(A))$.
4. Reconstruct $m = \bigotimes_A A^{w(A)}$ by sequentially combining the
   simple support functions $A^{w(A)}$ via the **conjunctive rule**, working
   from the smallest subsets up. (Each simple support has only two focal
   elements, so each step is $O(|F|)$ where $|F|$ is the running focal
   count.)

The reconstruction step in (4) goes back to mass space, but at that point
each multiplication is an $O(|F|)$ sparse cartesian product on a small BBA,
not a $|2^\Theta|$-wide product. Numerical risk is bounded.

### D3. The dense kernel

Cautious / bold genuinely need the dense $2^{|\Theta|}$ array (commonality,
weight function, log-weight). This is the role of
`combination/_dense_kernel.py`, currently a placeholder.

**Decision: ship `_dense_kernel.py` with three functions:**

```python
def commonality_log(m: MassFunction) -> npt.NDArray[np.float64]: ...
def weight_log_conjunctive(q_log: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]: ...
def reconstruct_from_weight(w_log, frame: Frame) -> MassFunction: ...
```

with all three working in log-space, contained, and reusable for any future
weight-function-based rule (e.g. cautious-discounting, Pichon's epistemic
combination).

### D4. Asymptotic complexity & frame-size cap

Each pipeline step is $O(|\Theta| \cdot 2^{|\Theta|})$ via the standard
fast-Möbius-transform recurrence (Yates 1937). For $|\Theta| \leq 12$
(4096 subsets, 49152 multiplications per rule application) this is ~1 ms
in Python, more than enough for the perception use case.

For $|\Theta| > 12$ the dense path becomes a hot loop. **Decision: emit a
`PerformanceWarning` for $|\Theta| > 12$ (configurable via
`carla_evidence.warn_dense_combination_size`).** No hard cap.

### D5. Multi-source via `combine_many`

The cautious rule **is** commutative and associative on the weight
function:
$\min(\min(w_1, w_2), w_3) = \min(w_1, \min(w_2, w_3)) = \min(w_1, w_2, w_3)$.

**Decision: override `combine_many` to compute the weight function once per
input** ($O(N \cdot |\Theta| \cdot 2^{|\Theta|})$) **and take the
element-wise minimum across all** ($O(N \cdot 2^{|\Theta|})$), then
reconstruct. This is asymptotically faster than left-folding the binary
form ($O(N^2 \cdot 2^{|\Theta|})$) and avoids accumulating numerical drift
through repeated reconstruction.

### D6. Unit-test reference values

`CLAUDE.md` §"Tests" requires every combination rule to have at least one
regression test against a literature numerical example.

**Decision: reproduce Denoeux 2008 §6 examples 1 and 2 verbatim.**
Specifically:

- Example 1 (Denoeux 2008 §6.1): $\Theta = \{a, b, c\}$ with two BBAs
  whose cautious combination is computed by hand in the paper.
- Example 2 (Denoeux 2008 §6.2): non-distinct bodies of evidence (two BBAs
  derived from the same source). Cautious is meant to handle this case
  correctly — Dempster does not.

These regression tests live in `tests/regression/test_denoeux2008.py`
alongside `test_zadeh1986.py`.

### D7. Sparse-vs-dense equivalence

The Phase 2 design template is *sparse rule + dense reference impl + property
test*. For cautious / bold the "sparse" implementation will itself use the
dense kernel (no choice — the algorithm is intrinsically dense). The
equivalent peer-review safeguard is:

**Decision: cross-check the log-space reconstruction against an
independently-coded mass-space reconstruction** that performs the conjunctive
$\bigotimes$ over simple support functions in the natural order. The two
implementations live in `tests/_references/dense_cautious.py` and
`tests/_references/mass_space_cautious.py` respectively, and agree to
`atol=1e-10` on every hypothesis-generated input.

## Out of scope for v0.2.1

- **Open-world cautious rule.** Pichon (2014) extended cautious to
  non-normalised BBAs (TBM mode). v0.2.1 ships the closed-world cautious
  only; TBM cautious lands in a future RFC.
- **Cautious discounting.** The natural pairing of Phase-4 discounting with
  cautious / bold (cautious-discount + cautious-combine) lands as a tutorial,
  not a separate rule.
- **DSmT cautious.** DSmT requires hyperpowerset enumeration; cautious on
  the hyperpowerset is post-DSmT scope.

## Acceptance criteria for the v0.2.1 PR

1. Two new rules `cautious` and `bold` exposed in
   `carla_evidence.combination`.
2. New exception `NonDogmaticError`; cautious / bold raise it on dogmatic
   input.
3. Dense kernel ships three log-space functions per D3.
4. Regression tests reproduce Denoeux 2008 §6 examples 1 and 2 (D6).
5. Property tests cover commutativity, associativity, neutral element
   (vacuous BBA, since vacuous is the maximum-entropy non-dogmatic input).
6. Coverage on `combination/cautious.py` and `bold.py` ≥ 90% incl. branches.
7. Numerical stability: `|Theta| = 12` with a worst-case BBA from the
   property fuzzer doesn't produce NaN, inf, or sub-tol negative masses.
8. CHANGELOG entry under `[Unreleased]` lands with the PR.

## References

- Denoeux, T. (2008). Conjunctive and disjunctive combination of belief
  functions induced by nondistinct bodies of evidence. *Artificial
  Intelligence*, 172(2–3), 234–264.
- Kennes, R. (1992). Computational aspects of the Möbius transformation of
  graphs. *IEEE Transactions on Systems, Man and Cybernetics*, 22(2), 201–223.
- Pichon, F., Dubois, D., Denoeux, T. (2012). Relevance and truthfulness in
  information correction and fusion. *International Journal of Approximate
  Reasoning*.
- Smets, P. (2002). The application of the matrix calculus to belief
  functions. *International Journal of Approximate Reasoning*.
- Yates, F. (1937). The design and analysis of factorial experiments. *Imperial
  Bureau of Soil Science Technical Communication 35.*
