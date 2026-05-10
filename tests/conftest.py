"""Top-level pytest configuration.

Hypothesis profiles, shared fixtures, and import gating for optional adapters
live here.

The active profile is selected by the ``HYPOTHESIS_PROFILE`` environment
variable (``dev`` by default, ``ci`` in CI). The ``ci`` profile runs 500
examples per property — about ten times the dev volume — so it can surface
counter-examples the dev profile misses without slowing local iteration.
"""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "dev",
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile(
    "ci",
    max_examples=500,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

_active = os.environ.get("HYPOTHESIS_PROFILE", "dev")
settings.load_profile(_active)
