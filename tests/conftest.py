"""Top-level pytest configuration.

Hypothesis profiles, shared fixtures, and import gating for optional adapters land
here as Phase 1+ ships. For Phase 0 we only register the hypothesis ``ci`` profile so
``pytest --hypothesis-profile=ci`` already works in CI before the strategies module
exists.
"""

from __future__ import annotations

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
settings.load_profile("dev")
