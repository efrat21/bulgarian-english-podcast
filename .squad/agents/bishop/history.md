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
- The `local-rss-delivery` CLI command prints a subscribable LAN URL, rebuilds delivery files from existing `data\audio\` artifacts, and keeps the first slice dependency-free by serving the current `.wav` output directly.

## Team Updates

📌 Team update (2026-04-17T16:07:23Z): Pipeline owns artifact persistence — keep artifact caching inside pipeline layer (HTML in data/articles, scripts in data/scripts before TTS), keep CLI thin with only reporting. Decided by Ripley

📌 Team update (2026-04-19T122809Z): Issues #8 and #9 verified and approved for publication. Both commits landed cleanly to master; artifact state validated; test suite green across both implementations. Close-out coordination delegated to Ripley. Signed off by Bishop

📌 Team update (2026-04-19T100000Z): Issue #9 completed. Local Flask web UI implemented with REST API endpoints for pipeline commands (`run`, `generate-audio`, `list-articles`). Web UI launches via `python main.py web` on localhost. CLI and web access coexist without conflicts. Commit a53c84e. Decided by Bishop

📌 Team update (2026-04-19T091835Z): Issue #8 completed. Durable artifact deduplication implemented via SHA-256 content hash + manifest at `my-project\data\audio\manifest.json`. Pipeline now idempotent; commit 93d31f9. Decided by Bishop

📌 Team update (2026-04-19T133000Z): Sentence prefix removal completed (commit a48e3f0) — removes "English:" and "Bulgarian:" from script body lines while preserving title markers and backward compatibility. Implementation tested (78 tests green), code reviewed and approved by Lambert. Publication BLOCKED by history divergence (local a48e3f0 vs remote 3d1ebce, no common ancestor). Requires Coordinator strategy for alignment. Documented by Scribe

📌 Team update (2026-04-19T133500Z): Force-push authorized and executed — nested repo remote history rewritten from 3d1ebce → a48e3f0. Commit a48e3f0 (Remove sentence prefixes from podcast scripts) now published to origin/master. Local and remote aligned. Decision #25 recorded. Decided by efratmiyara-work

📌 Team update (20260419T113723Z): Issue #11 completed — UI refinement (commit 116e9d9): artifact link behavior, progress messaging, section removal, category translation. Implemented by Bishop

📌 Team update (20260419T115408Z): Issue #11 reopened follow-up resolved — Bishop refined web UI success messaging per user feedback (commit bdb149c). Simplified artifact linking behavior, improved progress/completion messaging, removed redundant sections, translated category labels to English. Implementation tested and merged to master. Issue closed. Decided by Bishop

📌 Team update (2026-04-19T12:26:23Z): `local-rss-delivery` implementation complete — RSS service module at services/rss.py, CLI integration, test coverage green, validation passed. Workflow stages artifacts in `my-project\data\rss\`, serves over LAN with stdlib HTTP, reuses current `.wav` format. Decision #28 recorded. Ready for publication. Decided by Bishop

