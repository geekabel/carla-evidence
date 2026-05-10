# CLAUDE.md

> Ce fichier oriente Claude Code (et tout assistant IA) lorsqu'il intervient
> sur ce dépôt. Il complète, il ne remplace pas, le `README.md` et la doc.

## Mission

`carla-evidence` est une librairie Python de fusion évidentielle (Dempster-Shafer / DSmT)
pour la perception autonome. Public cible : chercheurs académiques et ingénieurs R&D
automotive. Priorité absolue : **rigueur mathématique > ergonomie > performance**.

Si un changement améliore l'ergonomie au prix de la correction théorique, **refuser**.

## Quick map

```
src/carla_evidence/
├── core/         ← MassFunction, Frame. Modifications ici cassent tout.
├── combination/  ← une règle par fichier, ABC dans base.py
├── discounting/  ← classical (Shafer), contextual (Mercier), temporal
├── decision/     ← BetP, Pl-transform, max-bel, intervalles
├── metrics/      ← K, non-spec, discord, AU, Jousselme
├── construction/ ← BBA from softmax / lidar / radar / detection
├── carla/        ← adapter CARLA (optionnel via extra [carla])
├── ros/          ← adapter ROS2 (optionnel via extra [ros])
├── opencda/      ← drop-in pour OpenCDA
├── viz/          ← matplotlib + plotly
└── benchmarks/   ← suite reproductible
```

**Règle d'architecture stricte** : couche N ne dépend que des couches < N.

- `core` ne dépend de rien sauf numpy/scipy.
- `combination`, `discounting`, `decision`, `metrics` ne dépendent que de `core`.
- `construction` dépend de `core` + pydantic.
- Les adapters (`carla`, `ros`, `opencda`) sont optionnels et isolés.

Ne jamais introduire d'import cyclique. Si tu en as besoin, tu modélises mal.

## Conventions de notation

### Mathématiques (dans docstrings et papers)

- $\Theta$ : frame of discernment (cadre de discernement)
- $2^\Theta$ : powerset (Shafer) ; $D^\Theta$ : hyperpowerset (DSmT)
- $m : 2^\Theta \to [0,1]$ : mass function (BBA), avec $\sum m(A) = 1$
- $\mathrm{Bel}, \mathrm{Pl}, q$ : belief, plausibility, commonality
- $K$ : conflit (masse sur $\emptyset$ avant normalisation)
- $\oplus$ : Dempster ; $\cap$ : conjunctive ; $\cup$ : disjunctive
- $\alpha$ : facteur de fiabilité (discounting), $\alpha \in [0,1]$

### Code

- `MassFunction` (jamais `BBA` ou `Mass` en standalone)
- `Frame` (pas `FoD`, pas `Theta`)
- `combine`, `discount`, `decide` comme verbes principaux
- `m1`, `m2`, `m_fused` pour variables BBA dans tests/exemples
- snake_case pour fonctions, PascalCase pour classes, UPPER pour constantes
- pas d'abréviations cryptiques (ex: `nonspecificity` pas `nonspec`, sauf nom de variable interne)

## Domain knowledge — pièges critiques

### 1. m(∅) selon le cadre théorique

- **Shafer (1976)** : $m(\emptyset) = 0$ par contrainte. Dempster normalise.
- **TBM (Smets 1990)** : $m(\emptyset) \geq 0$ autorisé, interprété comme "monde ouvert".
- **DSmT** : frame non-exclusif, hyperpowerset au lieu de powerset.

`MassFunction` accepte les trois via le paramètre `mode={"shafer", "tbm", "dsmt"}`.
Ne jamais hardcoder une supposition. Toujours respecter le mode déclaré à la construction.

### 2. Normalisation Dempster

La règle de Dempster divise par $1 - K$ où $K$ est le conflit.
**Si $K = 1$, lever `TotalConflictError`**, ne jamais retourner NaN ou silencieusement
basculer vers conjunctive. C'est un bug théorique, pas un cas limite à patcher.

### 3. PCR5 vs PCR6

- **PCR5** : 2 sources, redistribution proportionnelle stricte
- **PCR6** : généralisation multi-source de PCR5 (Martin-Osswald 2006)
- PCR5 sur 3+ sources via associativité = **erreur méthodologique**. Utiliser PCR6.

### 4. Cautious rule (Denoeux 2008) n'est pas commutative en présence de poids

La règle prudente $\bigotimes$ est commutative et associative *si* les poids
$w$ sont définis par la weight function. Avec discounting préalable hétérogène,
l'ordre peut compter. Documenter explicitement.

