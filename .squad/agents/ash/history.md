# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Language work will likely include translation quality, normalization, and preparation for TTS.
- Langbly translation now lives in `my-project\src\knigovishte_podcast\services\translator.py` and keeps the batch boundary explicit by sending title + sentence list in source order.
- Translator validation is part of the provider wrapper: reject partial/malformed Langbly batch responses before they can drift sentence alignment.
- Current dependency audit is reflected in `my-project\requirements.txt`; active non-stdlib imports remain `requests`, `python-dotenv`, and `pyttsx3`.
- Local RSS title extraction now prefers persisted `English title:` metadata from `my-project\data\scripts\{episode_slug}.translation.txt` or `.txt` before falling back to slug cleanup in `my-project\src\knigovishte_podcast\services\rss.py`.
- RSS regression coverage for issue #21 lives in `my-project\tests\test_rss.py`, including the `vijte-7549.wav` metadata case and metadata-over-filename precedence.
- `TranslationConfig.from_env()` in `my-project\src\knigovishte_podcast\config.py` now auto-adds Langbly's default host as a failover whenever a custom `LANGBLY_BASE_URL` is configured, with optional timeout/retry env knobs.
- Langbly resilience for issue #24 lives in `my-project\src\knigovishte_podcast\services\translator.py`: retryable transport/5xx failures can fail over across configured hosts while response-shape validation stays strict.
- Coverage for the timeout failover path is in `my-project\tests\test_translator.py` and `my-project\tests\test_config.py`, including regional-host timeout fallback and env-driven retry settings.
- Verified local `my-project/.env` contains `LANGBLY_API_KEY` and live translation calls succeed against `https://eu.langbly.com` with fallback to `https://api.langbly.com`.

## Team Updates

📌 Langbly translator decision (2026-04-17): Use Langbly API as the backend provider for ArticleTranslator interface. User preference for translation implementation. — decided by User
📌 Team update (2026-04-17T16:07:23Z): Langbly batch request shape — send title + sentences as one batch, include API key in payload, reject mismatched response counts. Decided by Ripley
📌 Team update (2026-04-26T08:56:42Z): Issue #21 RSS title metadata fix approved. RSS item titles now prefer persisted English title from translation artifacts; fallback to slug cleanup for legacy audio. All 78 regression tests pass. Ready for publication. Decided by Ash & Lambert

📌 Team update (2026-04-26T121307Z): Issue #24 Langbly timeout failover — initial revision submitted. Implemented regional-host timeout failover in translator service with dedicated `LangblyTimeoutError` exception and preserved auth/payload/timeout budget across retry attempts. Configuration auto-adds default host as known-good fallback. Regression tests cover technical correctness of failover mechanism. Blocked pending Bishop's repo fix with web UI retry message. Revision informational only; awaiting Bishop approval. Decided by Ash
