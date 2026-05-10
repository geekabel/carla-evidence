# `carla-evidence` — Architecture & Roadmap complète

> Librairie Python de référence pour la fusion évidentielle (Dempster-Shafer / DSmT)
> appliquée à la perception véhicule, avec adaptateurs CARLA et ROS2 first-class.

---

## 1. Vision

**Mission** : devenir l'équivalent évidentiel de ce que `OpenCOOD` est au deep learning coopératif. Une librairie *réutilisée* par tout chercheur travaillant sur DS/DSmT en automotive, avec une API stable, une documentation propre, et des benchmarks reproductibles.

**Trois critères de succès à 18 mois** :

1. Citée dans ≥ 10 papiers indépendants (hors UTBM)
2. Importée par ≥ 1 framework tiers (intégration OpenCDA, ms-van3t, ou autre)
3. Soumise et acceptée à JOSS (Journal of Open Source Software)

---

## 2. Principes de design

| Principe | Conséquence concrète |
|---|---|
| **Modularité dure** | construction / combination / discounting / decision = 4 sous-packages indépendants. On peut remplacer chacun sans toucher les autres. |
| **Frame-agnostic** | Pas de hardcode pour Θ = {occupied, free}. Support DSmT (frame ouvert, hyperpowerset). |
| **Vectorisation** | numpy par défaut, backend torch optionnel via extra `[ml]` (GPU + autograd pour learning). |
| **Standard-compliant** | Notation Shafer (1976), sémantique Smets (TBM, 1990), DSmT (Smarandache-Dezert). |
| **CARLA-friendly mais pas CARLA-locked** | Le core fonctionne sans CARLA. L'adapter est un sous-package optionnel. |
| **Reproductibilité** | Seeds explicites, déterminisme par défaut, scénarios versionnés (DOI). |
| **Performance honnête** | Profiling continu (asv ou pytest-benchmark). Régression de perf = CI rouge. |
| **Type safety** | mypy strict sur `src/`. Tous les API publics typés. |

---

## 3. Stack technique

```
Python ≥ 3.10
  ├── numpy ≥ 1.24       (core)
  ├── scipy ≥ 1.10       (optimization, special)
  ├── torch ≥ 2.0        (extra [ml], optionnel)
  ├── carla ≥ 0.9.15     (extra [carla])
  ├── opencda            (extra [carla])
  ├── rclpy              (extra [ros])
  ├── matplotlib         (viz)
  ├── plotly             (viz interactive)
  ├── pydantic ≥ 2.0     (sensor input validation)
  ├── pytest ≥ 7.0       (tests)
  ├── hypothesis ≥ 6.0   (property-based tests)
  ├── pytest-benchmark   (perf)
  ├── ruff               (lint)
  ├── black              (format)
  ├── mypy               (types)
  ├── sphinx + myst      (docs)
  └── pre-commit         (hooks)
```

---

