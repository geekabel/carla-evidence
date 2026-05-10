# Mass functions

A **mass function** (also called a *Basic Belief Assignment*, BBA) on a frame
of discernment $\Theta$ is a map

$$
m : 2^\Theta \to [0, 1], \qquad
\sum_{A \subseteq \Theta} m(A) = 1, \qquad
m(A) \geq 0 \;\; \forall A.
$$

The mass $m(A)$ quantifies the share of evidence that *exactly* commits to the
hypothesis "the truth is one of the elements of $A$, but I cannot say which" —
without leaking into any strict subset of $A$. A subset with $m(A) > 0$ is
called a *focal element*; the collection of focal elements is the *core* of
$m$.

## Belief, plausibility, commonality

From any mass function we derive three companion functions:

$$
\mathrm{Bel}(A) = \sum_{\emptyset \neq B \subseteq A} m(B),
\qquad
\mathrm{Pl}(A) = \sum_{B \cap A \neq \emptyset} m(B),
\qquad
Q(A) = \sum_{B \supseteq A} m(B).
$$

- $\mathrm{Bel}(A)$ — total mass that *implies* $A$.
- $\mathrm{Pl}(A)$ — total mass that *does not contradict* $A$.
- $Q(A)$ — *commonality*: total mass on every superset of $A$ (used by
  Dempster's rule and by the Möbius transform).

They satisfy $\mathrm{Bel}(A) \leq \mathrm{Pl}(A)$ for every $A$. The
*credibility interval* $[\mathrm{Bel}(A), \mathrm{Pl}(A)]$ summarises the
uncertainty on $A$ — it is degenerate only when the BBA is Bayesian.

## Modes

`carla-evidence` recognises three theoretical regimes through the `mode`
parameter on `MassFunction`. The mathematical pitfalls behind each are
documented in `CLAUDE.md` §"Domain knowledge — pièges critiques":

| Mode      | $m(\emptyset)$         | Interpretation                        |
| --------- | ---------------------- | ------------------------------------- |
| `shafer`  | $= 0$ (enforced)       | Closed-world; Dempster's framework.   |
| `tbm`     | $\geq 0$ (allowed)     | Open-world; Smets's TBM.              |
| `dsmt`    | (NotImplementedError)  | DSmT hyperpowerset; lands in v0.2.0.  |

A non-zero $m(\emptyset)$ in TBM mode encodes the belief that the truth lies
*outside* $\Theta$. Switching modes after the fact is intentionally not a
single-line operation — converting requires a normalisation choice the user
must make explicitly.

## Special BBAs

| Helper                          | Meaning                                                   |
| ------------------------------- | --------------------------------------------------------- |
| `MassFunction.vacuous(theta)`   | Total ignorance: $m(\Theta) = 1$.                         |
| `MassFunction.categorical(...)` | Certainty: $m(A) = 1$ for one subset.                     |
| `MassFunction.bayesian(...)`    | Singleton focals only; collapses to ordinary probability. |

For Bayesian BBAs $\mathrm{Bel}(A) = \mathrm{Pl}(A) = \sum_{x \in A} m(\{x\})$
— the credibility interval degenerates and the BBA is equivalent to a
probability distribution.

## Storage

Internally, a `MassFunction` is stored sparsely as a tuple of
`(bitmask, mass)` pairs sorted by `bitmask` (zero-mass entries dropped). The
bitmask encoding is documented in
{mod}`carla_evidence.core.encoding`. For algorithms that need a dense
$2^{|\Theta|}$ view, `to_dense()`, `to_bel_vector()`, `to_pl_vector()`, and
`to_q_vector()` produce the corresponding `numpy.ndarray` on demand.

## References

- Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton UP.
  — chapters 1 and 2 introduce $m$, $\mathrm{Bel}$, $\mathrm{Pl}$, $Q$.
- Smets, P. (1990). The combination of evidence in the Transferable Belief
  Model. *IEEE TPAMI* — open-world semantics for $m(\emptyset) > 0$.
- Smarandache, F. & Dezert, J. (2004). *Advances and Applications of DSmT
  for Information Fusion*, Vol. 1 — hyperpowerset and DSmT framework.
