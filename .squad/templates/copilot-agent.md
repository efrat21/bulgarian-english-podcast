# GitHub Copilot Coding Agent Reference

> GitHub Copilot can join the Squad as an autonomous team member. It picks up assigned issues, creates branches, and opens PRs.

## Overview

GitHub Copilot's autonomous coding agent (`@copilot`) can be added to the squad roster as a team member. Unlike AI agents spawned by the Coordinator, `@copilot` works asynchronously through GitHub issue assignment and PR automation.

## Adding @copilot to the Team

When the user says *"add @copilot"* or *"enable the coding agent"*:

1. **Name is always "@copilot"** — no casting, no alternatives
2. **Add to team.md roster:**

   ```markdown
   | @copilot | Coding Agent | — | 🤖 Coding Agent |
   ```

3. **Add capability profile to team.md** (under Coding Agent section):

   ```markdown
   ## Coding Agent

   <!-- copilot-auto-assign: true/false -->

   | Name | Role | Charter | Status |
   |------|------|---------|--------|
   | @copilot | Coding Agent | — | 🤖 Coding Agent |

   ### Capabilities

   **🟢 Good fit — auto-route when enabled:**
   - Bug fixes with clear reproduction steps
   - Test coverage (adding missing tests, fixing flaky tests)
   - Lint/format fixes and code style cleanup
   - Dependency updates and version bumps
   - Small isolated features with clear specs
   - Boilerplate/scaffolding generation
   - Documentation fixes and README updates

   **🟡 Needs review — route but flag for squad member PR review:**
   - Medium features with clear specs and acceptance criteria
   - Refactoring with existing test coverage
   - API endpoint additions following established patterns
   - Migration scripts with well-defined schemas

   **🔴 Not suitable — route to squad member instead:**
   - Architecture decisions and system design
   - Multi-system integration requiring coordination
   - Ambiguous requirements needing clarification
   - Security-critical changes (auth, encryption, access control)
   - Performance-critical paths requiring benchmarking
   - Changes requiring cross-team discussion
   ```

4. **Set auto-assign behavior** (in the HTML comment):

   ```html
   <!-- copilot-auto-assign: false -->
   ```

   - `true` → Issues labeled `squad:copilot` auto-assigned immediately (no Lead triage)
   - `false` → Issues labeled `squad:copilot` require Lead approval before @copilot starts

5. **Update routing.md** with @copilot rules, e.g.:
   - "Bug fixes with clear steps → @copilot"
   - "Test coverage → @copilot"
   - "Architecture decisions → Lead"

6. Acknowledge: *"✅ @copilot joined the team. Auto-assign: {enabled|disabled}."*

## Comparison: @copilot vs. Agents

| Aspect | Agent (Spawned) | @copilot (Autonomous) |
|--------|-----------------|----------------------|
| **Control** | Coordinator spawns on demand | Asynchronous, issue-driven |
| **Assignment** | Via `task` tool | Via issue labels (`squad:copilot`) |
| **Work tracking** | Orchestration log | GitHub issue & PR workflow |
| **Capability gate** | None — agents handle everything | Capability profile (🟢/🟡/🔴) — Lead evaluates |
| **Code review** | Via Scribe or Lead | GitHub PR review (human or Lead reviews PRs) |
| **Branches** | `squad/{issue}-{slug}` | `copilot/{issue}-{slug}` |
| **PR status** | Orchestration log | GitHub PR checks, reviews |

## How @copilot Works

1. **Issue created** → Lead triages (if auto-assign is false, or immediately if true)
2. **Labeled with `squad:copilot`** → @copilot detects (via GitHub webhook or action)
3. **Creates branch** `copilot/{issue-number}-{slug}` from main
4. **Develops solution** asynchronously (not visible in Copilot UI — happens in GitHub)
5. **Opens draft PR** with auto-generated description
6. **Pushes commits** as work progresses
7. **Marks PR ready** when complete
8. **Awaits review** (Lead or GitHub Actions checks)
9. **After approval** → merges automatically (if configured) or awaits manual merge
10. **Closes issue** when PR merges

## Triage: Lead Evaluates Issue Against Capability Profile

When an issue is labeled `squad` (but not yet `squad:copilot`), **Lead triages:**

