---
name: "local-rss-feed-staging"
description: "How to turn existing local audio artifacts into a restartable LAN RSS feed without adding server complexity."
domain: "backend-delivery"
confidence: "high"
source: "earned"
tools:
  - name: "apply_patch"
    description: "Add a feed builder, delivery staging directory, and thin CLI entrypoint."
    when: "A local content pipeline already emits audio files and needs a simple private RSS delivery path."
---

## Context

Use this when the product already creates local episode files, but the missing piece is letting another device subscribe to them over the LAN.

## Patterns

- Stage delivery artifacts in a **dedicated feed directory** such as `data\rss\` instead of serving the whole working tree.
- Build `podcast.xml` from the **already-materialized audio files** so feed generation is restartable and does not depend on rerunning expensive steps.
- Prefer a **thin stdlib HTTP server** for the first slice when the goal is local-network reachability, not hosted publishing.
- Keep the published base URL **explicit/overrideable** so enclosure links match what phones on the LAN can reach.
- If current audio is already acceptable, **reuse it directly** rather than inventing a transcoding dependency in v1.
- Prefer **persisted English title metadata** from adjacent script or translation artifacts when building RSS `<item><title>` values; only fall back to filename normalization when no metadata exists.
- Keep a **slug-cleanup fallback** so routing prefixes like `vijte-7549-` do not leak into RSS titles when metadata is unavailable.

## Examples

- `my-project\src\knigovishte_podcast\services\rss.py` rebuilds `data\rss\episodes\`, writes `podcast.xml`, exposes a stdlib server factory, and reads `English title:` lines from matching script artifacts.
- `my-project\src\knigovishte_podcast\cli.py` adds `local-rss-delivery` with `--public-host` and `--no-serve`.
- `my-project\tests\test_rss.py` verifies feed generation, staged file cleanup, and actual HTTP serving.

## Anti-Patterns

- Serving `data\audio\` directly without a stable feed root or cleanup step.
- Hiding feed URLs behind opaque autodiscovery with no user-visible override.
- Treating the audio filename as the canonical listener-facing title when richer translation metadata is already on disk.
- Introducing a heavyweight media conversion stack before proving the private-LAN subscription path works.
