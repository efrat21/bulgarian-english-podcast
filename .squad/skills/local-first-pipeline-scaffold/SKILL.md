---
name: "local-first-pipeline-scaffold"
description: "How to scaffold a small content-processing app with stable boundaries before provider choices are final."
domain: "architecture"
confidence: "high"
source: "earned"
tools:
  - name: "apply_patch"
    description: "Create the scaffold, interfaces, and supporting docs in one pass."
    when: "The repo is greenfield and the structure matters more than feature completion."
---

## Context

Use this when a project has a clear end-to-end shape but the external providers are still undecided. The goal is to make the next implementation step obvious without locking the team into premature vendor choices.

## Patterns

- Pick a **local-first layout** early so generated artifacts have predictable homes.
- Create **service boundaries** around unstable integrations such as fetching, translation, and TTS.
- Implement only the **deterministic core** if one part of the product contract is already clear.
- Prefer a **stdlib-first scaffold** for the first pass when environment readiness is uncertain.
- Keep README focused on the chosen stack, directory layout, and next concrete step.

## Examples

- `my-project\src\knigovishte_podcast\pipeline.py` wires fetcher, translator, script builder, and audio generator.
- `my-project\src\knigovishte_podcast\services\script_builder.py` implements the fixed podcast script shape while other integrations stay as placeholders.
- `my-project\data\articles\`, `data\scripts\`, and `data\audio\` define the local artifact contract.

## Anti-Patterns

- Hard-coding a translation or TTS vendor before fetch and parsing needs are proven.
- Building the full workflow in one file with no seams for replacement.
- Adding a heavy framework before the command surface is settled.