## 4. Architecture en couches

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5 — Applications: examples, benchmarks, scenarios CARLA  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4 — Adapters: carla.*, ros.*, opencda.*, viz.*           │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3 — Construction: from_softmax, from_lidar, from_radar…  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2 — Operators: combination, discounting, decision, metric│
├─────────────────────────────────────────────────────────────────┤
│  Layer 1 — Core: Frame, MassFunction, Powerset, Encoding        │
└─────────────────────────────────────────────────────────────────┘
```

**Règle d'or** : une couche ne dépend que des couches inférieures. Pas de couplage horizontal.

---

## 5. Structure du package

```
carla-evidence/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── LICENSE                         # BSD-3-Clause
├── CITATION.cff                    # citation propre + DOI Zenodo
├── CHANGELOG.md                    # auto-généré (semantic-release)
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md              # Contributor Covenant 2.1
│
├── docs/
│   ├── source/
│   │   ├── conf.py
│   │   ├── index.rst
│   │   ├── concepts/               # primer DS/DSmT (Shafer, Smets, DSmT)
│   │   ├── api/                    # autogénéré
│   │   ├── tutorials/              # 6 notebooks pédagogiques
│   │   ├── how_to/                 # cookbook : ajouter une règle, etc.
│   │   └── theory_refs/            # bibliographie canonique
│   └── Makefile
│
├── src/
│   └── carla_evidence/
│       ├── __init__.py
│       ├── _version.py             # géré par setuptools-scm
│       │
│       ├── core/
│       │   ├── frame.py            # Frame, FrameElement
│       │   ├── mass.py             # MassFunction (immutable)
│       │   ├── powerset.py         # enumeration + cache
│       │   ├── encoding.py         # bitmask <-> set conversions
│       │   └── exceptions.py
│       │
│       ├── combination/
│       │   ├── base.py             # CombinationRule ABC
│       │   ├── conjunctive.py      # Smets unnormalized
│       │   ├── dempster.py         # Shafer normalized
│       │   ├── disjunctive.py
│       │   ├── yager.py
│       │   ├── dubois_prade.py
│       │   ├── pcr5.py             # DSmT
│       │   ├── pcr6.py             # DSmT
│       │   ├── cautious.py         # Denoeux 2008
│       │   ├── bold.py             # disjonction prudente
│       │   ├── mean.py             # moyenne arithmétique
│       │   └── _utils.py
│       │
│       ├── discounting/
│       │   ├── classical.py        # α-discounting Shafer
│       │   ├── contextual.py       # Mercier 2012
│       │   └── temporal.py         # decay temporel
│       │
│       ├── decision/
│       │   ├── pignistic.py        # BetP
│       │   ├── plausibility.py     # PlP
│       │   ├── max_belief.py
│       │   └── interval.py         # [Bel, Pl]
│       │
│       ├── metrics/
│       │   ├── conflict.py         # K, weight of conflict
│       │   ├── uncertainty.py      # nonspecificity, discord, AU
│       │   ├── distance.py         # Jousselme
│       │   └── divergence.py       # Belief divergences
│       │
│       ├── construction/
│       │   ├── base.py             # BBABuilder ABC
│       │   ├── from_softmax.py     # NN classifier output -> BBA
│       │   ├── from_lidar.py       # geometric features -> BBA
│       │   ├── from_radar.py       # Doppler-aware BBA
│       │   ├── from_detection.py   # bbox + score -> BBA
│       │   └── inputs.py           # Pydantic models
│       │
│       ├── carla/
│       │   ├── sensor_wrappers.py
│       │   ├── ego.py
│       │   ├── recorder.py         # save sensor streams
│       │   └── scenarios/
│       │       ├── intersection_occlusion.py
│       │       ├── dense_traffic.py
│       │       ├── v2x_packet_loss.py
│       │       └── adversarial_ghost.py
│       │
│       ├── ros/
│       │   ├── nodes.py
│       │   └── msgs/               # custom MassFunction msg
│       │
│       ├── opencda/
│       │   └── fusion_module.py    # drop-in replacement
│       │
│       ├── viz/
│       │   ├── focal_plot.py       # Venn-like for small Θ
│       │   ├── conflict_plot.py    # K(t) trajectory
│       │   ├── grid_plot.py        # EOGM heatmaps
│       │   └── uncertainty_plot.py
│       │
│       └── benchmarks/
│           ├── scenarios/
│           ├── metrics_eval.py
│           └── report.py           # generate reproducible reports
│
├── tests/
│   ├── conftest.py
│   ├── unit/                       # pure function tests
│   ├── property/                   # hypothesis-based
│   ├── regression/                 # known numerical canon
│   ├── integration/
│   └── fixtures/
│       ├── small_frames.py
│       └── canonical_bbas.py
│
├── benchmarks/                     # pytest-benchmark
│   ├── bench_combination.py
│   ├── bench_decision.py
│   └── asv.conf.json
│
├── examples/
│   ├── 01_basic_fusion.ipynb
│   ├── 02_zadeh_paradox.ipynb
│   ├── 03_pcr5_vs_dempster.ipynb
│   ├── 04_carla_lidar_camera.ipynb
│   ├── 05_v2x_cooperative.ipynb
│   └── 06_evidential_grid.ipynb
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── docs.yml
│   │   ├── release.yml
│   │   └── benchmark.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .pre-commit-config.yaml
├── .gitignore
├── .editorconfig
└── .readthedocs.yaml
```

---

## 6. API canonique (preview, sera figée à v1.0)

```python
from carla_evidence import Frame, MassFunction
from carla_evidence.combination import dempster, pcr6, cautious
from carla_evidence.discounting import classical, contextual
from carla_evidence.decision import betp, plausibility
from carla_evidence.metrics import conflict, jousselme_distance

