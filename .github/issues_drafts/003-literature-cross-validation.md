# Literature cross-validation: numerical regression suite

<!-- labels: tests, tracking, good-first-issue -->

## Summary

We currently have one regression test against a literature numerical
example (`tests/regression/test_zadeh1986.py` for Zadeh 1986). For the
peer-review credibility we want at JOSS submission time, we should
cross-check every implemented operator against at least one canonical
numerical example.

This is a **continuous** issue — every PR that adds an operator, every
review of an existing one, every reference paper we read should result
in a regression test added here.

## Targets

| Operator family   | Reference                                            | Status |
|-------------------|------------------------------------------------------|--------|
| Conjunctive       | Smets (1990), §3 examples                            | TODO   |
| Dempster          | Shafer (1976), §3.1 worked examples                  | TODO   |
| Disjunctive       | Dubois-Prade (1986), §4                              | TODO   |
| Yager             | Yager (1987), §4 numerical examples                  | TODO   |
| Dubois-Prade      | Dubois-Prade (1988), §5                              | TODO   |
| PCR5              | Smarandache-Dezert (2005), §3 worked examples        | TODO   |
| PCR6              | Martin-Osswald (2006), §4 worked examples            | TODO   |
| Mean              | Murphy (2000), §3 case study                         | TODO   |
| Zadeh paradox     | Zadeh (1986)                                         | done   |
| Cautious / bold   | Denoeux (2008), §6 examples 1 & 2                    | v0.2.1 |
| Pignistic         | Smets (2005), §3 numerical examples                  | Phase 3|
| Plausibility xfm  | Cobb-Shenoy (2006), §4                               | Phase 3|
| Jousselme distance| Jousselme et al. (2001), §4                          | Phase 3|
| Klir-Wierman AU   | Klir-Wierman (1999), Ch. 6 examples                  | Phase 3|
| Mercier discount. | Mercier-Quost-Denoeux (2008), §5 case study          | Phase 4|

## Process

For each row above:

1. Read the cited source and locate a worked numerical example with
   tabulated input BBAs and expected output.
2. Reproduce the example in a `tests/regression/test_<author><year>.py`
   file (one file per author-year for grep-ability).
3. Use `pytest.approx` with the smallest tolerance that the source's
   stated precision supports (typically `1e-4` for hand-computed
   examples, `1e-9` for examples with full double-precision output).
4. Cite the reference at the top of the file, including page numbers
   and equation labels.
5. Update the table above in this issue.

## Why this is a `good-first-issue`

Each row is independent. A new contributor can pick one row, add
~30 lines of test code, and ship a meaningful PR without needing to
understand the rest of the library deeply. The bibliographic work is
half the contribution.
