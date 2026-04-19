---
name: "google-tts-voice-routing"
description: "How to extend a bilingual TTS pipeline so Google voice names route cleanly without breaking local-voice overrides."
domain: "audio-integration"
confidence: "high"
source: "earned"
tools:
  - name: "apply_patch"
    description: "Add config defaults, route voice-name prefixes, and lock the behavior with focused TTS tests."
    when: "A project already supports mixed-language TTS and needs deterministic Google voice selection alongside optional local voices."
---

## Context

Use this when a content pipeline already has bilingual script generation and file output, but the voice selection rules are split between local engines and Google Cloud TTS.

## Patterns

- Keep **voice routing declarative**: treat recognizable Google voice-name prefixes like `en-US-*` and `bg-BG-*` as the switch that selects Google synthesis.
- Store **per-language Google defaults** in config (`GOOGLE_TTS_EN_*`, `GOOGLE_TTS_BG_*`) so CLI wiring stays thin.
- Preserve **explicit local voice overrides** by continuing to accept local engine substrings on the same CLI flags.
- Route both single-language and bilingual generation through the **same Google synthesis helper** so one fix covers both paths.
- Add tests that prove **Google and local engines can coexist** in the same script render.

## Examples

- `my-project\src\knigovishte_podcast\config.py` now carries English and Bulgarian Google voice defaults plus inferred language codes.
- `my-project\src\knigovishte_podcast\services\tts.py` routes `en-US-*` and `bg-BG-*` names to Google while still allowing local pyttsx3 voices.
- `my-project\tests\test_tts.py` verifies single-voice Google English synthesis, bilingual Google Bulgarian synthesis, and default factory behavior.

## Anti-Patterns

- Hard-coding Google routing for only one language when the pipeline already supports bilingual segments.
- Replacing CLI flags or adding separate “provider” flags when the voice name itself can express the routing choice.
- Making the default output depend on whatever voices happen to exist on one local machine.
