# PRD Intake Reference

> How to ingest a Product Requirements Document and decompose it into work items.

## Overview

Squad can read a PRD (Product Requirements Document) and use it as the source of truth for work decomposition, prioritization, and routing.

## Triggers

| User says | Action |
|-----------|--------|
| "here's the PRD" / "work from this spec" | Expect file path or pasted content |
| "read the PRD at {path}" | Read file at that path |
| "the PRD changed" / "updated the spec" | Re-read and diff against previous decomposition |
| (pastes requirements text) | Treat as inline PRD |

## Intake Flow

### 1. Detect Source

- User provides file path → read it
- User pastes text → treat as inline PRD
- Path in team.md → re-read and diff

### 2. Store PRD Reference

Add to `.squad/team.md`:

```markdown
## PRD Source

**File:** {path or "inline"}  
**Updated:** {date}  
**Version:** {version if tracked}  
**Last decomposed:** {date}
```

### 3. Decompose (Lead Spawn)

Spawn **Lead** (sync, standard model) to decompose into work items:

**Spawn template:**

```
agent_type: "general-purpose"
mode: "sync"
description: "🏗️ {Lead}: Decompose PRD into work items"
prompt: |
  You are {Lead}, the Lead on this project.
  
  YOUR CHARTER:
  {paste .squad/agents/{lead}/charter.md}
  
  TEAM ROOT: {team_root}
  
  **Requested by:** {user}
  
  TASK: Read the attached PRD and decompose it into work items.
  
  For each work item:
  - Title (clear, actionable)
  - Description (what needs to happen)
  - Acceptance criteria (how to verify completion)
  - Estimated scope (small/medium/large)
  - Suggested agent role (who should own it)
  - Dependencies (which items must finish first)
  
  PRD:
  {paste full PRD text or file contents}
  
  Do the work. Respond as {Lead}.
```

**Lead produces:**
- Structured work item table
- Dependency graph
- Suggested assignment (which agent owns which items)
- Risk flags

### 4. Present for Approval

Show the coordinator's summary:

```
📋 PRD Decomposition — {count} work items

| # | Title | Scope | Owner | Deps |
|----|-------|-------|-------|------|
| 1 | {title} | small | {role} | — |
| 2 | {title} | medium | {role} | #1 |

Risk flags: {list}

Approve to route work?
```

### 5. Route Approved Items

Once approved:
1. Create GitHub issues for each work item (if connected to repo)
2. Label with `squad` and `squad:{assigned-role}`
3. Route agents respecting dependencies
4. Track progress in PRD source section of team.md

## Mid-Project Updates

If the PRD changes:

1. **Re-read** the new PRD
2. **Diff** against the previous decomposition
3. **Identify** what changed (new items, removed items, scope shifts)
4. **Update** work items in GitHub (close old, create new, retitle existing)
5. **Notify** team of changes

**Spawn Lead (sync) for diff analysis:**

```
You have a previous PRD decomposition (attached). The PRD has been updated (new version attached).

What changed?
- New work items
- Removed/completed items
- Scope shifts in existing items

Recommend action for each change. What should we do?
```

## Work Item Format

Use consistent format for decomposed items:

```markdown
## Item #N: {Title}

**Scope:** {small|medium|large}  
**Owner:** {agent-role}  
**Depends on:** #{list of item numbers} or "none"  

**Description:**
{what needs to happen}

**Acceptance Criteria:**
- [ ] {criterion 1}
- [ ] {criterion 2}

**Notes:**
{risks, blockers, research needed, etc.}
```

## GitHub Integration

When creating GitHub issues from work items:

```bash
gh issue create \
  --title "{Item title}" \
  --body "{Description}\n\n### Acceptance Criteria\n{criteria}" \
  --label "squad,squad:{role}" \
  --assignee "{agent or human name if applicable}"
```

Once issues are created, Ralph can manage triage and assignment automatically.

## Status Tracking

Update PRD source in team.md as work progresses:

```markdown
## PRD Source

**File:** /path/to/prd.md  
**Version:** 1.2 (updated 2026-04-15)  
**Last decomposed:** 2026-04-13  
**Status:** {X} of {Y} items complete
```

## Dependency Management

PRD decomposition should capture ALL dependencies:

```
Item #1 (Setup auth) → Item #2, #3, #4
Item #2 (Login form) → depends on Item #1
Item #3 (Token refresh) → depends on Item #1
Item #4 (API endpoints) → depends on Item #1
```

Lead's spawn should produce a dependency graph showing which items must finish before others can start. Coordinator uses this to route work in parallel where possible.

