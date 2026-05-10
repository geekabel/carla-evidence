# Releasing `carla-evidence`

This document is the operator's runbook. It complements `CLAUDE.md`
§"Sortie de release" with the exact commands and one-time setup that the
v0.2.0 cycle requires.

## One-time setup (per repository)

These items only need to be done once, the first time you ship a release.

### 1. Create the GitHub repository

```bash
gh repo create geekabel/carla-evidence \
    --public \
    --source . \
    --remote origin \
    --description "Evidential (Dempster-Shafer / DSmT) sensor fusion for autonomous driving"
git push -u origin main
```

### 2. Configure Test PyPI as a trusted publisher

1. Register `geekabel` on <https://test.pypi.org/account/register/>.
2. Reserve the project name: <https://test.pypi.org/manage/account/publishing/>.
3. Add a *pending publisher* with:
   - **PyPI Project Name**: `carla-evidence`
   - **Owner**: `geekabel`
   - **Repository name**: `carla-evidence`
   - **Workflow filename**: `release.yml`
   - **Environment name**: `test-pypi`
4. In the GitHub repo, go to *Settings → Environments → New environment*
   and create `test-pypi`. No protection rules required yet; you can add a
   "wait timer" or "required reviewers" once the workflow is exercised.

### 3. (Deferred) Configure PyPI

Real-PyPI publication is gated until v0.5.0+ (`if: false` in
`release.yml`). Repeat the trusted-publisher steps on
<https://pypi.org/manage/account/publishing/> when you're ready to flip
the flag.

### 4. Connect Zenodo

1. Sign in to <https://zenodo.org/account/settings/github/>.
2. Toggle the switch next to `geekabel/carla-evidence` to **on**. Zenodo
   now archives every published GitHub release as a snapshot, minting a
   fresh DOI for each version and a stable *concept DOI* for the project
   as a whole.
3. After the first release, copy the concept DOI from the Zenodo project
   page into `CITATION.cff` (replace the `10.5281/zenodo.PLACEHOLDER`
   value).

### 5. (Optional) Codecov token

If `codecov` is private to the org, mint a token at
<https://app.codecov.io/gh/geekabel/carla-evidence/settings> and add it as
the GitHub Actions secret `CODECOV_TOKEN`. For public repos with the
default Codecov setup the token is optional.

## Per-release runbook

### Pre-flight (before tagging)

```bash
# 1. Ensure CI is green on main.
gh run list --workflow=ci.yml --branch=main --limit=1

# 2. Ensure CHANGELOG.md has a populated [Unreleased] section.
grep -A2 "## \[Unreleased\]" CHANGELOG.md

# 3. Confirm tests + property suite pass under the CI hypothesis profile.
HYPOTHESIS_PROFILE=ci pytest tests/property -n auto

# 4. Confirm benchmarks meet the architecture targets.
pytest benchmarks/ --benchmark-only --override-ini="testpaths=benchmarks"
```

### Cut the tag

The version is taken from the most recent `v*` tag via `setuptools-scm`.
Tag from `main` only; never re-tag a previously released version.

```bash
# Annotated tag — release.yml triggers on push.
git tag -a v0.2.0 -m "Release v0.2.0 — combination layer (Phase 2)"
git push --tags
```

### Verify the pipeline

```bash
# Watch release.yml.
gh run watch --workflow=release.yml

# After publish-test-pypi succeeds, smoke-test in a throwaway venv:
python -m venv /tmp/smoke && /tmp/smoke/bin/pip install \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    carla-evidence==0.2.0
/tmp/smoke/bin/python -c "from carla_evidence import Frame, MassFunction; print('ok')"
```

The same smoke test runs automatically as the `smoke-test-test-pypi` job;
running it locally is a defence in depth.

### Post-release housekeeping

1. **Update `CITATION.cff`** — replace the placeholder DOI with the fresh
   Zenodo DOI for the new version. Commit and push to `main` (no tag).
2. **Update `CHANGELOG.md`** — replace `[Unreleased]` with `[v0.2.0] — 2026-MM-DD`
   and add a fresh empty `[Unreleased]` section above it. Commit and push.
3. **Open issues for known follow-ups** — see `.github/issues_drafts/` for
   the cautious/bold (v0.2.1), DSmT, and literature cross-validation
   tracking issues that should land alongside v0.2.0.
4. **Announce** — the v1.0.0 announcement plan in
   `carla-evidence-architecture.md` §11 doesn't apply to pre-1.0 tags. For
   v0.2.0, a short post on GitHub Discussions is enough.

## Aborting a botched release

If `release.yml` fails after the Test PyPI publish step succeeded, the
artefact is already on Test PyPI and **cannot be re-uploaded under the
same version**. You have two options:

1. **Yank** the affected version on Test PyPI
   (<https://test.pypi.org/manage/project/carla-evidence/releases/>) and
   ship a `v0.2.0.post1` or `v0.2.1` tag.
2. If the failure is downstream of Test PyPI (e.g. GitHub release
   creation), re-run the failed workflow job — Test PyPI publish is
   idempotent for an already-uploaded version (it returns a non-fatal
   warning).

## v0.2.0 release plan (specifically)

This is the version that's about to ship. Keep it on the runbook for one
cycle.

- **Pre-flight**: CI green on main (PR #1 if needed), CHANGELOG populated
  with the Phase 1 + Phase 2 entries, benchmarks at architecture targets.
- **Tag**: `v0.2.0` from `main` after PR merge.
- **Test PyPI**: smoke test must succeed.
- **Real PyPI**: deliberately skipped (`if: false` in `release.yml`).
- **GitHub release**: auto-generated notes with `prerelease: true`.
- **Zenodo**: webhook archives the tag → mint concept DOI → update
  CITATION.cff in a follow-up commit on `main`.
- **No public announcement** — pre-1.0; the lib is for self-validation
  and external testing only at this point.
