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
- Google voice routing now lives in `my-project\\src\\knigovishte_podcast\\services\\tts.py`: `en-US-*` and `bg-BG-*` voice names are treated as Google Cloud voices, while explicit local pyttsx3 substrings still route locally.
- `my-project\\src\\knigovishte_podcast\\config.py` now carries both English and Bulgarian Google TTS defaults, sourced from `GOOGLE_TTS_EN_*` and `GOOGLE_TTS_BG_*` environment variables.
- For issue #14, Parker selected `en-US-Standard-F` from the Google Cloud en-US Standard tier because it keeps standard-tier pricing and gives a clear neutral podcast read that pairs well with `bg-BG-Standard-B`.
- `my-project\\src\\knigovishte_podcast\\services\\tts.py` now exports final episodes as `.mp3` after rendering an intermediate `.wav`; conversion uses `imageio-ffmpeg` so local pyttsx3 and Google LINEAR16 paths can share one deterministic export step.
- `my-project\\src\\knigovishte_podcast\\services\\rss.py` now prefers `.mp3` when the same episode stem exists in multiple staged formats, while still accepting legacy `.wav`, `.m4a`, and `.aac` files.
- Verified quality commands for the app repo: `python -m unittest tests.test_tts tests.test_cli tests.test_rss tests.test_pipeline tests.test_dedup tests.test_scheduler tests.test_web -v`, `ruff check main.py src tests`, `mypy main.py src`, and `python -m build`.

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

📌 Team update (2026-04-17T20:55:00Z): PR #7 bilingual voice routing merged to master — stateless temp-WAV architecture approved as canonical design; local commit 14d429b superseded but preserved for reference. Issue #6 resolved. Decided by Ripley

📌 Team update (2026-04-17T18:39:32Z): Bulgarian voice validation confirmed — environment (pyttsx3/SAPI) exposes only English voices; no Bulgarian voice available on local machine; explicit voice-not-available errors working as designed. Verified by Parker & Lambert

## Recent Session (20260418T050000Z)

📌 **Google TTS Integration Implemented and Approved**
- Designed pluggable TTS provider abstraction (local pyttsx3 + external Google Cloud)
- Created GoogleTTSProvider with Bulgarian voice support (bg-BG-Standard-B)
- Refactored services/tts.py with provider factory pattern
- Added config.py for GoogleTTSConfig credential and voice management
- Updated CLI with --tts-provider flag for provider selection
- Comprehensive test coverage for both local and Google providers
- Updated README.md with setup and usage documentation
- Nested repo commit: ab50cd1 (feat: use Google TTS for Bulgarian audio)
- Lambert review: approved — architecture sound, implementation complete, backward compatible

## Team Updates

📌 Team update (2026-04-18T04:53:56Z): Google TTS integration complete — Bulgarian voice now available via pluggable provider system; local pyttsx3 (English-only) remains default, Google Cloud (Bulgarian + English) opt-in via CLI flag; live verification pending GOOGLE_APPLICATION_CREDENTIALS setup. Implemented by Parker, approved by Lambert

## Recent Session (20260418T160000Z)

📌 **Bulgarian Google TTS Test Generation**
- Generated fresh Bulgarian audio test file using GoogleTTSProvider
- Input: vijte-1532-kolko-tezhi-edna-leka-muha.txt (11.13 KB script)
- Output: vijte-1532-kolko-tezhi-edna-leka-muha-bg-google-test.wav (24.63 MB, ~6 min)
- Voice: Google Cloud bg-BG-Standard-B (Bulgarian female)
- Live Google authentication verified
- Ready for production podcast generation

## Recent Session (20260419T144115Z)

📌 **Issue #12 Windows COM Initialization Fix Complete**
- Implemented `_windows_com_initialized()` context manager in services/tts.py
- Wraps local pyttsx3 generation (single-voice and bilingual paths) in COM initialization
- Uses ctypes.windll.ole32.CoInitialize()/CoUninitialize() with proper HRESULT handling
- Comprehensive test coverage added: 125+ new test lines for COM contract verification
- Tested on Windows request-thread filtering + TTS flow; fixes crash
- Nested repo commit: 5543082 (Fix Windows filter-path TTS crash)
- Merged via PR #13 to master; issue #12 closed

## Team Updates

📌 Team update (20260419T113723Z): Issue #12 assigned and active — Windows COM initialization bug in pyttsx3; fix at TTS boundary. Decision documented: COM init/cleanup inside services/tts.py protects all callers (CLI, web, filtering, background). Routed by Ripley, working by Parker

📌 Team update (20260419T144115Z): Issue #12 complete — Windows COM initialization context manager deployed at TTS boundary; local pyttsx3 protected on Flask request threads; tests passing; PR #13 merged. Implemented by Parker, logged by Scribe.

📌 Team update (2026-04-19T12:26:24Z): Issue #14 ("new english voice") queued for Parker — GitHub enhancement request to add Google Cloud Text-to-Speech English-US Standard voice option. Scope: research available voices, select Standard-tier option, add CLI voice parameter support (similar to issue #6). Priority: Medium. Sequencing: Start after `local-rss-delivery` completion. Decision #30 recorded. Routed by Ripley

📌 Team update (2026-04-19T12:50:03Z): Issue #14 ("Google English voice") completed by Parker and approved by Lambert. Selected `en-US-Standard-F` as default English voice; implemented Google TTS routing for en-* patterns; added voice CLI parameters. Ripley revised routing to treat all en-* Google voices consistently (voice-name-first language derivation). Bishop aligned regression test expectations with real bilingual TTS flow (two English Google calls). Issue approved for publication and closure. Decision #31-32 recorded. Decided by Parker, Ripley; approved by Lambert