### 5. BetP n'est pas une projection arbitraire

BetP (transformation pignistique) répartit la masse de chaque focal element
$A$ uniformément sur ses singletons. Ce n'est **pas** la projection optimale au sens
de Cobb-Shenoy ; pour ça utiliser `plausibility_transform`.

### 6. Distance de Jousselme

Implémenter avec la matrice $D$ basée sur Jaccard ($D_{ij} = |A_i \cap A_j| / |A_i \cup A_j|$).
**Vérifier numériquement** l'inégalité triangulaire dans les tests, ce n'est
pas trivial à prouver pour des cas dégénérés.

## Style de code

- **Python ≥ 3.10**, syntaxe match/case, union types `|`, generic alias modernes
- **Type hints partout** dans le code public. mypy strict.
- **Frozen dataclasses** pour tous les objets de domaine (`MassFunction`, `Frame`).
- **Docstrings Google-style** avec sections : Args, Returns, Raises, Examples, References.
- **Pas de getters/setters Java-style**. Les `@property` que pour les invariants.
- **Pas de logique dans `__init__`** au-delà de validation. Méthodes de classe pour
  construction alternative : `MassFunction.vacuous(frame)`, `MassFunction.from_softmax(...)`.

### Exemple de docstring canonique

```python
def dempster(m1: MassFunction, m2: MassFunction) -> MassFunction:
    """Combine two BBAs using Dempster's rule of combination.

    Computes m1 ⊕ m2 = (m1 ∩ m2) / (1 - K), where K is the conflict mass.

    Args:
        m1: First mass function. Must share frame with m2.
        m2: Second mass function. Must share frame with m1.

    Returns:
        Combined mass function on the same frame.

    Raises:
        FrameMismatchError: If m1.frame != m2.frame.
        TotalConflictError: If K = 1 (combination undefined).

    Examples:
        >>> theta = Frame(["a", "b"])
        >>> m1 = MassFunction.from_dict(theta, {("a",): 0.6, theta.omega: 0.4})
        >>> m2 = MassFunction.from_dict(theta, {("b",): 0.3, theta.omega: 0.7})
        >>> m_fused = dempster(m1, m2)

    References:
        Shafer, G. (1976). A Mathematical Theory of Evidence. Princeton UP.
    """
```

## Tests : règles non-négociables

1. **Tout nouveau code** vient avec des tests unitaires + au moins une property-based test.
2. **Toute règle de combination** doit avoir :
   - Test unit avec exemple de la littérature (référence dans le test)
   - Property test pour commutativité (si applicable)
   - Property test pour élément neutre (vacuous BBA)
   - Test de regression sur 1 exemple canonique cité (Shafer/Smets/Smarandache/Denoeux)
3. **Coverage minimum** :
   - `core/` ≥ 95%, autres opérateurs ≥ 90%, adapters ≥ 70%, viz ≥ 60%
4. **Property-based via hypothesis** : utiliser les stratégies dans `carla_evidence.testing`.
5. **Ne jamais désactiver un test** sans ouvrir une issue référencée dans un commentaire `# noqa: TEST-XYZ`.

## Performance — règles

- **Vectorisation numpy first**. Boucles Python uniquement pour code de plomberie.
- **Pas de `.toarray()` implicite** sur sparse representations.
- **Cache les powersets** par frame (decorator `@lru_cache` sur méthodes idempotentes).
- **Profile avant d'optimiser**. Une PR perf doit montrer le before/after via `pytest-benchmark`.
- **Régression de perf > 20%** = CI rouge automatique.

## Comment ajouter une nouvelle règle de combination

1. Créer `src/carla_evidence/combination/<name>.py`
2. Hériter de `CombinationRule` (`combination/base.py`)
3. Implémenter `combine(m1, m2)` (et override `combine_many` si optimisable spécifiquement)
4. Ajouter dans `combination/__init__.py` : import explicite + ajout à `__all__`
5. Tests : `tests/unit/test_<name>.py`, `tests/property/test_<name>_props.py`,
   et regression dans `tests/regression/` si exemple canonique disponible
6. Doc : section dans `docs/source/concepts/combination_rules.md` + entrée dans
   le tableau récapitulatif
7. Mettre à jour le CHANGELOG (Unreleased / Added)
8. PR avec : référence académique de la règle, complexité asymptotique, benchmark

## DON'Ts (erreurs déjà commises ou tentations)

