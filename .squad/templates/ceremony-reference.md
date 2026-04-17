# Ceremonies Reference

> Team meetings before or after work. Each squad configures their own in `.squad/ceremonies.md`.

## Overview

Ceremonies are structured team meetings where agents align on decisions, risks, and next steps. They are defined in `.squad/ceremonies.md` and triggered automatically (before/after work) or on demand.

## Structure

Each ceremony has metadata and execution rules:

```yaml
{CeremonyName}:
  trigger: auto | manual
  when: before | after
  condition: "multi-agent task" | "build failure" | "test failure" | "reviewer rejection"
  facilitator: {lead-name}
  participants: all-relevant | all-involved | specific-agents
  time_budget: focused | thorough | extended
  enabled: true | false

  agenda:
    - {step 1}
    - {step 2}
```

- **trigger:** `auto` runs automatically when condition matches; `manual` runs on-demand only
- **when:** `before` runs before work; `after` runs after work completes
- **condition:** triggers ceremony when condition is met (e.g., "multi-agent task involving 2+ agents")
- **facilitator:** who runs the ceremony (usually Lead)
- **participants:** which agents attend
- **time_budget:** how focused vs. thorough the discussion should be
- **enabled:** whether this ceremony is active this session

## Standard Ceremonies

### Design Review

Run BEFORE multi-agent work to align on interfaces and contracts.

```yaml
designReview:
  trigger: auto
  when: before
  condition: "multi-agent task involving 2+ agents modifying shared systems"
  facilitator: lead
  participants: all-relevant
  time_budget: focused
  enabled: true

  agenda:
    1. Review the task and requirements
    2. Agree on interfaces and contracts between components
    3. Identify risks and edge cases
    4. Assign action items
```

**Outcome:** All agents understand the contract. No surprises during implementation.

### Retrospective

Run AFTER work fails to root-cause and plan fixes.

```yaml
retrospective:
  trigger: auto
  when: after
  condition: "build failure, test failure, or reviewer rejection"
  facilitator: lead
  participants: all-involved
  time_budget: focused
  enabled: true

  agenda:
    1. What happened? (facts only)
    2. Root cause analysis
    3. What should change?
    4. Action items for next iteration
```

**Outcome:** Team understands why work failed and what to fix.

### Other Ceremonies

Teams can define custom ceremonies for standups, planning, demos, etc.

## Facilitator Role

The facilitator (usually Lead) runs the ceremony:

1. **Before:** Schedule participants → gather context → run ceremony (sync) → document decisions → include summary in agent spawn prompts
2. **After:** Gather participants → run meeting → root-cause analysis → plan next steps → spawn follow-up agents if needed

Facilitators are spawned with the full agent prompt (charter + history + decisions). The ceremony output is logged to the orchestration log.

## Ceremony Cooldown

After a ceremony runs (before or after), skip auto-check for the immediately following step. This prevents cascading ceremony triggers and keeps the workflow focused.

Example:
- "Before" ceremony runs → agents work → no "after" ceremony check unless condition explicitly matches

## Orchestration Log

Ceremonies are logged to `.squad/orchestration-log/{timestamp}-ceremony-{name}.md`:

```markdown
## {CeremonyName}

**Facilitator:** {lead-name}
**Participants:** {agent1}, {agent2}, ...
**Decisions:** {count}
**Action items:** {list}

### Decisions Made
{summary}

### Action Items
- {item1}
- {item2}
```

## Configuration

Ceremonies are configured in `.squad/ceremonies.md` at the root of `.squad/`. The default set includes Design Review and Retrospective. Teams can customize or add ceremonies as needed.

Coordinator detects ceremony conditions and triggers facilitator spawn. See `.github/agents/squad.agent.md` "Ceremonies" section for full automation rules.