# 1. Frame de discernement
theta = Frame(["car", "truck", "pedestrian", "cyclist"])

# 2. BBA construction
m1 = MassFunction.from_dict(
    theta,
    {("car",): 0.6, ("car", "truck"): 0.3, theta.omega: 0.1},
)
m2 = MassFunction.from_softmax(
    theta,
    probs=[0.7, 0.2, 0.05, 0.05],
    nonspec_factor=0.15,
)

# 3. Discounting (reliability α=0.85)
m1_disc = classical(m1, alpha=0.85)

# 4. Combination
m_fused = dempster(m1_disc, m2)
# Or: pcr6([m1_disc, m2, m3]) for multi-source DSmT

# 5. Decision
betp_dist = betp(m_fused)              # → np.ndarray, distrib pignistique
pl = plausibility(m_fused)             # → dict {subset: pl}
decision = m_fused.max_belief()        # → singleton with highest belief

# 6. Metrics
K = conflict(m1_disc, m2)              # scalar in [0, 1]
d = jousselme_distance(m1, m2)         # scalar in [0, 1]
```

**Invariants** :

- `MassFunction` est immutable (frozen dataclass). Toutes les opérations retournent une nouvelle instance.
- `Frame` est hashable, comparable par identité ET valeur.
- Les opérations vectorielles supportent `MassFunction[]` (batch) sans changement d'API.

---

## 7. Roadmap par phases (mode plan complet)

### Phase 0 — Bootstrap (Semaine 1)

**Objectif** : repo opérationnel, CI verte minimale.

- [ ] `pyproject.toml` (PEP 621, setuptools-scm pour versioning)
- [ ] Structure `src/carla_evidence/` vide mais importable
- [ ] `.pre-commit-config.yaml` (ruff, black, mypy, end-of-file-fixer)
- [ ] `.github/workflows/ci.yml` minimal (lint + format check)
- [ ] `README.md` skeleton (mission, badges, install, citation)
- [ ] `LICENSE` (BSD-3-Clause)
- [ ] `CITATION.cff` avec placeholder DOI
- [ ] `CHANGELOG.md` initialisé
- [ ] `.editorconfig`, `.gitignore`
- [ ] Issue + PR templates
- [ ] `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1)
- [ ] Sphinx doc skeleton + Read the Docs config

**Deliverable** : `pip install -e ".[dev]"` fonctionne, CI verte sur PR vide.

---

### Phase 1 — Core v0.1.0 (Semaines 2-4)

**Objectif** : représentation BBA et opérations de base.

- [ ] `Frame` : dataclass immutable, `omega` = singleton du frame complet, `powerset()` cached
- [ ] `MassFunction` :
  - [ ] Stockage dense (vector size 2^|Θ|) pour |Θ| ≤ 14
  - [ ] Stockage sparse (dict) pour |Θ| > 14
  - [ ] Validation à la construction : Σm = 1, m(A) ≥ 0 ∀A
  - [ ] Mode TBM (m(∅) ≥ 0 autorisé) vs Shafer (m(∅) = 0 enforced)
  - [ ] Mode DSmT (hyperpowerset, frame non-exclusif)
