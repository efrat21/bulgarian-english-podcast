# Human Team Members Reference

> Humans can join the Squad roster alongside AI agents. They appear in routing, can be tagged, and the coordinator pauses for their input.

## Overview

A human (e.g., product manager, designer, architect) can be added to the squad roster. They are tracked in `team.md`, can be assigned work or routed for review, and the coordinator pauses for their input when work reaches them.

## Adding a Human Member

When the user says *"add {Name} as {Role}"* or *"I'm joining the team as {Role}"*:

1. **No casting.** Use the human's real name — NOT a fictional character name.
2. **Create team.md entry:**

   ```markdown
   | {Name} | {Role} | — | 👤 Human |
   ```

3. **No charter or history files.** Humans don't get `.squad/agents/{name}/charter.md` or `.squad/agents/{name}/history.md`.
4. **Update routing.md** with human-friendly routing rules (e.g., *"Product review → Brady (human)"*)
5. **Update casting registry** (mark as human, not an agent):

   ```json
   {
     "persistent_name": "{Real Name}",
     "role": "{role}",
     "type": "human",
     "status": "active"
   }
   ```

6. Acknowledge: *"✅ {Name} joined as {Role}."*

## Comparison: Humans vs. Agents

| Aspect | AI Agent | Human |
|--------|----------|-------|
| **Name** | Fictional (cast) | Real name |
| **Charter** | `.squad/agents/{name}/charter.md` | None |
| **History** | `.squad/agents/{name}/history.md` | None |
| **Spawnable** | Yes — via `task` tool | No — coordinator presents work, waits for input |
| **Input mode** | Async background by default | Sync — coordinator blocks until human responds |
| **Parallelism** | Work continues while agent runs | Work continues independently (human is not a blocker) |
| **Work examples** | Implementation, testing, research | Design review, product decisions, code review, approval |

## Routing Work to Humans

When work should go to a human:

1. **Identify human in routing.md:** e.g., *"Product feedback → Brady (human)"*
2. **Present work to human:** Show the specific task, context, and expected decision
3. **Wait for response:** Coordinator blocks until human provides input
4. **Continue with results:** Once human responds, treat their decision as a binding input and continue
5. **Log interaction:** Record in orchestration log that human was consulted

## Sync Interaction

When routing to a human:

```
📌 {Name}, you're up.

Task: {what needs human decision/review}
Context: {relevant details}
Options: {choices if applicable}

Please respond.
```

Coordinator **waits synchronously** for the human to reply. This is different from async agent work.

## Stale Reminder

If the human hasn't responded after 1+ turns:

```
📌 Still waiting on {Name} for {thing}.
```

**Humans are not a blocker for non-dependent work.** While waiting for the human's input, the coordinator can continue spawning agents for independent work.

## Reviewer Role (Humans as Gatekeepers)

If a human is assigned a **Reviewer** role:

- They can **approve** work from agents
- They can **reject** work and require revision
- **Rejection lockout applies:** If a human rejects an agent's work, that agent cannot revise. A different agent must do it.
- The human can reassign the work or escalate.

## Examples

### Example 1: Product Manager Review

```
PRD decomposition complete.

📌 Brady (PM), review these work items.

{table of items}

Approve to proceed, or request changes?
```

Brady responds: *"Approve — ship in order."* or *"Item #3 is out of scope."*

Coordinator continues based on Brady's decision.

### Example 2: Design Review

```
Frontend team has built the login flow.

📌 Alexis (Designer), review for brand compliance.

{link to component preview or screenshots}

Approve or request changes?
```

Alexis responds with feedback. If they request changes, the coordinator routes the revision to a different agent (not the original builder).

### Example 3: Security Approval

```
Authentication module is ready for security audit.

📌 Jordan (Security), approve before merge.

{details of auth implementation}
```

Jordan reviews and either approves or flags issues.

## Logging

Human interactions are logged in the orchestration log:

```markdown
## Interaction: {Name} (Human)

**Role:** {role}  
**Task:** {what was requested}  
**Decision:** {what human decided}  
**Impact:** {what happens next}
```

## No Async Work from Humans

Humans are always treated synchronously. The coordinator NEVER spawns a human as a background task. Humans are consulted, they respond, and the team moves forward.

This keeps the workflow responsive while maintaining the ability for non-dependent agents to continue work in parallel.

