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

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
