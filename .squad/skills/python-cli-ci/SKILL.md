---
name: "python-cli-ci"
description: "How to add minimal, practical CI to a small Python CLI that already has pyproject packaging."
domain: "testing"
confidence: "high"
source: "earned"
tools:
  - name: "powershell"
    description: "Run the actual lint, type, test, and build commands before wiring CI."
    when: "Use to verify the chosen checks pass locally from the real project directory."
---

## Context
Use this when a Python project has become concrete enough for automation, but it is still a local CLI rather than a service. The goal is to add durable quality gates without inventing containers, deployment stages, or extra orchestration.

## Patterns
- Prefer the tools the repo already implies: `pyproject.toml` for packaging, `unittest` if tests are already written that way, and a single CI workflow with a project working directory when the app lives below the repo root.
- Put developer-only tooling in a `dev` extra so CI and contributors install the same quality stack.
- Run four checks in CI: lint, type-check, tests, and package build.
- Scope lint/type targets to the supported code paths instead of stray exploratory scripts.
- Add targeted `mypy` overrides for untyped third-party libraries instead of weakening type-checking globally.

## Examples
- `my-project\pyproject.toml` defining `.[dev]` plus `ruff` and `mypy` configuration.
- `.github\workflows\python-ci.yml` using `defaults.run.working-directory: my-project`.
- `my-project\README.md` documenting the same commands CI enforces.

## Anti-Patterns
- Adding Docker or deployment infrastructure for a package that is still just a local CLI.
- Introducing `pytest` or another test runner when the repo already has a solid `unittest` suite.
- Running CI on the whole monorepo/workspace when only one subdirectory is the actual application.
