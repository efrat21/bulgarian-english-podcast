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
