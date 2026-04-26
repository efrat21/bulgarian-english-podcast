---
name: "intermediate-wav-mp3-export"
description: "How to keep a simple WAV-first TTS pipeline internally while shipping MP3 artifacts for listener-facing delivery."
domain: "audio-export"
confidence: "high"
source: "earned"
tools:
  - name: "apply_patch"
    description: "Switch final artifact extension, add a WAV-to-MP3 export helper, and update focused tests."
    when: "A Python audio pipeline already renders WAV reliably but needs MP3 output for podcast or streaming compatibility."
---

## Context

Use this when synthesis and segment stitching already work well in WAV, but the product requirement shifts toward MP3 for better streaming compatibility or podcast-client support.

## Patterns

- Keep the synthesis path **WAV-first internally** so local engines and concatenation code remain simple.
- Add a single explicit **WAV-to-MP3 export step** after rendering, rather than duplicating per-provider MP3 logic.
- Use a bundled FFmpeg path such as **`imageio-ffmpeg`** so MP3 export does not depend on a separately installed system binary.
- Separate **intermediate render files** from the final published artifact (for example `_{slug}.wav` → `{slug}.mp3`) and clean intermediates after export.
- If RSS or feed delivery already accepts multiple formats, add a **same-stem preference rule** so `.mp3` wins over `.wav` when both exist.

## Examples

- `my-project\src\knigovishte_podcast\services\tts.py` renders to an intermediate WAV, then calls FFmpeg once to publish the final MP3.
- `my-project\src\knigovishte_podcast\services\rss.py` prefers `.mp3` when both `episode.mp3` and `episode.wav` are present.
- `my-project\tests\test_tts.py` mocks the export helper for unit tests and separately verifies the FFmpeg invocation contract.

## Anti-Patterns

- Rewriting a stable WAV-generation path just to chase MP3 output at every provider boundary.
- Depending on a manual machine-level FFmpeg install when the app can carry its own resolver.
- Publishing both `.wav` and `.mp3` for the same episode stem in RSS without a preference rule.
