---
name: "stable-pipeline-wiring"
description: "How to finish a small content pipeline so the orchestration, caching, and CLI seam stay explicit."
domain: "backend-integration"
confidence: "high"
source: "earned"
tools:
  - name: "apply_patch"
    description: "Wire the pipeline, add focused tests, and keep CLI changes thin."
    when: "Service boundaries already exist but the end-to-end backend seam is still incomplete."
---

## Context

Use this when a project already has fetch, transform, and output services, but the real work is making them behave as one dependable flow without smearing orchestration across the CLI.

## Patterns

- Add a **default pipeline factory** that assembles real implementations in one place.
- Keep **artifact persistence** in the pipeline layer, not in the CLI, when the artifacts are part of the backend contract.
- Reuse split boundaries like `fetch_html()` and `parse_html()` to support **HTML caching without hiding parsing**.
- Return a plan object that exposes the **materialized artifact paths** callers care about.
- Add only the **smallest CLI command** needed to prove the integrated seam is reachable.

## Examples

- `my-project\src\knigovishte_podcast\pipeline.py` now exposes `pipeline()` plus `ArticleToPodcastPipeline.run()`.
- `my-project\src\knigovishte_podcast\models.py` carries script and cached-HTML paths in `PodcastPlan`.
- `my-project\tests\test_pipeline.py` verifies wiring, persisted artifacts, cached HTML reuse, and CLI reporting.

## Anti-Patterns

- Letting the CLI reimplement fetch/cache/script-writing instead of calling one backend seam.
- Treating service interfaces as “integrated” when no test proves the stages are invoked in order.
- Returning only in-memory data when the real product contract depends on files being created on disk.
