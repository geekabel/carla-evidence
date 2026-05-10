# carla-evidence

[![CI](https://github.com/geekabel/carla-evidence/actions/workflows/ci.yml/badge.svg)](https://github.com/geekabel/carla-evidence/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/carla-evidence/badge/?version=latest)](https://carla-evidence.readthedocs.io/en/latest/?badge=latest)
[![License: BSD-3](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230)](https://github.com/astral-sh/ruff)

> Evidential (Dempster-Shafer / DSmT) sensor fusion for autonomous driving — with first-class CARLA and ROS 2 adapters.

`carla-evidence` is a Python library for **belief-function-based sensor fusion** built for
researchers and R&D engineers in autonomous perception. It implements the canonical
combination rules (Dempster, conjunctive, disjunctive, Yager, Dubois-Prade, PCR5/PCR6,
cautious/bold), discounting (Shafer, Mercier contextual, temporal decay), decision
transforms (BetP, plausibility, max-belief), and uncertainty metrics (conflict,
non-specificity, discord, Jousselme distance) over Shafer powersets and DSmT
hyperpowersets.

The mathematical core is **frame-agnostic** and depends only on `numpy`, `scipy`,
`pydantic`. CARLA, ROS 2, OpenCDA, ML and visualization layers are isolated optional
extras.

## Status

**Phase 0 — bootstrap.** The package is currently a scaffold; the core API will land in
v0.1.0. See [`carla-evidence-architecture.md`](carla-evidence-architecture.md) for the
full roadmap and [`CHANGELOG.md`](CHANGELOG.md) for what is shipped.

## Installation

```bash
# Core (numpy, scipy, pydantic)
pip install carla-evidence

# With visualization
pip install "carla-evidence[viz]"

# With CARLA adapter
pip install "carla-evidence[carla]"

# With ML extras (torch, autograd-friendly BBA construction)
pip install "carla-evidence[ml]"

# Development install (from a clone)
git clone https://github.com/geekabel/carla-evidence
cd carla-evidence
pip install -e ".[dev]"
pre-commit install
```

Python 3.10 or newer is required.

## Quick example

```python
from carla_evidence import Frame, MassFunction
from carla_evidence.combination import dempster
from carla_evidence.decision import betp

theta = Frame(["car", "truck", "pedestrian", "cyclist"])

m1 = MassFunction.from_dict(
    theta,
    {("car",): 0.6, ("car", "truck"): 0.3, theta.omega: 0.1},
)
m2 = MassFunction.from_softmax(
    theta,
    probs=[0.7, 0.2, 0.05, 0.05],
    nonspec_factor=0.15,
)

m_fused = dempster(m1, m2)
print(betp(m_fused))
```

This API will be available starting **v0.1.0** (Phase 1).

## Documentation

Full documentation, tutorials, and theory references live at
<https://carla-evidence.readthedocs.io>.

## Citing

If you use `carla-evidence` in academic work, please cite via the metadata in
[`CITATION.cff`](CITATION.cff). A JOSS paper and a Zenodo DOI will accompany v1.0.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development workflow, conventional commits,
and how to add a new combination rule. By participating you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md).

## License

[BSD-3-Clause](LICENSE) — © 2026