- [ ] `bel()`, `pl()`, `q()` (commonality)
- [ ] Subset enumeration via bitmask (numpy uint64 pour |Θ| ≤ 64)
- [ ] Helpers : `vacuous(frame)`, `categorical(frame, subset)`, `bayesian(frame, probs)`
- [ ] Sérialisation : to_dict/from_dict, to_json, equality

**Tests** :

- [ ] Unit : 100% du core
- [ ] Property : Σm = 1 conservé après toute construction valide
- [ ] Property : Bel(A) + Bel(¬A) ≤ 1 (sub-additivité)
- [ ] Regression : exemples Shafer (1976) chap. 2

**Deliverable** : `MassFunction` utilisable, doc tutoriel 1 publiée.

---

### Phase 2 — Combination v0.2.0 (Semaines 5-8)

**Objectif** : catalogue complet des règles.

| Règle | Formule | Référence |
|---|---|---|
| Conjunctive | $m_∩(A) = \sum_{B∩C=A} m_1(B)m_2(C)$ | Smets 1990 |
| Dempster | conjunctive normalisée par $1/(1-K)$ | Shafer 1976 |
| Disjunctive | $m_∪(A) = \sum_{B∪C=A} m_1(B)m_2(C)$ | Dubois-Prade 1986 |
| Yager | conflit → Θ | Yager 1987 |
| Dubois-Prade | redistribution sur $B \cup C$ | Dubois-Prade 1988 |
| PCR5 | proportional conflict redistribution | Smarandache-Dezert 2005 |
| PCR6 | variante PCR5 multi-source | Martin-Osswald 2006 |
| Cautious | $\bigotimes$ basé sur weight function | Denoeux 2008 |
| Bold | dual disjonctif de cautious | Denoeux 2008 |
| Mean | moyenne arithmétique | Murphy 2000 |

**Tasks** :

