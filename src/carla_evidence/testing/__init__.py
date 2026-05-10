"""Hypothesis strategies for property-based testing of evidential code.

Lands in v0.1.0 alongside :class:`MassFunction`. The planned public surface includes
``mass_functions(frame_size=...)``, ``frames(min_size=..., max_size=...)``,
``categorical_bbas(...)``, and ``bayesian_bbas(...)`` so downstream users (and our
own tests) can write property tests against canonical strategies.
"""
