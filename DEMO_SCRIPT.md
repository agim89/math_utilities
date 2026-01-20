# Demo Script: CI/CD Flow for math_utilities

Use this as a spoken guide when recording the demo. It walks through what to show on screen and what to say for each stage of the pipeline.

---

## 1) Set the stage (context)
- Purpose: Cross-platform C++ lib built with CMake + Conan; automated RC + release via GitHub Actions.
- Repos: app code in math_utilities; reusable pipelines in shared-workflows.
- Remotes: conan-rc for RCs (`mylib/X.Y.Z-dev-<sha>`), conan-stable for releases (`mylib/X.Y.Z`).

## 2) Show the key workflows (quick tour)
- PR checks: [math_utilities/.github/workflows/pr.yaml](math_utilities/.github/workflows/pr.yaml) → shared build-test.
- Label guard: [math_utilities/.github/workflows/validate-version.yml](math_utilities/.github/workflows/validate-version.yml) (runs on label add).
- RC build: [math_utilities/.github/workflows/label-publish.yml](math_utilities/.github/workflows/label-publish.yml) (publish label).
- RC verify-only: [math_utilities/.github/workflows/label-verify.yml](math_utilities/.github/workflows/label-verify.yml) (verify label).
- Final release: [math_utilities/.github/workflows/release.yml](math_utilities/.github/workflows/release.yml) (PR merged to main with publish).
- Release notes: [math_utilities/.github/workflows/release-notes.yaml](math_utilities/.github/workflows/release-notes.yaml) (runs after merge).
- Branch protection: [math_utilities/.github/workflows/setup-branch-protection.yml](math_utilities/.github/workflows/setup-branch-protection.yml) (manual dispatch).

## 2b) Workflow deep dive (math_utilities repo)
- PR checks ([math_utilities/.github/workflows/pr.yaml](math_utilities/.github/workflows/pr.yaml))
  - Trigger: every PR event.
  - Single job `verify` calls shared build-test.yml; no extra logic here.

- Validate version ([math_utilities/.github/workflows/validate-version.yml](math_utilities/.github/workflows/validate-version.yml))
  - Trigger: PR labeled with `publish` or `verify`.
  - Steps: checks VERSION changed between base/head; enforces semver `X.Y.Z`; fails if unchanged or malformed; prints old→new.

- RC build (publish) ([math_utilities/.github/workflows/label-publish.yml](math_utilities/.github/workflows/label-publish.yml))
  - Trigger: PR labeled `publish` (while open).
  - Job get-sha: outputs `version` (from VERSION), `short_sha`, and `rc_version` (X.Y.Z-dev-<sha>).
  - Job rc-build: calls shared conan-package.yml with `is_rc=true`, remote=conan-rc. (Note: version input appends -dev- and shared workflow adds `<sha>` → results in `X.Y.Z-dev-<sha>`.)
  - Job integration-test: calls shared consumer-verify.yml to install `mylib/X.Y.Z-dev-<sha>` from conan-rc and run the consumer test.

- RC verify-only (verify) ([math_utilities/.github/workflows/label-verify.yml](math_utilities/.github/workflows/label-verify.yml))
  - Trigger: PR labeled `verify` (while open).
  - Job get-version: reads VERSION and exposes as output.
  - Job integration-test: calls shared consumer-verify.yml with version + `-dev-` to test existing RC in conan-rc (no build/upload).

- Final release ([math_utilities/.github/workflows/release.yml](math_utilities/.github/workflows/release.yml))
  - Trigger: PR closed on main; gated to merged=true.
  - Job check-publish-label: inspects merge commit to find PR number, fetches labels, sets `should_release=true` only if `publish` present; fallback: if VERSION is new and not tagged, also triggers.
  - Job get-version: reads VERSION.
  - Job create-release: if should_release, calls shared release.yml with VERSION; relies on matching RC existing in conan-rc; final job builds clean, uploads to conan-stable, tags `vX.Y.Z`, creates GitHub Release.

- Release notes ([math_utilities/.github/workflows/release-notes.yaml](math_utilities/.github/workflows/release-notes.yaml))
  - Trigger: PR closed on main; gated to merged=true.
  - Steps: checkout with fetch-depth 0, set remote with BRANCH_PROTECTION_TOKEN, create Release-Notes/Release-X.Y.Z.md from unreleased.md, clear unreleased.md, commit, push main. Skips if unreleased.md empty.

- Branch protection setup ([math_utilities/.github/workflows/setup-branch-protection.yml](math_utilities/.github/workflows/setup-branch-protection.yml))
  - Trigger: manual workflow_dispatch with branch input.
  - Steps: uses GH API to enforce required status checks (verify / Build and Test per OS), 1 approval, linear history, no force push/delete, required conversation resolution; then verifies.

## 3) Narrate the end-to-end flow
- "Open a PR": PR checks fire automatically on Linux/macOS/Windows. They run clang-format, Conan profile detect/install, CMake configure/build, and ctest.
- "Add a label": When we add `publish` or `verify`, the version guard enforces that `VERSION` changed, is semver, and increased vs base.
- "If label is publish": RC build runs. It builds `mylib/X.Y.Z-dev-<sha>`, uploads to conan-rc, then runs consumer-verify against the remote RC.
- "If label is verify": No build/upload; it just runs consumer-verify against the existing RC in conan-rc.
- "Merge with publish": Final release workflow triggers on PR close → merged to main. It checks the merged PR has the publish label (or a new VERSION not yet tagged), ensures the matching RC exists, rebuilds clean `mylib/X.Y.Z`, uploads to conan-stable, tags `vX.Y.Z`, and creates a GitHub Release.
- "After merge": Release-notes workflow generates `Release-Notes/Release-X.Y.Z.md` from `unreleased.md`, clears `unreleased.md`, commits, and pushes with BRANCH_PROTECTION_TOKEN. This push does not retrigger release.

