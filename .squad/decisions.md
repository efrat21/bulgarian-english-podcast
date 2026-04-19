# Squad Decisions

## Active Decisions

### 1. User Directive: Content Source & Podcast Format (2026-04-13T17:43:25Z)
**Source:** User request (via Copilot)

Podcast pipeline configuration:
- **Source website:** https://www.knigovishte.bg/ (Bulgarian articles)
- **Output format:** Bilingual English-Bulgarian sentence-by-sentence playback
- **Script template:**
  ```
  Welcome to your daily episode for improving your hearing comprehension. 
  Today we have [ENGLISH_TITLE], [BULGARIAN_TITLE]. 
  Let's hear the article sentence by sentence, first in English and then in Bulgarian:
  [ENGLISH-BULGARIAN PAIRS]
  Now, let's hear it again:
  [ENGLISH-BULGARIAN PAIRS]
  Good job! See you soon!
  ```

### 2. User Directive: Translation Provider (2026-04-15T12:25:27Z)
**Source:** User request (via Copilot)

Use Langbly API for the translator implementation instead of LLM or other translation services.

**Rationale:** User preference — explicit direction to integrate Langbly.

**Impact:** Ash (Language/AI Dev) should update translator.py to use Langbly API as the backend provider behind the ArticleTranslator interface.

### 3. Initial Project Structure (2026-04-13)
**Owner:** Ripley

Architectural decision for first-pass scaffold:
- **Tech Stack:** Python 3.11+ with stdlib-first CLI approach
- **Pattern:** Local-first with committed output folders for caching
- **Data paths:** `my-project/data/{articles,scripts,audio}` for stable artifact storage
- **Pipeline boundaries:** Fetcher → Translator → Script Builder → Audio Generator (stable now, concrete providers delayed until fetcher proven on knigovishte.bg)
- **First implementation:** Script builder module with bilingual formatting logic
- **Why:** Stabilizes module contracts now while deferring provider selection until fetcher is battle-tested

### 3. Copilot Instructions Created (2026-04-13)
**Owner:** Ripley

Early-stage guidance document created for `.github/copilot-instructions.md`:
- Documented Squad framework context and team roster
- Established branch/PR naming conventions
- Defined decision workflow for team consensus
- Noted that build/test/lint commands will be added when development begins

### 4. Copilot Instructions Refactored (2026-04-13)
**Owner:** Ripley

Refined instructions to reflect current project state:
- Removed future-facing speculative sections
- Kept only actionable guidance (Squad structure, routing rules, PR guidelines)
- Established principle: document only what is true and actionable today
- Identified duplicate file at root level for cleanup

### 5. Knigovishte Fetcher First Slice (2026-04-13T18:00:02Z)
**Owner:** Ripley

First implementation slice for article fetching from knigovishte.bg:
- **Architecture:** Stdlib-first approach using `urllib.request` and `html.parser.HTMLParser`
- **Boundary split:** Separate `fetch_html(url)` and `parse_html(url, html)` for caching and testability
- **Scope:** Support only public Knigovishte/Vijte article pages with `kmedia-article-title` and `kmedia-article-content`
- **Constraints:** Strip quiz/comment chrome and image captions; use punctuation/newline-based sentence splitting as first-slice limitation
- **Deliverables:** `src/knigovishte_podcast/services/fetcher.py`, `tests/test_fetcher.py`, README updates, decision inbox entry

### 6. Configure Git Origin Remote (2026-04-17T151016Z)
**Owner:** Ripley

Configured the repository's `origin` remote to point to the canonical upstream repository.

**Decision:** Added git remote `origin` with URL: `https://github.com/efrat21/bulgarian-english-podcast`

**Rationale:**
- No remote was previously configured
- This remote serves as the canonical upstream for all team members
- Enables push/pull operations and CI/CD integration

**Outcome:** Remote configuration complete with both fetch and push URLs configured.

### 7. Copilot Instructions Refactored (2026-04-17T151016Z)
**Owner:** Ripley

Refined `.github/copilot-instructions.md` to reflect what is true today, not future speculation.

**Changes:**
- Removed generic "When Code is Added" section
- Removed placeholder MCP servers section
- Kept and clarified Squad workspace structure, work routing rules, PR/branch guidelines, and decision-writing protocol

**Rationale:**
- Constraint: No build, test, or lint tooling yet. Stack is TBD.
- Principle: Document only what is actionable and true today.

**Outcome:** Agents can read instructions in 90 seconds without wading through conditional future sections. Clear, actionable guidance for current state.

### 8. User Directive: Task Board & Requirements Tracking (2026-04-17T12:30:04Z)
**By:** efratmiyara-work (via Copilot)

