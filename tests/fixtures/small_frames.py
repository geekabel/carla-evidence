"""Small canonical frames reused across the test suite."""

from __future__ import annotations

from carla_evidence import Frame

# A two-element frame, the smallest non-trivial case.
THETA_BINARY: Frame = Frame.of("yes", "no")

# A three-element frame matching the "three-suspects" archetype used in
# many Shafer/Smets examples (Peter, Paul, Mary).
THETA_SUSPECTS: Frame = Frame.of("peter", "paul", "mary")

# Four-element frame matching the canonical perception use case
# (vehicle, truck, pedestrian, cyclist).
THETA_OBJECTS: Frame = Frame.of("car", "truck", "pedestrian", "cyclist")
