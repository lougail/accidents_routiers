# CHANGELOG


## v0.1.0 (2026-02-22)

### Bug Fixes

- Imports triés dans notebooks (ruff --fix)
  ([`771de68`](https://github.com/lougail/accidents_routiers/commit/771de68d27b5ac2b2dbe6d018ab89fa09c388b82))

- **ci**: Add api dependencies to typecheck job
  ([`50f14d1`](https://github.com/lougail/accidents_routiers/commit/50f14d115daf0239d7b41550f19c4e7d2c980a01))

Mypy needs fastapi and sqlalchemy installed to check api/ modules. Add --group api to uv sync.

- **ci**: Format conftest and add api dependencies to tests job
  ([`75409d8`](https://github.com/lougail/accidents_routiers/commit/75409d8109e38e91973be39320d87e5c50bae2e9))

- **ci**: Remove empty tests job placeholder
  ([`2b2fb43`](https://github.com/lougail/accidents_routiers/commit/2b2fb432b4278aca33638ad01765c5f10308f9f3))

### Chores

- Add pre-commit hooks configuration and CI job
  ([`ba49223`](https://github.com/lougail/accidents_routiers/commit/ba492232a7b7704faaad8c0307bc848baef4303e))

Configure pre-commit with trailing-whitespace, end-of-file-fixer, check-yaml, ruff (lint+format),
  and mypy hooks. Add pre-commit job to CI workflow.

### Code Style

- Apply pre-commit auto-fixes across codebase
  ([`b208fe7`](https://github.com/lougail/accidents_routiers/commit/b208fe782b1e0c848433ef7c75cb7466145832de))

Trailing whitespace, end-of-file fixes, and ruff formatting applied automatically by pre-commit
  hooks.

- Format code with ruff
  ([`05179d2`](https://github.com/lougail/accidents_routiers/commit/05179d2ab1a55f77914b09ed8f2d742be28780d0))

### Continuous Integration

- Add CI workflow with lint, typecheck and security jobs
  ([`a79db90`](https://github.com/lougail/accidents_routiers/commit/a79db90693ae9ae39c8565042c4025b9f0a4b7c7))

- Add Docker GHCR build and push workflow
  ([`3f77ceb`](https://github.com/lougail/accidents_routiers/commit/3f77cebf69aa35db8a9258204fe6e021ff787e13))

Build and push Docker image to GitHub Container Registry on push to master/develop. Uses Buildx with
  GHA cache. Optimize .dockerignore for lighter builds.

### Documentation

- Add Phase 3 CI pipeline documentation
  ([`ea2abd9`](https://github.com/lougail/accidents_routiers/commit/ea2abd98a810406b47bfd51fbaa54f6e640b2447))

- Move brief documents to docs/brief/
  ([`bde4369`](https://github.com/lougail/accidents_routiers/commit/bde43698626c9dc87a97b74a9efb990577c83a18))

### Features

- Add semantic release with automated versioning
  ([`459a650`](https://github.com/lougail/accidents_routiers/commit/459a6505bafc954482763ac8141bf2d34e87098a))

Configure python-semantic-release in pyproject.toml for automated version bumping, CHANGELOG
  generation, and GitHub Releases. Add release workflow triggered after CI success and sync-develop
  workflow to keep develop in sync after releases.

- Add test suite with pytest and CI tests job
  ([`bee3593`](https://github.com/lougail/accidents_routiers/commit/bee35936b63f75c8603ce23dcd00d35e8f7ad3a9))