1. **Read the issue** — title, description, acceptance criteria
2. **Match against capability profile** (above):
   - Is it 🟢 (good fit for @copilot)? → Label `squad:copilot`
   - Is it 🟡 (needs review after)? → Label `squad:copilot` + `needs-review` flag
   - Is it 🔴 (not suitable)? → Label `squad:{agent-name}` (route to a human agent instead)
3. **Comment on the issue** with routing rationale (optional but helpful)

Example comment:
```
🤖 Routing to @copilot — this is a clear bug fix with reproduction steps.
Lead will review the PR before merge.
```

## PR Review Handling

When @copilot opens a PR:

1. **If auto-assign is enabled** and no special flags (🟡 needs-review):
   - GitHub Actions (CI) runs automatically
   - If CI passes → auto-merge (if configured)
   - If CI fails → @copilot is notified (via GitHub workflow)

2. **If labeled 🟡 (needs review)** or **auto-assign is disabled:**
   - Lead (or assigned human reviewer) reviews the PR
   - Approves or requests changes
   - If approved + CI passes → merges

3. **If @copilot encounters an issue:**
   - Opens a comment on the PR
   - Lead is notified
   - Lead decides: merge anyway, request changes, or reassign to a human agent

## Branch & PR Naming

@copilot uses slightly different naming than squad agents:

- **Branch:** `copilot/{issue-number}-{slug}` (not `squad/`)
- **PR title:** Auto-generated from issue title
- **PR description:** Auto-generated, includes "Closes #{issue-number}"

Example:
```
Branch:  copilot/42-fix-auth-timeout
PR:      Fix auth endpoint timeout (#42)
```

## Auto-Merge Configuration

If the repo supports auto-merge, configure in GitHub:

```bash
gh repo edit --enable-auto-merge
```

When enabled and CI is green:
- @copilot PRs auto-merge after approval (if no reviewer gate is set)
- Manual merges still work if auto-merge is disabled for specific PRs

## Disabling @copilot Temporarily

If you want to disable @copilot for a session:

```
Update team.md:
<!-- copilot-auto-assign: false -->

Or in routing.md:
All new issues → Lead (temporarily disable @copilot routing)
```

@copilot stays on the roster but receives no new assignments. Existing draft PRs continue (unless manually closed).

## Removing @copilot from the Team

If you want to remove @copilot:

1. **Remove from team.md** roster
2. **Update routing.md** — all `squad:copilot` routes become `squad:{agent-name}`
3. **Archive open PRs** (close draft PRs, merge approved ones, or reassign)

Acknowledge: *"✅ @copilot removed from the roster."*

## Routing Rules for @copilot

In `.squad/routing.md`, define when to route to @copilot vs. human agents:

```markdown
## Issue Routing

| Issue Type | Assigned to | Notes |
|------------|-------------|-------|
| Bug fix + clear repro | @copilot | Small scope, high confidence |
| Test coverage | @copilot | Test writing is straightforward |
| Dependency update | @copilot | Mechanical, low risk |
| Small feature (clear spec) | @copilot | If < 200 lines code |
| Architecture decision | Lead (human or agent) | Needs discussion, not code |
| Security-critical change | Lead (human or agent) | Requires review first |
| Ambiguous requirement | Lead (human or agent) | Needs clarification before coding |
```

The Lead uses this table during triage to assign labels.

## Example: Bug Fix Lifecycle with @copilot

```
1. User creates issue: "Fix: Login times out after 30 seconds"
   → Auto-labeled `squad` by GitHub workflow

2. Lead triages:
   → Matches "bug fix with clear steps" (🟢)
   → Labels `squad:copilot`

3. @copilot detects label:
   → Creates branch `copilot/42-fix-login-timeout`
   → Starts developing fix
   → Pushes commits

4. Solution ready:
   → Opens PR from `copilot/42-*` to `main`
   → PR description includes "Closes #42"

5. CI runs:
   → Tests pass ✅
   → Linting passes ✅

6. If auto-assign + no review needed:
   → PR auto-merges
   → Issue closes automatically

7. If marked 🟡 (needs-review):
   → Lead reviews PR
   → Approves or requests changes
   → @copilot notified via PR comment
   → Once approved, PR merges
```

