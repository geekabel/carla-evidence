# Implement cautious and bold combination rules (Denoeux 2008) — v0.2.1

<!-- labels: enhancement, tracking, milestone:v0.2.1 -->

## Summary

Phase 2 (v0.2.0) shipped eight combination rules but deliberately deferred
**cautious** and **bold** (Denoeux 2008) to v0.2.1. They require the
canonical decomposition of a non-dogmatic BBA into its weight function — a
standalone block of work (~250 lines + dedicated tests) with several design
choices that justified a separate RFC.

The design is settled in [RFC-001](../docs/rfcs/001-cautious-bold.md). This
issue tracks the implementation against the v0.2.1 release.

## Acceptance criteria

- [ ] Two new rules `cautious` and `bold` exposed in
      `carla_evidence.combination`.
- [ ] New exception `NonDogmaticError` (subclass of `EvidenceError`); both
      rules raise it on dogmatic input (RFC-001 D1).
- [ ] Dense kernel ships three log-space functions per RFC-001 D3:
      `commonality_log`, `weight_log_conjunctive`,
      `reconstruct_from_weight`.
- [ ] Regression tests reproduce Denoeux 2008 §6 examples 1 and 2 verbatim
      in `tests/regression/test_denoeux2008.py`.
- [ ] Property tests cover commutativity, associativity, neutral element
      (vacuous = max-entropy non-dogmatic input), and sparse-vs-dense
      equivalence between the two reference implementations described in
      RFC-001 D7.
- [ ] Coverage on `combination/cautious.py` and `combination/bold.py`
      ≥ 90% incl. branches.
- [ ] Numerical stability: `|Theta| = 12` with worst-case BBAs from the
      hypothesis fuzzer doesn't produce NaN, inf, or sub-tol negative
      masses.
- [ ] `multi_source` via `combine_many` overrides the default left-fold to
      compute weight functions once and take element-wise minimum
      (RFC-001 D5).
- [ ] CHANGELOG entry under `[Unreleased]` lands with the PR.

## Out of scope

- Open-world cautious (Pichon 2014) — future RFC.
- Cautious-discounting tutorial — Phase 4.
- DSmT cautious — post-DSmT enumeration scope.

## References

- Denoeux, T. (2008). Conjunctive and disjunctive combination of belief
  functions induced by nondistinct bodies of evidence. *Artificial
  Intelligence*, 172(2–3), 234–264.
- Kennes, R. (1992). Computational aspects of the Möbius transformation of
  graphs. *IEEE TSMC*, 22(2), 201–223.
- [RFC-001](../docs/rfcs/001-cautious-bold.md) — internal design doc.