- [ ] `CombinationRule` ABC avec `combine(m1, m2) -> MassFunction`
- [ ] Toutes les règles ci-dessus
- [ ] Multi-source : `combine_many([m1, m2, m3, ...], rule)`
- [ ] Optimisation PCR6 (vectorisation cruciale, c'est le bottleneck)

**Tests** :

- [ ] Property : commutativité (toutes sauf cautious avec poids différents)
- [ ] Property : associativité Dempster
- [ ] Property : élément neutre = vacuous BBA pour Dempster, conjunctive
- [ ] Regression : Zadeh 1986 paradox (Dempster = mauvais, Yager/PCR5 = OK)
- [ ] Regression : exemples Smarandache-Dezert canoniques (DSmT vol.1-4)
- [ ] Regression : Denoeux 2008 cautious examples

**Performance** :

- [ ] Bench : ≥ 10⁵ paires/sec sur Θ=4 (Dempster)
- [ ] Bench : ≥ 10⁴ paires/sec sur Θ=8 (PCR6)

**Deliverable** : `dempster`, `pcr6`, `cautious` etc. utilisables. Tutoriel 2 (Zadeh paradox).

---

### Phase 3 — Decision & Metrics v0.3.0 (Semaines 9-10)

**Objectif** : couche décision + indicateurs de qualité.

- [ ] `betp(m)` : transformation pignistique (Smets 2005)
- [ ] `plausibility_transform(m)` : Cobb-Shenoy 2006
- [ ] `max_belief(m)`, `max_plausibility(m)`
- [ ] `interval_probability(m, A)` → (Bel(A), Pl(A))
- [ ] `conflict(m1, m2)` : K
- [ ] `weight_of_conflict(m1, m2)` : Shafer log(1-K)
- [ ] `nonspecificity(m)` : Yager 1983
- [ ] `discord(m)` : Klir 1990
- [ ] `aggregate_uncertainty(m)` : Klir-Wierman
- [ ] `jousselme_distance(m1, m2)` : Jousselme 2001
- [ ] `belief_divergence(m1, m2)` (Bel-, Pl-)

**Tests** :

- [ ] Property : BetP(m) est une distrib de probabilité valide
- [ ] Property : 0 ≤ K ≤ 1
- [ ] Property : Jousselme est une vraie métrique (positivité, symétrie, inégalité triangulaire numérique)
- [ ] Regression : exemples Klir-Wierman 1999

**Deliverable** : tutoriel 3 (interpréter les métriques d'incertitude).

---

### Phase 4 — Discounting v0.4.0 (Semaine 11)

- [ ] `classical_discount(m, alpha)` : Shafer 1976, $m^α(A) = α·m(A)$ pour $A ≠ Θ$, $m^α(Θ) = α·m(Θ) + (1-α)$
- [ ] `contextual_discount(m, alpha_dict)` : Mercier 2012, discounting par focal element
- [ ] `temporal_decay(m, dt, half_life)` : exponentiel vers vacuous
- [ ] Reinforcement (α > 1) avec garde-fous + warnings

**Tests** :

- [ ] Property : `classical(m, 1.0)` = m
- [ ] Property : `classical(m, 0.0)` = vacuous
- [ ] Property : monotonie de la non-spécificité avec α décroissant

---

### Phase 5 — Construction layer v0.5.0 (Semaines 12-15)

**Objectif** : convertir des sorties capteur réalistes en BBAs.

- [ ] `from_softmax(theta, probs, nonspec_factor)` : Denoeux-style, masse résiduelle vers Θ
- [ ] `from_detection(theta, bbox, class_score, existence_prior)` : pour sortie détecteur 2D/3D
- [ ] `from_lidar_cluster(points, theta)` : features géométriques → BBA
- [ ] `from_radar_track(track, theta, doppler_aware=True)` : Doppler comme indicateur dynamique
- [ ] Pydantic models pour valider les inputs (`SensorReading`, `Detection2D`, `Detection3D`, `LidarCluster`, `RadarTrack`)

**Tests** :

- [ ] Round-trip : softmax → BBA → BetP retourne softmax si nonspec_factor=0
- [ ] Property : tout BBA construit est valide

---

### Phase 6 — CARLA adapter v0.6.0 (Semaines 16-19)

- [ ] `CarlaSensorWrapper` : abstraction commune au-dessus de `carla.Sensor`
- [ ] Wrappers spécifiques : `SemanticCameraWrapper`, `LidarWrapper`, `RadarWrapper`, `GnssWrapper`
- [ ] `EgoVehicle` : abstraction haut-niveau (auto-pilot off, sensors attachés, fusion pipeline)
- [ ] `CarlaRecorder` : enregistre tous les flux capteurs + GT vers HDF5 pour replay
- [ ] 4 scénarios canoniques :
  - [ ] `intersection_occlusion` : intersection 4-way, piéton occulté par véhicule garé
  - [ ] `dense_traffic` : trafic urbain dense, multi-association ambiguë
  - [ ] `v2x_packet_loss` : 2 ego, packet loss configurable
  - [ ] `adversarial_ghost` : injection ghost vehicle V2X (security)

**Tests** :

- [ ] Tests integration avec CARLA mock (skipif CARLA non installé)
- [ ] Tests E2E sur 1 scénario en CI auto-hébergée (optionnel, low priority)

---

### Phase 7 — ROS2 adapter v0.7.0 (Semaine 20)

- [ ] `MassFunctionMsg` : message ROS2 custom, encodage compact (sparse focal elements)
- [ ] Nodes streaming : `BBAFusionNode`, `BBABuilderNode`
- [ ] Plugin RViz pour visualiser BBAs sur grille (low priority, peut décaler post-1.0)

---

### Phase 8 — Visualization v0.8.0 (Semaines 21-22)

- [ ] `focal_plot(m)` : barres pondérées par focal element (Θ small)
- [ ] `conflict_trace(m_history)` : K(t) trajectoire
- [ ] `grid_betp_heatmap(grid)` : EOGM viz
- [ ] `uncertainty_decomposition(m)` : non-spec vs discord en stacked bar
- [ ] Tous matplotlib + équivalent plotly interactif

---

### Phase 9 — Benchmarks v0.9.0 (Semaines 23-26)

**Objectif** : suite reproductible pour comparer les choix de fusion.

- [ ] 5 scénarios CARLA versionnés avec GT (replay HDF5 distribué via Zenodo)
- [ ] Métriques : GOSPA, OSPA², ghost track count, conflict-mass-time, ignorance evolution
- [ ] Harness : `python -m carla_evidence.benchmarks run --rule pcr6 --scenario dense_traffic --output report.html`
- [ ] Report HTML/PDF avec graphes + tableaux LaTeX-ready
- [ ] Baselines pré-calculées pour 8 règles × 5 scénarios

---

### Phase 10 — v1.0.0 release (Semaine 27)

- [ ] API gelée, semver commitment public
- [ ] Doc complète (concepts + tutorials + API + how-to + theory refs)
- [ ] Soumission **JOSS paper** (templated)
- [ ] Préprint arXiv compagnon (méthodologie longue)
- [ ] Talk + démo IV ou ITSC 2027
- [ ] DOI Zenodo permanent
- [ ] Annonce communauté (BFAS mailing list, ROS Discourse, autonomous driving subreddits)

---

## 8. Stratégie de tests

### 8.1 Pyramide

```
        ┌──────────────┐
        │   E2E (5%)   │  CARLA scenarios complets
        ├──────────────┤
        │ Integ (15%)  │  multi-module, mock CARLA
        ├──────────────┤
        │ Property(30%)│  hypothesis-based
        ├──────────────┤
        │  Unit (50%)  │  pure functions, isolated
        └──────────────┘
```

### 8.2 Property-based critiques

```python
# tests/property/test_combination_props.py
from hypothesis import given, settings
from carla_evidence.testing import mass_functions

@given(m=mass_functions(frame_size=4))
def test_dempster_neutral_element(m):
    """Dempster avec vacuous laisse m inchangée."""
    vacuous = MassFunction.vacuous(m.frame)
    assert dempster(m, vacuous).is_close_to(m)

@given(m1=mass_functions(frame_size=4), m2=mass_functions(frame_size=4))
def test_dempster_commutativity(m1, m2):
    assert dempster(m1, m2).is_close_to(dempster(m2, m1))

@given(m1=mass_functions(frame_size=3),
       m2=mass_functions(frame_size=3),
       m3=mass_functions(frame_size=3))
@settings(max_examples=200)
def test_dempster_associativity(m1, m2, m3):
    left = dempster(dempster(m1, m2), m3)
    right = dempster(m1, dempster(m2, m3))
    assert left.is_close_to(right, atol=1e-9)

@given(m=mass_functions(frame_size=5))
def test_betp_is_probability(m):
    p = betp(m)
    assert abs(p.sum() - 1.0) < 1e-10
    assert (p >= 0).all()

@given(m=mass_functions(frame_size=4))
def test_pl_dominates_bel(m):
    for subset in m.frame.powerset():
        assert m.pl(subset) >= m.bel(subset) - 1e-12
```

### 8.3 Regression tests (numerical canon)

- **Zadeh 1986** : 2 médecins en désaccord, conclusion absurde de Dempster, OK avec Yager/PCR5
- **Smets 1990** : exemples TBM bookkeeping
- **Smarandache-Dezert** : 5+ exemples DSmT vol.1-4
- **Denoeux 2008** : cautious rule reproductions
- **Klir-Wierman 1999** : aggregate uncertainty exemples

### 8.4 Coverage targets

| Module | Min coverage |
|---|---|
| `core/` | 95% |
| `combination/`, `decision/`, `metrics/` | 90% |
| `construction/` | 85% |
| `carla/`, `ros/`, `opencda/` | 70% (hardware-dependent) |
| `viz/` | 60% (smoke tests) |
| **Global** | **≥ 85%** |

### 8.5 Fixtures partagées

`tests/fixtures/canonical_bbas.py` : ~30 BBAs de référence (vacuous, categorical, bayesian, conflictual pairs from literature) utilisés par tous les tests.

---

## 9. CI/CD pipeline complet

### 9.1 `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff black mypy
      - run: ruff check src tests
      - run: black --check src tests
      - run: mypy src/carla_evidence

  test:
    needs: lint
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # for setuptools-scm
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - run: pip install -e ".[dev,ml]"
      - run: pytest tests/unit tests/property tests/regression --cov=carla_evidence --cov-report=xml -n auto
      - uses: codecov/codecov-action@v4
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
        with:
          file: ./coverage.xml

  property-tests-deep:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest tests/property --hypothesis-profile=ci -n auto
        env:
          HYPOTHESIS_PROFILE: ci  # max_examples=500 in CI

  benchmark-regression:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest benchmarks/ --benchmark-json=output.json
      - uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: output.json
          alert-threshold: '120%'  # fail if 20% slower
          fail-on-alert: true
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### 9.2 `.github/workflows/docs.yml`

```yaml
name: Docs

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[docs]"
      - run: cd docs && make html
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build/html
```

### 9.3 `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish-test-pypi:
    needs: build
    runs-on: ubuntu-latest
    environment: test-pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-pypi:
    needs: publish-test-pypi
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1

  github-release:
    needs: publish-pypi
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true

  zenodo-archive:
    needs: github-release
    runs-on: ubuntu-latest
    steps:
      - run: echo "Zenodo webhook is configured at repo level (Settings > Integrations)"
```

### 9.4 `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies: [numpy, pydantic]
        files: ^src/

  - repo: https://github.com/kynan/nbstripout
    rev: 0.7.1
    hooks:
      - id: nbstripout

  - repo: https://github.com/codespell-project/codespell
    rev: v2.3.0
    hooks:
      - id: codespell
        args: [--ignore-words=.codespell-ignore]
```

### 9.5 `pyproject.toml` (extrait clé)

```toml
[build-system]
requires = ["setuptools>=68", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "carla-evidence"
description = "Evidential (Dempster-Shafer / DSmT) sensor fusion for autonomous driving"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "BSD-3-Clause"}
authors = [{name = "Godwin"}]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
dynamic = ["version"]
dependencies = [
    "numpy>=1.24",
    "scipy>=1.10",
    "pydantic>=2.0",
]

[project.optional-dependencies]
ml = ["torch>=2.0"]
carla = ["carla>=0.9.15"]
ros = ["rclpy"]
viz = ["matplotlib", "plotly"]
docs = ["sphinx", "myst-parser", "sphinx-rtd-theme", "sphinx-autodoc-typehints"]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "pytest-xdist",
    "pytest-benchmark",
    "hypothesis>=6.0",
    "ruff",
    "black",
    "mypy",
    "pre-commit",
]

[tool.setuptools_scm]
write_to = "src/carla_evidence/_version.py"

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM", "RUF"]

[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]

[tool.mypy]
strict = true
python_version = "3.10"
warn_unreachable = true
warn_redundant_casts = true

[tool.pytest.ini_options]
addopts = "--strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "slow: tests that take >1s",
    "carla: requires CARLA installation",
    "ros: requires ROS2",
]

