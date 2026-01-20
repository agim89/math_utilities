# CI/CD Pipeline: math_utilities + shared-workflows

Short guide to the pipeline, labels, and release flow.

---

## How the pipeline runs

1) PR checks (always)
- File: `math_utilities/.github/workflows/pr.yaml`
- Calls shared `build-test.yml`
- Runs clang-format check, CMake configure/build, ctest on Linux/macOS/Windows, Conan profile detect/install.

2) Version bump guard (on label add)
- File: `math_utilities/.github/workflows/validate-version.yml`
- Triggers when `publish` or `verify` label is added
- Requires `VERSION` to change, enforces semver, and ensures version > base branch.

3) Label-driven RC flows
- `publish` (file: `label-publish.yml`)
   - Build RC: `mylib/X.Y.Z-dev-<sha>` via shared `conan-package.yml`
   - Upload to `conan-rc`
   - Post-upload integration test from remote via shared `consumer-verify.yml`
- `verify` (file: `label-verify.yml`)
   - Integration test only against existing RC in `conan-rc` (no build/upload)

4) Final release (on PR merge/close to main)
- File: `math_utilities/.github/workflows/release.yml` (trigger: pull_request closed → merged to main)
- Calls shared `release.yml` to:
   - Verify RC exists in `conan-rc`
   - Build clean release `mylib/X.Y.Z` (no -dev)
   - Upload to `conan-stable`
   - Create tag `vX.Y.Z` and GitHub Release
- If the tag already exists, the workflow fails (no re-release).

5) Release notes (after merge)
- File: `math_utilities/.github/workflows/release-notes.yaml`
- On PR merge to main, writes `Release-Notes/Release-X.Y.Z.md` from `unreleased.md` and pushes
- Because Final Release triggers on PR close (not push)

6) Branch protection (manual)
- File: `math_utilities/.github/workflows/setup-branch-protection.yml`
- Run via workflow_dispatch to set required checks and rules. Currently requires PR checks (`verify / Build and Test (...)`), 1 approval, linear history, no force push/delete. Label workflows are not required checks.

---

## Labels reference

| Label | What happens | Builds RC | Tests RC | Releases on merge |
|-------|---------------|-----------|----------|-------------------|
| verify | Integration test existing RC from `conan-rc` | ❌ | ✅ (remote) | ❌ |
| publish | Build + upload RC to `conan-rc`, then test from remote | ✅ | ✅ | ✅ (Final Release on merge) |

Notes:
- Add only one of the labels. `publish` implies release intent after merge; `verify` is for test-only.
- Version bump guard runs when either label is added and will fail if `VERSION` isn’t updated.

---

## Versioning and remotes
- RC packages: `mylib/X.Y.Z-dev-<short-sha>` → `conan-rc`
- Release packages: `mylib/X.Y.Z` → `conan-stable`
- Semver stored in `VERSION` (single source of truth).

---

## How to cut a release
1) Bump `VERSION` and update `Release-Notes/unreleased.md`, open PR.
2) Add label `publish` (triggers version guard, RC build, upload, and RC integration test).
3) Wait for RC workflow to pass, then merge PR.
4) Final Release auto-runs on PR merge: builds clean release, uploads to `conan-stable`, tags `vX.Y.Z`, creates GitHub Release.
5) Release-notes workflow commits `Release-Notes/Release-X.Y.Z.md` to main (will not re-trigger release).

---

## Conan & shared workflows
- Shared repo: `shared-workflows/.github/workflows/`
- Build/test: `build-test.yml`
- RC/Release packaging: `conan-package.yml` (RC) and `release.yml` (final)
- Consumer integration: `consumer-verify.yml`

---

## Required secrets
- `CONAN_RC_URL`, `CONAN_STABLE_URL`, `CONAN_USERNAME`, `CONAN_PASSWORD`
- `BRANCH_PROTECTION_TOKEN` (for branch protection and release-notes push)

---

## Troubleshooting quick hits
- Tag push rejected: tag already exists → delete remote tag manually (`git push origin :refs/tags/vX.Y.Z`) then rerun release.
- RC not found in verify: ensure a `publish` run built/uploaded the matching `-dev-<sha>` package.
- Version guard failing: bump `VERSION` and keep semver format `X.Y.Z`.
