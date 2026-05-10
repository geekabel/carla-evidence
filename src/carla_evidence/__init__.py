"""carla-evidence: evidential (Dempster-Shafer / DSmT) sensor fusion for autonomous driving.

The public API is layered (see ``carla-evidence-architecture.md`` §4):

- :mod:`carla_evidence.core` — :class:`Frame`, :class:`MassFunction`, powerset utilities.
- :mod:`carla_evidence.combination` — Dempster, conjunctive, disjunctive, Yager,
  Dubois-Prade, PCR5/PCR6, cautious/bold, mean.
- :mod:`carla_evidence.discounting` — classical (Shafer), contextual (Mercier), temporal.
- :mod:`carla_evidence.decision` — BetP, plausibility transform, max-belief, intervals.
- :mod:`carla_evidence.metrics` — conflict, non-specificity, discord, AU, Jousselme.
- :mod:`carla_evidence.construction` — BBA from softmax / lidar / radar / detection.

The ``carla``, ``ros``, ``opencda``, and ``viz`` adapters are optional and live behind
extras (see ``pyproject.toml``).
"""

from __future__ import annotations

try:
    from carla_evidence._version import version as __version__
except ImportError:
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
