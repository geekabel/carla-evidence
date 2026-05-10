# Combination rules

Combining two BBAs $m_1$ and $m_2$ on a shared frame $\Theta$ requires a
**rule** — a mathematical commitment about *how the conflicting evidence is
treated*. There is no universally best rule; each makes a different
trade-off. `carla-evidence` v0.2.0 ships eight rules; cautious and bold
(Denoeux 2008) land in v0.2.1.

## The cartesian product, factored

Most rules iterate the cartesian product over focal pairs and route the
product mass $m_1(B) \cdot m_2(C)$ to one or more target subsets. The
library factors that loop into a single sparse kernel
(`combination/_sparse_kernel.py`); each rule is a routing policy. Complexity
is $O(|F_1| \cdot |F_2|)$ in the number of focal elements — well below the
naive $O(2^{|\Theta|} \cdot 2^{|\Theta|})$ dense reference impl.

The mean rule does not use the cartesian product at all (it averages
focal-by-focal). PCR6 uses an N-ary cartesian product, generalising PCR5.

## Conflict routing in one table

| Rule          | When $B \cap C = \emptyset$, send the product to                                            | Output mode |
|---------------|---------------------------------------------------------------------------------------------|-------------|
| conjunctive   | $\emptyset$ (kept as conflict mass)                                                          | tbm         |
| dempster      | $\emptyset$, then divide every other entry by $1 - K$; raise if $K = 1$                       | shafer      |
| disjunctive   | (no conflict; the rule routes to $B \cup C$ regardless of intersection)                     | shafer      |
| yager         | $\Theta$                                                                                    | shafer      |
| dubois\_prade | $B \cup C$                                                                                  | shafer      |
| pcr5          | proportional split: $\Delta B = m_1(B)^2 m_2(C) / (m_1(B) + m_2(C))$, symmetric for $C$       | shafer      |
| pcr6          | N-ary generalisation of pcr5 (Martin-Osswald 2006)                                          | shafer      |
| mean          | (no cartesian product; arithmetic average focal-by-focal)                                   | inherits    |

## Picking a rule

The choice depends on **what you want to do with conflict**:

- **You believe both sources are independent and reliable** → Dempster.
  Be ready to handle `TotalConflictError` when $K = 1$. Be wary of the Zadeh
  paradox at high $K$.
- **You'd rather acknowledge confusion than commit** → Yager. Conflict
  mass piles up on $\Theta$, leaving the decision-maker to ask for more
  evidence.
- **Conflicts are local and the joint support is informative** →
  Dubois-Prade. Mass on $B \cup C$ when sources disagree but their union is
  smaller than $\Theta$.
- **Decision-making under high conflict** → PCR5 (2 sources) or PCR6 (3+
  sources). The conflicting mass is fed back into the actual hypotheses
  rather than collapsed onto a survivor.
- **Robust baseline / aggregating many noisy sources** → mean (Murphy
  2000). Idempotent, never amplifies, never sharpens.
- **Raw evidence, deferring the conflict decision** → conjunctive. The
  result has $m(\emptyset) > 0$ which downstream code can normalise (Dempster),
  redirect (Yager / Dubois-Prade), or redistribute (PCR5).

## Three traps to avoid

1. **Dempster on near-total conflict.** The rule is technically defined for
   $K < 1$, but the *result* becomes numerically unstable as $K \to 1$. The
   Zadeh paradox shows the qualitative failure (Tutorial 2). For high-conflict
   regimes, prefer Yager / Dubois-Prade / PCR5.
2. **Iterating PCR5 over 3+ sources.** PCR5 is not associative; iterating
   it gives different results depending on the fusion order. The library
   raises `NotImplementedError` and points to PCR6 — `CLAUDE.md`
   §"Domain knowledge — pièges critiques", point 3.
3. **Treating $K = 1$ as a numerical edge case.** It is a methodological
   signal that the two sources are incompatible. The library raises
   `TotalConflictError` rather than returning `NaN`; do not paper over it
   with a `try/except` that returns the vacuous BBA — investigate why your
   sources contradict.

## What's next

- **v0.2.1** — Cautious and bold rules (Denoeux 2008), via canonical
  decomposition (Möbius / log-Möbius transform of the commonality vector,
  Kennes 1992).
- **Phase 3** — decision transforms (BetP, plausibility transform) and
  uncertainty metrics (conflict $K$, non-specificity, discord, $AU$,
  Jousselme distance) so the fused BBA can be turned into a decision.
- **Phase 4** — discounting (Shafer 1976 classical, Mercier 2008
  contextual), often applied *before* combination to model unreliable
  sources.

## References

- Smets, P. (1990). The combination of evidence in the Transferable Belief
  Model. *IEEE TPAMI*.
- Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton UP, §3.1.
- Dubois, D. & Prade, H. (1986). On the combination of uncertain or imprecise
  pieces of information in rule-based systems. *IJAR*.
- Yager, R. R. (1987). On the Dempster-Shafer framework and new combination
  rules. *Information Sciences*.
- Dubois, D. & Prade, H. (1988). Representation and combination of uncertainty
  with belief functions and possibility measures. *Computational Intelligence*.
- Smarandache, F. & Dezert, J. (2005). *Information Fusion Based on New
  Proportional Conflict Redistribution Rules*.
- Martin, A. & Osswald, C. (2006). A new generalization of the Proportional
  Conflict Redistribution rule stable in terms of decision (PCR6).
- Murphy, C. K. (2000). Combining belief functions when evidence conflicts.
  *Decision Support Systems*.
- Zadeh, L. A. (1986). A simple view of the Dempster-Shafer theory of evidence
  and its implication for the rule of combination. *AI Magazine*.
