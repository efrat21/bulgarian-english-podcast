# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Audio work will likely focus on TTS selection, output formats, and podcast file generation.
- `my-project\\src\\knigovishte_podcast\\services\\tts.py` is the local pyttsx3 boundary; it now standardizes output on `.wav`, clears stale files before synthesis, and raises if a requested voice is unavailable.
- `my-project\\tests\\test_tts.py` covers the TTS contract: empty-input validation, voice selection behavior, and proof that a fresh audio file was actually created.
- `my-project\\src\\knigovishte_podcast\\cli.py` plan output must match the real TTS artifact path so downstream pipeline work can trust `data\\audio\\*.wav`.

## Recent Session (20260417T173826Z)

📌 **Bilingual TTS Voice Routing Fixed (Issue #6)**
- Implemented multi-voice audio generation: `_split_script_by_language()` detects Bulgarian/English segments
- Added `_generate_bilingual()` path for per-segment voice switching and WAV concatenation
- Added `--en-voice` and `--bg-voice` CLI flags to `generate-audio` and `run` commands
- Comprehensive bilingual test coverage with voice availability validation and temp file cleanup
- Updated README.md with usage examples for bilingual voice configuration
- Nested repo commit: 14d429b (Fix bilingual TTS voice routing)
- Ready for push and PR #7 merge

## Team Updates

📌 Team update (2026-04-17T16:07:23Z): pyttsx3 output is WAV-first — standardize audio artifact on .wav format, explicit voice validation with failure on unavailable voice, future MP3 support as separate enhancement. Decided by Ripley

📌 Team update (20260417T173826Z): Bilingual TTS voice routing implemented — script language detection and per-segment voice switching via WAV concatenation; backward compatible single-voice path unchanged. Fixed by Parker
