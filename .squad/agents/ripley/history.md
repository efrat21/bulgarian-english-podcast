# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** Python 3.11+ stdlib-first CLI scaffold
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Initial squad cast created for a greenfield project with unclear stack choices.
- Copilot instructions file should be kept minimal and fact-based while project is in scaffolding phase. Removed generic "when code is added" future-facing sections and MCP placeholder guidance. Focused on workspace layout (squad at root, my-project as nested empty repo) and work routing rules that are already decided.
- Team consensus decisions properly recorded in `.squad/decisions/inbox/` for post-session processing.
- Principle: Document only what is true and actionable today, not speculative future states.
- The application scaffold now lives in `my-project\src\knigovishte_podcast\` with explicit boundaries for fetching, translation, script building, and audio generation.
- The initial stack choice is **Python 3.11+**, stdlib-first and CLI-oriented, to keep Windows setup simple while preserving good libraries later for scraping, translation, and TTS.
- Stable local artifact paths are `my-project\data\articles\`, `my-project\data\scripts\`, and `my-project\data\audio\`.
- The first implemented domain behavior is the bilingual script formatter in `my-project\src\knigovishte_podcast\services\script_builder.py`, with coverage started in `my-project\tests\test_script_builder.py`.
- The first fetcher slice now lives in `my-project\src\knigovishte_podcast\services\fetcher.py` and uses `urllib` plus `HTMLParser` so the project stays stdlib-first while the site shape is still being proven.
- The fetcher boundary is intentionally split into `fetch_html()` and `parse_html()` so the CLI can cache raw source HTML and tests can verify parsing without network access.
- `my-project\src\knigovishte_podcast\cli.py` now exposes a `fetch` command that caches article HTML under `my-project\data\articles\` and prints a parse summary for the fetched article.
- Fetcher tests live in `my-project\tests\test_fetcher.py` and mirror the existing `unittest` style with inline HTML fixtures.
- Created `.squad/taskboard.json` as the team's operational task tracker (non-markdown, JSON format for structured status tracking). Format includes task ID, owner, status, priority, dependencies, and notes.
- Taskboard workflow: when a task completes, update its `status` field from "pending" to "done" and commit with `git add .squad/taskboard.json && git commit -m 'Update task board: <task-id> complete'`.
- Audited actual imports across all Python files in `my-project/` and confirmed `requirements.txt` reflects reality: `requests>=2.31`, `python-dotenv>=1.0`, `pyttsx3>=2.90`. All other imports are stdlib or internal modules.
- Task `requirements-txt-audit` assigned to Bishop with high priority to ensure ongoing synchronization between code imports and declared dependencies.

## Recent Session (2026-04-13T180001Z)

📌 **Scribe Processing Complete**
- Merged 4 decision inbox entries (user directive, project structure, copilot instructions v1 & v2) into active decisions.md
- Created orchestration log for Ripley's scaffolding work
- Created session log documenting structure decisions
- Updated agent histories with consolidated context
- Inbox cleanup initiated (4 files marked for deletion)

## Recent Session (2026-04-13T180002Z)

📌 **Knigovishte Fetcher First Slice Completed**
- Implemented stdlib-first article fetcher using urllib and HTMLParser
- Split fetcher boundary into `fetch_html()` and `parse_html()` for caching and deterministic testing
- Supports public Knigovishte/Vijte article pages with `kmedia-article-title` and `kmedia-article-content`
- Comprehensive test suite with inline HTML fixtures
- Decision captured and consolidated into active decisions.md
- Orchestration and session logs created documenting deliverables
- Ready for translator integration in next slice

## Recent Session (2026-04-13T180003Z)

📌 **Squad Template Files Created**
- Created 5 missing reference/template files based on live coordinator contract in `.github/agents/squad.agent.md`:
  - `.squad/templates/ralph-reference.md` — Ralph's work monitoring cycle, activation, and idle-watch mode
  - `.squad/templates/ceremony-reference.md` — Ceremony metadata, triggers, facilitator role, and logging
  - `.squad/templates/prd-intake.md` — PRD decomposition flow, Lead spawn template, mid-project updates
  - `.squad/templates/human-members.md` — Adding humans to roster, sync routing, reviewer lockout, examples
  - `.squad/templates/copilot-agent.md` — @copilot autonomous coding agent, capability profile, triage, PR workflow
- All files kept concise but complete for coordinator behaviors they document
- No changes to unrelated project/app files
- Key patterns: Ralph's loop never asks permission; Ceremonies run before/after work; PRD uses Lead decomposition; Humans block sync only; @copilot routes via issues asynchronously

## Recent Session (2026-04-17T153000Z)

📌 **Taskboard and Requirements Audit Created**
- Created `.squad/taskboard.json` with 12 tracked tasks, all critical path items assigned to squad members
- Divided work into logical slices: scaffold (done), translator, TTS, pipeline, CLI, testing, CI/CD, documentation, deployment
- Established taskboard as the operational source of truth for status tracking and work sequencing
- Dependencies explicitly encoded (e.g., pipeline waits for all four core modules)
- Audited `my-project/requirements.txt` against actual imports; confirmed all non-stdlib dependencies are tracked
- Added task `requirements-txt-audit` assigned to Bishop with high priority to ensure ongoing sync
