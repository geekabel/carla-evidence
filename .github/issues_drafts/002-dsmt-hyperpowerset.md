# DSmT hyperpowerset support and DSmT-specific rules

<!-- labels: enhancement, tracking, scope:large -->

## Summary

DSmT (Smarandache-Dezert) operates on the **hyperpowerset** $D^\Theta$
rather than the Shafer powerset $2^\Theta$. The hyperpowerset is the
free distributive lattice on $|\Theta|$ generators; its size grows as
the Dedekind numbers ($D(4) = 168$, $D(5) = 7\,581$, $D(6) \approx 7.8 \times 10^6$).

Currently `MassFunction(..., mode="dsmt")` raises `NotImplementedError`.
PCR5 and PCR6 ship in v0.2.0 for the Shafer/TBM modes only; on those
frames they are mathematically well-defined.

This issue tracks the work to land:

1. Hyperpowerset enumeration for $|\Theta| \leq 5$ via the natural lattice
   recursion (or a Dedekind-number table for the count side-channel).
2. A DSmT mode for `MassFunction` whose focal subsets live in $D^\Theta$
   instead of $2^\Theta$.
3. PCR5 / PCR6 and the conjunctive family on $D^\Theta$ (the routers stay
   the same; only the lattice changes).
4. A frame-size cap with `PerformanceWarning` above $|\Theta| = 5$ and
   `NotImplementedError` above $|\Theta| = 6$ (the lattice is too large
   to enumerate naively).

## Why now? (Or rather: why not now)

DSmT enumeration is **not** a Phase 3 dependency. Phase 3 (decision +
metrics) operates over the existing focal-element representation; whether
those focals live in $2^\Theta$ or $D^\Theta$ is transparent to BetP,
plausibility transform, conflict $K$, etc.

DSmT *is* mostly demand-driven: ask the maintainers / open this issue
when an end user actually needs DSmT semantics, rather than building it
speculatively. The current "PCR5/6 on Shafer powerset" scope already
covers the autonomous-perception use cases that motivate the library.

## Open design questions

- **Lattice representation**: bitmask of generators (linear in $|\Theta|$
  but doesn't enumerate intersections), tuple of frozensets (canonical
  but slow), or DAG of nodes (fast but heavy)? Settle in a follow-up RFC.
- **Sparse-first storage**: the v0.2.0 storage format
  (`tuple[(bitmask, mass), ...]`) generalises well to a tuple of
  `(lattice_node, mass)` pairs, but `lattice_node` needs to be hashable
  and totally ordered for canonical sort.
- **Dedekind-bounded API**: do we expose a `Frame.is_exclusive` flag and
  switch lattice based on it, or do we have separate `Frame` /
  `DSmTFrame` types? The latter is cleaner but doubles the type surface.

## Out of scope

- Beyond $|\Theta| = 6$: this is methodologically inappropriate for the
  decision-aid contexts DSmT is designed for.
- Heuristic / approximate enumeration: not worth the complexity for the
  $|\Theta| \leq 5$ regime that real applications use.

## References

- Smarandache, F. & Dezert, J. (2004–2015). *Advances and Applications of
  DSmT for Information Fusion*, vols. 1–4.
- OEIS A000372 — Dedekind numbers.
