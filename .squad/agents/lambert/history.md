# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Testing will need to cover the full fetch → translate → audio pipeline, not just individual functions.
- The coverage gap was mostly execution-path, not missing files: translator tests existed but were not discoverable by unittest, so confidence improved by converting them into runnable suite coverage and adding failure-path checks for CLI and pipeline fallbacks.
- Environment validation: Bulgarian TTS voice generation is not supported on this machine; SAPI backend exposes English voices only; voice-not-available error correctly raised on explicit Bulgarian requests.
- Local Wi-Fi RSS delivery is wired through `my-project\src\knigovishte_podcast\services\rss.py` and exposed from the `local-rss-delivery` CLI entrypoint in `my-project\src\knigovishte_podcast\cli.py`.
- The delivery path publishes `data\rss\podcast.xml` plus copied episode enclosures under `data\rss\episodes\`; supported podcast-friendly enclosure formats are `.wav`, `.mp3`, `.m4a`, and `.aac`.
- Regression coverage for RSS feed generation, LAN file serving, CLI no-serve/serve paths, and IP-detection fallbacks now lives in `my-project\tests\test_rss.py` and `my-project\tests\test_cli.py`.
- RSS-specific verification still passes via `python -m unittest discover -s tests -p 'test_rss.py' -v` plus `python -m unittest discover -s tests -p 'test_cli.py' -k local_rss_delivery -v`; a live smoke run of `python main.py local-rss-delivery --host 127.0.0.1 --port 0 --public-host 127.0.0.1` served `data\rss\podcast.xml` and staged episodes from `my-project\data\audio\`.
- The broader `test_cli.py` suite currently has one unrelated failure in `test_web_command_starts_local_ui`, where patching `knigovishte_podcast.web.create_app` raises `AttributeError` before the RSS assertions run; RSS-local delivery tests themselves still pass.
- RSS item titles are currently derived from staged audio filename stems in `my-project\src\knigovishte_podcast\services\rss.py`; a probe with `vijte-7549.wav` produced the feed title `vijte 7549`, which matches issue #21's bug report.
- English title metadata already exists in translation artifacts rendered by `my-project\src\knigovishte_podcast\cli.py` (`scripts\<slug>.translation.txt` includes `English title: ...`), but `my-project\tests\test_rss.py` does not yet assert `<item><title>` content, so RSS title regressions can slip through even when enclosure URL tests pass.
- Issue #21 review outcome: `my-project\src\knigovishte_podcast\services\rss.py` now resolves RSS item titles from matching `data\scripts\<slug>.translation.txt` or `<slug>.txt` metadata before stripping `vijte-####` from filename stems; `my-project\tests\test_rss.py` now covers metadata-first title selection plus slug-cleanup fallback. Legacy audio that lacks matching metadata and has no title-bearing slug still falls back to `vijte ####`, so the fix depends on persisted script/translation artifacts being present.
- Issue #24 review target is `my-project\src\knigovishte_podcast\services\translator.py`: the current Langbly adapter makes one 60-second POST to `TranslationConfig.base_url` and bubbles timeout text up to the web UI through `my-project\src\knigovishte_podcast\web.py`.
- Existing coverage in `my-project\tests\test_translator.py` only proves generic request failures are wrapped; it does not yet prove recovery when a regional Langbly host such as `https://eu.langbly.com` times out and the canonical `https://api.langbly.com` endpoint is still usable.
- For issue #24 approval, I need concrete evidence on the user path: either the translator recovers from the regional-host timeout and the web-triggered run completes, or it fails fast with an explicit, intentional timeout message backed by targeted regression tests.
- Issue #24 review outcome: `my-project\src\knigovishte_podcast\services\translator.py` now raises `LangblyTimeoutError` only after every configured Langbly endpoint times out, while preserving identical payload, auth header, and timeout settings across `eu.langbly.com` → `api.langbly.com` failover attempts.
- The browser-facing timeout copy is intentionally shaped in `my-project\src\knigovishte_podcast\web.py` via `_format_error()`, and the regression gate for this path now lives in `my-project\tests\test_translator.py`, `my-project\tests\test_web.py`, and `my-project\tests\test_config.py`.
- Current verification for the Langbly timeout fix passed with `python -m unittest tests.test_translator tests.test_web tests.test_config` and `python -m unittest discover -s tests` from `my-project\`.

## Recent Session (20260417T183932Z)

📌 **Bulgarian Voice Validation Complete**
- Independent verification that environment cannot synthesize Bulgarian speech
- Confirmed SAPI voice enumeration: English-only voices available
- Explicit Bulgarian voice request fails as expected with voice-not-available error
- Edge case validated: error is raised, not silently falling back to wrong language

## Team Updates

📌 Team update (2026-04-17T18:39:32Z): Bulgarian voice validation confirmed — environment (pyttsx3/SAPI) exposes only English voices; no Bulgarian voice available on local machine; explicit voice-not-available errors working as designed. Verified by Parker & Lambert

## Recent Session (20260418T050000Z)

📌 **Google TTS Implementation Review and Approval**
- Reviewed Parker's pluggable TTS provider implementation
- Validated GoogleTTSProvider for Bulgarian voice (bg-BG-Standard-B)
- Confirmed architecture: provider factory pattern enables extensibility
- Verified test coverage comprehensive for both pyttsx3 and Google Cloud paths
- Checked backward compatibility: default behavior unchanged, Google opt-in
- Validated error handling and credential management
- Reviewed documentation accuracy and completeness
- Approved implementation: architecture sound, tests thorough, ready for production

## Team Updates

📌 Team update (2026-04-19T122809Z): Issue #9 local web UI (commit a53c84e) reviewed and approved. Flask-based REST API with HTML template, XSS protections active, pipeline integration correct, all 13 tests passing. Minor observations noted (generic exception path untested, inline template, filter selection deferred). Approved by Lambert

📌 Team update (2026-04-19T091835Z): Issue #8 artifact deduplication (commit 93d31f9) reviewed and approved. Content-aware SHA-256 hashing, atomic manifest writes, early exit before TTS, comprehensive test coverage. Minor observations noted (force-regenerate flag, concurrent write edge case). Decided by Lambert


📌 Team update (2026-04-19T133000Z): Sentence prefix removal review completed for commit a48e3f0. Verified all 78 tests pass (no regressions), full end-to-end integration trace validated through script builder and TTS language detection state machine, backward compatibility preserved. APPROVED FOR PUBLICATION pending history alignment. Non-blocking observations: add full-script integration test in future; control-line string matching edge case (low risk); blank-line segment boundaries harmless for TTS. Decided by Lambert

📌 Team update (2026-04-18T04:53:56Z): Google TTS integration complete — Bulgarian voice now available via pluggable provider system; local pyttsx3 (English-only) remains default, Google Cloud (Bulgarian + English) opt-in via CLI flag; live verification pending GOOGLE_APPLICATION_CREDENTIALS setup. Implemented by Parker, approved by Lambert

📌 Team update (2026-04-19T133500Z): Force-push resolution complete — commit a48e3f0 (Remove sentence prefixes from podcast scripts) published to origin/master. User explicitly authorized remote history rewrite. Local and remote now aligned at a48e3f0. Publication successful. Decision #25 recorded in decisions.md. Coordinated by Scribe

📌 Team update (20260419T115408Z): Issue #12 Windows COM initialization in TTS reviewed and approved (PR #13, commit 5543082). Context manager wraps all local TTS calls with CoInitialize/CoUninitialize handling; HRESULT edge cases properly managed (S_FALSE, RPC_E_CHANGED_MODE, failures). Cross-platform safe (no-op on non-Windows). All 85 tests pass. Minor observations: missing tests for COM failure path and non-Windows no-op branch (low risk). APPROVED FOR PUBLICATION. Decided by Lambert

📌 Team update (2026-04-19T12:26:25Z): Regression testing for `local-rss-delivery` complete — RSS feed generation with multiple formats (`.wav`, `.mp3`, `.m4a`, `.aac`), LAN serving with IP detection fallback, CLI command paths validated. All regression tests pass; no regressions detected. Feature package complete and ready for publication. Validated by Lambert

📌 Team update (2026-04-19T12:50:03Z): Issue #14 Google English voice review cycle completed. First pass rejected for inconsistent non-en-US override routing; second pass rejected for regression test mismatch (bilingual flow makes two Google calls, not one); final pass approved after Bishop aligned test expectations. Issue approved for publication and closure. Decision #31-32 recorded. Approved by Lambert


📌 Team update (2026-04-26T11:49:08Z): Issue #21 RSS title patch reviewed on working-tree changes to `my-project\src\knigovishte_podcast\services\rss.py` and `my-project\tests\test_rss.py`. Result: not approved yet — stripping `vijte NNNN` from sluggy filenames works for `vijte-7549-the-little-prince.wav`, but a probe with `vijte-7549.wav` still emits `vijte 7549`, and the implementation still does not read actual English title metadata from `scripts\<slug>.translation.txt`. Tests pass, but coverage remains partial because the new assertion only checks slug-derived lowercase title text.

📌 Team update (2026-04-26T08:56:42Z): Issue #21 RSS title metadata fix approved. Ash revised RSS service to prefer persisted English title from translation artifacts; fallback to slug cleanup for legacy audio without metadata. Regression tests now cover `vijte-7549.wav` metadata case and metadata-precedence. All 78 tests pass, no regressions. APPROVED FOR PUBLICATION. Decided by Lambert

📌 Team update (2026-04-26T121307Z): Issue #24 Langbly timeout failover — initial revision rejected. Ash submitted technical failover logic with preserved auth/payload/timeout across retry attempts. Blocking constraint: translator module correct but upstream caller (web UI) still bubbles raw timeout text; web layer must display deliberate "no episode generated" message. Requirement: Independent revision by Bishop with web UI integration. Revision informational only; awaiting approved fix. Decided by Lambert

📌 Team update (2026-04-26T121308Z): Issue #24 Langbly timeout failover — final revision approved. Bishop delivered complete fix with web UI integration. Translator failover logic merged; web.py formats `LangblyTimeoutError` with explicit "retry later" message. Regression tests cover both layers: translator preserves payload/auth/timeout, web message is intentional. All 3 test modules passing; no regressions detected. APPROVED FOR PUBLICATION AND CLOSURE. Decided by Lambert
