"""Construction layer (Layer 3): convert sensor outputs into mass functions.

Builders for softmax classifier output, 2D/3D detectors, lidar clusters, and
radar tracks (Doppler-aware). Inputs are validated with Pydantic models. Depends on
:mod:`carla_evidence.core` and ``pydantic`` only. Lands in v0.5.0 (Phase 5).
"""
