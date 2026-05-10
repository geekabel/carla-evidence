"""Core layer (Layer 1): frame of discernment, mass functions, powerset utilities.

This package depends only on ``numpy`` and ``scipy``. Modifications here have
project-wide impact — changes require explicit user confirmation per
``CLAUDE.md`` §"Quand demander confirmation utilisateur".
"""

from carla_evidence.core.encoding import (
    cardinality,
    complement,
    full_mask,
    intersection,
    is_proper_subset,
    is_subset,
    iter_subsets_of,
    union,
)
from carla_evidence.core.exceptions import (
    EvidenceError,
    FrameError,
    FrameMismatchError,
    InvalidMassError,
    ModeError,
    TotalConflictError,
)
from carla_evidence.core.frame import Frame
from carla_evidence.core.mass import DEFAULT_TOL, MassFunction, Mode, SubsetSpec
from carla_evidence.core.powerset import (
    iter_focal_pairs,
    iter_powerset,
    iter_powerset_masks,
)

__all__ = [
    "DEFAULT_TOL",
    "EvidenceError",
    "Frame",
    "FrameError",
    "FrameMismatchError",
    "InvalidMassError",
    "MassFunction",
    "Mode",
    "ModeError",
    "SubsetSpec",
    "TotalConflictError",
    "cardinality",
    "complement",
    "full_mask",
    "intersection",
    "is_proper_subset",
    "is_subset",
    "iter_focal_pairs",
    "iter_powerset",
    "iter_powerset_masks",
    "iter_subsets_of",
    "union",
]
