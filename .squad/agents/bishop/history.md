# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Backend work will likely center on fetching, parsing, translation orchestration, and audio handoff.
- `my-project\src\knigovishte_podcast\pipeline.py` is the stable backend seam for fetch → translate → script → audio orchestration.
- Default pipeline runs cache article HTML in `my-project\data\articles\` and always persist scripts in `my-project\data\scripts\` before TTS.
- Minimal CLI exposure for backend integration now lives in `my-project\src\knigovishte_podcast\cli.py` as the `run` subcommand.
- `my-project\tests\test_pipeline.py` covers orchestration wiring, artifact persistence, cached HTML reuse, and CLI run reporting.
- The CLI now covers fetch, translate, build-script, generate-audio, and run; translation previews are persisted as `my-project\data\scripts\{slug}.translation.txt` while `--refresh` forces a fresh article download over cached HTML.
- Local feed delivery now stages publishable artifacts under `my-project\data\rss\` (`podcast.xml` plus `episodes\`) instead of serving the whole data tree.
- `my-project\src\knigovishte_podcast\services\rss.py` is the new backend seam for rebuilding the LAN RSS feed and serving it with stdlib HTTP primitives.
- RSS subscriber-facing episode titles should normalize stored slug filenames by stripping the leading `vijte-{id}-` segment before publishing `<item><title>` text; regression coverage lives in `my-project\tests\test_rss.py`.
- The `local-rss-delivery` CLI command prints a subscribable LAN URL, rebuilds delivery files from existing `data\audio\` artifacts, and keeps the first slice dependency-free by serving the current `.wav` output directly.
- `my-project\tests\test_tts.py` bilingual Google-override regressions must assert per-segment synthesis calls, because `_split_script_by_language()` keeps English title and body as separate English segments around Bulgarian content.
- English Google voice routing should treat any valid `en-*` Google voice name as a Google path, not only `en-US-*`; derive the `language_code` from the selected voice name and fall back through `GoogleTTSConfig` only when needed.
- Key publication paths for issue #14 were `my-project\src\knigovishte_podcast\config.py`, `my-project\src\knigovishte_podcast\services\tts.py`, `my-project\src\knigovishte_podcast\cli.py`, `my-project\tests\test_tts.py`, and `my-project\tests\test_cli.py`; final published commit on nested app repo master was `4d1f36b`.
- README phone-side delivery docs should tell users to run `local-rss-delivery`, use the printed LAN URL (or `--public-host <LAN-IP>`), and keep both phone and computer on the same trusted Wi-Fi while the server is running.
- Local RSS README guidance should also note that Podcast Addict setup currently serves staged `.wav` enclosures, while `.mp3`, `.m4a`, and `.aac` are supported when those files exist under `data\rss\episodes\`.
- `my-project\src\knigovishte_podcast\services\rss.py` must load `my-project\.env` before resolving `PODCAST_BASE_URL`; otherwise `local-rss-delivery` ignores the documented base URL override unless the operator exports it in the live shell.
- Issue #23 validation path: rebuild with `python main.py local-rss-delivery --no-serve`, then inspect `my-project\data\rss\podcast.xml` for the expected LAN host and current metadata-derived episode titles.
- `my-project\src\knigovishte_podcast\services\translator.py` should raise a dedicated `LangblyTimeoutError` once all configured Langbly endpoints time out, so upstream callers can keep the timeout copy deliberate instead of echoing raw requests exceptions.
- `my-project\src\knigovishte_podcast\web.py` now owns the user-facing translation-timeout message via `_format_error()`, appending that no episode was generated and the operator should retry later.
- Issue #24 regression proof lives in `my-project\tests\test_translator.py` and `my-project\tests\test_web.py`; translator coverage must prove fallback preserves payload/header/timeout parity, and web coverage must assert the visible timeout message.

## Team Updates

📌 Team update (2026-04-17T16:07:23Z): Pipeline owns artifact persistence — keep artifact caching inside pipeline layer (HTML in data/articles, scripts in data/scripts before TTS), keep CLI thin with only reporting. Decided by Ripley

📌 Team update (2026-04-19T122809Z): Issues #8 and #9 verified and approved for publication. Both commits landed cleanly to master; artifact state validated; test suite green across both implementations. Close-out coordination delegated to Ripley. Signed off by Bishop

📌 Team update (2026-04-19T100000Z): Issue #9 completed. Local Flask web UI implemented with REST API endpoints for pipeline commands (`run`, `generate-audio`, `list-articles`). Web UI launches via `python main.py web` on localhost. CLI and web access coexist without conflicts. Commit a53c84e. Decided by Bishop

📌 Team update (2026-04-19T091835Z): Issue #8 completed. Durable artifact deduplication implemented via SHA-256 content hash + manifest at `my-project\data\audio\manifest.json`. Pipeline now idempotent; commit 93d31f9. Decided by Bishop

📌 Team update (2026-04-24T08:06:16Z): Daily Episode Automation (Issue #15) Decision #27 merged: Implemented hybrid scheduling with `daily-check` command (via external scheduler) and `daily-daemon` command (long-running background). Scheduler module at `services/scheduler.py`, state persisted in `data/scheduler_state.json`, deduplication via URL + content hash. 12 new unit tests, 2 CLI tests, 103 total passing, ruff/mypy clean. New module: `services/scheduler.py`; modified: `cli.py`, `README.md`, `tests/test_cli.py`. Ready for next phase. Decided by Bishop

📌 Team update (2026-04-24T08:06:16Z): Issue #16 Root Cause and Routing (Decision #28): `local-rss-delivery` CLI command was documented but not registered in `cli.py`, causing argparse "invalid choice" error. Ripley triaged and reassigned to Bishop for CLI integration completion. Task: wire `local-rss-delivery` subcommand, dispatch to RSS handler, end-to-end test with article generation, update task board. Priority HIGH, no blockers, depends on existing RSS modules from issue #15. Expected outcome: closes issue #16, unblocks issue #15 verification. Decided by Ripley

📌 Team update (2026-04-19T133000Z): Sentence prefix removal completed (commit a48e3f0) — removes "English:" and "Bulgarian:" from script body lines while preserving title markers and backward compatibility. Implementation tested (78 tests green), code reviewed and approved by Lambert. Publication BLOCKED by history divergence (local a48e3f0 vs remote 3d1ebce, no common ancestor). Requires Coordinator strategy for alignment. Documented by Scribe

📌 Team update (2026-04-19T133500Z): Force-push authorized and executed — nested repo remote history rewritten from 3d1ebce → a48e3f0. Commit a48e3f0 (Remove sentence prefixes from podcast scripts) now published to origin/master. Local and remote aligned. Decision #25 recorded. Decided by efratmiyara-work

📌 Team update (20260419T113723Z): Issue #11 completed — UI refinement (commit 116e9d9): artifact link behavior, progress messaging, section removal, category translation. Implemented by Bishop

📌 Team update (20260419T115408Z): Issue #11 reopened follow-up resolved — Bishop refined web UI success messaging per user feedback (commit bdb149c). Simplified artifact linking behavior, improved progress/completion messaging, removed redundant sections, translated category labels to English. Implementation tested and merged to master. Issue closed. Decided by Bishop

📌 Team update (2026-04-19T12:26:23Z): `local-rss-delivery` implementation complete — RSS service module at services/rss.py, CLI integration, test coverage green, validation passed. Workflow stages artifacts in `my-project\data\rss\`, serves over LAN with stdlib HTTP, reuses current `.wav` format. Decision #28 recorded. Ready for publication. Decided by Bishop

📌 Team update (2026-04-19T12:50:03Z): Issue #14 regression test alignment completed. Analyzed bilingual TTS flow: title segment + body segments make multiple Google calls. Updated test expectations from 1 to 2 English Google calls. Both bilingual and single-voice paths now tested correctly. Ready for Lambert's final approval. Alignment by Bishop


- Issue #16 root cause: `local-rss-delivery` was documented but not registered in `src\knigovishte_podcast\cli.py`, so argparse rejected it before any RSS flow could run.
- `ProjectPaths` now derives stable `data\rss\` and `data\rss\episodes\` locations automatically, which keeps RSS staging available to both CLI wiring and tests without changing existing callers.
- Regression coverage for local RSS should cover both seams: feed staging (`podcast.xml` plus copied enclosures) and actual HTTP serving, because the command must publish files and stay reachable on the LAN.

📌 Team update (2026-04-26T09:10:13Z): Issue #23 resolved — RSS service now loads `my-project\.env` before resolving `PODCAST_BASE_URL`. Modified `services/rss.py`, added regression test coverage, rebuilt `data\rss\podcast.xml` with corrected base URL and metadata-derived titles. CLI `--public-host` override still works. LAN delivery operational as documented. Decided by Bishop

📌 Team update (2026-04-26T121308Z): Issue #24 Langbly timeout failover — approved revision delivered. Merged Ash's translator failover implementation and added deliberate timeout error message in web UI. Modified `web.py` to format `LangblyTimeoutError` with explicit "no episode generated" message. Targeted regression tests cover translator failover, all-endpoints-down case, and web-layer message display. All 3 test modules passing; no regressions. Lambert approved for publication and closure. Decided by Bishop
