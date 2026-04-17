---
name: "nested-repo-hygiene"
description: "Keep a coordination repo clean when the real application lives in a nested git repository."
domain: "repository-management"
confidence: "high"
source: "earned"
tools:
  - name: "powershell"
    description: "Verify root and nested git status before changing ignore rules."
    when: "When repo dirt may come from nested repository boundaries."
---

## Context

Use this when a workspace root contains project-management files and the actual product code lives inside a separate nested git repository. The goal is to remove false-positive repo dirt without damaging the nested repo boundary.

## Patterns

- Check git status at both the workspace root and the nested app repo before changing anything.
- If the root repo is only dirty because the nested repo directory is untracked, ignore the nested repo at the root instead of deleting or flattening it.
- Keep app-facing documentation inside the nested repo, and keep coordination updates in `.squad\`.

## Examples

- Root `.gitignore` entry: `my-project/`
- Nested app repo remains responsible for `my-project\README.md`, source files, and tests.
- Root repo remains responsible for `.squad\taskboard.json`, `.squad\identity\now.md`, and decision inbox files.

## Anti-Patterns

- Do not delete the nested `.git` directory to make root status cleaner.
- Do not start tracking nested app files in the coordination repo by accident.
- Do not "clean" repo dirt before confirming which repository actually owns the files.
