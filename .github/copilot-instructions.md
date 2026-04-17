# Copilot Instructions — first_squad_project

You are working on a Squad AI-managed project building a Bulgarian-to-English article translator with podcast generation.

## Build, Test, and Lint

- No build, test, or lint commands exist yet.
- No single-test command exists yet.

## High-Level Architecture

- **Squad framework:** Lives at repo root under `.squad/`
  - `team.md` — roster of team members and their roles
  - `routing.md` — work assignment rules
  - `decisions.md` — team architectural decisions
  - `agents/{member}/charter.md` — each member's mandate
  - `decisions/inbox/` — where you write decisions for team review
- **Application code:** In `my-project/` (currently a nested git repo, empty except for `.git`)
- **Current big picture:** the coordination layer exists at the workspace root, but the actual app implementation has not been scaffolded yet.

## Key Conventions

1. **Before picking up an issue:** Check `.squad/team.md` for your role, then `.squad/routing.md` for who should handle this work.
2. **Branch naming:** `squad/{issue-number}-{kebab-case-slug}` (e.g., `squad/1-setup-build`)
3. **PR format:** Include `Closes #{issue-number}` and the co-author trailer:
   ```
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   ```
4. **Decisions:** If your work sets direction, write to `.squad/decisions/inbox/{your-name}-{slug}.md`. The Scribe will integrate it.
5. **Need another agent's input?** Say so in comments or decisions — the Coordinator will bring them in.

## Work Routing

| Work Type | Owner |
|-----------|-------|
| Architecture, scope, code review | **Ripley** (Lead) |
| Web ingestion, orchestration, backend | **Bishop** (Backend Dev) |
| Translation, language processing | **Ash** (Language/AI Dev) |
| Audio generation, TTS, podcasting | **Parker** (Audio Dev) |
| Testing, edge cases, verification | **Lambert** (Tester) |

See `.squad/routing.md` for the full routing table and issue labeling rules.