User directive captured for team memory:
- Keep a tracked task file (`.squad/taskboard.json`) as the source of truth for project work
- Update task statuses whenever work finishes
- Commit those updates to git
- Include explicit task to update `my-project\requirements.txt` with all imports used by the application

**Rationale:** User request — ensure all work is visible, tracked, and committed to version control. Requirements file must stay synchronized with actual code imports.

**Impact:** Ripley to establish taskboard as canonical tracking. All agents update status on completion. Bishop to audit and maintain requirements.txt alignment.

### 9. Ash Decision: Langbly Batch Request Shape (2026-04-17T16:07:23Z)
**Owner:** Ash

Keep the Langbly translator boundary explicit and sentence-safe:
- Send title plus article sentences as one ordered batch
- Include the API key in the request payload for the current Langbly integration
- Reject responses whose translation count does not match the submitted batch

**Rationale:** This keeps title/sentence alignment inspectable and prevents silent ordering drift from malformed provider responses.

**Affected paths:** `my-project\src\knigovishte_podcast\services\translator.py`, `my-project\tests\test_translator.py`

### 10. Bishop Decision: Pipeline Owns Artifact Persistence (2026-04-17T16:07:23Z)
**Owner:** Bishop

Keep artifact persistence inside the pipeline layer:
- The default `pipeline()` factory assembles the concrete fetcher, translator, script builder, and audio generator
- `ArticleToPodcastPipeline.run()` caches fetched HTML under `my-project\data\articles\`
- The pipeline writes the generated script under `my-project\data\scripts\` before invoking TTS
- The CLI stays thin and only reports the resulting artifact paths

**Rationale:** Keeps the orchestration understandable from the edges inward. Avoids duplicating fetch/cache/script-writing logic across CLI commands. Gives future callers one stable backend interface.

**Affected paths:** `my-project\src\knigovishte_podcast\pipeline.py`, `my-project\src\knigovishte_podcast\models.py`, `my-project\src\knigovishte_podcast\cli.py`

### 11. Parker Decision: pyttsx3 Output Is WAV-First (2026-04-17T16:07:23Z)
**Owner:** Parker

Standardize the local audio artifact on `.wav` output for the pyttsx3-backed generator and make planning/output messaging match that actual file path.

**Rationale:** The implementation already generates `.wav` files reliably with pyttsx3. Claiming `.mp3` in planning output created a mismatch between reported and real artifacts. Audio generation should only report success when a fresh file exists at the expected path.

**Impact:** TTS output under `my-project\data\audio\` is currently `*.wav`. Voice selection now fails explicitly when the requested voice is unavailable. Future MP3 support should be a separate enhancement with an explicit conversion step or different backend.

### 12. Ripley Decision: Nested Repository Hygiene (2026-04-17T16:07:23Z)
**Owner:** Ripley

Keep the workspace root and the application repo intentionally separate:
- The root repo owns `.squad\` coordination state
- `my-project\` remains its own git repository
- The root `.gitignore` must ignore `my-project\` so the coordination repo stays clean

**Rationale:** The current workspace uses a nested application repository. Without an explicit ignore, root-level git status shows `my-project\` as repo dirt even when the application repo is healthy. Ignoring the nested repo preserves the separation we already rely on and avoids accidental cross-repo staging.

**Impact:** Ripley and Scribe can keep the root repo focused on Squad state and decisions. App changes continue to be managed from `my-project\`. Future cleanup work should treat nested-repo noise as a repo-boundary problem first, not as a deletion target.

### 13. Ripley Decision: Python CI and Packaging Shape (2026-04-17T16:07:23Z)
**Owner:** Ripley

- Add a single GitHub Actions workflow at `.github/workflows/python-ci.yml`
- Run it on pushes and pull requests that touch `my-project/` or the workflow itself
- Validate four things only: lint (`ruff`), type-check (`mypy`), unit tests (`unittest`), and package build (`python -m build`)
- Treat the app as a standard Python package distributed via wheel/sdist for now; do not add Docker or hosted deployment infrastructure

**Rationale:** The stack is now concrete enough: the project already has `pyproject.toml`, a working unittest suite, and an installable CLI entry point. That makes package-build validation and lightweight static checks justified, while anything heavier would be invented infrastructure for a local CLI.

**Implications:** Dev tooling lives as a `dev` extra in `my-project/pyproject.toml`. `mypy` is scoped to real application entry points (`main.py`, `src/`) and explicitly tolerates the untyped `pyttsx3` dependency. Linting targets `main.py`, `src`, and `tests`, not ad hoc manual scripts outside the supported developer workflow.

### 14. Ripley Decision: TTS Voice Fix — Architecture Divergence (2026-04-17T20:50:00Z)
**Owner:** Ripley

Parker's local fix for issue #6 (commit `14d429b`, "Fix bilingual TTS voice routing") uses a **segment-directory caching architecture** for bilingual audio generation.

The existing draft PR #7 (`copilot/fix-bulgarian-voice-audio` on GitHub) implements the same feature using a **stateless temp-WAV concatenation approach** with explicit CLI argument handling.

**Both are functionally correct, but architecturally incompatible:**
- Local: Persistent `_segments/` directories + segment caching + Unicode-based language detection
- PR: Inline script splitting + temp file cleanup + prefix-based language detection

**Decision:** PR #7 is the canonical design for this fix. It is:
- Already drafted and visible on GitHub
- Simpler (no directory magic, uses stdlib `wave` module)
- Tested with comprehensive bilingual test cases
- Ready to merge and deploy

**Action for Ralph:**
1. Merge PR #7 directly to `master` on GitHub
2. Pull the merged code into `my-project/` locally
3. Parker can then decide: keep local work for reference, or discard and align with the merged version

**Why:** Avoids conflicting implementations in history. Publishes the cleaner, simpler design. Team consensus already visible in the PR review threads.

### 15. Ripley Blocker: Squad Repository Remote Conflict (2026-04-17T20:55:00Z)
**Owner:** Ripley  
**Status:** Blocker — prevents push of squad decisions

The root repository (hosting `.squad/` coordination) is configured with:
```
origin = https://github.com/efrat21/bulgarian-english-podcast
```

This is the **application repository**, not the squad coordination repository.

**Problem:** Squad decisions cannot be pushed because:
1. Root repo (`.squad/decisions.md`) is now ahead of `origin/master`
2. But `origin/master` is the app repo, which has unrelated commits
3. A non-fast-forward push would fail; a force push would clobber the app repo

**Current state:**
- Local root: commits `7d31cd8` (Ripley decision) + `8cf3ca3` + `f5efa22` + `13fe63f` + more
- Remote `origin/master`: `db023a1` (app repo)
- Divergence: root is 16+ commits ahead; remote is 7+ commits ahead of root's base

**Why this happened:**
- Decision #6 set `origin` to point to the app repo
- But root repo (squad coordination) and app repo (`my-project/`) are separate git repos
- Squad state should not be mixed into app repo history

**Recommendation:**
1. **Separate concerns:** Create a dedicated Squad coordination repo on GitHub (or local tracking branch)
2. **OR integrate:** Merge squad state into app repo master once app is stable
3. **OR manual sync:** Ralph pulls squad decisions from the root directory locally, without remote push

**For now:** Squad decisions are **locally safe** (committed to disk at `.squad/decisions.md`). They just cannot be pushed to remote until this root/app separation is clarified.

### 16. Ripley Decision: PR #7 Bilingual Voice Routing Approved & Merged (2026-04-17T20:55:00Z)

**Owner:** Ripley

Issue #6 (missing Bulgarian voice in podcast audio) is resolved by PR #7 merge.

**Solution:** Bilingual voice routing via language-based script segmentation and per-segment voice switching.
- Architecture: Stateless temp-WAV concatenation using stdlib `wave` module
- Language detection: Script prefixes (`"Bulgarian:"`, `"English:"`)
- CLI support: Added `--en-voice` and `--bg-voice` flags to `generate-audio` and `run` commands
- Test coverage: 66 passing tests including comprehensive bilingual test cases
- Backward compatible: Single-voice mode unchanged when `--bg-voice` not specified

**Design rationale:** This stateless temp-WAV approach is preferred over segment-directory caching because it is simpler, uses only stdlib dependencies, and has no persistent state management overhead.

**Impact:** Parker's local commit (14d429b) implements a valid but architecturally incompatible segment-directory approach. That work is superseded by PR #7 merge; Parker can reference it for alternative approaches but should align future voice work with the merged design.

**Outcome:** Master branch now reflects the canonical bilingual voice design. Issue #6 resolved and ready for closure.

### 17. User Directive: Google Bulgarian Voice Integration (2026-04-18T04:53:56Z)
**By:** efratmiyara-work (via Copilot)

Use Google Cloud Text-to-Speech `bg-BG-Standard-B` for Bulgarian audio output.

**Rationale:** User request — enable Bulgarian voice synthesis in the podcast pipeline. Local pyttsx3/SAPI environment cannot produce Bulgarian speech; Google Cloud TTS resolves this constraint while maintaining backward compatibility with existing pyttsx3 implementation.

**Implementation:** Parker designed and implemented pluggable TTS provider system with GoogleTTSProvider for Bulgarian voice support. Lambert reviewed and approved. Implementation includes:
- Provider factory pattern enabling both pyttsx3 (local) and Google Cloud (external) backends
- GoogleTTSConfig for credential and voice management
- CLI `--tts-provider` flag for provider selection (default: pyttsx3, optional: google)
- Comprehensive test coverage for both providers
- Updated documentation with setup and usage examples

**Impact:** Bulgarian voice now available via user choice between local (English-only pyttsx3) and cloud (Bulgarian + English) providers. Architecture supports future TTS provider extensions.

**Outcome:** Commit ab50cd1 (`feat: use Google TTS for Bulgarian audio`). Live Google synthesis not yet verified on this machine due to missing GOOGLE_APPLICATION_CREDENTIALS, but implementation is correct and complete.

### 18. Ripley Decision: Bulgarian Voice Selection Final (2026-04-18T15:36:11Z)
**Owner:** Ripley  
**Status:** Resolved

**Decision:** Keep `bg-BG-Standard-B` as the default Bulgarian voice.

**Evidence:**

Live verification confirmed on 2026-04-18 with user's Google credentials:

| Voice Tier | Bulgarian Options | Cost/1M chars | Free Tier |
|------------|------------------|---------------|-----------|
| Standard | `bg-BG-Standard-B` (female only) | $4 | 4M chars/month |
| Chirp3 HD | 30 voices (15M/15F) | $30 | 1M chars/month |
| WaveNet | **None for Bulgarian** | N/A | N/A |

Key findings:
1. **Credentials verified working** — live synthesis returned 61KB audio
2. **Only one Standard Bulgarian voice exists** — no alternative Standard choice
3. **7.5× price difference** — Standard is substantially cheaper
4. **4× better free allowance** — 4M vs 1M chars/month
5. **No WaveNet for Bulgarian** — mid-tier option does not exist

**Rationale:**

For a language-learning podcast:
- Standard voice quality is adequate for comprehension practice
- Cost efficiency matters for sustained production
- The generous free tier (4M chars ≈ 80+ episodes/month) enables testing without charges

Premium Chirp3 HD voices exist if future quality requirements justify the 7.5× cost increase. The architecture already supports voice selection via `--bg-voice` and `GOOGLE_TTS_BG_VOICE_NAME` env var.

**Remaining Uncertainty:**

Quality is subjective. Users sensitive to prosody may prefer a Chirp3 HD voice. The upgrade path is documented and requires no code changes — just specify the preferred voice name.

**Impact:**

No code changes required. Current defaults are correct.

### 19. Ripley Decision: Issues #8 and #9 Triage (2026-04-19T120000Z)
**Owner:** Ripley  
**Status:** Triage Complete

**Issue #8: Artifact Deduplication ("check if the article was used before creating a new audio file")**

**Assignment:** Bishop (Backend Dev)

**Scope:** Add idempotency check to the pipeline. Before generating a podcast for an article, verify if that article has already been processed. If yes, skip generation and report the existing artifact.

**Risk & Constraints:**
- Moderate scope: Requires persistent artifact tracking (manifest, hash registry, or database)
- Current architecture: Articles cached under `my-project\data\articles\` with filename = URL slug
- Dependency: Existing pipeline/CLI foundation (stable)
- Open question: What constitutes duplicate? URL? Content hash?

**Implementation Guidance:**
- Keep check lightweight (avoid rescan overhead)
- Suggested: Simple manifest approach at `my-project\data\.article_registry.json` with `{url, article_id, generated_at}` entries
- CLI should report whether generation was skipped or newly created

**Labels:** `squad`, `squad:bishop`

**Rationale:** Pipeline orchestration and artifact caching are backend responsibilities. Bishop owns data flow and can decide the tracking mechanism.

---

**Issue #9: Local UI ("create a local user interface")**

**Status:** Requires architecture decision before assignment

**Scope:** Build a local UI for the podcast pipeline with features:
1. Optional URL input field
2. Fallback to latest article if URL empty
3. Hyperlink to output folder
4. Status display of generated podcasts

**Risk & Constraints:**
- High scope: Requires UI framework decision (web, desktop, CLI-based)
- Ambiguous architecture: Issue doesn't specify UI type
- Cross-cutting: Affects CLI, pipeline, data model, and frontend tooling
- Dependency: Needs stable pipeline/CLI (in place)

**Routing:** Architecture-dependent. Options:
- **If web-based:** Bishop (backend API + Flask/Django) + frontend specialist (TBD)
- **If desktop:** Ripley (architecture) + specialist for PyQt/Tkinter/etc (TBD)
- **If enhanced CLI:** Bishop (extend existing CLI with interactive menu)

**Labels:** `squad` only (pending clarification)

**Next Step:** Ripley to propose UI type and sync with user (efratmiyara-work) before member assignment.

---

**Summary:**

| Issue | Owner | Status | Labels |
|-------|-------|--------|--------|
| #8 | Bishop | Assigned; awaiting pickup | `squad`, `squad:bishop` |
| #9 | TBD | Architecture pending | `squad` |

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
