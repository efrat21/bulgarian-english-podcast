# Ripley — Session History

## Recent Work

### 2026-04-13: Created Copilot Instructions
- Created `.github/copilot-instructions.md` for first_squad_project
- Documented Squad team context, Branch/PR guidelines, and MCP server guidance
- Project is in early-stage (no code yet), so instructions note current status and guide for future development

## Learnings

### Project Structure
- **Repository:** `first_squad_project/my-project` (empty, git initialized)
- **Team framework:** Squad with Coordinator, Scribe (Ralph), and other members
- **Key files:** `.squad/team.md`, `.squad/routing.md`, `.squad/decisions.md`
- **MCP config:** Available at `.copilot/mcp-config.json` with GitHub server configured

### Convention Patterns
- Branch naming: `squad/{issue-number}-{kebab-case-slug}`
- PR guidelines: Reference issue, mention squad member if labeled, co-author trailer required
- Decisions go to `.squad/decisions/inbox/` for Scribe integration
- Early-stage projects need clear guidance on where to add build/test/lint commands once development starts

### Key File Paths
- `.squad/team.md` - Team roster and capability profiles
- `.squad/routing.md` - Work routing rules
- `.squad/decisions.md` - Shared team decisions
- `.squad/agents/{member}/charter.md` - Individual member expertise and coding style
- `.github/copilot-instructions.md` - This session's main output
