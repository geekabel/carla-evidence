"""Combination layer (Layer 2): rules to fuse two or more mass functions.

Catalogue (planned, lands in v0.2.0): ``conjunctive``, ``dempster``, ``disjunctive``,
``yager``, ``dubois_prade``, ``pcr5``, ``pcr6``, ``cautious``, ``bold``, ``mean``.

Every rule inherits from :class:`carla_evidence.combination.base.CombinationRule` and
ships with literature-cited unit tests, hypothesis property tests (commutativity,
neutral element), and at least one numerical regression test from a canonical paper.
"""