[tool.coverage.run]
source = ["src/carla_evidence"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

---

## 10. Documentation

### Structure Sphinx

- **Concepts** : primer DS, primer DSmT, TBM, frames de discernement
- **Tutorials** : 6 notebooks pédagogiques (basic, paradox, PCR5, CARLA, V2X, evidential grid)
- **API reference** : autogénéré depuis docstrings (Google style)
- **How-to guides** : ajouter une règle, intégrer dans OpenCDA, écrire un benchmark
- **Theory references** : bibliographie canonique avec ~50 références

### Outils

- Sphinx + sphinx-rtd-theme
- myst-parser pour markdown
- sphinx-autodoc-typehints pour types
- jupyter-sphinx pour exécuter notebooks dans la doc
- sphinx-copybutton

### Hébergement

- Read the Docs (gratuit pour open-source)
- Versioning automatique : latest, stable, par tag

---

## 11. Stratégie communautaire

### Lancement

- v0.5.0 : annonce ciblée (mailing list BFAS, twitter académique sensor fusion, ROS Discourse)
- v1.0.0 : annonce large + JOSS submission + arXiv companion

### Engagement

- GitHub Discussions activé (Q&A, idées, show-and-tell)
- Issue triage hebdo
- Release cadence : minor toutes les 4-6 semaines pendant phase active, patch ad hoc
- Conventional commits pour CHANGELOG auto

### Citations

- `CITATION.cff` propre + DOI Zenodo permanent
- JOSS paper (~ 1000 mots, peer-reviewed, citable)
- arXiv preprint méthodologique (long format)

### Conférences cibles

- **IV** (IEEE Intelligent Vehicles) : démo + workshop paper
- **ITSC** (IEEE ITS Conference) : full paper sur architecture
- **FUSION** (Int'l Conf on Information Fusion) : papier méthodologique
- **JOSS** : software paper

---

## 12. Risques et mitigation

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Scope creep (trop de règles) | Haute | Moyen | Roadmap stricte par phase, pas de feature en dehors |
| Maintenance solo | Haute | Haut | Doc d'onboarding contributeur excellente, dès Phase 4 |
| CARLA breaking changes | Moyenne | Moyen | Pin version, tests integ skipif version mismatch |
| PCR6 trop lent en pratique | Moyenne | Haut | Profiling continu Phase 2, fallback Cython/numba si besoin |
| Pas adopté | Moyenne | Haut | Stratégie communauté (§11), JOSS, conférences |
| Doublon avec autre projet | Faible | Haut | Veille trimestrielle, repositionnement si besoin |

---

## 13. Métriques de succès (mesurables)

À 6 mois post-v1.0 :

- ⭐ ≥ 100 GitHub stars
- 📦 ≥ 1000 downloads PyPI/mois
- 📚 ≥ 5 citations académiques
- 🧑‍💻 ≥ 3 contributeurs externes (PR mergées)
- 🐛 issue resolution time médian < 14 jours

À 18 mois :

- ⭐ ≥ 500 stars
- 📚 ≥ 10 citations indépendantes (hors UTBM)
- 🔗 ≥ 1 framework tiers l'importe (OpenCDA, ms-van3t, ou nouveau)
- 📜 JOSS paper accepté

---

## 14. Calendrier global

```
S1     ████ Phase 0 (bootstrap)
S2-4   ████████████ Phase 1 (core)
S5-8   ████████████████ Phase 2 (combination)
S9-10  ████████ Phase 3 (decision/metrics)
S11    ████ Phase 4 (discounting)
S12-15 ████████████████ Phase 5 (construction)
S16-19 ████████████████ Phase 6 (CARLA)
S20    ████ Phase 7 (ROS2)
S21-22 ████████ Phase 8 (viz)
S23-26 ████████████████ Phase 9 (benchmarks)
S27    ████ Phase 10 (v1.0)
```

**Total** : ~27 semaines (~6 mois) en travail concentré, ~9 mois en parallèle de la thèse à 30%.

---

*Document v0.1 — itérations attendues sur priorisation des phases en fonction des retours.*
