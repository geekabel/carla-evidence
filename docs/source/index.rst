carla-evidence
==============

.. note::

   The library is in **Phase 0 — bootstrap**. The public API will land in v0.1.0.
   This documentation will fill in as phases ship; in the meantime, see the
   roadmap in `carla-evidence-architecture.md`_.

.. _carla-evidence-architecture.md: https://github.com/geekabel/carla-evidence/blob/main/carla-evidence-architecture.md

Mission
-------

`carla-evidence` is a Python library for evidential (Dempster-Shafer / DSmT) sensor
fusion applied to autonomous-vehicle perception, with first-class CARLA and ROS 2
adapters, reproducible benchmarks, and rigorous mathematical foundations.

Layered architecture
--------------------

* **Layer 1 — Core**: :class:`Frame`, :class:`MassFunction`, powerset utilities.
* **Layer 2 — Operators**: combination, discounting, decision, metrics.
* **Layer 3 — Construction**: build BBAs from softmax / detection / lidar / radar.
* **Layer 4 — Adapters**: CARLA, ROS 2, OpenCDA, visualization.
* **Layer 5 — Applications**: examples, benchmarks, scenarios.

A layer only depends on layers below it.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   concepts/index
   tutorials/index
   how_to/index
   api/index
   theory_refs/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
