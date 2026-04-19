# Google Voice Routing

## When to use

Use this pattern when a CLI or service accepts Google TTS voice-name overrides and can also fall back to a local speech engine.

## Pattern

1. Decide provider routing from the voice-name format, not from a hardcoded default locale.
2. For English Google voices, treat valid names broadly as `en-*`; for Bulgarian, treat them as `bg-BG-*`.
3. Once the request is on the Google path, derive `language_code` from the selected voice name and only use configured language codes as fallbacks.
4. Add regression tests for both single-voice and mixed bilingual flows so a new locale-specific override cannot silently fall back to the local engine.
5. In bilingual scripts, assert the actual segment count coming out of `_split_script_by_language()`; English title and English body may require separate Google synth calls when Bulgarian lines sit between them.

## First use here

- `my-project\src\knigovishte_podcast\services\tts.py`
- `my-project\tests\test_tts.py`
- Applied during issue #14 revision after Lambert's rejection of the original English Google voice handling