## 4) How to demo live (scripted steps)
- Show VERSION bump and unreleased notes edit, then open PR.
- Point at PR checks running (cross-platform matrix).
- Add label `publish`:
  - Explain guardrails (fails if VERSION unchanged or not semver).
  - Show RC build job output (package name `mylib/X.Y.Z-dev-<sha>`) and consumer test running from remote.
- Merge PR after green checks:
  - Show Final Release workflow verifying RC, rebuilding clean, pushing to conan-stable, creating tag `vX.Y.Z`, and GitHub Release.
- Show Release-Notes folder: new Release-X.Y.Z.md and cleared unreleased.md after the merge.

## 5) Branch protection and required checks
- Branch protection workflow (manual) sets required PR checks: verify / Build and Test on linux/macos/windows; requires 1 approval; blocks force pushes/deletes; linear history.
- Label workflows are not required checks (by design, they gate release intent but not merges without labels).

## 6) What to emphasize while speaking
- Label-driven control: `publish` is release intent; `verify` is test-only.
- Clean releases: final release rebuilds from source and fails if the tag already exists to avoid duplicates.
- RC safety: RCs are unique per commit (`-dev-<sha>`) and stored in conan-rc; release packages are suffix-free in conan-stable.
- Separation of concerns: shared-workflows host the reusable jobs; math_utilities wires triggers and label logic.
- Release notes are automated and do not loop-trigger the release pipeline.

## 6b) Workflow deep dive (shared-workflows repo)
- build-test ([shared-workflows/.github/workflows/build-test.yml](shared-workflows/.github/workflows/build-test.yml))
  - Matrix: ubuntu/macos/windows with profiles linux/macos/windows.
  - Steps: checkout; setup conan 2.24; install tools (clang-format/cmake/ninja on linux/macos); format check (`clang-format -i` then fail on diff); conan profile detect (macOS) and conan install per OS; configure CMake via presets (`conan-release` on *nix, `conan-default` on Windows); build with preset; run ctest on build dir.

- conan-package ([shared-workflows/.github/workflows/conan-package.yml](shared-workflows/.github/workflows/conan-package.yml))
  - Inputs: version, remote, is_rc.
  - Matrix OS with profiles; sets CONAN_VERSION either `{version}<sha>` for RC or exact version for release.
  - Remotes: resets and adds conancenter, conan-rc, conan-stable; logs in with secrets.
  - Guards: for RC, blocks if base version already exists in conan-stable; for release, blocks if version exists in conan-stable.
  - Builds: `conan create . --version=${CONAN_VERSION}`.
  - Verifies: `conan list` the package; RC path also runs local consumer-test build/install and executes the consumer binary before upload.
  - Upload: conan upload to specified remote.

- consumer-verify ([shared-workflows/.github/workflows/consumer-verify.yml](shared-workflows/.github/workflows/consumer-verify.yml))
  - Inputs: version (base), remote, git_sha (optional override).
  - Derives FULL_VERSION = `{version}{short_sha}`; configures remotes; logs into target remote; installs `mylib/FULL_VERSION` into consumer-test/build with CMakeDeps/Toolchain; configures/builds consumer-test; runs consumer executable (linux/macos or windows).

- release ([shared-workflows/.github/workflows/release.yml](shared-workflows/.github/workflows/release.yml))
  - Input: version.
  - Steps: setup conan; configure remotes; auth to conan-rc/stable; verify RC exists matching `{version}-dev-*`; set FINAL_VERSION; build clean release via `conan create` (no -dev); upload to conan-stable; create annotated tag `v{version}` (fails if tag exists remotely); create GitHub Release with install snippet.

## 7) Required secrets (mention once)
- CONAN_RC_URL, CONAN_STABLE_URL, CONAN_USERNAME, CONAN_PASSWORD
- BRANCH_PROTECTION_TOKEN (used by branch protection and release-notes push)

## 8) Quick troubleshooting talking points
- Tag already exists → delete remote tag if a rerun is intended.
- RC missing during release → ensure the publish-labeled PR produced the matching `-dev-<sha>` in conan-rc.
- Version guard failing → bump VERSION and keep X.Y.Z.
- Release-notes push blocked → check BRANCH_PROTECTION_TOKEN and branch permissions.

## 9) Optional live commands to show (prep before recording)
```
# Prep a release branch
echo "3.0.0" > VERSION
printf "## Changes\n- Feature A\n- Fix B\n" > Release-Notes/unreleased.md
git checkout -b release-3.0.0
git add VERSION Release-Notes/unreleased.md
git commit -m "Bump version to 3.0.0"
git push origin release-3.0.0
```
- Then demonstrate adding the `publish` label in the UI, watching RC build + consumer test, and merging.

---

Keep the narration concise: what triggered, what was built/tested, where artifacts went (conan-rc vs conan-stable), and how tags/releases are created.