- ❌ Ne pas mélanger DSmT et powerset Shafer dans une même `MassFunction`.
- ❌ Ne pas appeler `dempster(m1, m2)` directement si `K=1` sans try/except.
- ❌ Ne pas ajouter une dépendance core sans qu'elle soit *vraiment* nécessaire (numpy, scipy, pydantic seulement).
- ❌ Ne pas utiliser `print()` pour debug. Utiliser `logging` avec namespace `carla_evidence.<module>`.
- ❌ Ne pas importer `torch` au top-level d'un fichier hors de `[ml]`. Lazy import dans la fonction.
- ❌ Ne pas casser l'API publique sans bump majeur après v1.0. Avant v1.0, breaking changes
  via deprecation warning sur 1 release minor minimum.
- ❌ Ne pas commit de notebooks avec output (nbstripout en pre-commit).
- ❌ Ne pas hardcoder de seed dans le code applicatif. Toujours via paramètre `random_state`.

## Workflow de développement

```bash
# Setup
git clone https://github.com/<user>/carla-evidence
cd carla-evidence
pip install -e ".[dev]"
pre-commit install

# Avant tout commit
pre-commit run --all-files
pytest tests/unit tests/property -n auto

# Avant push
pytest                                    # full suite
mypy src/carla_evidence
pytest benchmarks/ --benchmark-only       # vérifier régressions perf

# Documentation locale
cd docs && make html && open build/html/index.html
```

## Convention de commits

[Conventional Commits](https://www.conventionalcommits.org/) :

- `feat(combination): add Dubois-Prade rule`
- `fix(core): handle K=1 in dempster gracefully`
- `docs(tutorials): add Zadeh paradox notebook`
- `test(property): tighten BetP probability invariant`
- `perf(pcr6): vectorize redistribution step (3x speedup)`
- `refactor(decision): extract shared transform logic`
- `chore(deps): bump pydantic to 2.5`

Le CHANGELOG est généré depuis ces messages.

## Sortie de release

1. Vérifier CI verte sur main
2. Merger PR "Release vX.Y.Z" qui :
   - Bump version (auto via setuptools-scm si tag)
   - Update CHANGELOG.md (semantic-release)
   - Update CITATION.cff
3. Tag annoté : `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. `git push --tags` → CI release.yml prend le relais
5. Vérifier publication Test PyPI, smoke test
6. Vérifier publication PyPI
7. Vérifier création GitHub Release avec notes
8. Vérifier archivage Zenodo (DOI mis à jour automatiquement)
9. Annoncer (cf. CONTRIBUTING.md section "Release announcement")

## Quand demander confirmation utilisateur (Claude Code)

- Avant tout `git push --force` ou rewrite d'historique
- Avant suppression de fichier non-versionné non-trivial
- Avant modification de la liste de dépendances `core` (numpy/scipy/pydantic)
- Avant tout changement dans `core/mass.py` ou `core/frame.py` (impact transverse)
- Avant édition de fichiers de release (CHANGELOG.md, CITATION.cff, _version.py)
- Avant désactivation d'un test ou suppression d'un workflow CI

## Références canoniques (à citer dans le code et la doc)

- Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton UP.
- Smets, P. (1990). The combination of evidence in the Transferable Belief Model. *IEEE TPAMI*.
- Smets, P. (2005). Decision making in the TBM: the necessity of the pignistic transformation.
- Smarandache, F. & Dezert, J. (2004-2015). *Advances and Applications of DSmT*, Vol. 1-4.
- Denoeux, T. (2008). Conjunctive and disjunctive combination of belief functions induced
  by nondistinct bodies of evidence. *Artificial Intelligence*.
- Mercier, D., Quost, B., Denoeux, T. (2008). Refined modeling of sensor reliability in the
  belief function framework using contextual discounting. *Information Fusion*.
- Yager, R. R. (1987). On the Dempster-Shafer framework and new combination rules.
- Dubois, D. & Prade, H. (1988). Representation and combination of uncertainty with belief
  functions and possibility measures.
- Jousselme, A.-L., Grenier, D., Bossé, É. (2001). A new distance between two bodies of evidence.
- Klir, G. J. & Wierman, M. J. (1999). *Uncertainty-Based Information*.
- Martin, A. & Osswald, C. (2006). A new generalization of the proportional conflict
  redistribution rule stable in terms of decision (PCR6).

Pour les questions méthodologiques, ces ouvrages priment sur l'intuition. Si une PR
contredit l'un d'eux, justifier explicitement.
