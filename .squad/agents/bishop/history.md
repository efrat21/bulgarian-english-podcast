# Project Context

- **Owner:** efratmiyara-work
- **Project:** App that grabs an article in Bulgarian from the web, translates it to English, and creates a podcast audio file.
- **Stack:** TBD
- **Created:** 2026-04-13T17:28:16.452Z

## Learnings

- Backend work will likely center on fetching, parsing, translation orchestration, and audio handoff.
- `my-project\src\knigovishte_podcast\pipeline.py` is the stable backend seam for fetch → translate → script → audio orchestration.
- Default pipeline runs cache article HTML in `my-project\data\articles\` and always persist scripts in `my-project\data\scripts\` before TTS.
- Minimal CLI exposure for backend integration now lives in `my-project\src\knigovishte_podcast\cli.py` as the `run` subcommand.
- `my-project\tests\test_pipeline.py` covers orchestration wiring, artifact persistence, cached HTML reuse, and CLI run reporting.
