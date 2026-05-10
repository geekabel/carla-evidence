"""Combination layer (Layer 2): rules to fuse two or more mass functions.

Eight rules ship in v0.2.0; cautious / bold (Denoeux 2008) land in v0.2.1
once the canonical-decomposition machinery (Möbius / log-Möbius transform of
the commonality vector) is implemented.

================  ====================================================  ==========
Rule              Behaviour on conflict ``B intersect C = empty-set``   Output mode
================  ====================================================  ==========
``conjunctive``   keeps mass on ``empty-set``                           tbm
``dempster``      normalises by ``1 / (1 - K)`` (raises if ``K = 1``)   shafer
``disjunctive``   not generated (uses ``B union C``)                    shafer
``yager``         redirected to ``Theta``                               shafer
``dubois_prade``  redirected to ``B union C``                           shafer
``pcr5``          redistributed onto ``B`` and ``C`` (2 sources)        shafer
``pcr6``          redistributed onto every conflicting focal            shafer
``mean``          arithmetic mean (no cartesian product)                inherits
================  ====================================================  ==========

Every rule is a callable instance: ``dempster(m1, m2)``,
``pcr6([m1, m2, m3])``, etc. The :class:`CombinationRule` ABC also exposes
``combine`` and ``combine_many`` for explicit dispatch.
"""

from carla_evidence.combination.base import CombinationRule
from carla_evidence.combination.conjunctive import ConjunctiveRule, conjunctive
from carla_evidence.combination.dempster import DempsterRule, dempster
from carla_evidence.combination.disjunctive import DisjunctiveRule, disjunctive
from carla_evidence.combination.dubois_prade import DuboisPradeRule, dubois_prade
from carla_evidence.combination.mean import MeanRule, mean
from carla_evidence.combination.pcr5 import PCR5Rule, pcr5
from carla_evidence.combination.pcr6 import PCR6Rule, pcr6
from carla_evidence.combination.yager import YagerRule, yager

__all__ = [
    "CombinationRule",
    "ConjunctiveRule",
    "DempsterRule",
    "DisjunctiveRule",
    "DuboisPradeRule",
    "MeanRule",
    "PCR5Rule",
    "PCR6Rule",
    "YagerRule",
    "conjunctive",
    "dempster",
    "disjunctive",
    "dubois_prade",
    "mean",
    "pcr5",
    "pcr6",
    "yager",
]
