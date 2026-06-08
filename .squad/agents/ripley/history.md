# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** Python 3.11+ stdlib-first CLI scaffold
- **Created:** 2026-04-13T17:28:16.452Z

## Core Context

**Architecture:**
- App scaffold at `my-project\src\knigovishte_podcast\` with fetcher, translator, script builder, audio generator
- Stable artifact paths: `my-project\data\{articles,scripts,audio,rss}`
- Nested repo pattern: `.squad/` at root for coordination, `my-project/` as independent git repo
- CLI-first, Python 3.11+ stdlib-first approach

**Key Decisions:**
- (D#3) Initial project structure: Python stdlib-first, data-local persistence, pipeline boundaries stable
- (D#13) Nested repository hygiene: `.squad/` coordination separate from app repo
- (D#14) CI packaging shape: Ruff lint, mypy type-check, unittest, build validation
- (D#32) Google English voice routing: treat all `en-*` Google voices consistently (voice-name-first language derivation)

**Active Work:**
- Assigned issues: #9 (local web UI, Bishop), #8 (artifact dedup, Bishop)

**Learnings (Historical):**
- English TTS voice routing must support en-* pattern broadly, not just en-US
- Regression coverage for bilingual flows: title + body segments make multiple Google calls
- Copilot instructions should be minimal and actionable (not speculative)
- Squad decisions recorded in inbox/ for post-session merge and cross-agent propagation
- Artifact regeneration vs. code bugs: when generated output (e.g., podcast.xml) is stale or incorrect but the generation code itself is sound, route to the orchestrator (Bishop) to rebuild with correct inputs/configuration—not a code refactor issue

## Legacy Sessions Summarized (2026-04-13 – 2026-04-17)

**Scaffold Phase (13–17 Apr):** Established Python 3.11+ stdlib-first, nested repo hygiene (`.squad/` coordination, `my-project/` app). Implemented fetcher (urllib + HTMLParser), script builder (bilingual), CI/CD (ruff, mypy, unittest), taskboard, marketplace, and template library. Artifact paths: `data/{articles,scripts,audio,rss}`. Verified nested-repo test flow and packaging via `pyproject.toml`.

**Key Learnings:** (1) Document only what is true/actionable today. (2) English Google TTS: treat `en-*` names as Google routes, derive `language_code` from voice. (3) Bilingual flows make multiple TTS calls (title + body segments). (4) Taskboard status field drives workflow; requirements.txt audit ongoing.

## Recent Sessions (2026-04-19+)

📌 **2026-04-26T090000Z: Issue #21 Reconciliation & Closeout**
- **#21 CLOSED:** Episode titles fix complete. Ash's revision (prefer persisted English title over filename cleanup) approved by Lambert. RSS regressions verified. Routing labels removed; issue marked completed.

📌 **2026-04-26T090300Z: Issue #23 Triage**
- **#23 TRIAGED:** podcast.xml contains stale artifacts (wrong base URL `efrat-tensor:8000`, old April 2026 timestamps). Root cause: artifact generation is correct, but inputs were wrong when last built. Routed to squad:bishop for artifact regeneration with correct base URL configuration.

📌 **2026-04-26T085000Z: Squad Inbox Cleanup**
- **#19:** CLOSED (state:completed) — PR #20 merged, UDP socket routing now resolves LAN IP correctly
- **#22:** MARKED BLOCKED (label:question) — awaiting user clarification on audio format choice and rationale

📌 **2026-04-26T091000Z: Issue #22 Triage & Routing**
- **#22 ROUTED TO PARKER:** User clarification received: "consider using mp3, for streaming compatibility"
- Action: Removed `question` label (blocker resolved), added `squad:parker` label
- Scope captured: Audio generation pipeline should output MP3 for broad streaming platform support
- Status: Ready for Parker (Audio Dev) to implement

📌 **2026-04-26T084500Z: Issue Triage #19, #21, #22**
- #19: RESOLVED (PR #20, UDP hostname LAN detection)
- #21: ROUTED TO BISHOP — strip "vijte NNNN" prefix from RSS titles (squad:bishop)
- #22: BLOCKED — needs format clarification from user

📌 **2026-04-24T08:06:16Z: Issue #16 Root Cause**
- `local-rss-delivery` CLI command not wired in `cli.py` (backend module exists, integration missing)
- Reassigned to Bishop; HIGH priority, blocks #15 verification

📌 **2026-04-19T122809Z: Approval & Closeout**
- Lambert approved issues #8 (artifact dedup) and #9 (local web UI)
- Both commits published to master; decision #28 recorded

📌 **2026-04-19T100000Z: Issue #9 Architecture**
- Decided: Flask backend + vanilla JS frontend, `/generate` endpoint
- Bishop implemented; commit a53c84e; CLI + web UI coexist

📌 **2026-04-19T12:50:03Z: Issue #14 Revision**
- Revised English voice routing to treat all `en-*` Google names consistently
- Language code derived from voice name; architectural alignment complete

📌 **2026-04-26T092000Z: Issue #24 Triage**
- **#24 TRIAGED:** Langbly API timeout (60s read timeout on `eu.langbly.com:443`) during web UI episode generation.
- Root cause: Provider reliability issue, not code bug
- Routed to squad:ash (Language/AI Dev) for diagnosis: verify API key, investigate endpoint health, consider retry strategy or fallback provider
- Status: Ready for Ash to investigate Langbly configuration and resilience options

📌 **2026-04-28T103000Z: Issue #26 Closeout**
- **#26 CLOSED:** RSS server disconnect resilience complete. Bishop implemented graceful error handling for client-aborted file transfers in `local-rss-delivery` command.
- Lambert approved after live validation (forced mid-transfer disconnect, verified server kept serving subsequent requests without traceback noise).
- Routing label (squad:bishop) left for audit trail; issue marked COMPLETED.

📌 **Earlier Sessions (2026-04-17 and earlier):**
- Issue #6 (Bulgarian voice): Fixed via PR #7; bilingual voice routing via language segmentation
- Issue #8 (artifact dedup): Bishop completed; manifest-based SHA-256 dedup in data/audio/
- PR cleanup verified; stale PRs (#4, #5) correctly closed


�� Team update (2026-05-09T12:47:57Z): Awesome-copilot marketplace registered in .squad/plugins/marketplaces.json. Squad now has access to both squad-skills and awesome-copilot marketplaces. Administrative registration completed by Ripley.
