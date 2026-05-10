"""Reference implementations of combination rules for cross-validation.

Naive O(2^|Θ| · 2^|Θ|) dense implementations used as oracles by hypothesis
property tests in :mod:`tests.property.test_combination_props`. These
implementations are deliberately written for readability, not performance —
their job is to be obviously correct so the sparse implementations in
:mod:`carla_evidence.combination` can be cross-checked.
"""
